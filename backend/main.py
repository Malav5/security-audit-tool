from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
# Import the scanner class from your existing script
from audit_tool import SecurityScanner 

app = FastAPI(
    title="CyberSecure Audit API",
    description="A White-Label API that generates PDF security reports.",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# This defines the data we expect from the frontend
class ScanRequest(BaseModel):
    url: str

def cleanup_file(path: str):
    """Deletes the PDF after sending it to save space."""
    if os.path.exists(path):
        os.remove(path)

@app.post("/generate-audit")
async def generate_audit(request: ScanRequest, background_tasks: BackgroundTasks):
    """
    Takes a URL, runs the scan, generates a PDF, and returns it.
    """
    target_url = request.url
    
    # 1. Initialize the Scanner
    scanner = SecurityScanner(target_url)
    
    # 2. Run the checks
    scanner.check_ports()
    scanner.check_ssl()
    scanner.check_security_headers()
    scanner.check_sensitive_files()
    
    # 3. Generate PDF (This now returns the filename)
    pdf_filename = scanner.generate_report()
    
    # 4. Check if file exists
    if os.path.exists(pdf_filename):
        # Schedule the file to be deleted after the user downloads it
        background_tasks.add_task(cleanup_file, pdf_filename)
        
        # 5. Send the file back to the browser
        return FileResponse(
            path=pdf_filename, 
            filename=pdf_filename, 
            media_type='application/pdf'
        )
    else:
        return {"error": "Failed to generate report"}

@app.get("/")
def home():
    return {"message": "CyberSecure API is Running. Go to /docs to test it."}
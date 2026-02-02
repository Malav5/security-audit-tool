import socket
import requests
import ssl
import sys  # Added for immediate logging
import os
from datetime import datetime
from fpdf import FPDF
import google.generativeai as genai

class AdvancedPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'CyberSecure India - Security Audit Report', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

class SecurityScanner:
    def __init__(self, target_url):
        self.target_url = target_url
        self.hostname = target_url.replace("https://", "").replace("http://", "").split('/')[0]
        self.issues = []

    def get_ai_summary(self, issues_list):
        """
        Sends findings to Gemini and gets an Executive Summary.
        """
        # 1. Get API Key safely
        api_key = os.getenv("GEMINI_API_KEY")
        
        # DEBUG: Check if key exists (Don't print the actual key for security)
        if not api_key:
            print("CRITICAL ERROR: GEMINI_API_KEY is missing from Environment!", file=sys.stderr)
            return "Error: AI API Key is missing. Please add GEMINI_API_KEY to Render Environment."

        if not issues_list:
            return "The security scan detected no major vulnerabilities. The system appears to follow standard security best practices."

        try:
            # 2. Configure Gemini
            genai.configure(api_key=api_key)
            
            # 3. Use the correct model
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            Act as a Senior Cyber Security Consultant.
            I have run an automated scan on a website and found the following issues:
            {issues_list}
            
            Write a concise, 3-sentence Executive Summary for the client.
            Focus on the business risk (e.g., "Data theft," "Reputation damage").
            Do not list the technical fixes yet, just summarize the risk level.
            """
            
            response = model.generate_content(prompt)
            return response.text

        except Exception as e:
            # 4. Force print the error to logs
            print(f"AI GENERATION ERROR: {str(e)}", file=sys.stderr)
            return "Automated analysis unavailable. Please review specific findings below."

    def check_ports(self):
        print(f"[*] Scanning ports for {self.hostname}...")
        common_ports = {
            21: "FTP (File Transfer)",
            22: "SSH (Secure Shell)",
            23: "Telnet (Insecure)",
            80: "HTTP (Web)",
            443: "HTTPS (Secure Web)",
            3306: "MySQL (Database)",
            8080: "Alternative HTTP"
        }
        
        for port, service in common_ports.items():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((self.hostname, port))
            if result == 0:
                self.issues.append({
                    "title": f"Open Port Detected: {port} ({service})",
                    "description": f"Port {port} is open to the public. If this is not intended, close it to prevent unauthorized access."
                })
            sock.close()

    def check_ssl(self):
        print(f"[*] Checking SSL for {self.hostname}...")
        try:
            context = ssl.create_default_context()
            with socket.create_connection((self.hostname, 443)) as sock:
                with context.wrap_socket(sock, server_hostname=self.hostname) as ssock:
                    cert = ssock.getpeercert()
                    # Basic check passed if no error
        except Exception as e:
            self.issues.append({
                "title": "SSL Certificate Issue",
                "description": f"SSL connection failed or certificate is invalid. Error: {str(e)}"
            })

    def check_security_headers(self):
        print(f"[*] Checking headers for {self.target_url}...")
        try:
            # Ensure URL has schema
            url = self.target_url if self.target_url.startswith("http") else f"https://{self.target_url}"
            response = requests.get(url, timeout=5)
            headers = response.headers
            
            missing_headers = []
            if "X-Frame-Options" not in headers:
                missing_headers.append("X-Frame-Options (Clickjacking Protection)")
            if "Content-Security-Policy" not in headers:
                missing_headers.append("Content-Security-Policy (XSS Protection)")
            if "Strict-Transport-Security" not in headers:
                missing_headers.append("HSTS (Enforce HTTPS)")
                
            if missing_headers:
                self.issues.append({
                    "title": "Missing Security Headers",
                    "description": "The following critical headers are missing: " + ", ".join(missing_headers)
                })
        except Exception as e:
            print(f"Header check error: {e}")

    def check_sensitive_files(self):
        # Placeholder for file check logic if you had it
        pass

    def generate_report(self):
        print("[*] Generating PDF Report...")
        
        # 1. Get AI Summary
        issue_titles = [i['title'] for i in self.issues]
        ai_summary_text = self.get_ai_summary(issue_titles)
        
        pdf = AdvancedPDF()
        pdf.add_page()
        
        # --- SECTION 1: HEADER ---
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, f"Security Audit: {self.hostname}", 0, 1, 'C')
        pdf.ln(5)

        # --- SECTION 2: AI EXECUTIVE SUMMARY ---
        pdf.set_font('Arial', 'B', 14)
        pdf.set_text_color(41, 128, 185) # Blue
        pdf.cell(0, 10, "AI-POWERED EXECUTIVE SUMMARY", 0, 1, 'L')
        
        # Grey box for AI text
        pdf.set_fill_color(245, 245, 245)
        pdf.set_font('Arial', '', 11)
        pdf.set_text_color(50, 50, 50)
        
        # Print AI text (multi_cell automatically wraps text)
        pdf.multi_cell(0, 8, ai_summary_text, 0, 'L', True)
        pdf.ln(10)

        # --- SECTION 3: DETAILED FINDINGS ---
        pdf.set_font('Arial', 'B', 14)
        pdf.set_text_color(231, 76, 60) # Red
        pdf.cell(0, 10, "DETAILED VULNERABILITY FINDINGS", 0, 1, 'L')
        pdf.set_text_color(0, 0, 0) # Reset to black
        
        if not self.issues:
            pdf.set_font('Arial', 'I', 12)
            pdf.cell(0, 10, "No high-risk vulnerabilities detected.", 0, 1)
        else:
            for issue in self.issues:
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 8, f"- {issue['title']}", 0, 1)
                
                pdf.set_font('Arial', '', 11)
                pdf.set_x(15) # Indent
                pdf.multi_cell(0, 6, f"{issue['description']}")
                pdf.ln(3)

        # Save File
        filename = f"Audit_Report_{self.hostname}.pdf"
        pdf.output(filename)
        return filename
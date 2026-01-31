# CyberSecure India Scanner

An enterprise-grade Full Stack Security Audit application. This tool allows users to scan websites for common vulnerabilities, check SSL certificates, analyze open ports, and generate comprehensive PDF audit reports.

## 🚀 Features

-   **Deep Security Analysis**: Scans ports, SSL details, security headers, and sensitive files.
-   **PDF Report Generation**: Automatically compiles findings into a professional PDF report.
-   **Modern UI**: Cyber-security themed interface with real-time status updates and animations.
-   **Instant Download**: Report is automatically downloaded upon completion.

## 🛠️ Tech Stack

### Backend
-   **Language**: Python 3.12+
-   **Framework**: FastAPI
-   **Tools**: `socket`, `ssl`, `requests`, `fpdf` (for PDF generation)

### Frontend
-   **Framework**: React (Vite)
-   **Styling**: Tailwind CSS
-   **Icons**: Lucide React
-   **HTTP Client**: Axios
-   **Animations**: Framer Motion

---

## ⚙️ Setup Instructions

### Prerequisites
-   Python 3.12 or higher
-   Node.js & npm

### 1. Backend Setup (FastAPI)

Navigate to the `backend` directory and install dependencies:

```bash
cd backend
pip install -r requirements.txt
```

Start the Backend Server:

```bash
uvicorn main:app --reload
```
*The API will start running at `http://127.0.0.1:8000`*

### 2. Frontend Setup (React + Tailwind)

Navigate to the `frontend` directory and install dependencies:

```bash
cd frontend
npm install
```

Start the Frontend Development Server:

```bash
npm run dev
```
*The App will open at `http://localhost:5173` (or similar)*

---

## 📝 Usage

1.  Ensure both Backend and Frontend terminal windows are running.
2.  Open your browser to the Frontend URL.
3.  Enter a valid URL (e.g., `https://google.com`) in the input field.
4.  Click **Run Scan**.
5.  Wait for the scan to complete. The PDF report will download automatically.

## ⚠️ Disclaimer

This tool is for **educational and authorized security testing purposes only**. Do not use this tool on websites you do not own or do not have explicit permission to test.

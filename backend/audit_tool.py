import requests
import socket
import ssl
import datetime
import certifi
from urllib.parse import urlparse
from fpdf import FPDF
import google.generativeai as genai
import os
import dns.resolver

# --- BRANDING ---
AGENCY_NAME = "CyberSecure India"
AGENCY_SITE = "www.cybersecure-india.com"
REPORT_TITLE = "Comprehensive Security Audit"

# --- COLORS ---
COLOR_HEADER_BG = (41, 128, 185)   # Corporate Blue
COLOR_HEADER_TXT = (255, 255, 255) # White
COLOR_HIGH_RISK = (231, 76, 60)    # Red
COLOR_MEDIUM_RISK = (243, 156, 18) # Orange
COLOR_SAFE = (39, 174, 96)         # Green
COLOR_TEXT_MAIN = (50, 50, 50)     # Dark Gray
COLOR_TEXT_LIGHT = (100, 100, 100) # Light Gray

class AdvancedPDF(FPDF):
    def header(self):
        # Header Background
        self.set_fill_color(*COLOR_HEADER_BG)
        self.rect(0, 0, 210, 45, 'F')
        
        # Agency Name
        self.set_text_color(*COLOR_HEADER_TXT)
        self.set_font('Arial', 'B', 22)
        self.set_xy(10, 12)
        self.cell(0, 10, AGENCY_NAME, 0, 1, 'L')
        
        # Report Title
        self.set_font('Arial', '', 12)
        self.set_xy(10, 22)
        self.cell(0, 10, REPORT_TITLE, 0, 1, 'L')

        # Link to Agency
        self.set_font('Arial', 'U', 10)
        self.set_xy(10, 32)
        self.cell(0, 10, AGENCY_SITE, link=f"https://{AGENCY_SITE}")
        
        # Confidential Stamp
        self.set_font('Arial', 'B', 12)
        self.set_text_color(255, 200, 200)
        self.set_xy(150, 18)
        self.cell(50, 10, "[ CONFIDENTIAL ]", 0, 0, 'C')
        
        self.ln(30)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()} | Automated Assessment by {AGENCY_NAME}', 0, 0, 'C')

    def draw_section_header(self, title):
        self.ln(10)
        self.set_font('Arial', 'B', 14)
        self.set_text_color(44, 62, 80)
        self.cell(0, 10, title.upper(), 0, 1, 'L')
        self.set_fill_color(44, 62, 80)
        self.rect(10, self.get_y(), 190, 1, 'F')
        self.ln(5)

    def add_issue_block(self, title, impact, fix, severity="HIGH"):
        # Select Color based on severity
        if severity == "HIGH":
            self.set_fill_color(*COLOR_HIGH_RISK)
            bg_badge = "CRITICAL"
        elif severity == "MEDIUM":
            self.set_fill_color(*COLOR_MEDIUM_RISK)
            bg_badge = "WARNING"
        else:
            self.set_fill_color(*COLOR_SAFE)
            bg_badge = "INFO"

        # Badge
        current_y = self.get_y()
        self.rect(10, current_y + 2, 22, 6, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 8)
        self.set_xy(10, current_y + 2)
        self.cell(22, 6, bg_badge, 0, 0, 'C')

        # Issue Title
        self.set_xy(35, current_y)
        self.set_text_color(*COLOR_TEXT_MAIN)
        self.set_font('Arial', 'B', 11)
        self.cell(0, 10, title, 0, 1)

        # Impact Section
        self.set_x(10)
        self.set_text_color(*COLOR_TEXT_MAIN)
        self.set_font('Arial', 'B', 9)
        self.cell(15, 6, "Impact:", 0, 0)
        self.set_font('Arial', '', 9)
        self.multi_cell(0, 6, impact)

        # Fix Section
        self.set_x(10)
        self.set_font('Arial', 'B', 9)
        self.set_text_color(41, 128, 185) # Blue for fix
        self.cell(22, 6, "Remediation:", 0, 0)
        self.set_font('Arial', '', 9)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 6, fix)
        
        self.ln(3) # Spacer

class SecurityScanner:
    def __init__(self, target_url):
        if not target_url.startswith(("http://", "https://")):
            self.target_url = "https://" + target_url
        else:
            self.target_url = target_url
        self.parsed_url = urlparse(self.target_url)
        self.hostname = self.parsed_url.netloc
        self.issues = []

    def check_ports(self):
        print("[*] Scanning common ports...")
        # Only scan top 5 dangerous ports to keep it fast
        ports = {
            21: "FTP (File Transfer)",
            22: "SSH (Secure Shell)",
            23: "Telnet (Unencrypted Remote Access)",
            3306: "MySQL Database",
            5432: "PostgreSQL Database"
        }
        for port, name in ports.items():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5) # Very fast timeout
            result = sock.connect_ex((self.hostname, port))
            if result == 0:
                self.issues.append({
                    "title": f"Open Port Detected: {port} ({name})",
                    "severity": "HIGH",
                    "impact": "Exposed ports can allow hackers to brute-force passwords or exploit service vulnerabilities directly.",
                    "fix": f"Close port {port} on your firewall if not absolutely necessary. Use VPNs for remote access."
                })
            sock.close()

    def check_security_headers(self):
        print("[*] Checking HTTP Headers...")
        try:
            resp = requests.get(self.target_url, timeout=5, verify=certifi.where())
            headers = resp.headers
            
            # 1. Clickjacking
            if "X-Frame-Options" not in headers:
                self.issues.append({
                    "title": "Missing Clickjacking Protection (X-Frame-Options)",
                    "severity": "MEDIUM",
                    "impact": "Attackers can embed your website inside an invisible frame (iframe) to trick users into clicking buttons they didn't intend to.",
                    "fix": "Configure your web server to send the 'X-Frame-Options: SAMEORIGIN' header."
                })
            
            # 2. XSS Protection
            if "Content-Security-Policy" not in headers:
                self.issues.append({
                    "title": "Missing Content Security Policy (CSP)",
                    "severity": "MEDIUM",
                    "impact": "Without CSP, your site is vulnerable to Cross-Site Scripting (XSS) and data injection attacks.",
                    "fix": "Implement a 'Content-Security-Policy' header to restrict where scripts and resources can load from."
                })

            # 3. Server Leak
            if "Server" in headers or "X-Powered-By" in headers:
                leaked = headers.get('Server', '') + " " + headers.get('X-Powered-By', '')
                self.issues.append({
                    "title": f"Server Information Disclosure: {leaked.strip()}",
                    "severity": "LOW",
                    "impact": "Revealing exact software versions helps hackers select specific exploits for your server.",
                    "fix": "Configure your server (Nginx/Apache) to hide the 'Server' and 'X-Powered-By' headers."
                })

            # 4. Cookie Security
            if "Set-Cookie" in headers:
                cookies = headers['Set-Cookie']
                if "Secure" not in cookies or "HttpOnly" not in cookies:
                     self.issues.append({
                        "title": "Insecure Cookies Detected",
                        "severity": "MEDIUM",
                        "impact": "Cookies without 'HttpOnly' can be stolen via XSS. Cookies without 'Secure' can be intercepted over Wifi.",
                        "fix": "Set the 'Secure' and 'HttpOnly' flags on all session cookies."
                    })

        except Exception:
            pass # Connection errors handled in main run

    def check_sensitive_files(self):
        print("[*] Checking for sensitive files...")
        # Check robots.txt
        try:
            resp = requests.get(self.target_url + "/robots.txt", timeout=3, verify=certifi.where())
            if resp.status_code == 200:
                if "admin" in resp.text or "backup" in resp.text or "config" in resp.text:
                     self.issues.append({
                        "title": "Sensitive Paths revealed in robots.txt",
                        "severity": "LOW",
                        "impact": "Your robots.txt file is telling hackers exactly where your Admin/Backup folders are.",
                        "fix": "Remove sensitive paths from robots.txt. Use server permissions to block them instead."
                    })
        except:
            pass

    def check_ssl(self):
        print("[*] Verifying SSL...")
        try:
            context = ssl.create_default_context(cafile=certifi.where())
            with socket.create_connection((self.hostname, 443), timeout=3) as sock:
                with context.wrap_socket(sock, server_hostname=self.hostname) as ssock:
                    cert = ssock.getpeercert()
                    # If successful, no issue added.
        except Exception as e:
             self.issues.append({
                "title": "SSL/HTTPS Configuration Error",
                "severity": "HIGH",
                "impact": "Users cannot securely connect to your site. Data is sent in plain text and can be stolen.",
                "fix": "Install a valid SSL Certificate immediately (e.g., Let's Encrypt)."
            })

    def generate_report(self):
        pdf = AdvancedPDF()
        pdf.add_page()
        
        # --- Executive Summary Box ---
        pdf.set_fill_color(240, 240, 240)
        pdf.rect(10, pdf.get_y(), 190, 30, 'F')
        
        pdf.set_xy(15, pdf.get_y() + 5)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 6, f"Target Host: {self.hostname}", 0, 1)
        
        pdf.set_x(15)
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 6, f"Scan Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1)
        
        # Score Logic
        risk_count = len(self.issues)
        pdf.set_xy(150, pdf.get_y() - 12)
        pdf.set_font('Arial', 'B', 24)
        if risk_count == 0:
            pdf.set_text_color(*COLOR_SAFE)
            pdf.cell(40, 10, "A+", 0, 1, 'C')
        elif risk_count < 3:
            pdf.set_text_color(*COLOR_MEDIUM_RISK)
            pdf.cell(40, 10, "B", 0, 1, 'C')
        else:
            pdf.set_text_color(*COLOR_HIGH_RISK)
            pdf.cell(40, 10, "F", 0, 1, 'C')
            
        pdf.ln(20)

        # --- Findings Section ---
        pdf.draw_section_header("Detailed Security Findings")
        
        if not self.issues:
            pdf.set_font('Arial', 'I', 11)
            pdf.cell(0, 10, "Great job! No common vulnerabilities were detected.", 0, 1)
        else:
            # Sort by severity (HIGH first)
            priority = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
            self.issues.sort(key=lambda x: priority.get(x["severity"], 3))
            
            for issue in self.issues:
                pdf.add_issue_block(issue['title'], issue['impact'], issue['fix'], issue['severity'])

        filename = f"Audit_Report_{self.hostname}.pdf"
        pdf.output(filename)
        print(f"\n✅ Report Generated: {filename}")
        return filename

    def check_critical_exposures(self):
        print("[*] Hunting for Critical Config Leaks (.env, .git)...")
        # These are the "Holy Grail" for hackers
        dangerous_files = {
            "/.env": "Environment File (Contains DB passwords & API Keys)",
            "/.git/HEAD": "Git Repository (Contains entire source code history)",
            "/.ds_store": "Mac System File (Reveals directory structure)",
            "/wp-config.php.bak": "WordPress Config Backup",
            "/sitemap.xml": "Sitemap (Not a bug, but reveals site structure)"
        }
        
        for path, name in dangerous_files.items():
            try:
                url = self.target_url.rstrip('/') + path
                resp = requests.get(url, timeout=3, verify=False) # verify=False to catch even if SSL is broken
                
                # If we get a 200 OK and the content looks real
                if resp.status_code == 200:
                    # Validate it's not a custom 404 page by checking content length or keywords
                    if "html" not in resp.headers.get("Content-Type", ""): 
                        self.issues.append({
                            "title": f"CRITICAL EXPOSURE: {name} Found",
                            "severity": "HIGH",
                            "impact": f"This file ({path}) is publicly accessible. Attackers can download it to steal passwords, API keys, or your entire codebase.",
                            "fix": f"Immediately configure your web server (Nginx/Apache) to deny access to {path}."
                        })
            except:
                pass

    def check_email_security(self):
        print("[*] Checking Email Security Records (SPF/DMARC)...")
        try:
            import dns.resolver
            domain = self.hostname
            
            # 1. Check SPF (Sender Policy Framework)
            try:
                answers = dns.resolver.resolve(domain, 'TXT')
                spf_found = False
                for rdata in answers:
                    if "v=spf1" in rdata.to_text():
                        spf_found = True
                        break
                if not spf_found:
                    self.issues.append({
                        "title": "Missing SPF Record (Email Security)",
                        "severity": "MEDIUM",
                        "impact": "You have not authorized any servers to send email for you. Hackers can easily spoof your domain to send phishing emails.",
                        "fix": "Add a TXT record for 'v=spf1' listing your authorized email servers."
                    })
            except:
                # If no TXT records at all
                self.issues.append({
                    "title": "Missing SPF Record (Email Security)",
                    "severity": "MEDIUM",
                    "impact": "No SPF record found. Email spoofing is possible.",
                    "fix": "Create an SPF TXT record."
                })

            # 2. Check DMARC (Domain-based Message Authentication)
            try:
                dmarc_domain = f"_dmarc.{domain}"
                dns.resolver.resolve(dmarc_domain, 'TXT')
                # If this passes, DMARC exists. Good.
            except:
                self.issues.append({
                    "title": "Missing DMARC Record",
                    "severity": "LOW",
                    "impact": "DMARC tells email providers (Gmail/Outlook) what to do if an email fails the SPF check. Without it, spoofed emails might still land in inboxes.",
                    "fix": "Add a TXT record for '_dmarc' to enforce a policy (e.g., 'v=DMARC1; p=none')."
                })

        except ImportError:
            print("Error: dnspython library not installed. Skipping email check.")
        except Exception as e:
            print(f"DNS Check failed: {e}")

    def run(self):
    self.check_ports()
    self.check_ssl()
    self.check_security_headers()
    self.check_sensitive_files()

    # --- THE NEW REAL STUFF ---
    self.check_critical_exposures() # <--- The Source Code Heist
    self.check_email_security()     # <--- The Email Imposter

    self.generate_report()

if __name__ == "__main__":
    target = input("Enter website URL: ")
    scanner = SecurityScanner(target)
    scanner.run()
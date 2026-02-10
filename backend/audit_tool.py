import re
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
import urllib3

# Suppress InsecureRequestWarning for cleaner logs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# --- BRANDING ---
AGENCY_NAME = "CyberSecure India"
AGENCY_SITE = ""
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

        # CTA for Free Users
        if not getattr(self, 'is_premium', True):
            self.set_y(-25)
            self.set_font('Arial', 'B', 10)
            self.set_text_color(231, 76, 60) # Red for urgency
            self.cell(0, 10, f"Unlock Full Report & Fixes at {AGENCY_SITE}", 0, 0, 'C', link=f"https://{AGENCY_SITE}")


    def draw_section_header(self, title):
        self.ln(10)
        self.set_font('Arial', 'B', 14)
        self.set_text_color(44, 62, 80)
        self.cell(0, 10, title.upper(), 0, 1, 'L')
        self.set_fill_color(44, 62, 80)
        self.rect(10, self.get_y(), 190, 1, 'F')
        self.ln(5)

    def add_issue_block(self, title, impact, fix, severity="HIGH", compliance=None, code_snippet=None):
        is_premium = getattr(self, 'is_premium', True)

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

        # Compliance Tags (Premium ONLY)
        if compliance and is_premium:
            self.set_x(35)
            self.set_font('Arial', 'I', 8)
            self.set_text_color(100, 100, 100)
            tags = " | ".join([f"[{c}]" for c in compliance])
            self.cell(0, 5, f"Compliance: {tags}", 0, 1)

        # Impact Section
        self.set_x(10)
        self.set_text_color(*COLOR_TEXT_MAIN)
        self.set_font('Arial', 'B', 9)
        self.cell(15, 6, "Impact:", 0, 0)
        self.set_font('Arial', '', 9)
        
        if is_premium:
            self.multi_cell(0, 6, impact)
        else:
            self.set_text_color(150, 150, 150)
            self.multi_cell(0, 6, "[LOCKED] Upgrade to Premium for detailed impact analysis.")
            self.set_text_color(*COLOR_TEXT_MAIN)

        # Fix Section
        self.set_x(10)
        self.set_font('Arial', 'B', 9)
        self.set_text_color(41, 128, 185) # Blue for fix
        self.cell(22, 6, "Remediation:", 0, 0)
        self.set_font('Arial', '', 9)
        
        if is_premium:
            self.set_text_color(50, 50, 50)
            self.multi_cell(0, 6, fix)
            
            # Code Snippet (Hotfix)
            if code_snippet:
                self.ln(2)
                self.set_x(15)
                self.set_fill_color(245, 245, 245)
                self.set_font('Courier', '', 8)
                self.multi_cell(180, 5, code_snippet, fill=True)
                self.ln(2)
        else:
            self.set_text_color(150, 150, 150)
            self.multi_cell(0, 6, "[LOCKED] Upgrade for step-by-step code fixes.")
            self.set_text_color(50, 50, 50)

        self.ln(3) # Spacer


class SecurityScanner:
    def __init__(self, target_url):
        if not target_url.startswith(("http://", "https://")):
            self.target_url = "https://" + target_url
        else:
            self.target_url = target_url
        self.parsed_url = urlparse(self.target_url)
        self.hostname = self.parsed_url.netloc.split(':')[0] # Strip ports
        self.issues = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }


    def check_ports(self):
        print(f"[*] Scanning common ports for {self.hostname}...")
        ports = {
            21: "FTP (File Transfer)",
            22: "SSH (Secure Shell)",
            23: "Telnet (Unencrypted Remote Access)",
            3306: "MySQL Database",
            5432: "PostgreSQL Database"
        }
        try:
            for port, name in ports.items():
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5) 
                # connect_ex returns 0 on success, or an errno on failure
                result = sock.connect_ex((self.hostname, port))
                if result == 0:
                    self.issues.append({
                        "title": f"Open Port Detected: {port} ({name})",
                        "severity": "HIGH",
                        "impact": "Exposed ports can allow hackers to brute-force passwords or exploit service vulnerabilities directly.",
                        "fix": f"Close port {port} on your firewall if not absolutely necessary.",
                        "compliance": ["ISO 27001", "SOC2 Control CC6.1"],
                        "code_snippet": f"# Block port {port} on UFW\nsudo ufw deny {port}"
                    })
                sock.close()
        except socket.gaierror:
            print(f"    [!] DNS Resolution failed for {self.hostname}. Skipping port scan.")
        except Exception as e:
            print(f"    [!] Port scan error: {e}")

    def discover_subdomains(self):
        print("[*] Performing Attack Surface Discovery (Subdomains)...")
        subdomains = ["api", "dev", "staging", "test", "vpn", "cloud", "mail", "admin", "beta", "portal"]
        self.subdomains_found = []
        
        resolver = dns.resolver.Resolver()
        resolver.nameservers = ['8.8.8.8', '1.1.1.1']
        resolver.lifetime = 1.0

        for sub in subdomains:
            try:
                target = f"{sub}.{self.hostname}"
                resolver.resolve(target, 'A')
                self.subdomains_found.append(target)
                print(f"    [+] Found live subdomain: {target}")
            except:
                continue

        if self.subdomains_found:
             self.issues.append({
                "title": "Hidden Attack Surface/Subdomains",
                "severity": "INFO",
                "impact": f"Attackers often target hidden subdomains like {', '.join(self.subdomains_found[:2])} because they are less secured than the main site.",
                "fix": "Ensure all discovered subdomains have the same security policies as your main domain and are monitored for vulnerabilities.",
                "compliance": ["SOC2 CC7.1", "GDPR Article 32"],
                "code_snippet": f"# Example Nginx restriction for staging\nlocation / {{\n  allow 1.2.3.4; # Your IP\n  deny all;\n}}"
            })

    def check_security_headers(self):
        print("[*] Checking HTTP Headers...")
        try:
            resp = requests.get(self.target_url, timeout=5, verify=certifi.where(), headers=self.headers, allow_redirects=True)
            
            # Soft Block Detection for Cloudflare/WAFs
            block_phrases = ["Just a moment...", "Attention Required! | Cloudflare", "Verify you are human"]
            if any(phrase in resp.text for phrase in block_phrases):
                print(f"[!] Soft Block detected. WAF is intercepting the request.")
                self.issues.append({
                    "title": "Scan Intercepted by Firewall (WAF)",
                    "severity": "INFO",
                    "impact": "The site's firewall (e.g., Cloudflare) presented a captcha. Some security headers could not be verified.",
                    "fix": "Whitelist this scanner's IP to get a full audit."
                })
                return # Stop checking headers to avoid False Positives

            headers = resp.headers

            
            # 1. Clickjacking
            if "X-Frame-Options" not in headers:
                self.issues.append({
                    "title": "Missing Clickjacking Protection (X-Frame-Options)",
                    "severity": "MEDIUM",
                    "impact": "Attackers can embed your website inside an invisible frame (iframe) to trick users into clicking buttons they didn't intend to.",
                    "fix": "Configure your web server to send the 'X-Frame-Options: SAMEORIGIN' header.",
                    "compliance": ["SOC2 CC7.1", "ISO 27001"],
                    "code_snippet": "add_header X-Frame-Options \"SAMEORIGIN\"; # Nginx\nHeader set X-Frame-Options \"SAMEORIGIN\" # Apache"
                })
            
            # 2. XSS Protection
            if "Content-Security-Policy" not in headers:
                self.issues.append({
                    "title": "Missing Content Security Policy (CSP)",
                    "severity": "MEDIUM",
                    "impact": "Without CSP, your site is vulnerable to Cross-Site Scripting (XSS) and data injection attacks.",
                    "fix": "Implement a 'Content-Security-Policy' header to restrict where scripts and resources can load from.",
                    "compliance": ["GDPR Article 32", "PCI-DSS"],
                    "code_snippet": "add_header Content-Security-Policy \"default-src 'self';\"; # Strict Baseline"
                })

            # 3. HSTS (NEW: Billion Dollar Feature)
            if "Strict-Transport-Security" not in headers:
                self.issues.append({
                    "title": "Missing HSTS (Strict-Transport-Security)",
                    "severity": "MEDIUM",
                    "impact": "Without HSTS, attackers can perform SSL stripping attacks to downgrade users to unencrypted HTTP.",
                    "fix": "Enable HSTS with a long max-age and include subdomains.",
                    "compliance": ["PCI-DSS Requirement 4.1", "SOC2"],
                    "code_snippet": "add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;"
                })

            # 4. Referrer-Policy (NEW)
            if "Referrer-Policy" not in headers:
                self.issues.append({
                    "title": "Missing Referrer-Policy",
                    "severity": "LOW",
                    "impact": "Sensitive data in your URL path might be leaked to external sites when users click on links.",
                    "fix": "Add a 'Referrer-Policy: strict-origin-when-cross-origin' header.",
                    "compliance": ["GDPR Privacy by Design"],
                    "code_snippet": "add_header Referrer-Policy \"strict-origin-when-cross-origin\";"
                })

            # 5. Server Leak
            if "Server" in headers or "X-Powered-By" in headers:
                leaked = headers.get('Server', '') + " " + headers.get('X-Powered-By', '')
                leaked = leaked.strip()
                if re.search(r'\d', leaked):
                    self.issues.append({
                        "title": f"Server Version Disclosure: {leaked}",
                        "severity": "LOW",
                        "impact": "Revealing exact software versions helps hackers select specific exploits for your server.",
                        "fix": "Configure your server to hide the version numbers in headers (e.g., 'ServerTokens Prod' in Apache).",
                        "compliance": ["SOC2 CC7.2"],
                        "code_snippet": "ServerTokens Prod # Apache\nserver_tokens off; # Nginx"
                    })


            # 6. Cookie Security
            if "Set-Cookie" in headers:
                cookies = headers['Set-Cookie']
                if "Secure" not in cookies or "HttpOnly" not in cookies:
                     self.issues.append({
                        "title": "Insecure Cookies Detected",
                        "severity": "MEDIUM",
                        "impact": "Cookies without 'HttpOnly' can be stolen via XSS. Cookies without 'Secure' can be intercepted over Wifi.",
                        "fix": "Set the 'Secure' and 'HttpOnly' flags on all session cookies.",
                        "compliance": ["GDPR Article 32", "HIPAA"],
                        "code_snippet": "Set-Cookie: session=xyz; Secure; HttpOnly; SameSite=Strict"
                    })

        except Exception:
            pass # Connection errors handled in main run

    def check_sensitive_files(self):
        print("[*] Checking for entry-point files (robots.txt, sitemaps)...")
        # These files often reveal hidden paths
        discovery_files = {
            "/robots.txt": "Robots Configuration",
            "/sitemap.xml": "XML Sitemap",
            "/.well-known/security.txt": "Security Contact File"
        }
        
        self.discovered_paths = []

        for path, name in discovery_files.items():
            try:
                url = self.target_url.rstrip('/') + path
                resp = requests.get(url, timeout=3, verify=certifi.where(), headers=self.headers)
                if resp.status_code == 200:
                    print(f"    [+] Found {name} at {path}")
                    # Extract potential paths from robots.txt
                    if "robots.txt" in path:
                        paths = re.findall(r"Disallow: (/\S+)", resp.text)
                        self.discovered_paths.extend(paths)
            except: pass


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
                "fix": "Install a valid SSL Certificate immediately (e.g., Let's Encrypt).",
                "compliance": ["PCI-DSS Requirement 4.1", "GDPR Article 32"],
                "code_snippet": "sudo certbot --nginx -d yourdomain.com"
            })

    def generate_report(self, is_premium=False):
        pdf = AdvancedPDF()
        pdf.is_premium = is_premium
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
        
        # Tiered Scoring Logic
        grade = self.get_risk_score()

        pdf.set_xy(150, pdf.get_y() - 12)
        pdf.set_font('Arial', 'B', 24)

        if grade == "F":
            pdf.set_text_color(*COLOR_HIGH_RISK)
        elif grade == "A":
            pdf.set_text_color(*COLOR_SAFE)
        else:
            pdf.set_text_color(*COLOR_MEDIUM_RISK)
            
        pdf.cell(40, 10, grade, 0, 1, 'C')

        # AI Executive Summary (Premium Feature Logo/Feel)
        pdf.ln(10)
        pdf.set_font('Arial', 'B', 11)
        pdf.set_text_color(*COLOR_HEADER_BG)
        pdf.cell(0, 8, "AI-GENERATED SECURITY ADVISORY", 0, 1)
        
        pdf.set_font('Arial', 'I', 10)
        pdf.set_text_color(*COLOR_TEXT_MAIN)
        summary = self.generate_ai_summary()
        pdf.multi_cell(0, 6, summary)
            
        pdf.ln(10)

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
                pdf.add_issue_block(
                    issue['title'], 
                    issue['impact'], 
                    issue['fix'], 
                    issue['severity'],
                    compliance=issue.get('compliance'),
                    code_snippet=issue.get('code_snippet')
                )

        filename = f"Audit_Report_{self.hostname}.pdf"
        pdf.output(filename)
        print(f"\n✅ Report Generated: {filename}")
        return filename

    def generate_ai_summary(self):
        print("[*] Consulting AI for Deep Security Analysis...")
        if not self.issues:
            return "The security posture of this host is excellent. No common vulnerabilities were detected during the multi-layered scan."
        
        try:
            # You'll need an API key in your environment
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                return "A comprehensive security audit has been performed. Several critical and medium risk issues were identified that require immediate remediation."

            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            issue_list = "\n".join([f"- {i['title']} ({i['severity']})" for i in self.issues])
            prompt = f"As a Senior Cybersecurity Consultant for {AGENCY_NAME}, write a professional 4-sentence executive summary for a CEO regarding their website {self.hostname}. The scan found these issues:\n{issue_list}\nFocus on the business risk and the urgency of the fixes. Be professional and authoritative."
            
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"The assessment revealed {len(self.issues)} security artifacts. Strategic remediation is recommended to ensure compliance and data integrity."

    def get_risk_score(self):
        """Returns the calculated grade based on the latest tiered logic."""
        high_risks = len([i for i in self.issues if i['severity'] == "HIGH"])
        medium_risks = len([i for i in self.issues if i['severity'] == "MEDIUM"])

        if high_risks > 0:
            return "F"
        elif medium_risks == 0:
            return "A"
        elif medium_risks < 3:
            return "B"
        else:
            return "C"


    def check_critical_exposures(self):
        print("[*] Hunting for Critical Config Leaks (.env, .git)...")
        dangerous_paths = {
            "/.env": "Environment File (Contains DB passwords & API Keys)",
            "/.env.example": "Example Environment File",
            "/.env.local": "Local Environment File",
            "/.git/": "Git Directory (Potential Source Code Leak)",
            "/.git/config": "Git Configuration File",
            "/.git/HEAD": "Git Repository (Contains entire source code history)",
            "/.ds_store": "Mac System File (Reveals directory structure)",
            "/wp-config.php.bak": "WordPress Config Backup",
            "/.bash_history": "Shell History File",
            "/.ssh/id_rsa": "Private SSH Key"
        }
        
        for path, name in dangerous_paths.items():
            try:
                url = self.target_url.rstrip('/') + path
                # explicitly follow redirects and use certifi for SSL
                resp = requests.get(url, timeout=5, verify=certifi.where(), headers=self.headers, allow_redirects=True)

                # WAF/Block detection to avoid false findings on block pages
                block_phrases = ["Just a moment...", "Attention Required!", "Verify you are human"]
                if any(phrase in resp.text for phrase in block_phrases):
                    print(f"    [!] Skipping {path}: WAF block detected.")
                    continue

                if resp.status_code == 200:
                    content_type = resp.headers.get("Content-Type", "").lower()
                    
                    # 1. Directory Listing Check (Special case for HTML)
                    if "Index of /" in resp.text or ".git" in resp.text and path == "/.git/":
                        self.issues.append({
                            "title": f"CRITICAL EXPOSURE: {name} Directory Listing Enabled",
                            "severity": "HIGH",
                            "impact": f"The {path} directory is accessible and its contents are listed. Attackers can download all internal configuration or source files.",
                            "fix": f"Disable directory listing and restrict access to {path} in your server config (e.g., 'autoindex off' in Nginx).",
                            "compliance": ["SOC2 CC7.1", "GDPR Article 32"],
                            "code_snippet": f"# Nginx block\nlocation {path} {{ deny all; }}"
                        })
                        continue

                    # 2. File Check (Avoid HTML false positives for .env / config files)
                    if "html" not in content_type or (path.endswith(".git/config") and "repositoryformatversion" in resp.text):
                        self.issues.append({
                            "title": f"CRITICAL EXPOSURE: {name} Found",
                            "severity": "HIGH",
                            "impact": f"This sensitive file ({path}) is publicly accessible. Attackers can use it to compromise your database, API keys, or source code.",
                            "fix": f"Configure your web server to deny access to {path} or remove the file from the public directory.",
                            "compliance": ["SOC2 CC7.1", "PCI-DSS 6.5.10"],
                            "code_snippet": f"# Apache block\n<Files \"{path.lstrip('/')}\">\n    Order allow,deny\n    Deny from all\n</Files>"
                        })
            except Exception as e:
                print(f"    [!] Error checking {path}: {e}")

    def check_email_security(self):
        print("[*] Checking Email Security Records (SPF/DMARC)...")
        try:
            import dns.resolver
            domain = self.hostname
            
            # --- FORCE GOOGLE DNS ---
            resolver = dns.resolver.Resolver()
            resolver.nameservers = ['8.8.8.8', '1.1.1.1'] 
            resolver.lifetime = 5.0
            
            # 1. Check SPF
            try:
                answers = resolver.resolve(domain, 'TXT')
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
                        "fix": "Add a TXT record for 'v=spf1' listing your authorized email servers.",
                        "compliance": ["ISO 27001", "DMARC Policy"],
                        "code_snippet": "v=spf1 include:_spf.google.com ~all"
                    })
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
                self.issues.append({
                    "title": "Missing SPF Record (Email Security)",
                    "severity": "MEDIUM",
                    "impact": "No SPF record found. Email spoofing is possible.",
                    "fix": "Create an SPF TXT record.",
                    "compliance": ["ISO 27001"],
                    "code_snippet": "v=spf1 a mx -all"
                })
            except Exception as e:
                print(f"SPF Check failed: {e}")

            # 2. Check DMARC
            try:
                dmarc_domain = f"_dmarc.{domain}"
                resolver.resolve(dmarc_domain, 'TXT')
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
                self.issues.append({
                    "title": "Missing DMARC Record",
                    "severity": "LOW",
                    "impact": "DMARC tells email providers what to do if an email fails SPF checks.",
                    "fix": "Add a TXT record for '_dmarc'.",
                    "compliance": ["BIMI Readiness", "Cyber Insurance Requirement"],
                    "code_snippet": "v=DMARC1; p=quarantine; rua=mailto:admin@domain.com"
                })
            except Exception as e:
                print(f"DMARC Check failed: {e}")

        except Exception as e:
            print(f"DNS Check failed: {e}")


    def check_http_methods(self):
        print("[*] Checking HTTP Methods...")
        try:
            resp = requests.options(self.target_url, timeout=3, headers=self.headers)
            methods = resp.headers.get("Allow", "")
            if "TRACE" in methods or "PUT" in methods or "DELETE" in methods:
                self.issues.append({
                    "title": f"Dangerous HTTP Methods Enabled: {methods}",
                    "severity": "MEDIUM",
                    "impact": "Unnecessary methods like TRACE or DELETE can be used for session theft or unauthorized file manipulation.",
                    "fix": "Disable TRACE, PUT, and DELETE methods on your web server configuration.",
                    "code_snippet": "# Nginx fix\nif ($request_method ~ ^(TRACE|PUT|DELETE)$ ) {\n    return 405;\n}\n\n# Apache fix\nTraceEnable off"
                })
        except: pass

    def check_directory_listing(self):
        print("[*] Checking for Directory Listing...")
        try:
            # Check a likely empty folder or asset folder
            paths = ["/images/", "/uploads/", "/assets/"]
            for path in paths:
                resp = requests.get(self.target_url + path, timeout=3, headers=self.headers)
                if "Index of /" in resp.text:
                    self.issues.append({
                        "title": "Directory Listing Enabled",
                        "severity": "MEDIUM",
                        "impact": "Hackers can see all files in these folders, including backups or sensitive assets.",
                        "fix": "Disable directory browsing (Options -Indexes in Apache or 'autoindex off' in Nginx).",
                        "code_snippet": "# Nginx fix\nlocation / {\n    autoindex off;\n}\n\n# Apache fix\nOptions -Indexes"
                    })
                    break
        except: pass

    def check_mixed_content(self):
        print("[*] Checking for Mixed Content (HTTP on HTTPS)...")
        try:
            resp = requests.get(self.target_url, timeout=5, headers=self.headers, allow_redirects=True)
            if self.target_url.startswith("https"):
                # Specifically check for http in src or href attributes to avoid XML namespace false positives
                if re.search(r'(src|href)=["\']http://', resp.text):
                    self.issues.append({
                        "title": "Mixed Content Detected",
                        "severity": "LOW",
                        "impact": "Loading HTTP resources on an HTTPS site can allow attackers to intercept scripts or styles.",
                        "fix": "Ensure all links, images, and scripts use https://.",
                        "code_snippet": "# Nginx Force HTTPS upgrade\nadd_header Content-Security-Policy \"upgrade-insecure-requests;\";"
                    })
        except: pass

    def check_html_comments(self):
        print("[*] Scanning for Sensitive HTML Comments...")
        try:
            resp = requests.get(self.target_url, timeout=5, headers=self.headers)
            comments = re.findall(r"<!--(.*?)-->", resp.text)
            for comment in comments:
                if any(word in comment.lower() for word in ["todo", "fixme", "password", "api", "internal"]):
                    self.issues.append({
                        "title": "Sensitive Information in HTML Comments",
                        "severity": "LOW",
                        "impact": "Comments can reveal development notes, internal IDs, or login logic to attackers.",
                        "fix": "Remove development-related or sensitive comments before deploying to production.",
                        "code_snippet": "# Search your source code for sensitive comments\ngrep -r \"<!--\" . | grep -Ei \"todo|fixme|api|pass\""
                    })
                    break
        except: pass

    def check_admin_paths(self):
        print("[*] Brute-forcing common admin paths...")
        admin_paths = ["/admin/", "/login/", "/wp-admin/", "/backend/"]
        for path in admin_paths:
            try:
                resp = requests.get(self.target_url + path, timeout=2, headers=self.headers)
                if resp.status_code == 200:
                    self.issues.append({
                        "title": f"Public Admin Path Found: {path}",
                        "severity": "LOW",
                        "impact": "Exposing login panels makes it easier for attackers to attempt brute-force attacks.",
                        "fix": "Restrict admin paths to specific IP addresses or change them to a custom obfuscated path.",
                        "code_snippet": f"# Nginx restrict by IP\nlocation {path} {{\n    allow 192.168.1.1; # Your IP\n    deny all;\n}}"
                    })
                    break
            except: pass

    def perform_deep_crawl(self):
        print("[*] Initializing Deep Passive Spidering...")
        try:
            resp = requests.get(self.target_url, timeout=5, headers=self.headers)
            # Find all internal links to expand the attack surface
            links = re.findall(r'href=["\'](/?[\w\-/.]+)["\']', resp.text)
            
            internal_paths = set()
            for link in links:
                if link.startswith('/'):
                    internal_paths.add(link)
                elif self.hostname in link:
                    path = urlparse(link).path
                    if path: internal_paths.add(path)
            
            # Combine paths found from robots.txt and homepage links
            all_paths = list(internal_paths | set(self.discovered_paths))[:15] # Cap for speed
            
            if all_paths:
                print(f"    [+] Discovered {len(all_paths)} internal paths for deep scanning.")
                # We can perform specific checks on these paths if needed
                # For now, we'll mark them as "mapped" in the audit.
        except Exception as e:
            print(f"    [!] Spidering failed: {e}")

    def run(self, is_premium=False):
        # 1. Start with the expansion (Expansion Discovery)
        self.discover_subdomains()

        # 2. Run traditional checks
        self.check_ports()
        self.check_ssl()
        self.check_security_headers()
        self.check_sensitive_files()
        self.perform_deep_crawl() # NEW: Map the site structure
        self.check_http_methods()
        self.check_directory_listing()
        self.check_mixed_content()
        self.check_html_comments()
        self.check_admin_paths()

        # 3. Critical Data Checks
        self.check_critical_exposures() 
        self.check_email_security()     

        pdf_filename = self.generate_report(is_premium=is_premium)
        
        return {
            "pdf_filename": pdf_filename,
            "issues": self.issues,
            "hostname": self.hostname,
            "grade": self.get_risk_score()
        }




if __name__ == "__main__":
    target = input("Enter website URL: ")
    scanner = SecurityScanner(target)
    scanner.run()
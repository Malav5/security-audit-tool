"""
Enhanced Security Scanner using Selenium
Provides deeper analysis of JavaScript-heavy sites and client-side security
"""

import time
import json
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager


class SeleniumSecurityScanner:
    """
    Advanced security scanner using Selenium for JavaScript-rendered content
    and client-side security analysis
    """
    
    def __init__(self, url: str, headless: bool = True):
        self.url = url if url.startswith('http') else f'https://{url}'
        self.hostname = urlparse(self.url).netloc
        self.headless = headless
        self.driver = None
        self.findings = []
        
    def _setup_driver(self):
        """Initialize Selenium WebDriver with security-focused options"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless=new')
        
        # Security and performance options
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # User agent to appear as normal browser
        chrome_options.add_argument(
            'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        # Initialize driver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.set_page_load_timeout(30)
        
        # Execute CDP commands to hide automation
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": self.driver.execute_script("return navigator.userAgent").replace('Headless', '')
        })
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def check_client_side_security(self) -> List[Dict]:
        """Analyze client-side security configurations"""
        findings = []
        
        try:
            # Check for sensitive data in localStorage
            local_storage = self.driver.execute_script(
                "return Object.keys(localStorage).map(key => ({key: key, value: localStorage.getItem(key)}));"
            )
            
            sensitive_patterns = ['token', 'password', 'secret', 'api_key', 'auth', 'session']
            for item in local_storage:
                key_lower = item['key'].lower()
                if any(pattern in key_lower for pattern in sensitive_patterns):
                    findings.append({
                        'title': 'Sensitive Data in LocalStorage',
                        'severity': 'HIGH',
                        'impact': f'Sensitive key "{item["key"]}" found in localStorage. This data is accessible to JavaScript and vulnerable to XSS attacks.',
                        'fix': 'Store sensitive data in httpOnly cookies or server-side sessions instead of localStorage.',
                        'compliance': ['OWASP A3:2021', 'PCI-DSS 3.4']
                    })
            
            # Check cookies security
            cookies = self.driver.get_cookies()
            for cookie in cookies:
                issues = []
                
                if not cookie.get('secure'):
                    issues.append('not marked as Secure')
                if not cookie.get('httpOnly'):
                    issues.append('not marked as HttpOnly')
                if cookie.get('sameSite') not in ['Strict', 'Lax']:
                    issues.append('missing SameSite attribute')
                
                if issues:
                    findings.append({
                        'title': f'Insecure Cookie: {cookie["name"]}',
                        'severity': 'MEDIUM',
                        'impact': f'Cookie "{cookie["name"]}" is {", ".join(issues)}. This increases vulnerability to XSS and CSRF attacks.',
                        'fix': 'Set cookies with Secure, HttpOnly, and SameSite=Strict attributes.',
                        'compliance': ['OWASP A5:2021', 'GDPR Article 32']
                    })
            
            # Check for inline JavaScript (potential XSS vector)
            inline_scripts = self.driver.find_elements(By.XPATH, "//script[not(@src)]")
            if len(inline_scripts) > 5:
                findings.append({
                    'title': 'Excessive Inline JavaScript',
                    'severity': 'LOW',
                    'impact': f'Found {len(inline_scripts)} inline script tags. Inline scripts bypass CSP protection and increase XSS risk.',
                    'fix': 'Move JavaScript to external files and implement a strict Content Security Policy.',
                    'compliance': ['OWASP A3:2021']
                })
            
            # Check for console errors (may reveal security issues)
            logs = self.driver.get_log('browser')
            severe_errors = [log for log in logs if log['level'] == 'SEVERE']
            if severe_errors:
                findings.append({
                    'title': 'JavaScript Console Errors Detected',
                    'severity': 'LOW',
                    'impact': f'Found {len(severe_errors)} severe JavaScript errors. These may reveal implementation details or security misconfigurations.',
                    'fix': 'Review and fix JavaScript errors. Implement proper error handling.',
                    'compliance': ['OWASP A6:2021']
                })
                
        except Exception as e:
            print(f"Error in client-side security check: {e}")
        
        return findings
    
    def check_form_security(self) -> List[Dict]:
        """Analyze forms for security vulnerabilities"""
        findings = []
        
        try:
            forms = self.driver.find_elements(By.TAG_NAME, 'form')
            
            for idx, form in enumerate(forms):
                form_action = form.get_attribute('action') or 'same-page'
                form_method = form.get_attribute('method') or 'GET'
                
                # Check for forms submitting over HTTP
                if form_action.startswith('http://'):
                    findings.append({
                        'title': f'Form Submitting Over HTTP (Form #{idx + 1})',
                        'severity': 'HIGH',
                        'impact': f'Form submits to {form_action} over unencrypted HTTP. Credentials and sensitive data can be intercepted.',
                        'fix': 'Change form action to use HTTPS protocol.',
                        'compliance': ['PCI-DSS 4.1', 'OWASP A2:2021']
                    })
                
                # Check for password fields without autocomplete=off
                password_fields = form.find_elements(By.CSS_SELECTOR, 'input[type="password"]')
                for pwd_field in password_fields:
                    autocomplete = pwd_field.get_attribute('autocomplete')
                    if autocomplete != 'off' and autocomplete != 'new-password':
                        findings.append({
                            'title': 'Password Field Allows Autocomplete',
                            'severity': 'MEDIUM',
                            'impact': 'Password fields allow browser autocomplete, which may store credentials insecurely.',
                            'fix': 'Add autocomplete="new-password" or autocomplete="off" to password fields.',
                            'compliance': ['OWASP A7:2021']
                        })
                
                # Check for CSRF token presence in POST forms
                if form_method.upper() == 'POST':
                    csrf_tokens = form.find_elements(By.CSS_SELECTOR, 
                        'input[name*="csrf"], input[name*="token"], input[name="_token"]')
                    if not csrf_tokens:
                        findings.append({
                            'title': f'Missing CSRF Protection (Form #{idx + 1})',
                            'severity': 'HIGH',
                            'impact': 'POST form lacks CSRF token. Vulnerable to Cross-Site Request Forgery attacks.',
                            'fix': 'Implement CSRF tokens for all state-changing forms.',
                            'compliance': ['OWASP A1:2021', 'CWE-352']
                        })
                        
        except Exception as e:
            print(f"Error in form security check: {e}")
        
        return findings
    
    def check_exposed_admin_paths(self) -> List[Dict]:
        """Check for exposed admin/sensitive paths"""
        findings = []
        
        admin_paths = [
            '/admin', '/administrator', '/wp-admin', '/admin.php',
            '/phpmyadmin', '/admin/login', '/admin/dashboard',
            '/api/admin', '/api/v1/admin', '/backend', '/panel'
        ]
        
        try:
            for path in admin_paths:
                test_url = urljoin(self.url, path)
                self.driver.get(test_url)
                time.sleep(1)
                
                # Check if we got redirected or got a 404
                current_url = self.driver.current_url
                page_title = self.driver.title.lower()
                
                # Look for admin-related keywords
                admin_keywords = ['admin', 'login', 'dashboard', 'control panel', 'management']
                if any(keyword in page_title for keyword in admin_keywords):
                    findings.append({
                        'title': f'Exposed Admin Panel: {path}',
                        'severity': 'MEDIUM',
                        'impact': f'Admin interface accessible at {test_url}. This exposes the login page to brute-force attacks.',
                        'fix': 'Restrict admin panel access by IP whitelist or move to non-standard path. Implement rate limiting.',
                        'compliance': ['OWASP A1:2021', 'CWE-425']
                    })
                    break  # Found one, no need to check more
                    
        except Exception as e:
            print(f"Error checking admin paths: {e}")
        
        # Return to original URL
        try:
            self.driver.get(self.url)
        except:
            pass
            
        return findings
    
    def check_javascript_libraries(self) -> List[Dict]:
        """Check for vulnerable JavaScript libraries"""
        findings = []
        
        try:
            # Get all script sources
            scripts = self.driver.find_elements(By.TAG_NAME, 'script')
            script_sources = [s.get_attribute('src') for s in scripts if s.get_attribute('src')]
            
            # Known vulnerable library patterns
            vulnerable_patterns = {
                'jquery-1.': 'jQuery 1.x (outdated, multiple XSS vulnerabilities)',
                'jquery-2.': 'jQuery 2.x (outdated, security issues)',
                'angular.js/1.0': 'AngularJS 1.0 (multiple security vulnerabilities)',
                'angular.js/1.1': 'AngularJS 1.1 (multiple security vulnerabilities)',
                'bootstrap/3.': 'Bootstrap 3.x (XSS vulnerabilities)',
            }
            
            for src in script_sources:
                for pattern, description in vulnerable_patterns.items():
                    if pattern in src.lower():
                        findings.append({
                            'title': f'Vulnerable JavaScript Library Detected',
                            'severity': 'MEDIUM',
                            'impact': f'Using {description}. Source: {src}',
                            'fix': 'Update to the latest stable version of the library.',
                            'compliance': ['OWASP A6:2021', 'CWE-1035']
                        })
            
            # Check for unminified libraries in production
            unminified = [src for src in script_sources if '.js' in src and '.min.js' not in src]
            if len(unminified) > 3:
                findings.append({
                    'title': 'Unminified JavaScript in Production',
                    'severity': 'LOW',
                    'impact': f'Found {len(unminified)} unminified JavaScript files. This exposes source code and slows page load.',
                    'fix': 'Use minified versions of JavaScript libraries in production.',
                    'compliance': ['OWASP A6:2021']
                })
                
        except Exception as e:
            print(f"Error checking JavaScript libraries: {e}")
        
        return findings
    
    def take_screenshot(self, filename: str = None) -> str:
        """Take a screenshot for evidence"""
        if not filename:
            filename = f"{self.hostname}_screenshot.png"
        
        try:
            self.driver.save_screenshot(filename)
            return filename
        except Exception as e:
            print(f"Error taking screenshot: {e}")
            return None
    
    def run_scan(self) -> Dict:
        """Run complete Selenium-based security scan"""
        print(f"[SELENIUM SCANNER] Starting enhanced scan for {self.url}")
        
        try:
            self._setup_driver()
            
            # Load the page
            print(f"[SELENIUM SCANNER] Loading page...")
            self.driver.get(self.url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            time.sleep(2)  # Additional wait for dynamic content
            
            # Run all checks
            print(f"[SELENIUM SCANNER] Running client-side security checks...")
            self.findings.extend(self.check_client_side_security())
            
            print(f"[SELENIUM SCANNER] Analyzing forms...")
            self.findings.extend(self.check_form_security())
            
            print(f"[SELENIUM SCANNER] Checking for exposed admin paths...")
            self.findings.extend(self.check_exposed_admin_paths())
            
            print(f"[SELENIUM SCANNER] Analyzing JavaScript libraries...")
            self.findings.extend(self.check_javascript_libraries())
            
            # Take screenshot
            screenshot_path = self.take_screenshot()
            
            print(f"[SELENIUM SCANNER] Scan complete. Found {len(self.findings)} issues.")
            
            return {
                'hostname': self.hostname,
                'findings': self.findings,
                'screenshot': screenshot_path,
                'scan_type': 'selenium_enhanced'
            }
            
        except Exception as e:
            print(f"[SELENIUM SCANNER] Error during scan: {e}")
            return {
                'hostname': self.hostname,
                'findings': self.findings,
                'error': str(e),
                'scan_type': 'selenium_enhanced'
            }
        
        finally:
            if self.driver:
                self.driver.quit()


# Example usage
if __name__ == "__main__":
    scanner = SeleniumSecurityScanner("example.com", headless=True)
    results = scanner.run_scan()
    
    print(f"\n{'='*60}")
    print(f"SELENIUM SECURITY SCAN RESULTS")
    print(f"{'='*60}")
    print(f"Target: {results['hostname']}")
    print(f"Findings: {len(results['findings'])}")
    print(f"\nDetailed Findings:")
    
    for idx, finding in enumerate(results['findings'], 1):
        print(f"\n{idx}. {finding['title']}")
        print(f"   Severity: {finding['severity']}")
        print(f"   Impact: {finding['impact']}")
        print(f"   Fix: {finding['fix']}")

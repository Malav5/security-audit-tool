# Selenium-Enhanced Security Scanning Guide

## Overview

This guide explains how to use Selenium to enhance your security audit tool with browser-based analysis capabilities.

## 🎯 What Selenium Adds to Your Security Audit

### Traditional HTTP Scanning (Current)
- ✅ Headers analysis
- ✅ SSL/TLS checks
- ✅ Port scanning
- ✅ Static file detection
- ❌ JavaScript-rendered content
- ❌ Client-side security
- ❌ Dynamic forms
- ❌ Browser storage analysis

### Selenium-Enhanced Scanning (New)
- ✅ All traditional checks PLUS:
- ✅ **JavaScript-rendered content** (SPAs, React, Vue, Angular)
- ✅ **Client-side security** (localStorage, sessionStorage, cookies)
- ✅ **Dynamic form analysis** (CSRF tokens, autocomplete)
- ✅ **JavaScript library vulnerabilities**
- ✅ **Console errors and warnings**
- ✅ **Screenshot evidence**
- ✅ **Exposed admin panels** (interactive testing)

---

## 📦 Installation

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This will install:
- `selenium>=4.16.0` - Browser automation framework
- `webdriver-manager>=4.0.1` - Automatic ChromeDriver management

### 2. Install Chrome/Chromium

**macOS:**
```bash
brew install --cask google-chrome
```

**Linux:**
```bash
sudo apt-get update
sudo apt-get install -y chromium-browser
```

**Windows:**
Download from https://www.google.com/chrome/

---

## 🚀 Usage

### Option 1: Standalone Selenium Scanner

```python
from selenium_scanner import SeleniumSecurityScanner

# Create scanner instance
scanner = SeleniumSecurityScanner("example.com", headless=True)

# Run scan
results = scanner.run_scan()

# View findings
for finding in results['findings']:
    print(f"[{finding['severity']}] {finding['title']}")
    print(f"Impact: {finding['impact']}")
    print(f"Fix: {finding['fix']}\n")
```

### Option 2: Hybrid Scanner (Recommended)

```python
from hybrid_scanner import HybridSecurityScanner

# Create hybrid scanner
scanner = HybridSecurityScanner("example.com")

# Run with Selenium enabled
results = scanner.run_full_scan(use_selenium=True, is_premium=True)

# Results include both HTTP and Selenium findings
print(f"Total issues: {len(results['issues'])}")
print(f"Grade: {results['grade']}")
```

### Option 3: Command Line

```bash
# HTTP scan only (fast)
python hybrid_scanner.py example.com

# Full scan with Selenium (thorough)
python hybrid_scanner.py example.com --selenium
```

---

## 🔍 Security Checks Performed by Selenium

### 1. Client-Side Security Analysis

**What it checks:**
- Sensitive data in `localStorage` (tokens, passwords, API keys)
- Cookie security attributes (Secure, HttpOnly, SameSite)
- Inline JavaScript (CSP bypass risk)
- JavaScript console errors

**Example Finding:**
```
Title: Sensitive Data in LocalStorage
Severity: HIGH
Impact: Token "auth_token" found in localStorage. Vulnerable to XSS.
Fix: Store sensitive data in httpOnly cookies instead.
Compliance: OWASP A3:2021, PCI-DSS 3.4
```

### 2. Form Security Analysis

**What it checks:**
- Forms submitting over HTTP (credential theft risk)
- Password fields with autocomplete enabled
- Missing CSRF tokens in POST forms
- Form validation bypass opportunities

**Example Finding:**
```
Title: Missing CSRF Protection (Form #1)
Severity: HIGH
Impact: POST form lacks CSRF token. Vulnerable to CSRF attacks.
Fix: Implement CSRF tokens for all state-changing forms.
Compliance: OWASP A1:2021, CWE-352
```

### 3. Exposed Admin Paths

**What it checks:**
- Common admin paths (/admin, /wp-admin, /phpmyadmin)
- Admin login pages accessible without authentication
- Management interfaces exposed to public

**Example Finding:**
```
Title: Exposed Admin Panel: /admin
Severity: MEDIUM
Impact: Admin interface accessible. Exposed to brute-force attacks.
Fix: Restrict by IP whitelist or implement rate limiting.
Compliance: OWASP A1:2021, CWE-425
```

### 4. JavaScript Library Vulnerabilities

**What it checks:**
- Outdated jQuery versions (1.x, 2.x)
- Vulnerable AngularJS versions
- Outdated Bootstrap versions
- Unminified libraries in production

**Example Finding:**
```
Title: Vulnerable JavaScript Library Detected
Severity: MEDIUM
Impact: Using jQuery 1.x (outdated, multiple XSS vulnerabilities)
Fix: Update to jQuery 3.x or newer.
Compliance: OWASP A6:2021, CWE-1035
```

---

## ⚙️ Configuration Options

### Headless vs. Headed Mode

```python
# Headless (faster, for production)
scanner = SeleniumSecurityScanner("example.com", headless=True)

# Headed (for debugging, see browser actions)
scanner = SeleniumSecurityScanner("example.com", headless=False)
```

### Custom User Agent

The scanner automatically uses a realistic user agent to avoid detection:
```
Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) 
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
```

### Screenshot Capture

```python
# Take screenshot for evidence
screenshot_path = scanner.take_screenshot("evidence.png")
```

---

## 🔒 About CAPTCHA Handling

### Important Legal & Ethical Considerations

**✅ Legitimate Use:**
- Testing your own websites
- Authorized penetration testing (with written permission)
- Internal security audits

**❌ Not Recommended:**
- Bypassing CAPTCHAs on third-party sites without permission
- Automated scraping of protected content
- Circumventing security measures you don't own

### CAPTCHA Bypass Techniques (For Authorized Testing Only)

If you have **explicit permission** to test a site with CAPTCHAs:

#### 1. Manual Solving (Recommended)
```python
# Pause for manual CAPTCHA solving
input("Please solve the CAPTCHA manually, then press Enter...")
```

#### 2. CAPTCHA Solving Services (Paid)
```python
# Example with 2Captcha API (requires API key)
from twocaptcha import TwoCaptcha

solver = TwoCaptcha('YOUR_API_KEY')
result = solver.recaptcha(sitekey='SITE_KEY', url='TARGET_URL')
```

#### 3. Headless Browser Detection Bypass
```python
# Already implemented in selenium_scanner.py
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
```

### Our Recommendation

**For security auditing, we recommend:**
1. **Request CAPTCHA-free test accounts** from the site owner
2. **Use API endpoints** instead of web scraping when available
3. **Test in staging environments** without CAPTCHA protection
4. **Focus on authorized testing** only

---

## 🎯 Integration with Main Application

### Update main.py to Support Selenium

```python
from hybrid_scanner import HybridSecurityScanner

@app.post("/generate-audit")
async def generate_audit(
    request: ScanRequest, 
    background_tasks: BackgroundTasks,
    authorization: Optional[str] = Header(None),
    use_selenium: bool = False  # New parameter
):
    # ... existing auth code ...
    
    # Use hybrid scanner instead of SecurityScanner
    scanner = HybridSecurityScanner(target_url)
    results = scanner.run_full_scan(
        use_selenium=use_selenium and is_premium,  # Only for premium users
        is_premium=is_premium
    )
    
    # ... rest of the code ...
```

### Update Frontend to Enable Selenium

```javascript
// In api.js
export const generateAudit = async (url, token = null, useSelenium = false) => {
    const config = { headers: {} };
    if (token) {
        config.headers['Authorization'] = `Bearer ${token}`;
    }
    
    const response = await api.post('/generate-audit', { 
        url, 
        use_selenium: useSelenium 
    }, config);
    return response.data;
};
```

```jsx
// In App.jsx - Add toggle for Selenium scanning
const [useSelenium, setUseSelenium] = useState(false);

// In the form
<label>
    <input 
        type="checkbox" 
        checked={useSelenium} 
        onChange={(e) => setUseSelenium(e.target.checked)}
        disabled={!session}
    />
    Enable Deep Scan (Selenium) - Premium Only
</label>
```

---

## 📊 Performance Considerations

### Scan Times

| Scan Type | Average Time | Findings |
|-----------|-------------|----------|
| HTTP Only | 10-30 seconds | 5-15 issues |
| Selenium Enhanced | 45-90 seconds | 10-25 issues |

### Resource Usage

- **Memory**: ~200-500 MB per scan (Chrome browser)
- **CPU**: Moderate (browser rendering)
- **Disk**: Minimal (screenshots only)

### Optimization Tips

1. **Use headless mode** for production
2. **Limit concurrent scans** (max 2-3 simultaneous)
3. **Cache ChromeDriver** (webdriver-manager handles this)
4. **Set timeouts** to prevent hanging scans

---

## 🐛 Troubleshooting

### Issue: ChromeDriver not found

**Solution:**
```bash
# webdriver-manager will auto-download, but you can force it:
pip install --upgrade webdriver-manager
```

### Issue: Chrome not found

**Solution:**
```bash
# macOS
brew install --cask google-chrome

# Linux
sudo apt-get install chromium-browser
```

### Issue: Selenium scan hangs

**Solution:**
```python
# Add timeout in selenium_scanner.py
self.driver.set_page_load_timeout(30)  # Already implemented
```

### Issue: "DevToolsActivePort file doesn't exist"

**Solution:**
```python
# Add these options (already in selenium_scanner.py):
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
```

---

## 🔐 Security Best Practices

### 1. Rate Limiting
```python
import time

# Add delay between scans
time.sleep(2)  # Already implemented
```

### 2. User Agent Rotation
```python
# Use realistic user agents (already implemented)
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64)...',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...',
]
```

### 3. Respect robots.txt
```python
import requests

def check_robots_txt(url):
    robots_url = f"{url}/robots.txt"
    response = requests.get(robots_url)
    # Parse and respect rules
```

---

## 📈 Future Enhancements

Consider adding:
- [ ] Proxy support for anonymity
- [ ] Multiple browser support (Firefox, Safari)
- [ ] Parallel scanning for multiple pages
- [ ] Advanced XSS payload testing
- [ ] SQL injection detection
- [ ] API endpoint discovery
- [ ] Subdomain enumeration via browser
- [ ] Cookie manipulation testing

---

## 📚 Additional Resources

- **Selenium Documentation**: https://www.selenium.dev/documentation/
- **OWASP Testing Guide**: https://owasp.org/www-project-web-security-testing-guide/
- **WebDriver Manager**: https://github.com/SergeyPirogov/webdriver_manager
- **Chrome DevTools Protocol**: https://chromedevtools.github.io/devtools-protocol/

---

## 📞 Support

For issues or questions:
1. Check this guide first
2. Review Selenium documentation
3. Check browser console for errors
4. Verify Chrome/ChromeDriver compatibility

---

**Last Updated**: February 4, 2026  
**Version**: 1.0  
**Author**: CyberSecure India Development Team

# Selenium Security Scanner - Quick Reference

## 🚀 Quick Start

### Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Run Basic Scan
```bash
python selenium_scanner.py
```

### Run Hybrid Scan
```bash
# HTTP only (fast)
python hybrid_scanner.py example.com

# With Selenium (thorough)
python hybrid_scanner.py example.com --selenium
```

---

## 📋 Common Use Cases

### 1. Scan a Single Page Application (SPA)
```python
from selenium_scanner import SeleniumSecurityScanner

scanner = SeleniumSecurityScanner("https://react-app.com", headless=True)
results = scanner.run_scan()

print(f"Found {len(results['findings'])} issues")
```

### 2. Check for Sensitive Data in Browser Storage
```python
# Automatically checks localStorage, sessionStorage, and cookies
scanner = SeleniumSecurityScanner("https://example.com")
results = scanner.run_scan()

# Filter for storage-related findings
storage_issues = [f for f in results['findings'] 
                  if 'localStorage' in f['title'] or 'Cookie' in f['title']]
```

### 3. Analyze Form Security
```python
# Checks for CSRF tokens, autocomplete, HTTP submission
scanner = SeleniumSecurityScanner("https://example.com/login")
results = scanner.run_scan()

form_issues = [f for f in results['findings'] if 'Form' in f['title']]
```

### 4. Detect Vulnerable JavaScript Libraries
```python
# Scans for outdated jQuery, Angular, Bootstrap, etc.
scanner = SeleniumSecurityScanner("https://example.com")
results = scanner.run_scan()

lib_issues = [f for f in results['findings'] if 'Library' in f['title']]
```

### 5. Take Screenshot for Evidence
```python
scanner = SeleniumSecurityScanner("https://example.com")
scanner._setup_driver()
scanner.driver.get("https://example.com")

# Take screenshot
screenshot_path = scanner.take_screenshot("evidence.png")
print(f"Screenshot saved to: {screenshot_path}")

scanner.driver.quit()
```

---

## 🎯 What Gets Checked

| Category | Checks | Severity |
|----------|--------|----------|
| **Client Storage** | Sensitive data in localStorage | HIGH |
| | Insecure cookie attributes | MEDIUM |
| **Forms** | Missing CSRF tokens | HIGH |
| | HTTP form submission | HIGH |
| | Password autocomplete | MEDIUM |
| **JavaScript** | Vulnerable libraries (jQuery 1.x, etc.) | MEDIUM |
| | Unminified code in production | LOW |
| **Admin Access** | Exposed admin panels | MEDIUM |
| | Unprotected management interfaces | MEDIUM |
| **Errors** | JavaScript console errors | LOW |
| | Inline scripts (CSP bypass) | LOW |

---

## ⚡ Performance Tips

### Faster Scans
```python
# Use headless mode
scanner = SeleniumSecurityScanner(url, headless=True)

# Skip admin path checks (saves ~10 seconds)
# Comment out in selenium_scanner.py:
# self.findings.extend(self.check_exposed_admin_paths())
```

### Parallel Scanning
```python
from concurrent.futures import ThreadPoolExecutor

urls = ["site1.com", "site2.com", "site3.com"]

def scan_site(url):
    scanner = SeleniumSecurityScanner(url)
    return scanner.run_scan()

# Scan up to 3 sites simultaneously
with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(scan_site, urls))
```

---

## 🔧 Customization

### Add Custom Security Check
```python
# In selenium_scanner.py, add new method:

def check_custom_vulnerability(self) -> List[Dict]:
    """Your custom security check"""
    findings = []
    
    try:
        # Your check logic here
        element = self.driver.find_element(By.ID, "sensitive-data")
        if element.is_displayed():
            findings.append({
                'title': 'Custom Vulnerability Found',
                'severity': 'HIGH',
                'impact': 'Description of the impact',
                'fix': 'How to fix it',
                'compliance': ['OWASP A1:2021']
            })
    except:
        pass
    
    return findings

# Then call it in run_scan():
self.findings.extend(self.check_custom_vulnerability())
```

### Change Timeout Settings
```python
# In selenium_scanner.py, modify _setup_driver():

self.driver.set_page_load_timeout(60)  # Increase from 30 to 60 seconds
```

### Add More Admin Paths
```python
# In selenium_scanner.py, modify check_exposed_admin_paths():

admin_paths = [
    '/admin', '/administrator', '/wp-admin',
    '/admin.php', '/phpmyadmin', '/admin/login',
    '/your-custom-path',  # Add your paths here
]
```

---

## 🐛 Common Issues & Fixes

### Issue: "ChromeDriver not found"
```bash
pip install --upgrade webdriver-manager
```

### Issue: Scan takes too long
```python
# Reduce timeout
self.driver.set_page_load_timeout(15)  # Default is 30

# Or skip slow checks
# Comment out check_exposed_admin_paths() call
```

### Issue: "Element not found"
```python
# Add explicit wait
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

wait = WebDriverWait(self.driver, 10)
element = wait.until(EC.presence_of_element_located((By.ID, "myElement")))
```

### Issue: Memory usage too high
```python
# Limit concurrent scans
max_concurrent = 2  # Instead of 5+

# Close driver after each scan
scanner.driver.quit()
```

---

## 📊 Output Format

### Findings Structure
```python
{
    'title': 'Vulnerability Name',
    'severity': 'HIGH' | 'MEDIUM' | 'LOW',
    'impact': 'Description of the security impact',
    'fix': 'How to remediate this issue',
    'compliance': ['OWASP A1:2021', 'PCI-DSS 4.1']
}
```

### Results Structure
```python
{
    'hostname': 'example.com',
    'findings': [...],  # List of findings
    'screenshot': 'path/to/screenshot.png',
    'scan_type': 'selenium_enhanced'
}
```

---

## 🔒 Legal & Ethical Use

### ✅ DO:
- Test your own websites
- Get written permission for penetration testing
- Use in authorized security audits
- Respect rate limits and robots.txt

### ❌ DON'T:
- Bypass CAPTCHAs on sites you don't own
- Perform unauthorized security testing
- Use for malicious purposes
- Ignore terms of service

---

## 📞 Quick Help

| Problem | Solution |
|---------|----------|
| Slow scans | Use headless mode, reduce timeout |
| High memory | Limit concurrent scans, close drivers |
| Chrome errors | Update Chrome, reinstall webdriver-manager |
| Missing findings | Enable all checks, increase wait times |
| False positives | Review findings manually, adjust thresholds |

---

## 🎓 Learning Resources

- **Selenium Docs**: https://selenium.dev/documentation
- **OWASP Guide**: https://owasp.org/www-project-web-security-testing-guide
- **Chrome DevTools**: https://developer.chrome.com/docs/devtools

---

**Quick Reference v1.0** | Last Updated: Feb 2026

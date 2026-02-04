"""
Integration module to combine traditional HTTP scanning with Selenium-based scanning
"""

from audit_tool import SecurityScanner
from selenium_scanner import SeleniumSecurityScanner
from typing import Dict, List


class HybridSecurityScanner:
    """
    Combines traditional HTTP-based scanning with Selenium browser automation
    for comprehensive security analysis
    """
    
    def __init__(self, url: str):
        self.url = url
        self.http_scanner = SecurityScanner(url)
        self.selenium_scanner = None
        
    def run_full_scan(self, use_selenium: bool = False, is_premium: bool = True) -> Dict:
        """
        Run comprehensive security scan
        
        Args:
            use_selenium: Whether to include Selenium-based checks (slower but more thorough)
            is_premium: Whether this is a premium scan
            
        Returns:
            Combined results from both scanners
        """
        print(f"\n{'='*60}")
        print(f"HYBRID SECURITY SCAN STARTING")
        print(f"{'='*60}")
        print(f"Target: {self.url}")
        print(f"Selenium Enabled: {use_selenium}")
        print(f"Premium Mode: {is_premium}")
        print(f"{'='*60}\n")
        
        # Run traditional HTTP scan
        print("[1/2] Running traditional HTTP-based security scan...")
        http_results = self.http_scanner.run(is_premium=is_premium)
        
        all_findings = http_results['issues']
        
        # Run Selenium scan if enabled
        if use_selenium:
            print("\n[2/2] Running Selenium-based browser security scan...")
            try:
                self.selenium_scanner = SeleniumSecurityScanner(self.url, headless=True)
                selenium_results = self.selenium_scanner.run_scan()
                
                # Merge findings
                selenium_findings = selenium_results.get('findings', [])
                all_findings.extend(selenium_findings)
                
                print(f"\n✓ Selenium scan added {len(selenium_findings)} additional findings")
                
            except Exception as e:
                print(f"\n✗ Selenium scan failed: {e}")
                print("  Continuing with HTTP scan results only...")
        
        # Update results
        http_results['issues'] = all_findings
        http_results['total_issues'] = len(all_findings)
        http_results['scan_type'] = 'hybrid' if use_selenium else 'http_only'
        
        # Recalculate grade based on all findings
        http_results['grade'] = self._calculate_grade(all_findings)
        
        print(f"\n{'='*60}")
        print(f"SCAN COMPLETE")
        print(f"{'='*60}")
        print(f"Total Issues Found: {len(all_findings)}")
        print(f"Overall Grade: {http_results['grade']}")
        print(f"{'='*60}\n")
        
        return http_results
    
    def _calculate_grade(self, findings: List[Dict]) -> str:
        """Calculate overall security grade based on findings"""
        if not findings:
            return 'A'
        
        high_count = sum(1 for f in findings if f.get('severity') == 'HIGH')
        medium_count = sum(1 for f in findings if f.get('severity') == 'MEDIUM')
        
        if high_count >= 3:
            return 'F'
        elif high_count >= 1 or medium_count >= 5:
            return 'C'
        elif medium_count >= 2:
            return 'B'
        else:
            return 'A'


# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python hybrid_scanner.py <url> [--selenium]")
        sys.exit(1)
    
    url = sys.argv[1]
    use_selenium = '--selenium' in sys.argv
    
    scanner = HybridSecurityScanner(url)
    results = scanner.run_full_scan(use_selenium=use_selenium, is_premium=True)
    
    print("\nDetailed Findings:")
    for idx, finding in enumerate(results['issues'], 1):
        print(f"\n{idx}. [{finding['severity']}] {finding['title']}")
        print(f"   {finding['impact']}")

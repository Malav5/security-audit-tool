"""
Tier-based PDF generator - Shows different content based on subscription level
"""

from fpdf import FPDF
from datetime import datetime
from typing import List, Dict

class TieredPDFGenerator(FPDF):
    """PDF generator that adapts content based on subscription tier"""
    
    def __init__(self, tier: str = "free"):
        super().__init__()
        self.tier = tier
        self.set_auto_page_break(auto=True, margin=15)
        
    def clean_text(self, text):
        """Removes non-latin-1 characters to prevent PDF generation errors."""
        if not isinstance(text, str): return str(text)
        return text.encode('latin-1', 'ignore').decode('latin-1')
        
    def header(self):
        """Premium PDF Header"""
        # Blue Header Banner
        self.set_fill_color(41, 128, 185)
        self.rect(0, 0, 210, 40, 'F')
        
        self.set_xy(10, 12)
        self.set_font('Arial', 'B', 22)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, 'CYBERSECURE INDIA', 0, 0, 'L')
        
        self.set_font('Arial', 'B', 10)
        self.set_text_color(200, 230, 255)
        self.set_xy(160, 13)
        self.cell(40, 10, '[ CONFIDENTIAL ]', 0, 0, 'R')
        
        self.ln(35)
        
    def footer(self):
        """PDF Footer"""
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
        
    def add_upgrade_notice(self):
        """Add upgrade notice for free tier"""
        self.set_fill_color(255, 243, 205)
        self.set_draw_color(255, 193, 7)
        self.rect(10, self.get_y(), 190, 30, 'DF')
        
        self.set_font('Arial', 'B', 12)
        self.set_text_color(255, 152, 0)
        self.cell(0, 8, 'Upgrade to See Full Report', 0, 1, 'C')
        
        self.set_font('Arial', '', 9)
        self.set_text_color(100, 100, 100)
        self.multi_cell(0, 5, 
            'This is a limited preview. Upgrade to Basic ($29/mo) or higher to access:\n'
            '• All security findings (currently showing 3 of X)\n'
            '• Detailed fix instructions with code snippets\n'
            '• Compliance mapping (OWASP, PCI-DSS, GDPR)\n'
            '• Selenium-based browser security checks',
            0, 'C')
        self.ln(5)
        
    def add_tier_badge(self):
        """Add subscription tier badge"""
        tier_colors = {
            'free': (158, 158, 158),
            'basic': (0, 188, 212),
            'professional': (156, 39, 176),
            'enterprise': (255, 152, 0)
        }
        
        tier_names = {
            'free': 'FREE PREVIEW',
            'basic': 'BASIC PLAN',
            'professional': 'PROFESSIONAL',
            'enterprise': 'ENTERPRISE'
        }
        
        color = tier_colors.get(self.tier, (128, 128, 128))
        name = tier_names.get(self.tier, 'FREE')
        
        self.set_fill_color(*color)
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 8)
        
        # Draw badge
        x = self.w - 50
        y = 10
        self.set_xy(x, y)
        self.cell(35, 6, name, 0, 0, 'C', True)
        
    def add_title_section(self, hostname: str, grade: str, scan_date: str):
        """Add modern summary dashboard section"""
        hostname = self.clean_text(hostname)
        grade = self.clean_text(grade)
        scan_date = self.clean_text(scan_date)
        
        self.add_tier_badge()
        
        # Summary Card Background
        self.set_fill_color(245, 247, 250)
        self.rect(10, self.get_y(), 190, 45, 'F')
        
        start_y = self.get_y()
        self.set_xy(15, start_y + 8)
        
        # Labels
        self.set_font('Arial', 'B', 14)
        self.set_text_color(44, 62, 80)
        self.cell(0, 10, f'Target: {hostname}', 0, 1)
        
        self.set_x(15)
        self.set_font('Arial', '', 10)
        self.set_text_color(127, 140, 141)
        self.cell(0, 6, f'Audit Timestamp: {scan_date}', 0, 1)
        
        # Huge Grade on the Right
        grade_colors = {
            'A': (39, 174, 96),
            'B': (139, 195, 74),
            'C': (243, 156, 18),
            'D': (230, 126, 34),
            'F': (231, 76, 60)
        }
        color = grade_colors.get(grade, (127, 140, 141))
        
        self.set_xy(160, start_y + 8)
        self.set_font('Arial', 'B', 32)
        self.set_text_color(*color)
        self.cell(30, 25, grade, 0, 1, 'C')
        
        self.set_xy(10, start_y + 45 + 10)
        
    def add_executive_summary(self, total_issues: int, high: int, medium: int, low: int):
        """Add executive summary"""
        self.set_font('Arial', 'B', 16)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, 'Executive Summary', 0, 1)
        
        self.set_font('Arial', '', 11)
        self.set_text_color(60, 60, 60)
        
        # Summary boxes
        box_width = 45
        box_height = 25
        spacing = 5
        start_x = 10
        
        summaries = [
            ('Total Issues', str(total_issues), (100, 100, 100)),
            ('High Risk', str(high), (244, 67, 54)),
            ('Medium Risk', str(medium), (255, 152, 0)),
            ('Low Risk', str(low), (33, 150, 243))
        ]
        
        y_pos = self.get_y()
        
        for i, (label, value, color) in enumerate(summaries):
            x_pos = start_x + (i * (box_width + spacing))
            
            # Draw box
            self.set_fill_color(*color)
            self.rect(x_pos, y_pos, box_width, box_height, 'F')
            
            # Add text
            self.set_xy(x_pos, y_pos + 5)
            self.set_font('Arial', 'B', 20)
            self.set_text_color(255, 255, 255)
            self.cell(box_width, 8, value, 0, 0, 'C')
            
            self.set_xy(x_pos, y_pos + 15)
            self.set_font('Arial', '', 9)
            self.cell(box_width, 5, label, 0, 0, 'C')
        
        self.set_y(y_pos + box_height + 10)
        
    def add_findings_section(self, findings: List[Dict], tier: str):
        """Add findings section with tier-based filtering"""
        self.add_page()
        
        # Filter findings based on tier
        if tier == "free":
            # Show only 3 high-severity findings
            findings = [f for f in findings if f.get('severity') == 'HIGH'][:3]
            self.add_upgrade_notice()
        elif tier == "basic":
            # Show all findings but no code snippets
            pass
        # Professional and Enterprise show everything
        
        self.set_font('Arial', 'B', 16)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, 'Security Findings', 0, 1)
        
        if not findings:
            self.set_font('Arial', 'I', 11)
            self.set_text_color(100, 100, 100)
            self.cell(0, 10, 'No security issues found. Great job!', 0, 1)
            return
        
        for idx, finding in enumerate(findings, 1):
            self._add_finding(idx, finding, tier)
            
        # Add upgrade CTA for free tier
        if tier == "free":
            self.ln(10)
            self.add_upgrade_notice()
            
    def _add_finding(self, number: int, finding: Dict, tier: str):
        """Add individual finding"""
        severity = self.clean_text(finding.get('severity', 'UNKNOWN'))
        title = self.clean_text(finding.get('title', 'Unknown Issue'))
        impact = self.clean_text(finding.get('impact', 'No description available'))
        fix = self.clean_text(finding.get('fix', 'No fix available'))
        compliance = [self.clean_text(c) for c in finding.get('compliance', [])]
        
        # Severity color
        severity_colors = {
            'HIGH': (244, 67, 54),
            'MEDIUM': (255, 152, 0),
            'LOW': (33, 150, 243)
        }
        color = severity_colors.get(severity, (128, 128, 128))
        
        # Finding Block Styling
        self.ln(8)
        # Background for the finding card
        self.set_fill_color(252, 253, 255)
        rect_y = self.get_y()
        self.rect(10, rect_y, 190, 60, 'F') # Approx height, will adjust or use better flow
        
        # Vertical Severity Sidebar
        self.set_fill_color(*color)
        self.rect(10, rect_y, 2, 60, 'F')

        self.set_xy(15, rect_y + 5)
        self.set_font('Arial', 'B', 12)
        self.set_text_color(44, 62, 80)
        self.multi_cell(0, 8, f'{number}. {title}')
        
        # Severity Badge
        self.set_x(15)
        self.set_fill_color(*color)
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 8)
        self.cell(20, 6, severity, 0, 1, 'C', True)
        self.ln(4)
        
        # Impact
        self.set_font('Arial', 'B', 10)
        self.set_text_color(0, 0, 0)
        self.cell(0, 6, 'Impact:', 0, 1)
        
        self.set_font('Arial', '', 10)
        self.set_text_color(60, 60, 60)
        self.multi_cell(0, 5, impact)
        self.ln(2)
        
        # Fix instructions (limited for free tier)
        if tier == "free":
            self.set_font('Arial', 'I', 9)
            self.set_text_color(100, 100, 100)
            self.multi_cell(0, 5, '🔒 Detailed fix instructions available in Basic plan and above')
        else:
            self.set_font('Arial', 'B', 10)
            self.set_text_color(0, 0, 0)
            self.cell(0, 6, 'How to Fix:', 0, 1)
            
            self.set_font('Arial', '', 10)
            self.set_text_color(60, 60, 60)
            self.multi_cell(0, 5, fix)
        
        # Compliance (only for Basic and above)
        if tier != "free" and compliance:
            self.ln(2)
            self.set_font('Arial', 'B', 9)
            self.set_text_color(0, 0, 0)
            self.cell(0, 5, 'Compliance: ', 0, 0)
            
            self.set_font('Arial', '', 9)
            self.set_text_color(100, 100, 100)
            self.cell(0, 5, ', '.join(compliance), 0, 1)
        
        # Code snippet (only for Professional and Enterprise)
        if tier in ["professional", "enterprise"] and finding.get('code_snippet'):
            self.ln(2)
            self.set_font('Arial', 'B', 9)
            self.set_text_color(0, 0, 0)
            self.cell(0, 5, 'Code Example:', 0, 1)
            
            self.set_fill_color(240, 240, 240)
            self.set_font('Courier', '', 8)
            self.set_text_color(0, 0, 0)
            
            code = self.clean_text(finding.get('code_snippet', ''))
            for line in code.split('\n'):
                if line.strip():
                    self.cell(0, 4, '  ' + line, 0, 1, '', True)
        
        self.ln(3)
        
    def add_recommendations(self, tier: str):
        """Add recommendations section"""
        self.add_page()
        
        self.set_font('Arial', 'B', 16)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, 'Recommendations', 0, 1)
        
        recommendations = [
            '1. Address all HIGH severity issues immediately',
            '2. Implement security headers (CSP, HSTS, X-Frame-Options)',
            '3. Enable HTTPS across all pages',
            '4. Regular security audits (monthly recommended)',
            '5. Keep all software and dependencies up to date'
        ]
        
        if tier in ["professional", "enterprise"]:
            recommendations.extend([
                '6. Enable automated 24/7 security scanning',
                '7. Implement Web Application Firewall (WAF)',
                '8. Set up security monitoring and alerting',
                '9. Conduct penetration testing quarterly',
                '10. Train development team on secure coding practices'
            ])
        
        self.set_font('Arial', '', 11)
        self.set_text_color(60, 60, 60)
        
        for rec in recommendations:
            self.multi_cell(0, 6, rec)
            self.ln(2)
            
        if tier == "free":
            self.ln(5)
            self.add_upgrade_notice()


def generate_tiered_pdf(hostname: str, grade: str, findings: List[Dict], tier: str = "free", ai_summary: str = None) -> str:
    """
    Generate PDF report based on subscription tier
    """
    pdf = TieredPDFGenerator(tier=tier)
    pdf.add_page()
    
    # Title section
    scan_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    pdf.add_title_section(hostname, grade, scan_date)
    
    # AI Summary Section (If provided)
    if ai_summary:
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 11)
        pdf.set_text_color(41, 128, 185)
        pdf.cell(0, 8, 'AI-GENERATED EXECUTIVE SUMMARY', 0, 1)
        
        pdf.set_font('Arial', 'I', 10)
        pdf.set_text_color(60, 60, 60)
        pdf.multi_cell(0, 6, pdf.clean_text(ai_summary))
        pdf.ln(5)
    
    # Executive summary
    high_count = sum(1 for f in findings if f.get('severity') == 'HIGH')
    medium_count = sum(1 for f in findings if f.get('severity') == 'MEDIUM')
    low_count = sum(1 for f in findings if f.get('severity') == 'LOW')
    
    pdf.add_executive_summary(len(findings), high_count, medium_count, low_count)
    
    # Findings section (filtered by tier)
    pdf.add_findings_section(findings, tier)
    
    # Recommendations
    pdf.add_recommendations(tier)
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"security_audit_{hostname}_{timestamp}_{tier}.pdf"
    
    pdf.output(filename)
    return filename


# Example usage
if __name__ == "__main__":
    sample_findings = [
        {
            "title": "Missing Security Headers",
            "severity": "HIGH",
            "impact": "Your site is vulnerable to clickjacking and XSS attacks",
            "fix": "Add Content-Security-Policy and X-Frame-Options headers",
            "compliance": ["OWASP A5:2021", "PCI-DSS 6.5.10"],
            "code_snippet": "# Add to your server config\nHeader set X-Frame-Options \"DENY\"\nHeader set Content-Security-Policy \"default-src 'self'\""
        },
        {
            "title": "Insecure Cookie Configuration",
            "severity": "MEDIUM",
            "impact": "Session cookies can be stolen via XSS attacks",
            "fix": "Set HttpOnly and Secure flags on all cookies",
            "compliance": ["OWASP A7:2021"],
            "code_snippet": "Set-Cookie: sessionid=abc123; HttpOnly; Secure; SameSite=Strict"
        }
    ]
    
    # Generate PDFs for different tiers
    for tier in ["free", "basic", "professional", "enterprise"]:
        filename = generate_tiered_pdf("example.com", "C", sample_findings, tier)
        print(f"Generated {tier} tier PDF: {filename}")

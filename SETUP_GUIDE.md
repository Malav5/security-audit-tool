# Security Audit Tool - Authentication & Email Setup Guide

## Overview
This guide covers the recent updates to restrict PDF downloads to authenticated users and configure the email confirmation system.

## 🔒 Feature 1: Restricted PDF Downloads

### What Changed
PDF reports can now **only be downloaded by authenticated users**. This ensures that sensitive security audit reports are protected and only accessible to registered users.

### Backend Changes
**File**: `backend/main.py`

The `/download-pdf/{filename}` endpoint now requires authentication:
```python
@app.get("/download-pdf/{filename}")
async def download_pdf(
    filename: str, 
    background_tasks: BackgroundTasks,
    authorization: Optional[str] = Header(None)
):
    """Returns the generated PDF file. Requires authentication."""
    # Verify user is authenticated
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required to download PDF reports")
    
    token = authorization.split(" ")[1]
    user = await verify_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired authentication token")
    
    # Check if file exists and return
    ...
```

### Frontend Changes
**File**: `frontend/src/api.js`

Updated the `downloadPDF` function to pass authentication token:
```javascript
export const downloadPDF = async (filename, token) => {
    try {
        const config = {
            responseType: 'blob'
        };
        
        if (token) {
            config.headers = {
                'Authorization': `Bearer ${token}`
            };
        }
        
        const response = await api.get(`/download-pdf/${filename}`, config);
        return response.data;
    } catch (error) {
        if (error.response?.status === 401) {
            throw new Error("Please sign in to download PDF reports.");
        }
        throw new Error("Failed to download report. It may have expired.");
    }
};
```

**File**: `frontend/src/App.jsx`

Updated the `handleDownloadReport` function to pass the session token:
```javascript
const handleDownloadReport = async (filename) => {
    if (!session) {
      setShowAuth(true);
      return;
    }

    try {
      const blob = await downloadPDF(filename, session.access_token);
      // ... rest of download logic
    } catch (err) {
      alert(err.message);
    }
};
```

### User Experience
- **Signed-in users**: Can download PDFs normally
- **Non-signed-in users**: Will see the sign-in modal when attempting to download
- **Invalid token**: Will receive an error message prompting them to sign in again

---

## 📧 Feature 2: Email Confirmation Template

### What's Included
A professionally designed HTML email template for account confirmation with:
- ✅ Modern cybersecurity aesthetic matching your brand
- ✅ Animated elements (floating shield icon, pulsing effects)
- ✅ Responsive design for all devices
- ✅ Feature highlights showcasing platform capabilities
- ✅ Security notice badge
- ✅ Professional footer with links

### Files Created
1. **`backend/email_templates/confirmation_email.html`** - Production template for Supabase
2. **`backend/email_templates/preview.html`** - Preview version you can open in browser
3. **`backend/email_templates/README.md`** - Detailed configuration guide

### How to Configure in Supabase

#### Step 1: Access Email Templates
1. Go to your [Supabase Dashboard](https://app.supabase.com)
2. Select your project
3. Navigate to **Authentication** → **Email Templates**

#### Step 2: Update Confirmation Email Template
1. Select **"Confirm signup"** from the template list
2. Copy the entire content from `backend/email_templates/confirmation_email.html`
3. Paste it into the Supabase email template editor
4. Click **Save**

#### Step 3: Configure Email Settings (if not already done)
1. Go to **Authentication** → **Settings**
2. Under **Email Settings**, ensure:
   - **Enable email confirmations** is checked
   - **Site URL** is set to your production URL (e.g., `https://your-app.com`)
   - **Redirect URLs** includes your confirmation redirect URL

#### Step 4: Test the Email
1. Sign up with a test email address
2. Check your inbox for the confirmation email
3. Verify the design renders correctly
4. Test the confirmation link

### Customization Options

#### Update Brand Colors
In the CSS section, modify these gradient values:
```css
/* Header gradient */
background: linear-gradient(135deg, #0A0F1C 0%, #1e3a8a 100%);

/* Button gradient */
background: linear-gradient(135deg, #22d3ee 0%, #06b6d4 100%);
```

#### Add Your Logo
Replace the shield SVG with your own logo image:
```html
<div class="shield-icon">
    <img src="https://your-cdn.com/logo.png" alt="Logo" style="width: 45px; height: 45px;">
</div>
```

#### Update Footer Links
Replace the placeholder links with your actual URLs:
```html
<div class="footer-links">
    <a href="https://your-app.com/docs">Documentation</a>
    <a href="https://your-app.com/support">Support</a>
    <a href="https://your-app.com/privacy">Privacy Policy</a>
</div>
```

#### Add Social Media Links
Update the social links in the footer:
```html
<div class="social-links">
    <a href="https://twitter.com/yourhandle" aria-label="Twitter"></a>
    <a href="https://linkedin.com/company/yourcompany" aria-label="LinkedIn"></a>
    <a href="https://github.com/yourorg" aria-label="GitHub"></a>
</div>
```

### Supabase Template Variables

The template uses Supabase's built-in variables:
- `{{ .ConfirmationURL }}` - The confirmation link (already implemented)
- `{{ .Email }}` - User's email address (optional)
- `{{ .SiteURL }}` - Your site URL from settings (optional)
- `{{ .Token }}` - The confirmation token (optional)

Example of adding user's email to greeting:
```html
<h2 class="greeting">Welcome, {{ .Email }}! 🎉</h2>
```

---

## 🧪 Testing Guide

### Test PDF Download Restriction
1. **Without signing in**:
   - Run a security scan
   - Try to download the PDF
   - Should see sign-in modal
   
2. **After signing in**:
   - Sign in to your account
   - Run a security scan
   - Click download PDF
   - Should download successfully

3. **From dashboard**:
   - Sign in
   - Go to dashboard
   - Click download on any previous scan
   - Should download successfully

### Test Email Confirmation
1. **Preview the email**:
   - Open `backend/email_templates/preview.html` in your browser
   - Verify the design looks correct
   
2. **Test signup flow**:
   - Create a new account with a real email
   - Check your inbox for the confirmation email
   - Verify the email design matches the preview
   - Click the confirmation link
   - Verify you're redirected correctly and can sign in

3. **Test edge cases**:
   - Try signing up with the same email twice
   - Check if the email arrives in spam folder
   - Test on mobile email clients (Gmail, Outlook, Apple Mail)

---

## 🚀 Deployment Checklist

### Before Deploying to Production

- [ ] **Backend Changes**
  - [ ] Updated `backend/main.py` with authentication for PDF downloads
  - [ ] Tested the endpoint with valid and invalid tokens
  - [ ] Verified error messages are user-friendly

- [ ] **Frontend Changes**
  - [ ] Updated `frontend/src/api.js` to pass tokens
  - [ ] Updated `frontend/src/App.jsx` to handle authentication
  - [ ] Tested download flow for signed-in and non-signed-in users

- [ ] **Email Template**
  - [ ] Uploaded template to Supabase
  - [ ] Customized brand colors and logos
  - [ ] Updated footer links to production URLs
  - [ ] Added social media links
  - [ ] Tested email delivery
  - [ ] Verified email renders correctly in major email clients

- [ ] **Supabase Configuration**
  - [ ] Email confirmations enabled
  - [ ] Site URL configured correctly
  - [ ] Redirect URLs added to allowed list
  - [ ] SMTP settings configured (if using custom SMTP)

---

## 🐛 Troubleshooting

### PDF Download Issues

**Problem**: "Authentication required" error even when signed in
- **Solution**: Check if the session token is being passed correctly. Open browser DevTools → Network tab → Check the request headers for the Authorization header.

**Problem**: PDF download fails with 404
- **Solution**: The PDF file may have been cleaned up. Re-run the scan to generate a new PDF.

### Email Issues

**Problem**: Confirmation email not received
- **Solutions**:
  1. Check spam/junk folder
  2. Verify email settings in Supabase dashboard
  3. Check Supabase logs for email delivery errors
  4. Ensure SMTP is configured correctly

**Problem**: Email design looks broken
- **Solutions**:
  1. Some email clients strip certain CSS
  2. Test with the preview.html file first
  3. Use inline styles for critical styling
  4. Avoid complex CSS animations in production emails

**Problem**: Confirmation link doesn't work
- **Solutions**:
  1. Verify Site URL in Supabase settings
  2. Check that redirect URL is in allowed list
  3. Ensure the token hasn't expired (24 hours)

---

## 📝 Additional Notes

### Security Considerations
- PDF downloads now require authentication, preventing unauthorized access to sensitive security reports
- Email confirmation ensures users have access to their registered email
- Tokens expire after 24 hours for security

### Performance
- PDF files are automatically cleaned up after download to save server space
- Email templates are cached by email clients for faster rendering

### Future Enhancements
Consider adding:
- Password reset email template
- Welcome email after confirmation
- Scan completion notification emails
- Weekly digest emails for automated scans
- Two-factor authentication

---

## 📞 Support

If you encounter any issues:
1. Check this guide first
2. Review the Supabase documentation: https://supabase.com/docs/guides/auth
3. Check browser console for errors
4. Review backend logs for API errors

---

**Last Updated**: February 4, 2026  
**Version**: 1.0  
**Author**: CyberSecure India Development Team

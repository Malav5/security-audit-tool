# Email Template Configuration Guide

## Overview
This directory contains the HTML email template for account confirmation emails sent to new users.

## Files
- `confirmation_email.html` - The main email template with modern cybersecurity design

## How to Configure in Supabase

### Step 1: Access Supabase Dashboard
1. Go to your Supabase project dashboard
2. Navigate to **Authentication** → **Email Templates**

### Step 2: Configure Confirmation Email
1. Select **Confirm signup** from the template list
2. Replace the default template with the content from `confirmation_email.html`
3. The template uses Supabase's built-in variable: `{{ .ConfirmationURL }}`

### Step 3: Customize (Optional)
You can customize the following elements:
- **Brand Colors**: Update the gradient colors in the CSS
- **Logo**: Replace the shield SVG with your own logo
- **Footer Links**: Update the links to your actual documentation, support, and privacy policy pages
- **Social Media**: Add your social media links in the footer

### Step 4: Test the Email
1. Create a test account to trigger the confirmation email
2. Check your inbox to verify the email renders correctly
3. Test the confirmation link functionality

## Template Features

### Design Elements
- ✅ Modern cybersecurity aesthetic with gradient backgrounds
- ✅ Animated shield icon with floating effect
- ✅ Responsive design for mobile and desktop
- ✅ Feature highlights grid showcasing platform capabilities
- ✅ Security notice badge for important information
- ✅ Professional footer with links and social media

### Technical Features
- ✅ Inline CSS for maximum email client compatibility
- ✅ Mobile-responsive with media queries
- ✅ Fallback text link for accessibility
- ✅ Clean, semantic HTML structure
- ✅ Cross-email-client tested styling

## Email Client Compatibility
This template has been designed to work with:
- Gmail (Web, iOS, Android)
- Outlook (Web, Desktop)
- Apple Mail
- Yahoo Mail
- ProtonMail
- And most modern email clients

## Variables Available in Supabase

Supabase provides the following variables you can use:
- `{{ .ConfirmationURL }}` - The confirmation link (already used)
- `{{ .Email }}` - User's email address
- `{{ .SiteURL }}` - Your site URL from Supabase settings
- `{{ .Token }}` - The confirmation token
- `{{ .TokenHash }}` - Hashed version of the token

## Customization Examples

### Adding User's Email
Replace the greeting line with:
```html
<h2 class="greeting">Welcome, {{.Email}}! 🎉</h2>
```

### Custom Redirect After Confirmation
Update the Supabase auth settings to redirect to a custom page:
```javascript
// In your frontend signup code
const { error } = await supabase.auth.signUp({
  email: authEmail,
  password: authPassword,
  options: {
    emailRedirectTo: `${window.location.origin}/welcome`,
  }
});
```

## Troubleshooting

### Email Not Sending
1. Check Supabase email settings are configured
2. Verify SMTP settings if using custom SMTP
3. Check spam folder
4. Verify email rate limits haven't been exceeded

### Styling Issues
1. Some email clients strip certain CSS properties
2. Always test with inline styles
3. Avoid using `<style>` tags in `<body>` - keep them in `<head>`
4. Use tables for complex layouts if needed

### Link Not Working
1. Verify the `{{ .ConfirmationURL }}` variable is correctly placed
2. Check Supabase site URL settings
3. Ensure redirect URL is in allowed redirect URLs list

## Support
For issues with:
- **Email template**: Check this README or contact your development team
- **Supabase configuration**: Visit [Supabase Documentation](https://supabase.com/docs/guides/auth/auth-email-templates)
- **Email delivery**: Check Supabase email logs in the dashboard

## Preview
To preview the email template:
1. Open `confirmation_email.html` in a web browser
2. Note: The `{{ .ConfirmationURL }}` will show as-is in preview
3. For actual preview, create a test signup in your application

---

**Last Updated**: February 2026  
**Version**: 1.0  
**Maintained by**: CyberSecure India Development Team

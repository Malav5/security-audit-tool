# 🚀 Razorpary Deployment Guide for Render

To successfully deploy your security audit tool with Razorpay integration on Render, follow these steps to configure your environment variables.

---

## 1. Backend Configuration (FastAPI)

On the Render Dashboard, go to your **`security-audit-backend`** service -> **Settings** -> **Environment Variables**. Add the following:

| Key | Value | Description |
|-----|-------|-------------|
| `RAZORPAY_KEY_ID` | `rzp_live_...` or `rzp_test_...` | Your Razorpay API Key ID |
| `RAZORPAY_KEY_SECRET` | `...` | Your Razorpay API Key Secret |

---

## 2. Frontend Configuration (Vite)

Go to your **`security-audit-frontend`** service -> **Settings** -> **Environment Variables**. 

**IMPORTANT**: Vite requires environment variables used in the browser to be prefixed with `VITE_`.

| Key | Value | Description |
|-----|-------|-------------|
| `VITE_RAZORPAY_KEY_ID` | `rzp_live_...` or `rzp_test_...` | Your Razorpay API Key ID (Publicly exposed to frontend) |

---

## 3. Razorpay Webhook (Optional but Recommended)

If you want to handle payments when the user closes the browser accidentally, you should set up a Webhook in the Razorpay Dashboard.

1.  Go to **Razorpay Dashboard** -> **Settings** -> **Webhooks**.
2.  Add a new Webhook with URL: `https://your-backend-url.onrender.com/api/verify-payment` (You may need a separate webhook endpoint for true async processing).
3.  Select Event: `payment.captured`.

---

## 4. Verification

After adding these variables, Render will automatically trigger a redeploy. 

1.  Open your frontend URL.
2.  Log in and try to upgrade.
3.  The Razorpay modal should now appear and correctly process test payments using your Key ID.

---

### Need Help?
- Check the **Render Logs** for any `RAZORPAY_ERROR` messages.
- Ensure your Razorpay account is in **Test Mode** during development.

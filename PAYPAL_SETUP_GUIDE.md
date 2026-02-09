# 🛠️ PayPal Payment Setup Guide

This guide will help you set up PayPal for your **CyberSecure India Scanner**.

## 1. Get Your PayPal Developer Credentials

1.  Log in to the [PayPal Developer Portal](https://developer.paypal.com/dashboard/applications/sandbox).
2.  Go to **Apps & Credentials**.
3.  Create a new **REST API App** (e.g., "CyberSecure India").
4.  Copy your **Client ID** and **Secret**.
5.  Paste them into your `.env` file:

```env
PAYPAL_CLIENT_ID=your_client_id_here
PAYPAL_CLIENT_SECRET=your_client_secret_here
PAYPAL_MODE=sandbox
```

## 2. Set Up Webhooks (For Payment Confirmation)

Webhooks allow the backend to automatically upgrade the user's tier when a payment is successful.

1.  Scroll down to the **Webhooks** section in your PayPal App settings.
2.  Click **Add Webhook**.
3.  **Webhook URL**: Use your backend URL followed by `/webhook` (e.g., `https://your-api.com/webhook`).
    - *For local testing, use a tool like Ngrok to get a public URL.*
4.  **Event types**: Select **"Checkout order completed"** or **"Payment capture completed"**.
5.  Save and copy the **Webhook ID** into your `.env`:

```env
PAYPAL_WEBHOOK_ID=your_webhook_id_here
```

## 3. Testing with PayPal Sandbox

1.  Start your backend: `uvicorn main:app --reload`
2.  Start your frontend: `npm run dev`
3.  Go to the **Pricing** page.
4.  Click **Upgrade**. You will be redirected to PayPal's checkout page.
5.  Log in with a **Sandbox Personal Account** (find these in your [Developer Dashboard](https://developer.paypal.com/dashboard/accounts)).
6.  Complete the payment.
7.  Check your Dashboard to see if your plan updated to "Basic/Pro/Enterprise"!

## 4. Going Live (Production)

1.  Switch the toggle from **Sandbox** to **Live** in the PayPal Developer Dashboard.
2.  Get your **Live Client ID** and **Secret**.
3.  Update your production `.env` file and set `PAYPAL_MODE=live`.
4.  Create a **Live Webhook** pointing to your production server.

# Clerk Webhooks Configuration Guide

This guide explains how to set up and test Clerk webhooks for the CELPIP Simulator backend. Webhooks are essential for **asynchronous user provisioning** and **automated approval workflows**.

## 1. Why Webhooks?

Webhooks allow Clerk to notify your backend immediately when certain events occur (e.g., `user.created`). This ensures your local database is updated the moment a user signs up, without waiting for their first login.

## 2. Local Development (ngrok)

Since Clerk cannot reach your `localhost`, you must use a tunneling service to expose your backend to the internet.

### Step 1: Install and Start ngrok
1. Install ngrok: `npm install -g ngrok` (or via [ngrok.com](https://ngrok.com)).
2. Start the tunnel for your FastAPI port (default `8000`):
   ```bash
   ngrok http 8000
   ```
3. Copy the **Forwarding URL** provided by ngrok (e.g., `https://a1b2-c3d4.ngrok-free.app`).

### Step 2: Configure Clerk Dashboard
1. Go to the [Clerk Dashboard](https://dashboard.clerk.com) → **Webhooks**.
2. Click **Add Endpoint**.
3. **Endpoint URL**: `[YOUR_NGROK_URL]/api/v1/webhooks/clerk`
   - *Example*: `https://a1b2-c3d4.ngrok-free.app/api/v1/webhooks/clerk`
4. **Events to deliver**: Select `user.created`.
5. Click **Create**.

### Step 3: Set Webhook Secret
1. Copy the **Signing Secret** (starts with `whsec_`) from the endpoint page in Clerk.
2. Add it to your `.env` file:
   ```dotenv
   CLERK_WEBHOOK_SECRET=whsec_your_secret_here
   ```

## 3. Production Deployment (Vercel)

When deploying to production, follow the same steps but use your production URL:
- **Endpoint URL**: `https://your-app.vercel.app/api/v1/webhooks/clerk`

---

## 4. Troubleshooting

### "Invalid Signature" Error
If the backend returns a `400 Bad Request` with "Invalid signature," double-check that:
- Your `CLERK_WEBHOOK_SECRET` in `.env` matches the one in the Clerk Dashboard.
- You are using the correct signing secret for the specific endpoint.

### Webhook Not Reaching Backend
- Ensure ngrok is running and the URL matches exactly.
- Check the **Succeeded/Failed** logs in the Clerk Dashboard to see the exact error response from your server.
- Ensure your backend is running (`uvicorn app.main:app --reload`).

# API Testing Guide (Postman & Swagger)

This guide explains how to test the CELPIP Simulator API using authentication.

## 1. Get a Bearer Token (JWT)

Since the API is protected by Clerk, you need a valid JWT from your session.

### From the Browser (Easiest)
1. Open the [CELPIP Simulator Frontend](https://celpip-simulator.vercel.app) and log in.
2. Open **Developer Tools** (F12) -> **Network** tab.
3. Refresh the page or click a button that fetches data.
4. Look for a request to the backend (e.g., `/api/v1/tests`).
5. In the **Headers** tab, find the `Authorization` header.
6. Copy the string starting after `Bearer ` (e.g., `eyJhbG...`).

---

## 2. Testing in Swagger UI

1. Open the Swagger docs: [http://localhost:8000/docs](http://localhost:8000/docs) (or your production URL).
2. Click the **Authorize** button at the top right.
3. Paste the token into the **Value** field and click **Authorize**.
4. Now you can use any protected endpoint by clicking **Try it out** and then **Execute**.

---

## 3. Testing in Postman

1. Create a new Request in Postman.
2. Set the method (e.g., `GET`) and URL (e.g., `https://celpip-simulator-fast-api.vercel.app/api/v1/tests`).
3. Go to the **Auth** tab.
4. Select **Type**: `Bearer Token`.
5. Paste your JWT into the **Token** field.
6. Click **Send**.

---

## 4. Troubleshooting

- **401 Unauthorized**: Your token has expired. In Clerk, tokens are short-lived. Refresh the frontend and get a new one.
- **403 Forbidden**: Your user exists but is not "APPROVED" in the database.
- **404 Not Found**: Ensure you are using the correct prefix (we added `/api/v1/tests` as an alias for `/api/v1/test-available`).

### Checking User Status via Admin API
If you are an admin, you can approve yourself:
`POST /api/v1/admin/users/{user_id}/authorize`
(Requires an Admin token).

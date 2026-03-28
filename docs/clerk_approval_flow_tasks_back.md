# tasks-backend.md (COMPLETED)

## 🧠 Overview
Backend (FastAPI) handles:
- [x] User persistence (SQLAlchemy + TiDB)
- [x] Approval workflow (Status Enum: PENDING, APPROVED, REJECTED)
- [x] Authorization validation (get_authorized_user dependency)
- [x] Email triggers (Mock implementation in app/core/email.py)

---

## 1. Setup Dependencies [x]
- [x] Install Clerk SDK (clerk-sdk-python)
- [x] Install Svix for Webhooks
- [x] Install FastAPI dependencies

---

## 2. Database [x]
- [x] Create `users` table with `status` Enum.
- [x] Apply Alembic migration.

---

## 3. Clerk Webhook Endpoint [x]
- [x] Implement `POST /api/v1/webhooks/clerk`
- [x] Validate webhook signature (Svix)
- [x] Handle `user.created` event

---

## 4. Email: Pending Approval [x]
- [x] Trigger "Your account is under review" email after user creation.

---

## 5. Admin APIs [x]
- [x] List pending users: `GET /api/v1/admin/users/pending`
- [x] Approve user: `POST /api/v1/admin/users/{id}/authorize`
- [x] Reject user: `POST /api/v1/admin/users/{id}/reject`

---

## 6. Email: Approval / Rejection [x]
- [x] On APPROVED → send "You can now access the system"
- [x] On REJECTED → send "Your request was denied"

---

## 7. Authentication Middleware [x]
- [x] Implement `get_authorized_user` dependency.

---

## 8. Protect Routes [x]
- [x] Apply dependency to routers (tests, results, etc.)

---

## 9. Optional: Sync Clerk Metadata [x]
- [x] Sync status and role back to Clerk's `public_metadata`.

---

## 10. Logging & Auditing [x]
- [x] Track: `authorized_by_admin_id` and `authorized_at`.

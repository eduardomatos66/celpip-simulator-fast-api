# tasks-frontend.md

## 🧠 Overview
Frontend (React) will handle:
- Signup/Login via Clerk
- UI feedback (pending/approved)
- Admin dashboard

---

## 1. Setup Clerk

Install:
```
npm install @clerk/clerk-react
```

Wrap app:

```tsx
<ClerkProvider>
  <App />
</ClerkProvider>
```

---

## 2. Authentication

Use Clerk components:

- <SignUp />
- <SignIn />

---

## 3. Fetch Backend User Status

After login:

```ts
const response = await fetch('/api/me')
const user = await response.json()
```

---

## 4. Route Guard Logic

```ts
if (user.status === 'PENDING') {
  navigate('/waiting-approval')
}

if (user.status === 'REJECTED') {
  navigate('/rejected')
}
```

---

## 5. Waiting Approval Screen

Page: `/waiting-approval`

Content:
- Message: "Your account is under review"
- Disable system features

---

## 6. Approved Flow

If APPROVED:
- Allow navigation
- Load main app

---

## 7. Admin Dashboard

### Features
- List pending users
- Approve / reject

### Example

```ts
await fetch(`/admin/users/${id}/approve`, {
  method: 'PATCH'
})
```

---

## 8. UI Feedback

- Toast on approval/rejection
- Loading states

---

## 9. Clerk Session Usage

Use:

```ts
const { user } = useUser()
```

Optional:

```ts
user?.publicMetadata.status
```

---

## 10. Error Handling

If backend returns 403:

```ts
redirect('/waiting-approval')
```

---

## 🚀 Final Flow

1. User signs up (Clerk UI)
2. Backend creates PENDING user
3. Frontend shows waiting page
4. Admin approves
5. User logs in again
6. Full access granted

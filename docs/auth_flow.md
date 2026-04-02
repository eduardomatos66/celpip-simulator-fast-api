# Authentication & Authorization Flow

The following sequence details how a user joins the platform, gets authorized by an admin, and accesses protected resources.

```mermaid
sequenceDiagram
    participant User as "User (Browser)"
    participant Clerk as "Clerk (Auth Provider)"
    participant API as "FastAPI Backend"
    participant DB as "TiDB / Local Database"
    participant Admin as "Admin (Browser)"

    Note over User, Clerk: Phase 1: Sign-up
    User->>Clerk: Sign up / Sign in
    Clerk-->>User: ID Token (JWT)

    Note over Clerk, API: Phase 1.5: Webhook Provisioning
    Clerk->>API: POST /api/v1/webhooks/clerk (user.created)
    API->>API: verify_webhook_signature()
    API->>DB: create_user(status = PENDING)
    API-->>User: Send "Under Review" Email

    Note over User, API: Phase 2: Login / JIT Sync
    User->>API: GET /api/v1/users/me (Bearer JWT)
    API->>API: verify_clerk_token()
    API->>DB: get_or_create_user(clerk_id)
    DB-->>API: User Record (Status: PENDING)
    API-->>User: Profile Data (403 if accessing protected)

    Note over Admin, DB: Phase 3: Admin Approval
    Admin->>API: POST /api/v1/admin/users/{id}/authorize (Admin Bearer)
    API->>DB: update(status = APPROVED)
    API->>API: sync_to_clerk_metadata()
    API-->>User: Send "Approved" Email
    API-->>Admin: Success

    Note over User, DB: Phase 4: Authorized Access
    User->>API: GET /api/v1/test-results/user (Bearer JWT)
    API->>DB: check user.status == APPROVED
    DB-->>API: True
    API->>DB: Query Results
    API-->>User: List of Results
```

### Production Security Hardening

The backend implements several production-grade security measures to ensure high availability and prevent unauthorized access:

- **JWKS Key Rotation Support**: The API caches Clerk's JSON Web Key Set (public keys) with a 1-hour TTL. If a token verification fails due to an unknown key (common when Clerk rotates keys), the backend automatically triggers a one-time fresh fetch of the JWKS and retries the verification.
- **Issuer Validation**: The backend strictly validates the `iss` (issuer) claim in the JWT against the configured `CLERK_ISSUER_URL`. This ensures that tokens issued from other Clerk instances cannot be used to authenticate against this backend.
- **Webhook-First Provisioning**: While it supports "Just-in-Time" provisioning as a fallback, the system is designed to create user records immediately upon signup via Clerk Webhooks. This allows for immediate "Under Review" notifications.
- **Expressive Status Machine**: Uses a `UserStatus` Enum (`PENDING`, `APPROVED`, `REJECTED`) instead of a simple boolean. This allows the system to explicitly block rejected users with custom messaging.
- **Clerk Metadata Sync**: Local approval states are synchronized back to Clerk's `public_metadata`. This enables the frontend to implement route guards based on the Clerk user object without additional backend roundtrips.
- **Transactional Notifications**: Triggered on signup, approval, and rejection to keep the user informed of their access status.
- **Sanitized Error Responses**: Authentication failure details (such as raw JWT parsing errors) are logged internally but hidden from the end user to prevent information leakage.
- **Bootstrapping**: The very first user to log in to a fresh database is automatically promoted to an Admin and Approved status to allow for initial system setup.

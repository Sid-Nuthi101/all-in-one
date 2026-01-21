# Apple Login (Python Frontend)

This repository implements a **Python-only authentication frontend** using **Sign in with Apple** as the primary login method and **Firebase** as the user data store.

This repo intentionally excludes any UI components. It focuses purely on:
- Apple OAuth authentication
- Token verification
- Normalized user creation / login
- Persisting user data to Firebase
- Full unit-test coverage

---

## Scope

### ✅ In Scope
- Sign in with Apple (OAuth2 + JWT verification)
- Python orchestration layer (no UI)
- Firebase user upsert on login/signup
- Fully testable logic with mocks

### ❌ Out of Scope
- UI / buttons / web views
- iOS / macOS / web frontend
- Long-lived backend services

---

## High-Level Login Flow

1. Generate Apple OAuth authorization URL (PKCE recommended).
2. User completes login via browser.
3. App receives authorization code on local callback.
4. Exchange code for Apple tokens.
5. Verify and decode `id_token`.
6. Normalize Apple user claims.
7. Upsert user record in Firebase.
8. Return normalized user object.

## Firebase Intended User Schema

```json
{
  "apple_sub": "000123.abc",
  "email": "user@example.com",
  "name": {
    "given": "First",
    "family": "Last"
  },
  "created_at": "ISO-8601",
  "last_login_at": "ISO-8601",
  "providers": ["apple"]
}
```

# Notes & Implementation Considerations

This document captures important behavioral, security, and architectural notes for the Python-based Apple Login + Firebase flow.

These notes are **non-optional assumptions** that influence how the system must be implemented and tested.

---

## Apple Sign-In Data Behavior

### Email and Name Are Not Guaranteed

Apple’s Sign in with Apple behaves differently from most OAuth providers:

- `email` and `name` are **only returned on the first successful authorization**
- On subsequent logins:
  - `email` may be missing
  - `name` will almost always be missing

### Required Handling Rules

- Treat `email` as **optional**
- Treat `name` as **optional**
- Never overwrite existing stored values with `null`
- Always persist the stable Apple user identifier (`sub`)

**The `sub` claim is the only guaranteed long-term identifier.**

---

## Apple User Identity

### Stable Identifier

- Use the Apple JWT claim `sub` as:
  - Firebase document ID
  - Internal user ID
- `sub` is:
  - Stable per Apple ID + Service ID
  - Not globally unique across different apps

### Do NOT Use Email As an ID

- Email may:
  - Be hidden (private relay)
  - Change
  - Be missing on later logins
- Email must never be treated as a primary key

---

## Firebase Usage Notes

### Firestore Schema Strategy

- Collection: `users`
- Document ID: `apple_sub`
- Writes should always use:
  ```python
  set(data, merge=True)
  ```

This ensures:

- First login creates the user
- Subsequent logins update timestamps without data loss

## Timestamp Semantics

Required Fields

- created_at / Set only once
- last_login_at	/ Updated on every login

---

## Firebase Configuration (Required)

### 1. Create Firebase Project & Enable Firestore

1. Create a Firebase project.
2. Enable **Cloud Firestore** in Native mode.
3. Create a **Service Account** with Firestore access and download the JSON key.
4. Set environment variables for the Python process:

```bash
export FIREBASE_PROJECT_ID="your-project-id"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
```

### 2. Configure Sign in with Apple (Apple Developer Portal)

1. In the Apple Developer Portal:
   - Create a **Service ID** (this is your `client_id`).
   - Enable **Sign in with Apple** for the Service ID.
   - Register a **Redirect URI** that matches your app.
2. Create a **Sign in with Apple Key** and note:
   - Key ID
   - Team ID
   - Private key (`.p8`)
3. Generate the Apple client secret (JWT) with those values.

### 3. (Optional) Enable Apple Provider in Firebase Auth

If you also want Firebase Auth integration on other clients:
1. Enable **Apple** in Firebase Authentication providers.
2. Provide the Service ID and Team ID.
3. Upload the Apple key.

This Python login flow only needs Firestore for persistence, but Firebase Auth can be used by front-end clients for session management.

---

## Sign in with Apple Button/Prompt Integration

Use the new helper to generate the authorization URL and PKCE verifier for a **Sign in with Apple** button or prompt:

```python
request = login.create_apple_auth_request(
    client_id="your-service-id",
    redirect_uri="https://example.com/callback",
    state="csrf-token",
)

# Show request["authorization_url"] when the user clicks "Sign in with Apple".
```

Then call `ensure_user_logged_in` to keep the user logged in by reusing the stored
`apple_sub` and only prompting when no session exists.

### Desktop App Environment Variables

The PySide desktop app reads these variables to configure Sign in with Apple + Firebase:

```bash
export FIREBASE_PROJECT_ID="your-project-id"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
export APPLE_CLIENT_ID="com.example.service"
export APPLE_CLIENT_SECRET="your-apple-client-secret-jwt"
export APPLE_REDIRECT_URI="https://example.com/callback"
```

If these are set, the app will show a **Sign in with Apple** button and prompt for the
authorization code to complete the Firebase-backed login.

## Testing Requirement

- Time must be mockable in unit tests
- Use frozen timestamps (freezegun) to ensure deterministic tests

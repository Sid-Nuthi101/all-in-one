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

## Testing Requirement

- Time must be mockable in unit tests
- Use frozen timestamps (freezegun) to ensure deterministic tests

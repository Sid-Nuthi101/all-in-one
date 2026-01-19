
---

# 📄 `TESTING_LIBRARY_SETUP.md` (optional but recommended)

```md
# Unit Test Library Initialization

This project uses **pytest** as the testing framework.

---

## Why pytest?

- Clean syntax
- Powerful fixtures
- Excellent mocking support
- Industry standard

---

## conftest.py Responsibilities

- Shared fixtures
- Mock Apple tokens
- Mock Firebase clients
- Freeze time if needed

---

## Best Practices

- One behavior per test
- Avoid test interdependence
- Mock at boundaries, not internals
- Name tests after behavior, not functions

---

## Example Fixture Types

- `mock_apple_token_response`
- `mock_firestore_client`
- `fixed_timestamp`
- `fake_user_claims`

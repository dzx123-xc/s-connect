# Security Architecture

This document describes the **actual implemented** security architecture in Phase 0.

---

## Authentication

### Password Hashing: Argon2id
- **Algorithm**: Argon2id (hybrid of Argon2i and Argon2d)
- **Parameters** (configurable via environment):
  - Time cost: 3 iterations
  - Memory cost: 65,536 KB (64 MB)
  - Parallelism: 4 threads
  - Hash length: 32 bytes
  - Salt length: 16 bytes
- **Implementation**: `app/auth/password.py` using `argon2-cffi`
- **Verification**: Constant-time comparison via `PasswordHasher.verify()`

### Session Management: Server-Side Database Sessions
- **Session ID**: 32-byte URL-safe random token (`secrets.token_urlsafe(32)`)
- **Storage**: SHA-256 hash of session ID in database (`sessions` table)
- **Cookie**: `HttpOnly`, `SameSite=Lax`, `Secure` (production only)
- **Expiry**: 30 days rolling (extended on each request)
- **Revocation**: Immediate via `revoked_at` timestamp
- **No JWT**: Tokens are opaque references, not self-contained claims

### Session Flow
```
1. User logs in → verify password → create Session row → return session_id in HttpOnly cookie
2. Request arrives → SessionMiddleware reads cookie → hashes ID → looks up Session row
3. Valid + not expired + not revoked → attach User to request.state
4. Logout / revoke → set revoked_at → delete cookie
```

---

## Authorization

### Role-Based Access Control (Foundation)
- **Roles**: `player`, `coach`, `club`, `organizer`, `referee`, `admin`
- **Enforcement**: `require_role(*roles)` dependency in route handlers
- **Admin Separation**: `admin` role distinct from user roles; separate dashboard route

### Current Protections
- `/auth/me` requires any authenticated role
- Role-specific redirects on login/register
- Profile creation tied to role at registration

---

## Transport Security

| Setting | Development | Production |
|---------|-------------|------------|
| `session_cookie_secure` | `False` | `True` (HTTPS only) |
| `session_cookie_httponly` | `True` | `True` |
| `session_cookie_samesite` | `lax` | `lax` or `strict` |
| CORS | `localhost:8000` | Specific domains only |

---

## Database Security

- **SQL Injection**: Prevented via SQLAlchemy ORM (parameterized queries)
- **Passwords**: Never logged; only Argon2 hash stored
- **Session IDs**: Only SHA-256 hash stored; plaintext only in client cookie
- **Connection**: SQLite local; PostgreSQL with SSL in production

---

## Frontend Security

- **No localStorage auth**: Session only via HttpOnly cookie
- **No JWT in browser**: No token parsing/storage in JavaScript
- **API client**: `credentials: 'include'` for cookie transport
- **CSRF**: SameSite=Lax provides baseline; consider CSRF tokens for state-changing ops in Phase 1

---

## Configuration Security

| Variable | Required | Min Length | Notes |
|----------|----------|------------|-------|
| `SECRET_KEY` | Yes | 32 chars | Rotate periodically |
| `DATABASE_URL` | Yes | - | Use PostgreSQL in production |
| `SESSION_MAX_AGE` | No | - | Default 30 days |
| `CORS_ORIGINS` | Yes | - | Restrict to known origins |

---

## Threat Model (Phase 0)

| Threat | Mitigation |
|--------|------------|
| Password breach | Argon2id with high memory cost |
| Session hijacking | HttpOnly + Secure + SameSite cookies; short expiry |
| Session fixation | New session ID on login; old sessions revocable |
| Brute force | Argon2id slow hash; consider rate limiting in Phase 1 |
| SQL injection | SQLAlchemy ORM |
| XSS | HttpOnly cookies; CSP headers (planned) |
| CSRF | SameSite=Lax; explicit tokens (planned) |

---

## Planned Enhancements (Phase 1+)

- [ ] Rate limiting on auth endpoints
- [ ] CSRF tokens for forms
- [ ] Content Security Policy headers
- [ ] Audit logging for auth events
- [ ] Password strength requirements
- [ ] Multi-factor authentication (TOTP)
- [ ] Session device tracking
- [ ] Account lockout after failed attempts
- [ ] Password rotation policy
- [ ] OAuth2/OIDC integration

---

## Reporting Security Issues

Email: security@sconnect.example.com (placeholder)

Do not open public issues for security vulnerabilities.
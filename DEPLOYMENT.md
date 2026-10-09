# Deployment Guide

This document covers **local development** and **planned production architecture**.

---

## Local Development

### Prerequisites
- Python 3.11+
- Git

### Setup
```bash
# Clone and enter
git clone <repo-url>
cd SConnect

# Backend
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Environment
cp ../.env.example .env
# Edit .env with local values

# Run server
python -m app.main
```

### Access
- API: `http://localhost:8000`
- Health: `http://localhost:8000/health`
- Frontend: `http://localhost:8000/` (served by FastAPI)

### Database
- Default: SQLite at `./data/sconnect.db`
- Auto-created on first run
- Migrations: `alembic upgrade head` (after model changes)

### Tests
```bash
cd backend
pytest tests/ -v
pytest tests/ --cov=app --cov-report=term-missing
```

---

## Production Architecture (Planned)

### Stack
| Layer | Technology |
|-------|------------|
| API | FastAPI (uvicorn/gunicorn) |
| Database | PostgreSQL (Supabase / managed) |
| Cache/Queue | Redis (optional, Phase 1+) |
| Reverse Proxy | Nginx / Cloudflare |
| Process Manager | systemd / Docker |
| TLS | Let's Encrypt / Cloudflare |

### Environment Variables (Production)
```bash
# Required
DATABASE_URL=postgresql://user:pass@host:5432/sconnect
SECRET_KEY=your-32-char-min-secret-key-here
CORS_ORIGINS=["https://app.sconnect.example.com","https://sconnect.example.com"]

# Security
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_SAMESITE=lax

# Optional
SESSION_MAX_AGE=2592000  # 30 days
ARGON2_TIME_COST=3
ARGON2_MEMORY_COST=65536
ARGON2_PARALLELISM=4
```

### Database Migration
```bash
# Production
alembic upgrade head

# Or with env var
DATABASE_URL=postgresql://... alembic upgrade head
```

### Reverse Proxy (Nginx Example)
```nginx
server {
    listen 443 ssl http2;
    server_name api.sconnect.example.com;

    ssl_certificate /etc/letsencrypt/live/api.sconnect.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.sconnect.example.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Process Manager (systemd)
```ini
# /etc/systemd/system/sconnect.service
[Unit]
Description=SConnect FastAPI
After=network.target

[Service]
Type=exec
User=sconnect
WorkingDirectory=/opt/sconnect/backend
EnvironmentFile=/opt/sconnect/.env
ExecStart=/opt/sconnect/backend/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### Docker (Planned)
```dockerfile
# Dockerfile (planned)
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/app ./app
COPY backend/alembic.ini .
COPY backend/migrations ./migrations
ENV PYTHONPATH=/app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## CI/CD (Planned)

### GitHub Actions Example
```yaml
# .github/workflows/ci.yml (planned)
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_DB: sconnect_test
          POSTGRES_PASSWORD: test
        ports: ["5432:5432"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install -r backend/requirements.txt
      - run: cd backend && DATABASE_URL=postgresql://postgres:test@localhost:5432/sconnect_test pytest tests/ -v
```

---

## Monitoring (Planned)

- **Health**: `GET /health`, `GET /health/db`
- **Metrics**: Prometheus `/metrics` endpoint (Phase 1+)
- **Logs**: Structured JSON logging (Phase 1+)
- **Alerting**: Uptime checks on `/health`

---

## Backup Strategy (Planned)

- **Database**: Daily automated backups (Supabase/managed PG)
- **Point-in-time recovery**: Enabled on managed PostgreSQL
- **Test restores**: Monthly

---

## Rollback Procedure (Planned)

1. Deploy previous Docker image / checkout previous commit
2. Run `alembic downgrade -1` if migration applied
3. Restart service
4. Verify `/health` and `/health/db`

---

## Current Limitations

| Area | Status |
|------|--------|
| Production deployment | Not yet configured |
| Load balancing | Not implemented |
| Horizontal scaling | Not tested |
| CDN for static assets | Not configured |
| Database connection pooling | Default SQLAlchemy only |
| Secrets management | `.env` file only |

---

## Checklist Before Production

- [ ] `SECRET_KEY` generated (32+ random chars)
- [ ] `DATABASE_URL` points to managed PostgreSQL
- [ ] `CORS_ORIGINS` restricted to production domains
- [ ] `SESSION_COOKIE_SECURE=true`
- [ ] TLS certificates configured
- [ ] Rate limiting implemented
- [ ] Logging structured and aggregated
- [ ] Monitoring/alerting configured
- [ ] Backup/restore tested
- [ ] Security headers (CSP, HSTS, etc.)
- [ ] Dependency vulnerability scan
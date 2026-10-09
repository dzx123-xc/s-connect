# SConnect

**SConnect** is a sports community platform connecting players, coaches, clubs, organizers, and referees across India.

## Current Status: Phase 0 Foundation ✅

This repository contains the **Phase 0 foundation** only. Phase 1+ features are **planned, not implemented**.

---

## Implemented in Phase 0

### Backend (FastAPI + SQLAlchemy)
- **Health endpoints**: `GET /health`, `GET /health/db`
- **Authentication foundation**:
  - User registration with role-based profiles (player, coach, club, organizer, referee, admin)
  - Argon2id password hashing
  - Server-side database sessions with HttpOnly cookies
  - Session creation, validation, revocation
  - Role-based authorization foundation
  - Admin role separation
- **Location hierarchy models**: State → District → City/Town/Mandal → Village
- **Database**: SQLite (local), PostgreSQL-ready via SQLAlchemy
- **Migrations**: Alembic configured

### Frontend (Vanilla HTML/CSS/JS)
- Design system with CSS custom properties
- Component library (buttons, forms, cards, modals, etc.)
- Responsive layout system
- Animation utilities
- API client with cookie-based auth
- Auth state management

### Testing
- `pytest` configuration with FastAPI TestClient
- Auth tests: password hashing, verification, session lifecycle
- Health endpoint tests

---

## Planned (Not Implemented)

| Feature | Status |
|---------|--------|
| Player/Coach/Club dashboards | 📋 Planned |
| Discovery & search | 📋 Planned |
| Court/venue management | 📋 Planned |
| Match scheduling & scoring | 📋 Planned |
| Tournaments & events | 📋 Planned |
| Notifications | 📋 Planned |
| Real-time chat | 📋 Planned |
| Payment integration | 📋 Planned |
| Mobile apps | 📋 Planned |

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js not required (vanilla frontend)

### Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env  # Edit values as needed
python -m app.main
```
Server runs at `http://localhost:8000`

### Run Tests
```bash
cd backend
pytest tests/ -v
```

### Frontend
Static files served automatically by FastAPI from `../frontend/`

---

## Project Structure

```
SConnect/
├── backend/
│   ├── app/
│   │   ├── auth/           # Argon2, sessions, dependencies
│   │   ├── config.py       # Settings via pydantic-settings
│   │   ├── database.py     # SQLAlchemy engine, session
│   │   ├── main.py         # FastAPI app, lifespan, middleware
│   │   ├── models/         # SQLAlchemy models
│   │   ├── routes/         # API routers (health, auth)
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── utils/          # Validators
│   ├── migrations/         # Alembic migrations
│   ├── tests/              # Pytest tests
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── css/                # Design system, components, layout, animations
│   └── js/                 # API client, auth state
├── data/
│   └── locations/          # JSON location data (AP, Kerala)
├── .env.example
├── .gitignore
├── README.md
├── SECURITY.md
└── DEPLOYMENT.md
```

---

## API Endpoints (Phase 0)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Service health check |
| GET | `/health/db` | Database connectivity check |
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login user |
| POST | `/auth/logout` | Logout user |
| GET | `/auth/me` | Get current user (auth required) |

---

## Environment Variables

See `.env.example` for all configurable options.

Key variables:
- `DATABASE_URL` - SQLite (local) or PostgreSQL (production)
- `SECRET_KEY` - Session signing key (min 32 chars in production)
- `SESSION_MAX_AGE` - Session lifetime in seconds
- `CORS_ORIGINS` - Allowed frontend origins

---

## License

Proprietary - All rights reserved.
# Matamaal - Kitchen Production Tracker

## Project Overview
Matamaal (मालमाता - \"Inventory Mother\") is a full-stack web application for tracking daily kitchen production in a restaurant specializing in authentic Kashmiri/Wazwan cuisine. Cooks log quantities of prepared menu items (grouped by categories like Appetisers, Wazwan), while admins oversee, filter, and manage entries. Built with modern Python FastAPI backend and vanilla JS frontend, it supports role-based access (admin/cook), category permissions, and SQLite persistence.

Key workflow:
1. Cook logs into dashboard, selects category ID, loads menu, submits production (qty + unit: kg/portion/pieces).
2. Admin views all entries, filters by category/date, deletes if needed.
3. Auto-seeded with ~50 real Kashmiri menu items across 5 categories (Veg/Non-Veg tagged).

Live demo ready: Backend API + frontend dashboard functional (login currently uses test token for quick access).

## Features
### Backend (Completed)
- ✅ User auth (JWT) with roles: admin (full access), cook (category-restricted)
- ✅ Menu management: Seeded Kashmiri dishes (Paneer Roganjosh, Mutton Rista, etc.)
- ✅ Production tracking: POST/GET/DELETE entries with validation (active items, perms)
- ✅ Category-based access: Cooks assigned to specific categories
- ✅ API docs at `/docs`
- ✅ CORS enabled for frontend

### Frontend (Mostly Complete)
- ✅ Login page (mock token for now)
- ✅ Role-aware dashboard:
  - Cook: Load menu by category, single/bulk submit production
  - Admin: List/filter/delete entries, category loader
- ✅ Responsive JS with fetch API, localStorage tokens

## Tech Stack
- **Backend**: FastAPI, SQLAlchemy, SQLite (`matamaal.db`), Pydantic, JWT
- **Frontend**: HTML5, Vanilla JS, CSS
- **Database**: SQLite (auto-migrate, seed on startup)
- **Dev**: uvicorn, pip

## Project Structure
```
mtml/
├── README.md                 # This file
├── TODO.md                   # Progress tracker
├── backend/
│   ├── main.py              # FastAPI app entry
│   ├── database.py          # DB engine/Session
│   ├── models.py            # User, Category, MenuItem, ProductionEntry
│   ├── auth.py              # Password hash, JWT deps
│   ├── requirements.txt     # fastapi, uvicorn, sqlalchemy, python-jose, passlib
│   ├── matamaal.db          # SQLite DB (gitignored)
│   └── routers/             # auth.py, production.py, admin.py, MenuItemResponse.py
└── frontend/
    ├── index.html           # Login
    ├── dashboard.html       # Main UI
    ├── script.js            # API logic, auth, tables
    └── styles.css           # Styling
```

## Quick Start
### 1. Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```
- API: http://localhost:8000/docs
- Health: http://localhost:8000/health

### 2. Frontend
Open `frontend/index.html` in browser (served statically, connects to backend).

### Sample Credentials (Auto-seeded)
- Admins: `admin1` / `pw123` | `admin2` / `pw123`
- Cooks: `cook1` / `pw123` | `cook2` / `pw123`
*(Note: Real login backend-ready; frontend uses test token for instant dashboard access)*

## API Endpoints Overview
| Method | Endpoint | Role | Description |
|--------|----------|------|-------------|
| POST | `/auth/login` | Any | Get JWT |
| POST | `/production-entries/` | Cook/Admin | Log production |
| GET | `/production-entries/` | Admin/Cook | List entries |
| GET | `/production-entries/menu-items/?category_id=X` | Cook/Admin | Load active menu |
| DELETE | `/production-entries/{id}` | Admin | Delete entry |
| GET | `/admin/categories` | Admin | List categories |

## Current Progress
### Completed
- [x] Backend core: Models (w/ units/categories), routers (production CRUD + perms), seeding (~50 menu items)
- [x] DB migration (manual ALTER for legacy compat)
- [x] Frontend: Login → Dashboard flow, cook production UI (load/submit), admin list/delete
- [x] Role/permission logic (cook category-restricted)
- [x] CORS, auto-table creation, startup seeding

### In Progress (Per backend/TODO.md)
- Testing: POST/GET/DELETE as admin/cook (endpoints ready)
- Recent: Added `unit` field, menu-item loading, category_id to User

## Planned Features / Next Steps
- [ ] Fix real login (connect frontend form to `/auth/login`)
- [ ] Complete admin router: Category CRUD, user assignment
- [ ] Polish frontend: Real auth check, error UX, date filters, charts/reports
- [ ] Testing: Unit/integration tests (pytest)
- [ ] Deploy: Docker, Railway/Vercel, PostgreSQL prod DB
- [ ] Mobile: PWA support
- [ ] Enhancements: Inventory deduction, reports (daily total kg), multi-unit, photos

## What I Learned
- FastAPI + SQLAlchemy: Rapid API dev, ORM relations (back_populates), deps injection.
- Role-based perms: JWT claims + endpoint guards.
- Seeding: Startup events for prod data.
- Vanilla JS frontend: Fetch, localStorage, dynamic tables/selects (no framework overhead).
- Kashmiri cuisine: Wazwan traditions (36+ dishes, category-specific prep).
- DB migrations: Manual ALTER for dev SQLite.
- Project planning: TODO.md tracking iterative updates.

## Author
**Admin** - Full-stack developer experimenting with FastAPI + vanilla web.
- GitHub: [Add your username]
- Started: Recent dev session on Desktop/mtml
- Status: WIP - Push to GitHub for future completion!

## License
MIT - Feel free to fork/complete!

---

*Push to GitHub anytime: `git init && git add . && git commit -m "WIP: Matamaal v1.0"`*


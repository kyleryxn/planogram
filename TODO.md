# 📋 Planogram To-Do List

This file tracks the development progress of the **Planogram** project.
Sections are divided into **To Do**, **In Progress**, and **Done**.

## 🚧 To Do
- [ ] Implement user authentication (OAuth2 password flow)
- [ ] Finalize Google OAuth redirect URIs for local and production
- [ ] **Google OCR integration (Cloud Vision API)**
  - [ ] Upload image of work schedule
  - [ ] Extract structured text from schedule (date, time, shift type)
  - [ ] Parse extracted data into events
  - [ ] Insert parsed events into user’s Google Calendar
- [ ] Create form-based schedule input (manual entry fallback)
- [ ] Implement event scheduling logic around work shifts
- [ ] Add Alembic migrations for new features
- [ ] Add Docker support for local dev/test environment
- [ ] Add static file handling for Sass 7-1 pattern
- [ ] Write tests for routes (`auth.py`, `home.py`, `calendar.py`)
- [ ] Setup CI/CD pipeline with GitHub Actions (lint, test, format, changelog, version bump)
- [ ] Document project structure and setup in `README.md`

## ⏳ In Progress
- [ ] Centralized template mapping for Jinja2
- [ ] Static files integration alongside templates
- [ ] Database integration with SQLAlchemy + AsyncSession
- [ ] View and query database with DataGrip (fix schema visibility/search path issues)
- [ ] Calendar route: list user calendars and events in Jinja2

## ✅ Done
- [x] Project structure setup (`planogram` package, package-by-feature layout)
- [x] Database created (`planogram` DB, Alembic migrations working)
- [x] Google tokens table implemented
- [x] Token persistence and refresh logic (`save_user_creds_db`, `get_user_creds_db`)
- [x] FastAPI routes package created with initial routes (`auth.py`, `home.py`, `calendar.py`)
- [x] Base Jinja2 template (`base.html`) with extendable blocks
- [x] Global template map utility for route rendering
- [x] Initial Git commit templates configured

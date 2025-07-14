""
# Calendar Stacker Project Plan

## Project Overview

Calendar Stacker is a Flask-based application designed to stack and synchronize multiple calendars through a centralized OAuth integration, enabling users to consolidate scheduling information seamlessly.

---

## Phase 1: Project Initialization & Core OAuth Logic (Complete ✅)

### Week 1–2
- [x] Project structure created with Flask blueprints and modules
- [x] Initial GitHub repository set up (`rank_rocket_calendar_stacker`)
- [x] `client.py`, `calendar.py`, `user.py` routes implemented
- [x] Core OAuth model scaffolded (`OAuthCredential`)
- [x] CI pipeline configured via GitHub Actions
- [x] `pytest.ini` and base unit test structure created

---

## Phase 2: OAuth Routes, Models, and Unit Tests

### Week 3 (In Progress)

#### ✅ Completed
- [x] `oauth.py` routes implemented with `/authorize` and `/callback` endpoints
- [x] Created `OAuthCredential` SQLAlchemy model with proper serialization and constraints
- [x] Unit test structure setup with `conftest.py` providing Flask test app and database context
- [x] `Client` model patched to accept `name` and `email`
- [x] Added `TestingConfig` class to `config.py`
- [x] Database initialization and teardown implemented in `conftest.py`
- [x] Project-wide import errors and circular dependency issues resolved

#### ❗ Outstanding
- [ ] Tests still failing due to import/config errors (likely `src.config` path or fixture reuse)
- [ ] Final OAuth routes (`refresh_token`, token expiry handling) not yet implemented
- [ ] Basic front-end UI for user authorization flow still needed

---

## Phase 3: Calendar Integration Layer

### Week 4 (Upcoming)
- [ ] Implement Google Calendar API wrapper (`calendar_google.py`)
- [ ] Define core calendar sync strategy and logic
- [ ] Connect authorized users' credentials to pull/push calendar events

---

## Phase 4: UI Integration & Launch Prep

### Week 5
- [ ] Build simple UI dashboard with React
- [ ] Integrate login/auth flow into front-end
- [ ] Final polish and deploy to production

---

## Time Log

| Date       | Hours | Tasks Completed                                |
|------------|-------|------------------------------------------------|
| 13-07-2025 | 6     | Patched tests, OAuth model, config setup, debugging CI errors |
""

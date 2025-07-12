## Phase 1: MVP Development (Weeks 1–4)&#x20;

### Week 1 – Project Setup & Core Infrastructure

* **Dev environment & repo**

  * Initialize Git, define Python 3.10+ venv, add `.gitignore`.
  * Install key deps: Flask, SQLAlchemy, Google API client, Bootstrap, axios/fetch polyfill.
* **Project structure**

  * `main.py`: Flask app factory, blueprint registration (`client_bp`, later `calendar_bp`).
  * `src/models/`: define `Client` and `OAuthCredential` SQLAlchemy models.
  * `src/routes/`: create `client.py` (you have this) and empty `calendar.py`.
* **Database schema**

  * Migrate or create tables for clients, oauth\_credentials.
  * Ensure fields match: `google_client_secret`, `scopes`, `is_valid`, `expires_at`.
* **UI scaffolding**

  * `index.html`: navigation skeleton (Dashboard, Clients, Events, OAuth, Settings).
  * `app.js`: empty functions for `loadClients()`, `loadCalendars()`, `loadEvents()`, `saveOAuthCredentials()`.
* **Validation & error handling**

  * Global Flask error handler and `@app.errorhandler` for 404/500.
  * Front-end `showAlert()` utility for user feedback.

### Week 2 – Client Management System

* **Backend**

  * Fully implement CRUD endpoints in `src/routes/client.py`:

    * `GET /api/clients`, `POST /api/clients`, `PUT /api/clients/<id>`, `DELETE /api/clients/<id>`.
    * Input validation (e.g. non-empty name/email).
  * Unit tests for each endpoint (pytest + coverage).
* **Frontend**

  * `loadClientsForEventSection()` & `loadClientsForOAuth()` in `app.js` to populate `<select>`s.
  * Modals/forms for Add/Edit/Delete client in `index.html`.
  * Client-side form validation (HTML5 + custom JS).
* **QA**

  * Manual test per **Run & Test Guide** .
  * Ensure 100% of client paths work end-to-end.

### Week 3 – OAuth Integration Foundation

* **OAuth CRUD**

  * REST endpoints in `src/routes/oauth.py` (or in `client.py`):

    * `POST /api/oauth` to save Google Client ID/Secret + scopes.
    * `GET`, `PUT`, `DELETE /api/oauth/<id>`.
  * Model enhancements: `scopes`, `access_token`, `refresh_token`, `expires_at`, `is_valid`.
* **OAuth flow**

  * `POST /api/oauth/<id>/authorize` → generate Google consent URL.
  * Callback route (e.g. `/api/oauth/callback`) to exchange code for tokens.
  * Store tokens, set `is_valid=True`.
* **UI**

  * OAuth modal in `index.html` with fields: Client, Google Client ID, Secret, Scopes.
  * `saveOAuthCredentials()` and `authorizeOAuth()` in `app.js` .
* **Testing**

  * Simulate the full OAuth handshake in dev (use ngrok or loopback).
  * Validate token storage and auto-refresh logic.

### Week 4 – Basic Event Management

* **API Wrapper**

  * `src/google_calendar.py`: implement `list_calendars()`, `list_events()`, `get_event()`, `create_event()`, `update_event()`, `delete_event()` .
* **Backend endpoints**

  * `GET /api/clients/<client_id>/calendars` → returns `[ {id, summary} ]`.
  * `GET /api/clients/<c>/calendars/<cal>/events`, `POST`, `PUT`, `DELETE /events`.
* **Frontend integration**

  * `loadCalendars()` and `loadEvents()` in `app.js` to fetch and populate dropdowns and event list .
  * Event-modal form with fields for title, description, start/end, attendees, recurrence.
* **Integration testing**

  * Full workflow: select client → select calendar → list/create/update/delete events.

---

## Phase 2: Enhanced Features (Weeks 5–8)&#x20;

1. **Advanced Data Validation & UI/UX**

   * Time-zone conversion, recurrence rule validation, attendee email checks.
   * Adopt a JS calendar library (e.g., FullCalendar) for interactive event views.
2. **Asynchronous Processing & Caching**

   * Integrate Celery + Redis for background tasks (bulk imports/exports).
   * In-memory or Redis caching of calendar lists and recent events with TTL.
3. **Multi-Client & Multi-User Prep**

   * Extend schema: associate events and credentials clearly to clients.
   * UI “Switch Client” control and bulk operations for events across calendars.
4. **Performance & Rate-Limit Management**

   * API call throttling, exponential backoff, quota monitoring.
   * DB indexing on common query fields (client\_id, calendar\_id).
5. **Error Handling & Monitoring**

   * Centralized logging (e.g., Sentry), health-check endpoints, APM integration.
   * Enhanced user guidance for transient failures and token expiries.

---

## Phase 3: Production & Launch (Weeks 9–10)&#x20;

### Week 9 – Production Preparation

* **Infrastructure**

  * Provision production server (Heroku/Docker on AWS/GCP), configure Gunicorn + nginx.
  * Secure database (PostgreSQL), apply migrations.
  * Set up HTTPS/SSL, environment variables for secrets.
* **CI/CD**

  * GitHub Actions pipeline: run tests, lint (flake8/Black), build Docker image, deploy.
* **Security Hardening**

  * CSRF protection, input sanitization, AES-256 encryption for tokens at rest.

### Week 10 – Deployment & Launch

* **UAT & Training**

  * Conduct user acceptance tests, finalize UI tweaks.
  * Prepare end-user guide (based on your Run & Test doc) .
* **Monitoring & Support**

  * Enable logging dashboards, alerting on error thresholds and latency.
  * Rollout plan with rollback and incident response procedures.

---

### Success Criteria & Next Steps

* **MVP live** with full CRUD for clients, OAuth, calendars, and events.
* **Performance**: 95% of API calls <2 s; error rate <1%.
* **Adoption**: User on-boarding completion >90%; task completion <30 s .

# Calendar Stacker Project Plan (Updated 2025-07-15)

## ✅ Completed (Week 2)

### Backend

* Fully implemented **CRUD API** for Clients in `src/routes/client.py`:

  * `GET /api/clients`
  * `POST /api/clients`
  * `PUT /api/clients/<id>`
  * `DELETE /api/clients/<id>`
* Added validation logic for name/email
* Verified that all endpoints properly commit to the DB
* Added `GET /api/clients/<client_id>/calendars` to list calendars using `GoogleCalendarService`

  * Injected `OAuthCredential` properly
  * Correctly passed `google_account_email` and/or credential object depending on implementation

### Debugging

* Fixed incorrect constructor usage for `GoogleCalendarService`
* Resolved Pylance false-positives related to:

  * missing parameters (`google_account_email`, `oauth_credentials`)
  * unresolvable imports

### Code Quality

* File headers standardized per coding guidelines
* Semantic versioning and modification timestamps applied to `client.py`

---

## Next Session (Week 3)

### OAuth Integration Foundation

* Implement OAuth CRUD routes in `src/routes/oauth.py`
* Add modal/form in UI to input Google OAuth credentials
* Enable Google consent flow (initiate + callback handler)
* Store access/refresh tokens securely in DB
* Mark OAuth record as `is_valid=True` after token exchange

### Tasks

* Scaffold `OAuthCredential` model if not already defined
* Register and test new OAuth blueprint
* Begin integration testing for full OAuth handshake

---

## Tracking

* **Current file:** `src/routes/client.py`
* **Version:** 1.07
* **Next target file:** `src/routes/oauth.py` and `src/models/oauth_credential.py`
* **Environment:** Python 3.10+, Flask, SQLAlchemy, Google API client

---

# Calendar Stacker Project Plan (Updated 2025-07-15)

## ✅ Completed to Date

### Week 2 – Client Management & Preliminary Calendar

* **Clients CRUD API** in `src/routes/client.py`: GET, POST, PUT, DELETE with full validation and tests.
* **Client → Calendar endpoint**: `GET /api/clients/<client_id>/calendars` wired to `GoogleCalendarService`.
* **Debug fixes**: constructor misuse, Pylance import errors.
* **Code quality**: standardized file headers, semantic versioning, PR linting.

### Week 3 (So Far) – OAuth Model & Migration Setup

* **Model scaffolding**: `src/models/oauth.py` created for `OAuthCredential`.
* **Package initializers**: added `src/__init__.py` and `src/models/__init__.py` for proper imports.
* **VS Code config**: `.vscode/settings.json` set `python.analysis.extraPaths = ["./src"]`.
* **Alembic environment**: patched `migrations/env.py` to import all models and use `db.metadata`.

---

## 🎯 Next Steps (Week 3 Continued)

1. **Generate & Apply Migration**

   * Run `alembic revision --autogenerate -m "Add OAuthCredential model"`
   * Review generated script for `oauth_credentials` table and FK to `clients`
   * Execute `alembic upgrade head` to apply

2. **OAuth CRUD API** (`src/routes/oauth.py`)

   * `POST /api/oauth` → create credential record
   * `GET /api/oauth/<id>` → fetch by ID
   * `PUT /api/oauth/<id>` → update client ID/secret & scopes
   * `DELETE /api/oauth/<id>` → remove credentials
   * Add unit tests for each endpoint (pytest + mocks)

3. **OAuth Authorization Flow**

   * `POST /api/oauth/<id>/authorize` → generate Google consent URL
   * Callback route `/api/oauth/callback` → exchange code for tokens
   * Store `access_token`, `refresh_token`, `expires_at`; set `is_valid = True`
   * Handle token refresh logic in background or on-demand

4. **Frontend OAuth Integration**

   * Add OAuth modal in `index.html`: client selector, ID, Secret, Scopes
   * Implement `saveOAuthCredentials()` & `authorizeOAuth()` in `app.js`
   * Visual feedback via `showAlert()` for success/errors

### Milestone: End of Week 3

* OAuth model in DB
* Full CRUD + authorization handshake working end-to-end
* Automated tests covering API + migration

---

## 🗓️ Looking Ahead (Week 4)

* **Event Management API** and calendar wrapper (`src/google_calendar.py`)
* **Frontend calendar & event UI** (dropdowns, lists, modals)
* **Integration testing** for workflows

---

**Onward to OAuth!** Let me know when you’re ready to scaffold the routes or mock the Google flow.



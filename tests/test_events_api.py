"""
Module/Script Name: tests/test_events_api.py

Description:
Pytest suite for the Event CRUD JSON API endpoints in src/routes/events_api.py.
Covers listing, creation, retrieval, updating, and deletion operations with a stubbed service for deterministic testing.

Author(s):
Skippy the Code Slayer

Created Date:
18-07-2025

Last Modified Date:
18-07-2025

Version:
v1.09

Comments:
- Uses a unique in-memory SQLite database per test via a UUID-based URI
- Seeds a Client and fully populated OAuthCredential (google_client_id, google_client_secret, google_redirect_uri, scopes, token_status, expires_at, is_valid)
- Stubs GoogleCalendarService via DummyService for predictable API responses
- Does not manually register the `events_bp` blueprint (already registered in `create_app`)
- Ensures engine disposal in teardown
"""

import pytest
import uuid
import datetime
from src.main import create_app
from src.extensions import db
from src.models.client import Client
from src.models.oauth_credential import OAuthCredential
from src.services.google_calendar_service import GoogleCalendarService
from src.routes.events_api import events_bp  # imported for context, not re-registered


# Stubbed service implementation for testing
class DummyService:
    def __init__(self, creds):
        pass

    def list_events(self, calendar_id):
        return {
            "success": True,
            "data": [
                {
                    "id": "evt1",
                    "summary": "Test Event",
                    "start": {"dateTime": "2025-07-28T10:00:00Z"},
                    "end": {"dateTime": "2025-07-28T11:00:00Z"},
                }
            ],
        }

    def get_event(self, calendar_id, event_id):
        return {
            "success": True,
            "data": {
                "id": event_id,
                "summary": "Test Event",
                "start": {"dateTime": "2025-07-28T10:00:00Z"},
                "end": {"dateTime": "2025-07-28T11:00:00Z"},
            },
        }

    def create_event(self, calendar_id, data):
        return {"success": True, "data": {"id": "new_evt", **data}}

    def update_event(self, calendar_id, event_id, data):
        return {"success": True, "data": {"id": event_id, **data}}

    def delete_event(self, calendar_id, event_id):
        return {"success": True, "data": {"deleted": True}}


@pytest.fixture
def app():
    # Configure a unique in-memory SQLite database
    uid = uuid.uuid4().hex
    db_uri = f"sqlite:///file:{uid}?mode=memory&cache=shared&uri=true"
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": db_uri})
    with app.app_context():
        # Reset schema
        db.drop_all()
        db.create_all()
        # Seed Client and OAuthCredential with required fields
        client_obj = Client(
            name="C1", email="c1@example.com", google_account_email="g1@example.com"
        )
        db.session.add(client_obj)
        db.session.commit()
        expires = datetime.datetime(2026, 1, 1, 0, 0, 0)
        cred = OAuthCredential(
            client_id=client_obj.id,
            google_client_id="dummy_client",
            google_client_secret="dummy_secret",
            google_redirect_uri="https://dummy/callback",
            scopes=["dummy_scope"],
            token_status="valid",
            expires_at=expires,
            is_valid=True,
        )
        db.session.add(cred)
        db.session.commit()
        yield app
        # Teardown: close session and dispose engine
        db.session.remove()
        db.drop_all()
        engine = db.get_engine(app=app)
        engine.dispose()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def stub_service(monkeypatch):
    # Replace GoogleCalendarService methods with DummyService equivalents
    monkeypatch.setattr(GoogleCalendarService, "__init__", lambda self, creds: None)
    monkeypatch.setattr(GoogleCalendarService, "list_events", DummyService.list_events)
    monkeypatch.setattr(GoogleCalendarService, "get_event", DummyService.get_event)
    monkeypatch.setattr(
        GoogleCalendarService, "create_event", DummyService.create_event
    )
    monkeypatch.setattr(
        GoogleCalendarService, "update_event", DummyService.update_event
    )
    monkeypatch.setattr(
        GoogleCalendarService, "delete_event", DummyService.delete_event
    )


def test_list_events(client):
    client_obj = Client.query.first()
    assert client_obj is not None
    cid = client_obj.id
    resp = client.get(f"/api/clients/{cid}/calendars/cal1/events")
    assert resp.status_code == 200
    json_data = resp.get_json()
    assert isinstance(json_data, dict)
    assert "data" in json_data and isinstance(json_data["data"], list)


def test_get_event(client):
    client_obj = Client.query.first()
    assert client_obj is not None
    cid = client_obj.id
    resp = client.get(f"/api/clients/{cid}/calendars/cal1/events/evt1")
    assert resp.status_code == 200
    data = resp.get_json().get("data")
    assert data is not None
    assert data["id"] == "evt1"


def test_create_event(client):
    client_obj = Client.query.first()
    assert client_obj is not None
    cid = client_obj.id
    payload = {
        "summary": "New Event",
        "start": {"dateTime": "2025-07-29T09:00:00Z"},
        "end": {"dateTime": "2025-07-29T10:00:00Z"},
    }
    resp = client.post(f"/api/clients/{cid}/calendars/cal1/events", json=payload)
    assert resp.status_code == 201
    data = resp.get_json().get("data")
    assert data is not None
    assert data["id"] == "new_evt"


def test_update_event(client):
    client_obj = Client.query.first()
    assert client_obj is not None
    cid = client_obj.id
    payload = {
        "summary": "Updated",
        "start": {"dateTime": "2025-07-29T11:00:00Z"},
        "end": {"dateTime": "2025-07-29T12:00:00Z"},
    }
    resp = client.put(f"/api/clients/{cid}/calendars/cal1/events/evt1", json=payload)
    assert resp.status_code == 200
    data = resp.get_json().get("data")
    assert data is not None
    assert data["summary"] == "Updated"


def test_delete_event(client):
    client_obj = Client.query.first()
    assert client_obj is not None
    cid = client_obj.id
    resp = client.delete(f"/api/clients/{cid}/calendars/cal1/events/evt1")
    assert resp.status_code == 200
    json_data = resp.get_json().get("data")
    assert json_data is not None
    assert json_data.get("deleted") is True

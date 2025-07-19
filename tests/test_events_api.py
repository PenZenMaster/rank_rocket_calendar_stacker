"""
Module/Script Name: tests/test_events_api.py

Description:
Pytest suite for the Event CRUD JSON API endpoints in src/routes/events_api.py.
Covers list, create, retrieve, update, and delete operations, mocking GoogleCalendarService.

Author(s):
Skippy the Code Slayer

Created Date:
28-07-2025

Last Modified Date:
29-07-2025

Version:
v1.01

Comments:
- Uses unique in-memory SQLite DB per test via UUID URI for isolation
- Seeds a test client and valid OAuthCredential in setup
- Monkeypatches GoogleCalendarService to return controlled responses
- Asserts client exists before accessing `id` to avoid None issues
"""

import pytest
import uuid
from src.main import create_app
from src.extensions import db
from src.models.client import Client
from src.models.oauth_credential import OAuthCredential
from src.routes.events_api import events_bp
from src.services.google_calendar_service import GoogleCalendarService


# Dummy service for testing
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
    # Unique in-memory DB for events API tests
    uid = uuid.uuid4().hex
    db_uri = f"sqlite:///file:{uid}?mode=memory&cache=shared&uri=true"
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": db_uri})
    app.register_blueprint(events_bp)
    with app.app_context():
        db.drop_all()
        db.create_all()
        # Seed a client and valid OAuthCredential
        client_obj = Client(
            name="C1", email="c1@example.com", google_account_email="g1@example.com"
        )
        db.session.add(client_obj)
        db.session.commit()
        cred = OAuthCredential(
            client_id=client_obj.id,
            token_status="valid",
            expires_at="2026-01-01T00:00:00Z",
            is_valid=True,
        )
        db.session.add(cred)
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()
        engine = db.get_engine(app=app)
        engine.dispose()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def stub_service(monkeypatch):
    # Replace real service with dummy implementation
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
    # Ensure client exists
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

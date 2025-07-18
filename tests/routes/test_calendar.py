"""
Module/Script Name: tests/routes/test_calendar.py

Description:
Unit tests for calendar routes, covering list, event CRUD flows and error handling.

Author(s):
Skippy the Code Slayer with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
17-07-2025

Last Modified Date:
19-07-2025

Version:
v1.03

Comments:
- Adjusted URL paths to match calendar_bp route prefixes under /clients/<client_id>/calendars
- Added secret_key to app fixture to enable session for flash messages
"""

import pytest
from unittest.mock import patch, MagicMock
from src.main import create_app  # factory returns Flask app


@pytest.fixture
def app():
    # Initialize Flask app with TESTING and session support
    app = create_app({"TESTING": True})
    app.secret_key = "test-secret-key"
    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    with app.test_client() as client:
        with app.app_context():
            yield client


@patch("src.routes.calendar.OAuthCredential")
@patch("src.routes.calendar.GoogleCalendarService")
def test_list_calendars_success(mock_service_cls, mock_cred_cls, client):
    # Setup mock credential lookup
    mock_cred = MagicMock(is_valid=True)
    mock_cred_cls.query.filter_by.return_value.first.return_value = mock_cred
    # Setup service.list_calendars
    service = mock_service_cls.return_value
    service.list_calendars.return_value = [{"id": "cal1", "summary": "Cal 1"}]

    # Use actual route: GET /clients/1/calendars
    resp = client.get("/clients/1/calendars")
    assert resp.status_code == 200
    assert b"Cal 1" in resp.data


@patch("src.routes.calendar.OAuthCredential")
@patch("src.routes.calendar.GoogleCalendarService")
def test_list_calendars_no_cred(mock_service_cls, mock_cred_cls, client):
    # No credentials found → redirect to client list
    mock_cred_cls.query.filter_by.return_value.first.return_value = None
    resp = client.get("/clients/1/calendars", follow_redirects=False)
    assert resp.status_code == 302
    assert "/clients" in resp.headers["Location"]


@patch("src.routes.calendar.OAuthCredential")
@patch("src.routes.calendar.GoogleCalendarService")
def test_create_event_post(mock_service_cls, mock_cred_cls, client):
    # Setup valid cred and service
    mock_cred = MagicMock(is_valid=True)
    mock_cred_cls.query.filter_by.return_value.first.return_value = mock_cred
    service = mock_service_cls.return_value
    service.create_event.return_value = {"id": "evt1"}

    data = {"summary": "Test", "start": "2025-07-17T10:00", "end": "2025-07-17T11:00"}
    # Use actual route: POST /clients/1/calendars/events/new
    resp = client.post(
        "/clients/1/calendars/events/new", data=data, follow_redirects=True
    )
    assert resp.status_code == 200
    assert b"Event created successfully" in resp.data


@patch("src.routes.calendar.OAuthCredential")
@patch("src.routes.calendar.GoogleCalendarService")
def test_edit_event_get_and_post(mock_service_cls, mock_cred_cls, client):
    # Setup valid cred and service
    mock_cred = MagicMock(is_valid=True)
    mock_cred_cls.query.filter_by.return_value.first.return_value = mock_cred
    service = mock_service_cls.return_value
    # GET returns existing event
    service.get_event.return_value = {
        "id": "evt1",
        "summary": "Existing",
        "start": {"dateTime": "2025-07-17T10:00:00Z"},
        "end": {"dateTime": "2025-07-17T11:00:00Z"},
    }
    # Actual route: GET /clients/1/calendars/events/evt1/edit
    resp_get = client.get("/clients/1/calendars/events/evt1/edit")
    assert resp_get.status_code == 200
    assert b"Existing" in resp_get.data

    # POST updates via same URL
    data = {
        "summary": "Updated",
        "start": "2025-07-17T12:00",
        "end": "2025-07-17T13:00",
    }
    resp_post = client.post(
        "/clients/1/calendars/events/evt1/edit", data=data, follow_redirects=True
    )
    assert resp_post.status_code == 200
    assert b"Event updated successfully" in resp_post.data


@patch("src.routes.calendar.OAuthCredential")
@patch("src.routes.calendar.GoogleCalendarService")
def test_delete_event(mock_service_cls, mock_cred_cls, client):
    # Setup valid cred and service
    mock_cred = MagicMock(is_valid=True)
    mock_cred_cls.query.filter_by.return_value.first.return_value = mock_cred
    service = mock_service_cls.return_value

    # Use actual route: POST /clients/1/calendars/events/evt1/delete
    resp = client.post("/clients/1/calendars/events/evt1/delete", follow_redirects=True)
    assert resp.status_code == 200
    assert b"Event deleted successfully" in resp.data

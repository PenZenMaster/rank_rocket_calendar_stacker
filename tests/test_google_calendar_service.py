"""
Module/Script Name: tests/test_google_calendar_service.py

Description:
Unit tests for GoogleCalendarService class including calendar and event operations.

Author(s):
Skippy the Code Slayer with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
15-07-2025

Last Modified Date:
15-07-2025

Version:
v1.01

Comments:
- Corrected mock path to point to src.google_calendar instead of nonexistent module
"""

import pytest
from unittest.mock import patch, MagicMock
from src.google_calendar import GoogleCalendarService


@pytest.fixture
def mock_credential():
    client = MagicMock(client_id="client_id", client_secret="client_secret")
    return MagicMock(
        access_token="token",
        refresh_token="refresh_token",
        client=client,
    )


@patch("src.google_calendar.build")
def test_list_calendars(mock_build, mock_credential):
    service_instance = MagicMock()
    mock_build.return_value = service_instance
    service_instance.calendarList().list().execute.return_value = {
        "items": ["calendar1", "calendar2"]
    }

    calendar_service = GoogleCalendarService(mock_credential)
    calendars = calendar_service.list_calendars()

    assert calendars == ["calendar1", "calendar2"]
    mock_build.assert_called_once()


@patch("src.google_calendar.build")
def test_list_events(mock_build, mock_credential):
    service_instance = MagicMock()
    mock_build.return_value = service_instance
    service_instance.events().list().execute.return_value = {
        "items": ["event1", "event2"]
    }

    calendar_service = GoogleCalendarService(mock_credential)
    events = calendar_service.list_events()

    assert events == ["event1", "event2"]


@patch("src.google_calendar.build")
def test_get_event(mock_build, mock_credential):
    service_instance = MagicMock()
    mock_build.return_value = service_instance
    service_instance.events().get().execute.return_value = {"id": "1234"}

    calendar_service = GoogleCalendarService(mock_credential)
    event = calendar_service.get_event("primary", "1234")

    assert event["id"] == "1234"


@patch("src.google_calendar.build")
def test_create_event(mock_build, mock_credential):
    service_instance = MagicMock()
    mock_build.return_value = service_instance
    service_instance.events().insert().execute.return_value = {"id": "new_event"}

    calendar_service = GoogleCalendarService(mock_credential)
    result = calendar_service.create_event("primary", {"summary": "Test Event"})

    assert result["id"] == "new_event"


@patch("src.google_calendar.build")
def test_update_event(mock_build, mock_credential):
    service_instance = MagicMock()
    mock_build.return_value = service_instance
    service_instance.events().update().execute.return_value = {"id": "updated_event"}

    calendar_service = GoogleCalendarService(mock_credential)
    result = calendar_service.update_event(
        "primary", "event_id", {"summary": "Updated Event"}
    )

    assert result["id"] == "updated_event"


@patch("src.google_calendar.build")
def test_delete_event(mock_build, mock_credential):
    service_instance = MagicMock()
    mock_build.return_value = service_instance
    service_instance.events().delete().execute.return_value = {}

    calendar_service = GoogleCalendarService(mock_credential)
    result = calendar_service.delete_event("primary", "event_id")

    assert result == {}

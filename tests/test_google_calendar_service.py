"""
Module/Script Name: tests/test_google_calendar_service.py

Description:
Unit tests for GoogleCalendarService using mocked Google API client.

Author(s):
Skippy the Code Slayer with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
15-07-2025

Last Modified Date:
15-07-2025

Version:
v1.00

Comments:
- Mocks build() and service methods for isolated logic testing
"""

import pytest
from unittest.mock import patch, MagicMock
from src.google_calendar_service import GoogleCalendarService


@pytest.fixture
def mock_creds():
    return {
        "token": "fake-token",
        "refresh_token": "fake-refresh",
        "client_id": "abc",
        "client_secret": "xyz",
        "token_uri": "https://oauth2.googleapis.com/token",
    }


@patch("src.google_calendar_service.build")
def test_list_events(mock_build, mock_creds):
    mock_service = MagicMock()
    mock_events = [{"id": "1", "summary": "Test Event"}]
    mock_service.events.return_value.list.return_value.execute.return_value = {
        "items": mock_events
    }
    mock_build.return_value = mock_service

    service = GoogleCalendarService(mock_creds)
    events = service.list_events()

    assert events == mock_events


@patch("src.google_calendar_service.build")
def test_get_event(mock_build, mock_creds):
    mock_service = MagicMock()
    expected = {"id": "123", "summary": "Sample Event"}
    mock_service.events.return_value.get.return_value.execute.return_value = expected
    mock_build.return_value = mock_service

    service = GoogleCalendarService(mock_creds)
    result = service.get_event("primary", "123")

    assert result == expected


@patch("src.google_calendar_service.build")
def test_create_event(mock_build, mock_creds):
    mock_service = MagicMock()
    new_event = {"summary": "Created"}
    mock_service.events.return_value.insert.return_value.execute.return_value = (
        new_event
    )
    mock_build.return_value = mock_service

    service = GoogleCalendarService(mock_creds)
    created = service.create_event("primary", {"summary": "Created"})

    assert created == new_event


@patch("src.google_calendar_service.build")
def test_update_event(mock_build, mock_creds):
    mock_service = MagicMock()
    updated_event = {"summary": "Updated"}
    mock_service.events.return_value.update.return_value.execute.return_value = (
        updated_event
    )
    mock_build.return_value = mock_service

    service = GoogleCalendarService(mock_creds)
    result = service.update_event("primary", "1", updated_event)

    assert result == updated_event


@patch("src.google_calendar_service.build")
def test_delete_event(mock_build, mock_creds):
    mock_service = MagicMock()
    mock_service.events.return_value.delete.return_value.execute.return_value = {}
    mock_build.return_value = mock_service

    service = GoogleCalendarService(mock_creds)
    result = service.delete_event("primary", "1")

    assert result == {}

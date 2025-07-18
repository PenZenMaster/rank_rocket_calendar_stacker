"""
Module/Script Name: tests/test_google_calendar_service.py

Description:
Unit tests for GoogleCalendarService, mocking googleapiclient calls and verifying retry logic, credential refresh, and CRUD operations.

Author(s):
Skippy the Code Slayer with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
15-07-2025

Last Modified Date:
17-07-2025

Version:
v1.03

Comments:
- Extended to cover list_events, get_event, create_event, update_event, delete_event.
- Mocked HttpError for retry and non-retry scenarios.
"""

import pytest
import time
from unittest.mock import MagicMock, patch
from googleapiclient.errors import HttpError
from src.models.oauth_credential import OAuthCredential
from src.google_calendar import GoogleCalendarService, CalendarApiError


@pytest.fixture
def fake_credential():
    # Create a dummy OAuthCredential instance
    return OAuthCredential(
        access_token="initial-token",
        refresh_token="refresh-token",
        google_client_id="client-id",
        google_client_secret="client-secret",
        scopes="https://www.googleapis.com/auth/calendar",
        expires_at=time.time() - 3600,  # expired
        is_valid=False,
    )


def make_http_error(status):
    resp = MagicMock()
    resp.status = status
    return HttpError(resp, b"")


@patch("src.google_calendar.build")
@patch("src.google_calendar.Credentials.from_authorized_user_info")
def test_service_build_and_refresh(mock_from_info, mock_build, fake_credential):
    # Setup service builder and credentials
    fake_service = MagicMock()
    mock_build.return_value = fake_service
    creds_obj = MagicMock()
    mock_from_info.return_value = creds_obj

    # Simulate refresh behavior
    with patch.object(creds_obj, "refresh") as mock_refresh:  # Remove autospec=True
        service = GoogleCalendarService(fake_credential)
        # Ensure service build was invoked correctly
        mock_build.assert_called_once_with("calendar", "v3", credentials=creds_obj)
        # Force invalid/expired credentials
        creds_obj.valid = False
        creds_obj.expired = True
        service.credentials = creds_obj
        service._ensure_valid_credentials()
        mock_refresh.assert_called_once()


@patch("src.google_calendar.build")
@patch("src.google_calendar.Credentials.from_authorized_user_info")
def test_list_calendars_retry_and_failure(mock_from_info, mock_build, fake_credential):
    fake_service = MagicMock()
    mock_build.return_value = fake_service
    mock_from_info.return_value = MagicMock()

    # Retry once on 500, then succeed
    http500 = make_http_error(500)
    stub_list = MagicMock()
    stub_list.execute.return_value = {
        "items": [{"id": "cal1", "summary": "Calendar One"}]
    }
    fake_service.calendarList.return_value.list.side_effect = [http500, stub_list]
    service = GoogleCalendarService(fake_credential)
    calendars = service.list_calendars()
    assert calendars == [{"id": "cal1", "summary": "Calendar One"}]

    # Non-retryable error
    fake_service.calendarList.return_value.list.side_effect = [make_http_error(404)]
    with pytest.raises(CalendarApiError):
        service.list_calendars()


@patch("src.google_calendar.build")
@patch("src.google_calendar.Credentials.from_authorized_user_info")
def test_list_events_retry_and_failure(mock_from_info, mock_build, fake_credential):
    fake_service = MagicMock()
    mock_build.return_value = fake_service
    mock_from_info.return_value = MagicMock()

    # Retry once on 500, then succeed
    http500 = make_http_error(500)
    stub_events = MagicMock()
    stub_events.execute.return_value = {"items": [{"id": "evt1"}]}
    fake_service.events.return_value.list.side_effect = [http500, stub_events]
    service = GoogleCalendarService(fake_credential)
    events = service.list_events("cal-id")
    assert events == [{"id": "evt1"}]

    # Non-retryable error
    fake_service.events.return_value.list.side_effect = [make_http_error(404)]
    with pytest.raises(CalendarApiError):
        service.list_events("cal-id")


@patch("src.google_calendar.build")
@patch("src.google_calendar.Credentials.from_authorized_user_info")
def test_get_event_retry_and_failure(mock_from_info, mock_build, fake_credential):
    fake_service = MagicMock()
    mock_build.return_value = fake_service
    mock_from_info.return_value = MagicMock()

    # Retry once on 500, then succeed
    http500 = make_http_error(500)
    stub_get = MagicMock()
    stub_get.execute.side_effect = [http500, {"id": "evt1", "summary": "Event One"}]
    fake_service.events.return_value.get.return_value = stub_get
    service = GoogleCalendarService(fake_credential)
    event = service.get_event("cal-id", "evt-id")
    assert event == {"id": "evt1", "summary": "Event One"}

    # Non-retryable error
    stub_fail = MagicMock()
    stub_fail.execute.side_effect = [make_http_error(404)]
    fake_service.events.return_value.get.return_value = stub_fail
    with pytest.raises(CalendarApiError):
        service.get_event("cal-id", "evt-id")


@patch("src.google_calendar.build")
@patch("src.google_calendar.Credentials.from_authorized_user_info")
def test_create_event_retry_and_failure(mock_from_info, mock_build, fake_credential):
    fake_service = MagicMock()
    mock_build.return_value = fake_service
    mock_from_info.return_value = MagicMock()

    # Retry once on 500, then succeed
    http500 = make_http_error(500)
    stub_insert = MagicMock()
    stub_insert.execute.side_effect = [http500, {"id": "evt2"}]
    fake_service.events.return_value.insert.return_value = stub_insert
    service = GoogleCalendarService(fake_credential)
    result = service.create_event("cal-id", {"summary": "New Event"})
    assert result == {"id": "evt2"}

    # Non-retryable error
    stub_fail = MagicMock()
    stub_fail.execute.side_effect = [make_http_error(403)]
    fake_service.events.return_value.insert.return_value = stub_fail
    with pytest.raises(CalendarApiError):
        service.create_event("cal-id", {"summary": "New Event"})


@patch("src.google_calendar.build")
@patch("src.google_calendar.Credentials.from_authorized_user_info")
def test_update_event_retry_and_failure(mock_from_info, mock_build, fake_credential):
    fake_service = MagicMock()
    mock_build.return_value = fake_service
    mock_from_info.return_value = MagicMock()

    # Retry once on 500, then succeed
    http500 = make_http_error(500)
    stub_update = MagicMock()
    stub_update.execute.side_effect = [http500, {"id": "evt3"}]
    fake_service.events.return_value.update.return_value = stub_update
    service = GoogleCalendarService(fake_credential)
    result = service.update_event("cal-id", "evt-id", {"summary": "Upd"})
    assert result == {"id": "evt3"}

    # Non-retryable error
    stub_fail = MagicMock()
    stub_fail.execute.side_effect = [make_http_error(410)]
    fake_service.events.return_value.update.return_value = stub_fail
    with pytest.raises(CalendarApiError):
        service.update_event("cal-id", "evt-id", {"summary": "Upd"})


@patch("src.google_calendar.build")
@patch("src.google_calendar.Credentials.from_authorized_user_info")
def test_delete_event_retry_and_failure(mock_from_info, mock_build, fake_credential):
    fake_service = MagicMock()
    mock_build.return_value = fake_service
    mock_from_info.return_value = MagicMock()

    # Retry once on 500, then succeed
    http500 = make_http_error(500)
    stub_delete = MagicMock()
    stub_delete.execute.side_effect = [http500, {}]
    fake_service.events.return_value.delete.return_value = stub_delete
    service = GoogleCalendarService(fake_credential)
    result = service.delete_event("cal-id", "evt-id")
    assert result == {}

    # Non-retryable error
    stub_fail = MagicMock()
    stub_fail.execute.side_effect = [make_http_error(404)]
    fake_service.events.return_value.delete.return_value = stub_fail
    with pytest.raises(CalendarApiError):
        service.delete_event("cal-id", "evt-id")

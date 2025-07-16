"""
Module/Script Name: src/google_calendar.py

Description:
Unified Google Calendar API wrapper to manage calendars and event CRUD operations.

Author(s):
Skippy the Code Slayer with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
15-07-2025

Last Modified Date:
16-07-2025

Version:
v1.02

Comments:
- Added automatic token refresh and persistence
- Implemented HttpError handling with retry logic and custom CalendarApiError
- Introduced CalendarApiError for API error propagation
"""

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
import time

from src.extensions import db
from src.models.oauth import OAuthCredential


class CalendarApiError(Exception):
    """Custom exception for Google Calendar API errors."""

    pass


class GoogleCalendarService:
    def __init__(self, oauth_credential: OAuthCredential):
        self.oauth_credential = oauth_credential
        creds_dict = {
            "token": oauth_credential.access_token,
            "refresh_token": oauth_credential.refresh_token,
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": oauth_credential.google_client_id,
            "client_secret": oauth_credential.google_client_secret,
            "scopes": (
                oauth_credential.scopes.split(",")
                if oauth_credential.scopes
                else ["https://www.googleapis.com/auth/calendar"]
            ),
        }
        self.credentials = Credentials.from_authorized_user_info(creds_dict)
        self.service = build("calendar", "v3", credentials=self.credentials)

    def _ensure_valid_credentials(self):
        """Refresh credentials if expired and persist updates to the database."""
        if not self.credentials.valid or self.credentials.expired:
            try:
                self.credentials.refresh(Request())
            except Exception as e:
                raise CalendarApiError(f"Failed to refresh credentials: {e}") from e
            # Persist updated tokens and expiry to the OAuthCredential model
            self.oauth_credential.access_token = self.credentials.token
            if getattr(self.credentials, "refresh_token", None):
                self.oauth_credential.refresh_token = self.credentials.refresh_token
            self.oauth_credential.expires_at = self.credentials.expiry
            self.oauth_credential.is_valid = True
            db.session.commit()

    def list_calendars(self):
        """List calendars for the authenticated user."""
        self._ensure_valid_credentials()
        attempt = 0
        while True:
            try:
                return self.service.calendarList().list().execute().get("items", [])
            except HttpError as e:
                status = e.resp.status
                if 500 <= status < 600 and attempt < 1:
                    attempt += 1
                    time.sleep(2**attempt)
                    continue
                raise CalendarApiError(f"Error listing calendars: {e}") from e

    def list_events(self, calendar_id="primary", max_results=10):
        """List events in a calendar."""
        self._ensure_valid_credentials()
        attempt = 0
        while True:
            try:
                events_result = (
                    self.service.events()
                    .list(
                        calendarId=calendar_id,
                        maxResults=max_results,
                        singleEvents=True,
                        orderBy="startTime",
                    )
                    .execute()
                )
                return events_result.get("items", [])
            except HttpError as e:
                status = e.resp.status
                if 500 <= status < 600 and attempt < 1:
                    attempt += 1
                    time.sleep(2**attempt)
                    continue
                raise CalendarApiError(f"Error listing events: {e}") from e

    def get_event(self, calendar_id, event_id):
        """Retrieve a single event by ID."""
        self._ensure_valid_credentials()
        attempt = 0
        while True:
            try:
                return (
                    self.service.events()
                    .get(calendarId=calendar_id, eventId=event_id)
                    .execute()
                )
            except HttpError as e:
                status = e.resp.status
                if 500 <= status < 600 and attempt < 1:
                    attempt += 1
                    time.sleep(2**attempt)
                    continue
                raise CalendarApiError(f"Error getting event {event_id}: {e}") from e

    def create_event(self, calendar_id, event_body):
        """Create a new calendar event."""
        self._ensure_valid_credentials()
        attempt = 0
        while True:
            try:
                return (
                    self.service.events()
                    .insert(calendarId=calendar_id, body=event_body)
                    .execute()
                )
            except HttpError as e:
                status = e.resp.status
                if 500 <= status < 600 and attempt < 1:
                    attempt += 1
                    time.sleep(2**attempt)
                    continue
                raise CalendarApiError(f"Error creating event: {e}") from e

    def update_event(self, calendar_id, event_id, event_body):
        """Update an existing calendar event."""
        self._ensure_valid_credentials()
        attempt = 0
        while True:
            try:
                return (
                    self.service.events()
                    .update(calendarId=calendar_id, eventId=event_id, body=event_body)
                    .execute()
                )
            except HttpError as e:
                status = e.resp.status
                if 500 <= status < 600 and attempt < 1:
                    attempt += 1
                    time.sleep(2**attempt)
                    continue
                raise CalendarApiError(f"Error updating event {event_id}: {e}") from e

    def delete_event(self, calendar_id, event_id):
        """Delete a calendar event."""
        self._ensure_valid_credentials()
        attempt = 0
        while True:
            try:
                return (
                    self.service.events()
                    .delete(calendarId=calendar_id, eventId=event_id)
                    .execute()
                )
            except HttpError as e:
                status = e.resp.status
                if 500 <= status < 600 and attempt < 1:
                    attempt += 1
                    time.sleep(2**attempt)
                    continue
                raise CalendarApiError(f"Error deleting event {event_id}: {e}") from e

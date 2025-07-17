"""
Module/Script Name: src/google_calendar.py

Description:
Unified Google Calendar API wrapper to manage calendars and event CRUD operations.

Author(s):
Skippy the Code Slayer with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
15-07-2025

Last Modified Date:
17-07-2025

Version:
v1.04

Comments:
- Updated to persist token expiration to `expires_at`, matching OAuthCredential model.
- Consolidated credential refresh logic.
- Retained retry logic in CRUD methods.
"""

import time
import logging
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.extensions import db
from src.models.oauth_credential import OAuthCredential

logger = logging.getLogger(__name__)


class CalendarApiError(Exception):
    """Custom exception for Google Calendar API errors."""

    pass


class GoogleCalendarService:
    """Service class for Google Calendar API interactions"""

    TOKEN_URI = "https://oauth2.googleapis.com/token"

    def __init__(self, oauth_credential: OAuthCredential):
        """
        Initialize the service with OAuth credentials.
        Build the Google Calendar service client.
        Refresh and persist tokens as needed.
        """
        self.oauth_credential = oauth_credential
        creds_info = {
            "token": oauth_credential.access_token,
            "refresh_token": oauth_credential.refresh_token,
            "token_uri": self.TOKEN_URI,
            "client_id": oauth_credential.google_client_id,
            "client_secret": oauth_credential.google_client_secret,
            "scopes": (
                oauth_credential.scopes.split(",")
                if oauth_credential.scopes
                else ["https://www.googleapis.com/auth/calendar"]
            ),
        }
        self.credentials = Credentials.from_authorized_user_info(creds_info)
        try:
            self.service = build("calendar", "v3", credentials=self.credentials)
        except Exception as e:
            logger.error(f"Failed to build Google Calendar service: {e}")
            raise CalendarApiError(f"Service build failed: {e}") from e

    def _ensure_valid_credentials(self):
        """Refresh credentials if expired and persist updates to DB."""
        if not self.credentials.valid or self.credentials.expired:
            try:
                self.credentials.refresh(Request())
                # Persist refreshed tokens
                self.oauth_credential.access_token = self.credentials.token
                if getattr(self.credentials, "refresh_token", None):
                    self.oauth_credential.refresh_token = self.credentials.refresh_token
                # Persist expiry to model's expires_at
                self.oauth_credential.expires_at = self.credentials.expiry
                self.oauth_credential.is_valid = True
                db.session.commit()
                logger.info("Refreshed OAuth access token and updated database")
            except Exception as e:
                logger.error(f"Failed to refresh token: {e}")
                raise CalendarApiError(f"Token refresh failed: {e}") from e

    def list_calendars(self):
        """List all calendars for the authenticated user."""
        self._ensure_valid_credentials()
        attempt = 0
        while True:
            try:
                resp = self.service.calendarList().list().execute()
                items = resp.get("items", [])
                return [{"id": c["id"], "summary": c.get("summary", "")} for c in items]
            except HttpError as e:
                status = e.resp.status
                if 500 <= status < 600 and attempt < 1:
                    attempt += 1
                    time.sleep(2**attempt)
                    continue
                logger.error(f"HTTP error listing calendars: {e}")
                raise CalendarApiError(f"Error listing calendars: {e}") from e

    def list_events(self, calendar_id, time_min=None, time_max=None):
        """List events on a calendar, optionally within a time window."""
        self._ensure_valid_credentials()
        attempt = 0
        while True:
            try:
                req = self.service.events().list(calendarId=calendar_id)
                if time_min:
                    req = req.list(calendarId=calendar_id, timeMin=time_min)
                if time_max:
                    req = req.list(calendarId=calendar_id, timeMax=time_max)
                resp = req.execute()
                return resp.get("items", [])
            except HttpError as e:
                status = e.resp.status
                if 500 <= status < 600 and attempt < 1:
                    attempt += 1
                    time.sleep(2**attempt)
                    continue
                logger.error(f"HTTP error listing events: {e}")
                raise CalendarApiError(
                    f"Error listing events for calendar {calendar_id}: {e}"
                ) from e

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
                logger.error(f"HTTP error getting event: {e}")
                raise CalendarApiError(f"Error retrieving event {event_id}: {e}") from e

    def create_event(self, calendar_id, event_body):
        """Create a new event on a calendar."""
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
                logger.error(f"HTTP error creating event: {e}")
                raise CalendarApiError(f"Error creating event: {e}") from e

    def update_event(self, calendar_id, event_id, event_body):
        """Update an existing event."""
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
                logger.error(f"HTTP error updating event: {e}")
                raise CalendarApiError(f"Error updating event {event_id}: {e}") from e

    def delete_event(self, calendar_id, event_id):
        """Delete an event from a calendar."""
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
                logger.error(f"HTTP error deleting event: {e}")
                raise CalendarApiError(f"Error deleting event {event_id}: {e}") from e

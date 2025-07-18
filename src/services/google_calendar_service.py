"""
Module/Script Name: src/services/google_calendar_service.py

Description:
Service class for interacting with the Google Calendar API, handling OAuth credentials, token refresh, and CRUD operations on calendars and events.

Author(s):
Skippy the Code Slayer with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
22-07-2025

Last Modified Date:
23-07-2025

Version:
v1.01

Comments:
- Implemented CRUD methods for calendars and events to allow UI verification
- Methods return a consistent {'success': bool, 'data': ..., 'error': ...} structure
"""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging

logger = logging.getLogger(__name__)


class GoogleCalendarService:
    """Service class for Google Calendar API interactions"""

    service: Any  # type: googleapiclient.discovery.Resource

    def __init__(self, oauth_credentials):
        """
        Initialize the service with OAuth credentials

        Args:
            oauth_credentials: OAuthCredential model instance
        """
        self.oauth_credentials = oauth_credentials
        self.service: Any = None
        self._build_service()

    def _build_service(self) -> None:
        """Build the Google Calendar service with OAuth credentials"""
        try:
            creds = Credentials(
                token=self.oauth_credentials.access_token,
                refresh_token=self.oauth_credentials.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.oauth_credentials.google_client_id,
                client_secret=self.oauth_credentials.google_client_secret,
                scopes=(
                    json.loads(self.oauth_credentials.scopes)
                    if self.oauth_credentials.scopes
                    else []
                ),
            )

            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                self._update_stored_credentials(creds)

            self.service = build("calendar", "v3", credentials=creds)

        except Exception as e:
            logger.error(f"Failed to build Google Calendar service: {e}")
            raise

    def list_calendars(self) -> Dict[str, Any]:
        """List all calendars for the authenticated user"""
        try:
            response = self.service.calendarList().list().execute()
            items = response.get("items", [])
            return {"success": True, "data": items}
        except Exception as e:
            logger.error(f"Error in list_calendars: {e}")
            return {"success": False, "error": str(e)}

    def list_events(
        self,
        calendar_id: str,
        time_min: Optional[datetime] = None,
        time_max: Optional[datetime] = None,
        max_results: int = 250,
    ) -> Dict[str, Any]:
        """List events from a specific calendar"""
        try:
            params: Dict[str, Any] = {
                "calendarId": calendar_id,
                "maxResults": max_results,
            }
            if time_min:
                params["timeMin"] = time_min.isoformat() + "Z"
            if time_max:
                params["timeMax"] = time_max.isoformat() + "Z"

            response = self.service.events().list(**params).execute()
            items = response.get("items", [])
            return {"success": True, "data": items}
        except Exception as e:
            logger.error(f"Error in list_events: {e}")
            return {"success": False, "error": str(e)}

    def create_event(
        self, calendar_id: str, event_body: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new event in a calendar"""
        try:
            created = (
                self.service.events()
                .insert(calendarId=calendar_id, body=event_body)
                .execute()
            )
            return {"success": True, "data": created}
        except Exception as e:
            logger.error(f"Error in create_event: {e}")
            return {"success": False, "error": str(e)}

    def get_event(self, calendar_id: str, event_id: str) -> Dict[str, Any]:
        """Retrieve a specific event by ID"""
        try:
            event = (
                self.service.events()
                .get(calendarId=calendar_id, eventId=event_id)
                .execute()
            )
            return {"success": True, "data": event}
        except Exception as e:
            logger.error(f"Error in get_event: {e}")
            return {"success": False, "error": str(e)}

    def update_event(
        self, calendar_id: str, event_id: str, event_body: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing event"""
        try:
            updated = (
                self.service.events()
                .update(calendarId=calendar_id, eventId=event_id, body=event_body)
                .execute()
            )
            return {"success": True, "data": updated}
        except Exception as e:
            logger.error(f"Error in update_event: {e}")
            return {"success": False, "error": str(e)}

    def delete_event(self, calendar_id: str, event_id: str) -> Dict[str, Any]:
        """Delete an event by ID"""
        try:
            self.service.events().delete(
                calendarId=calendar_id, eventId=event_id
            ).execute()
            return {"success": True, "data": None}
        except Exception as e:
            logger.error(f"Error in delete_event: {e}")
            return {"success": False, "error": str(e)}

    def _update_stored_credentials(self, creds: Credentials) -> None:
        """Persist refreshed credentials back to the database"""
        self.oauth_credentials.access_token = creds.token
        self.oauth_credentials.refresh_token = creds.refresh_token
        self.oauth_credentials.scopes = json.dumps(creds.scopes)
        # Commit should be handled by caller

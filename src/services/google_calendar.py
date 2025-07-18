import json
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging
from typing import Any

logger = logging.getLogger(__name__)


class GoogleCalendarService:
    """Service class for Google Calendar API interactions"""

    service: Any  # type: googleapiclient.discovery.Resource
    """Service class for Google Calendar API interactions"""

    def __init__(self, oauth_credentials):
        """
        Initialize the service with OAuth credentials

        Args:
            oauth_credentials: OAuthCredential model instance
        """
        self.oauth_credentials = oauth_credentials
        self.service: Any = None
        self._build_service()

    def _build_service(self):
        """Build the Google Calendar service with OAuth credentials"""
        try:
            # Create credentials object
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

            # Check if token needs refresh
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                # Update the stored credentials
                self._update_stored_credentials(creds)

            # Build the service
            self.service = build("calendar", "v3", credentials=creds)

        except Exception as e:
            logger.error(f"Failed to build Google Calendar service: {str(e)}")
            raise Exception(f"Failed to initialize Google Calendar service: {str(e)}")

    # ... rest of methods

    def list_calendars(self):
        try:
            calendars_result = self.service.calendarList().list().execute()
            calendars = calendars_result.get("items", [])

            return {"success": True, "data": calendars}

        except HttpError as e:
            logger.error(f"HTTP error in list_calendars: {str(e)}")
            return {"success": False, "error": f"Google Calendar API error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error in list_calendars: {str(e)}")
            return {"success": False, "error": f"Failed to list calendars: {str(e)}"}

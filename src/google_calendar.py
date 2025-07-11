# src/google_calendar.py

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


class GoogleCalendarService:
    def __init__(self, oauth_credentials):
        """
        oauth_credentials: an instance of your OAuthCredential model
        with .access_token, .refresh_token, .google_client_id,
        .google_client_secret, and optionally .scopes (comma-separated).
        """
        # Build a Credentials object for google-api-client
        self.creds = Credentials(
            token=oauth_credentials.access_token,
            refresh_token=oauth_credentials.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=oauth_credentials.google_client_id,
            client_secret=oauth_credentials.google_client_secret,
            scopes=(
                oauth_credentials.scopes.split(",")
                if oauth_credentials.scopes
                else ["https://www.googleapis.com/auth/calendar"]
            ),
        )
        # Instantiate the Calendar v3 API
        self.service = build("calendar", "v3", credentials=self.creds)

    def list_calendars(self):
        """
        Returns a list of dicts with keys 'id' and 'summary' for each calendar.
        """
        calendars = []
        page_token = None
        while True:
            resp = self.service.calendarList().list(pageToken=page_token).execute()
            for cal in resp.get("items", []):
                calendars.append({"id": cal["id"], "summary": cal.get("summary")})
            page_token = resp.get("nextPageToken")
            if not page_token:
                break
        return calendars

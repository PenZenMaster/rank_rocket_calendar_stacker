"""
Module/Script Name: src/google_calendar_service.py

Description:
Google Calendar API wrapper to manage event CRUD operations.

Author(s):
Skippy the Code Slayer with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
15-07-2025

Last Modified Date:
15-07-2025

Version:
v1.00

Comments:
- Initial implementation of GoogleCalendarService with event CRUD methods
"""

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials


class GoogleCalendarService:
    def __init__(self, credentials_dict):
        self.credentials = Credentials.from_authorized_user_info(credentials_dict)
        self.service = build("calendar", "v3", credentials=self.credentials)

    def list_events(self, calendar_id="primary", max_results=10):
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

    def get_event(self, calendar_id, event_id):
        return (
            self.service.events()
            .get(calendarId=calendar_id, eventId=event_id)
            .execute()
        )

    def create_event(self, calendar_id, event_body):
        return (
            self.service.events()
            .insert(calendarId=calendar_id, body=event_body)
            .execute()
        )

    def update_event(self, calendar_id, event_id, event_body):
        return (
            self.service.events()
            .update(calendarId=calendar_id, eventId=event_id, body=event_body)
            .execute()
        )

    def delete_event(self, calendar_id, event_id):
        return (
            self.service.events()
            .delete(calendarId=calendar_id, eventId=event_id)
            .execute()
        )

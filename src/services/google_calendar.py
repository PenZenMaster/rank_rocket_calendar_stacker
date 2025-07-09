import json
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging

logger = logging.getLogger(__name__)

class GoogleCalendarService:
    """Service class for Google Calendar API interactions"""
    
    def __init__(self, oauth_credentials):
        """
        Initialize the service with OAuth credentials
        
        Args:
            oauth_credentials: OAuthCredential model instance
        """
        self.oauth_credentials = oauth_credentials
        self.service = None
        self._build_service()
    
    def _build_service(self):
        """Build the Google Calendar service with OAuth credentials"""
        try:
            # Create credentials object
            creds = Credentials(
                token=self.oauth_credentials.access_token,
                refresh_token=self.oauth_credentials.refresh_token,
                token_uri='https://oauth2.googleapis.com/token',
                client_id=self.oauth_credentials.google_client_id,
                client_secret=self.oauth_credentials.google_client_secret,
                scopes=json.loads(self.oauth_credentials.scopes) if self.oauth_credentials.scopes else []
            )
            
            # Check if token needs refresh
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                # Update the stored credentials
                self._update_stored_credentials(creds)
            
            # Build the service
            self.service = build('calendar', 'v3', credentials=creds)
            
        except Exception as e:
            logger.error(f"Failed to build Google Calendar service: {str(e)}")
            raise Exception(f"Failed to initialize Google Calendar service: {str(e)}")
    
    def _update_stored_credentials(self, creds):
        """Update stored OAuth credentials with refreshed tokens"""
        try:
            from src.models.client import db
            
            self.oauth_credentials.access_token = creds.token
            if creds.refresh_token:
                self.oauth_credentials.refresh_token = creds.refresh_token
            if creds.expiry:
                self.oauth_credentials.token_expires_at = creds.expiry
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Failed to update stored credentials: {str(e)}")
    
    def list_calendars(self):
        """
        List all calendars for the authenticated user
        
        Returns:
            dict: Response containing calendar list or error
        """
        try:
            calendars_result = self.service.calendarList().list().execute()
            calendars = calendars_result.get('items', [])
            
            return {
                'success': True,
                'data': calendars
            }
            
        except HttpError as e:
            logger.error(f"HTTP error in list_calendars: {str(e)}")
            return {
                'success': False,
                'error': f"Google Calendar API error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error in list_calendars: {str(e)}")
            return {
                'success': False,
                'error': f"Failed to list calendars: {str(e)}"
            }
    
    def create_event(self, calendar_id, event_data):
        """
        Create a new event in the specified calendar
        
        Args:
            calendar_id (str): ID of the calendar
            event_data (dict): Event details
            
        Returns:
            dict: Response containing created event or error
        """
        try:
            # Validate required fields
            required_fields = ['summary', 'start', 'end']
            for field in required_fields:
                if field not in event_data:
                    return {
                        'success': False,
                        'error': f"Missing required field: {field}"
                    }
            
            # Create the event
            event = self.service.events().insert(
                calendarId=calendar_id,
                body=event_data
            ).execute()
            
            return {
                'success': True,
                'data': event
            }
            
        except HttpError as e:
            logger.error(f"HTTP error in create_event: {str(e)}")
            return {
                'success': False,
                'error': f"Google Calendar API error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error in create_event: {str(e)}")
            return {
                'success': False,
                'error': f"Failed to create event: {str(e)}"
            }
    
    def get_event(self, calendar_id, event_id):
        """
        Get a specific event by ID
        
        Args:
            calendar_id (str): ID of the calendar
            event_id (str): ID of the event
            
        Returns:
            dict: Response containing event details or error
        """
        try:
            event = self.service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            return {
                'success': True,
                'data': event
            }
            
        except HttpError as e:
            logger.error(f"HTTP error in get_event: {str(e)}")
            return {
                'success': False,
                'error': f"Google Calendar API error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error in get_event: {str(e)}")
            return {
                'success': False,
                'error': f"Failed to get event: {str(e)}"
            }
    
    def update_event(self, calendar_id, event_id, event_data):
        """
        Update an existing event
        
        Args:
            calendar_id (str): ID of the calendar
            event_id (str): ID of the event
            event_data (dict): Updated event details
            
        Returns:
            dict: Response containing updated event or error
        """
        try:
            event = self.service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event_data
            ).execute()
            
            return {
                'success': True,
                'data': event
            }
            
        except HttpError as e:
            logger.error(f"HTTP error in update_event: {str(e)}")
            return {
                'success': False,
                'error': f"Google Calendar API error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error in update_event: {str(e)}")
            return {
                'success': False,
                'error': f"Failed to update event: {str(e)}"
            }
    
    def delete_event(self, calendar_id, event_id):
        """
        Delete an event
        
        Args:
            calendar_id (str): ID of the calendar
            event_id (str): ID of the event
            
        Returns:
            dict: Response indicating success or error
        """
        try:
            self.service.events().delete(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            return {
                'success': True,
                'message': 'Event deleted successfully'
            }
            
        except HttpError as e:
            logger.error(f"HTTP error in delete_event: {str(e)}")
            return {
                'success': False,
                'error': f"Google Calendar API error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error in delete_event: {str(e)}")
            return {
                'success': False,
                'error': f"Failed to delete event: {str(e)}"
            }
    
    def list_events(self, calendar_id, time_min=None, time_max=None, max_results=250):
        """
        List events from a calendar
        
        Args:
            calendar_id (str): ID of the calendar
            time_min (str): Lower bound for event start time (RFC3339 timestamp)
            time_max (str): Upper bound for event start time (RFC3339 timestamp)
            max_results (int): Maximum number of events to return
            
        Returns:
            dict: Response containing events list or error
        """
        try:
            # Set default time range if not provided
            if not time_min:
                time_min = datetime.utcnow().isoformat() + 'Z'
            if not time_max:
                # Default to 1 year from now
                time_max = (datetime.utcnow() + timedelta(days=365)).isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            return {
                'success': True,
                'data': events,
                'next_page_token': events_result.get('nextPageToken')
            }
            
        except HttpError as e:
            logger.error(f"HTTP error in list_events: {str(e)}")
            return {
                'success': False,
                'error': f"Google Calendar API error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error in list_events: {str(e)}")
            return {
                'success': False,
                'error': f"Failed to list events: {str(e)}"
            }
    
    def validate_credentials(self):
        """
        Validate the current OAuth credentials
        
        Returns:
            dict: Response indicating credential validity
        """
        try:
            # Try to make a simple API call to validate credentials
            result = self.service.calendarList().list(maxResults=1).execute()
            
            return {
                'success': True,
                'valid': True,
                'message': 'Credentials are valid'
            }
            
        except HttpError as e:
            logger.error(f"HTTP error in validate_credentials: {str(e)}")
            return {
                'success': True,
                'valid': False,
                'error': f"Invalid credentials: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error in validate_credentials: {str(e)}")
            return {
                'success': False,
                'error': f"Failed to validate credentials: {str(e)}"
            }


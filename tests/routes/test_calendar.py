"""
Module/Script Name: tests/routes/test_calendar.py

Description:
Unit tests for calendar routes, covering list, event CRUD flows and error handling.

Author(s):
Skippy the Code Slayer with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
17-07-2025

Last Modified Date:
17-07-2025

Version:
v1.00

Comments:
- Tests mock OAuthCredential and GoogleCalendarService
- Covers GET and POST flows for list, create, edit, delete routes
"""

import pytest
from unittest.mock import patch, MagicMock
from flask import url_for
from src.main import create_app  # assumption: factory returns Flask app

@pytest.fixture
def app():
    app = create_app({'TESTING': True})
    with app.app_context():
        yield app

@pytest.fixture
def client(app):
    with app.test_client() as client:
        with app.app_context():
            yield client

@patch('src.routes.calendar.OAuthCredential')
@patch('src.routes.calendar.GoogleCalendarService')
def test_list_calendars_success(mock_service_cls, mock_cred_cls, client):
    # Setup mock credential lookup
    mock_cred = MagicMock(is_valid=True)
    mock_cred_cls.query.filter_by.return_value.first.return_value = mock_cred
    # Setup service.list_calendars
    service = mock_service_cls.return_value
    service.list_calendars.return_value = [{'id':'cal1','summary':'Cal 1'}]

    resp = client.get(url_for('calendar.list_calendars', client_id=1))
    assert resp.status_code == 200
    assert b'Cal 1' in resp.data

@patch('src.routes.calendar.OAuthCredential')
@patch('src.routes.calendar.GoogleCalendarService')
def test_list_calendars_no_cred(mock_service_cls, mock_cred_cls, client):
    # No credentials found → redirect
    mock_cred_cls.query.filter_by.return_value.first.return_value = None
    resp = client.get(url_for('calendar.list_calendars', client_id=1), follow_redirects=False)
    assert resp.status_code == 302
    assert '/clients' in resp.headers['Location']

@patch('src.routes.calendar.OAuthCredential')
@patch('src.routes.calendar.GoogleCalendarService')
def test_create_event_post(mock_service_cls, mock_cred_cls, client):
    # Setup valid cred and service
    mock_cred = MagicMock(is_valid=True)
    mock_cred_cls.query.filter_by.return_value.first.return_value = mock_cred
    service = mock_service_cls.return_value
    service.create_event.return_value = {'id':'evt1'}

    data = {'summary':'Test','start':'2025-07-17T10:00','end':'2025-07-17T11:00'}
    resp = client.post(url_for('calendar.create_event', client_id=1), data=data, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Event created successfully' in resp.data

@patch('src.routes.calendar.OAuthCredential')
@patch('src.routes.calendar.GoogleCalendarService')
def test_edit_event_get_and_post(mock_service_cls, mock_cred_cls, client):
    mock_cred = MagicMock(is_valid=True)
    mock_cred_cls.query.filter_by.return_value.first.return_value = mock_cred
    service = mock_service_cls.return_value
    # GET returns existing event
    service.get_event.return_value = {
        'id':'evt1',
        'summary':'Existing',
        'start': {'dateTime': '2025-07-17T10:00:00Z'},
        'end': {'dateTime': '2025-07-17T11:00:00Z'}
    }
    resp_get = client.get(url_for('calendar.edit_event', client_id=1, event_id='evt1'))
    assert resp_get.status_code == 200
    assert b'Existing' in resp_get.data
    # POST updates
    data = {'summary':'Updated','start':'2025-07-17T12:00','end':'2025-07-17T13:00'}
    resp_post = client.post(url_for('calendar.edit_event', client_id=1, event_id='evt1'), data=data, follow_redirects=True)
    assert resp_post.status_code == 200
    assert b'Event updated successfully' in resp_post.data

@patch('src.routes.calendar.OAuthCredential')
@patch('src.routes.calendar.GoogleCalendarService')
def test_delete_event(mock_service_cls, mock_cred_cls, client):
    mock_cred = MagicMock(is_valid=True)
    mock_cred_cls.query.filter_by.return_value.first.return_value = mock_cred
    service = mock_service_cls.return_value
    resp = client.post(url_for('calendar.delete_event', client_id=1, event_id='evt1'), follow_redirects=True)
    assert resp.status_code == 200
    assert b'Event deleted successfully' in resp.data

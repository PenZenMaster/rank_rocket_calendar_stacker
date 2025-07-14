"""
Module/Script Name: test_oauth_flow.py

Description:
Unit tests for Google OAuth2 authorization and callback routes.

Author(s):
Skippy the Code Slayer with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
13-07-2025

Last Modified Date:
13-07-2025

Version:
v1.00

Comments:
- Mocks Google Flow, session, and token exchange behavior
"""

import pytest
from unittest.mock import patch, MagicMock
from flask import session
from src.models.oauth import OAuthCredential
from src.extensions import db


def test_authorize_redirect(client, setup_db):
    # Setup test credential
    oauth = OAuthCredential(
        client_id=1,
        google_client_id="test-google-client",
        google_client_secret="test-secret",
        scopes='["scope1", "scope2"]',
        is_valid=False,
    )
    db.session.add(oauth)
    db.session.commit()

    with patch("src.routes.oauth_flow.Flow.from_client_config") as mock_flow:
        mock_instance = MagicMock()
        mock_instance.authorization_url.return_value = (
            "http://mock.google.auth",
            "state-token",
        )
        mock_flow.return_value = mock_instance

        response = client.get(f"/authorize/{oauth.id}", follow_redirects=False)

        assert response.status_code == 302
        assert response.location.startswith("http://mock.google.auth")


def test_callback_exchanges_token(client, setup_db):
    oauth = OAuthCredential(
        client_id=1,
        google_client_id="test-google-client",
        google_client_secret="test-secret",
        scopes='["scope1", "scope2"]',
        is_valid=False,
    )
    db.session.add(oauth)
    db.session.commit()

    with client.session_transaction() as sess:
        sess["oauth_state"] = "valid-state"
        sess["oauth_id"] = oauth.id

    with patch("src.routes.oauth_flow.Flow.from_client_config") as mock_flow:
        mock_instance = MagicMock()
        mock_instance.fetch_token.return_value = None
        mock_instance.credentials.token = "access-token"
        mock_instance.credentials.refresh_token = "refresh-token"
        mock_instance.credentials.expiry = "2025-12-31T23:59:59"
        mock_flow.return_value = mock_instance

        response = client.get("/callback?state=valid-state&code=fake-code")
        assert response.status_code == 302  # redirect to home

        updated = OAuthCredential.query.get(oauth.id)
        assert updated.access_token == "access-token"
        assert updated.refresh_token == "refresh-token"
        assert updated.is_valid is True

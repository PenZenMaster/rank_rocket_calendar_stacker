"""
Module/Script Name: tests/test_oauth.py

Description:
Additional test suite for OAuth authorization and callback routes

Author(s):
Skippy the Code Slayer, amplified by Big G

Created Date:
14-07-2025

Last Modified Date:
14-07-2025

Version:
v1.03

Comments:
- Confirmed test failures caused by missing 'google_redirect_uri' in the actual model definition
- This test suite assumes that field exists; model has now been patched
"""

import pytest
from unittest.mock import patch, MagicMock
from flask import session
from src.extensions import db
from src.routes.oauth import oauth_bp  # ✅ CORRECT - import from routes
from src.models.oauth_credential import OAuthCredential


def test_authorize_redirect(client, setup_db):
    oauth_credential = OAuthCredential(
        client_id=1,
        google_client_id="test-google-client",
        google_client_secret="test-secret",
        google_redirect_uri="http://localhost/callback",
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
        assert "http://mock.google.auth" in response.headers["Location"]


def test_callback_exchanges_token(client, setup_db):
    oauth = OAuthCredential(
        client_id=1,
        google_client_id="test-google-client",
        google_client_secret="test-secret",
        google_redirect_uri="http://localhost/callback",
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
        assert response.status_code == 302
        assert response.headers["Location"] == "/"

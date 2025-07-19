"""
Module/Script Name: src/models/oauth_credential.py

Description:
Unified SQLAlchemy model for Google OAuth credentials linked to a client, consolidating fields and behavior from `oauth.py` and `oauth_credential.py`.

Author(s):
Skippy the Magnificent with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
12-07-2025

Last Modified Date:
18-07-2025

Version:
v1.07

Comments:
- Changed `scopes` column from Text to JSON to support list of scopes
- Added `google_redirect_uri` field to support redirect URIs
- Normalized column types and lengths (`String(256)` for client ID/secret, `Text` for tokens)
- Introduced `__table_args__ = {"extend_existing": True}` to prevent duplicate table errors during tests
- Implemented dynamic `__init__` for dict-style construction and `to_dict` for JSON serialization
- Subclasses Flask-SQLAlchemy `db.Model` for shared metadata
- Uses string-based relationship for deferred resolution: `relationship("Client")`
"""

from datetime import datetime
from src.extensions import db


class OAuthCredential(db.Model):
    __tablename__ = "oauth_credentials"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)

    google_client_id = db.Column(db.String(256), nullable=False)
    google_client_secret = db.Column(db.String(256), nullable=False)
    google_redirect_uri = db.Column(db.String(512), nullable=False)
    scopes = db.Column(db.JSON, nullable=False)  # changed to JSON type

    access_token = db.Column(db.Text, nullable=True)
    refresh_token = db.Column(db.Text, nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)

    is_valid = db.Column(db.Boolean, default=False)

    # Deferred relationship lookup to avoid circular imports
    client = db.relationship(
        "Client",
        back_populates="oauth_credentials",
        lazy=True,
    )

    def __init__(self, **kwargs):
        """Dynamic constructor supporting dict-style input."""
        for field in (
            "client_id",
            "google_client_id",
            "google_client_secret",
            "google_redirect_uri",
            "scopes",
            "access_token",
            "refresh_token",
            "expires_at",
            "is_valid",
        ):
            if field in kwargs:
                setattr(self, field, kwargs[field])

    def to_dict(self):
        """Return a JSON-serializable dictionary of the model."""
        return {
            "id": self.id,
            "client_id": self.client_id,
            "google_client_id": self.google_client_id,
            "google_client_secret": self.google_client_secret,
            "google_redirect_uri": self.google_redirect_uri,
            "scopes": self.scopes,
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_valid": self.is_valid,
        }

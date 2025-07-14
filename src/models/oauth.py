"""
Module/Script Name: oauth.py

Description:
OAuthCredential SQLAlchemy model with JSON serialization support.

Author(s):
Skippy the Code Slayer with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
13-07-2025

Last Modified Date:
13-07-2025

Version:
v1.02

Comments:
- Added extend_existing=True to avoid duplicate table definition error
"""

from datetime import datetime
from src.extensions import db


class OAuthCredential(db.Model):
    __tablename__ = "oauth_credentials"
    __table_args__ = {"extend_existing": True}  # Prevent duplicate table error in tests

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
    google_client_id = db.Column(db.String(256), nullable=False)
    google_client_secret = db.Column(db.String(256), nullable=False)
    scopes = db.Column(db.Text, nullable=False)
    access_token = db.Column(db.Text)
    refresh_token = db.Column(db.Text)
    expires_at = db.Column(db.DateTime)
    is_valid = db.Column(db.Boolean, default=False)

    def __init__(self, **kwargs):
        """Dynamic constructor supporting dict-style input."""
        for field in (
            "client_id",
            "google_client_id",
            "google_client_secret",
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
            "scopes": self.scopes,
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_valid": self.is_valid,
        }

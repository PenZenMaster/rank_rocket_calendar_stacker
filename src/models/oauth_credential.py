"""
Module/Script Name: src/models/oauth_credential.py
Path: E:/projects/rank_rocket_calendar_stacker/src/models/oauth_credential.py

Description:
SQLAlchemy model for storing Google OAuth credentials linked to a client.

Author(s):
Skippy the Magnificent with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
12-07-2025

Last Modified Date:
17-07-2025

Version:
v1.05

Comments:
- Removed cascade delete-orphan from OAuthCredential.client relationship to avoid InvalidRequestError
- Retained string-based relationship for deferred resolution
- Continues to share metadata with Client via Flask-SQLAlchemy db.Model
"""

from datetime import datetime
from src.extensions import db


class OAuthCredential(db.Model):
    __tablename__ = "oauth_credentials"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)

    google_client_id = db.Column(db.String(255), nullable=False)
    google_client_secret = db.Column(db.String(255), nullable=False)
    scopes = db.Column(db.String(1000), nullable=True)

    access_token = db.Column(db.String(500), nullable=True)
    refresh_token = db.Column(db.String(500), nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)

    is_valid = db.Column(db.Boolean, default=False)

    # String-based relationship to Client; delete-orphan cascade on parent side only
    client = db.relationship("Client", back_populates="oauth_credentials", lazy=True)

    def __repr__(self):
        return f"<OAuthCredential client_id={self.client_id} valid={self.is_valid}>"

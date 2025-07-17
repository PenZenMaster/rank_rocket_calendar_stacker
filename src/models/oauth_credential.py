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
v1.04

Comments:
- Switched to use Flask-SQLAlchemy `db.Model` to share metadata with `Client` and avoid missing table issues
- Removed separate declarative Base import
- Retained string-based relationship for deferred resolution
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

    # String-based relationship to Client; resolved after both classes are defined
    client = db.relationship(
        "Client",
        back_populates="oauth_credentials",
        cascade="all, delete-orphan",
        lazy=True,
    )

    def __repr__(self):
        return f"<OAuthCredential client_id={self.client_id} valid={self.is_valid}>"

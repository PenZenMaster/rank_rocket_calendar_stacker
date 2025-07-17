"""
Module/Script Name: src/models/client.py
Path: E:/projects/rank_rocket_calendar_stacker/src/models/client.py

Description:
SQLAlchemy model for Client entities, including name, email, google_email, and OAuth credential relationship.

Author(s):
Skippy the Code Slayer with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
14-07-2025

Last Modified Date:
17-07-2025

Version:
v1.10

Comments:
- Directly import OAuthCredential class for relationship to avoid mapping resolution issues
- Removed incorrect string path and replaced with class reference in `oauth_credentials` relationship
"""

from src.extensions import db
from src.models.oauth_credential import OAuthCredential


class Client(db.Model):
    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    google_email = db.Column(db.String(120), unique=True, nullable=False)
    oauth_credentials = db.relationship(
        OAuthCredential,
        back_populates="client",
        cascade="all, delete-orphan",
        lazy=True,
    )

    def __init__(self, name, email, google_email):
        """Initialize a new Client."""
        self.name = name
        self.email = email
        self.google_email = google_email

    def __repr__(self):
        return f"<Client {self.name}>"

    def to_dict(self):
        """Return a JSON-serializable dictionary of the Client model."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "google_email": self.google_email,
        }

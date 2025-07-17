"""
Module/Script Name: src/models/client.py

Description:
SQLAlchemy model for Client entities, including name, email, google_email, and OAuth credential relationship.

Author(s):
Skippy the Code Slayer with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
14-07-2025

Last Modified Date:
17-07-2025

Version:
v1.09

Comments:
- Added google_email column to persist client's Gmail address
"""

from src.extensions import db


class Client(db.Model):
    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    google_email = db.Column(db.String(120), unique=True, nullable=False)
    oauth_credentials = db.relationship(
        "src.models.oauth.OAuthCredential",  # Fully-qualified path to avoid ambiguity
        back_populates="client",
        cascade="all, delete-orphan",
        lazy=True,
    )

    def __init__(self, name, email, google_email):
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

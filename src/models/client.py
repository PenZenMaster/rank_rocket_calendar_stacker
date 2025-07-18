"""
Module/Script Name: src/models/client.py

Description:
SQLAlchemy model for Client entities, including name, email, google_email (aliased as google_account_email for API consistency), and OAuth credential relationship.

Author(s):
Skippy the Code Slayer with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
14-07-2025

Last Modified Date:
18-07-2025

Version:
v1.11

Comments:
- Added support for `google_account_email` keyword in `__init__` to match frontend API payload.
- Updated `to_dict` to return `google_account_email` key for consistency with client-side code.
"""

from src.extensions import db
from src.models.oauth_credential import OAuthCredential


class Client(db.Model):
    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # Underlying column remains google_email, but aliased for API consistency
    google_email = db.Column(db.String(120), unique=True, nullable=False)
    oauth_credentials = db.relationship(
        "OAuthCredential",
        back_populates="client",
        cascade="all, delete-orphan",
        lazy=True,
    )

    def __init__(self, name, email, google_email=None, google_account_email=None):
        """
        Initialize a new Client.

        Accepts either `google_email` or `google_account_email` from API payload.
        """
        self.name = name
        self.email = email
        # Prefer google_account_email if provided by API, else use google_email
        self.google_email = (
            google_account_email if google_account_email is not None else google_email
        )  # noqa: E501

    def __repr__(self):
        return f"<Client {self.name}>"

    def to_dict(self):
        """Return a JSON-serializable dictionary of the Client model."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            # Return key matching frontend expectation
            "google_account_email": self.google_email,
        }

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
v1.03

Comments:
- Removed direct import of Client to eliminate circular import
- Switched relationship to string-based reference for deferred resolution
- Ensured relationship resolution via configure_mappers in app setup or conftest
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from src.models.base import Base


class OAuthCredential(Base):
    __tablename__ = "oauth_credentials"

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)

    google_client_id = Column(String(255), nullable=False)
    google_client_secret = Column(String(255), nullable=False)
    scopes = Column(String(1000), nullable=True)

    access_token = Column(String(500), nullable=True)
    refresh_token = Column(String(500), nullable=True)
    expires_at = Column(DateTime, nullable=True)

    is_valid = Column(Boolean, default=False)

    # String-based relationship to avoid circular import; resolved via configure_mappers()
    client = relationship("Client", back_populates="oauth_credentials")

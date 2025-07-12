"""
Module/Script Name: oauth_credential.py

Description:
SQLAlchemy model for storing Google OAuth credentials linked to a client.

Author(s):
Skippy the Magnificent with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
2025-07-12

Last Modified Date:
2025-07-12

Comments:
- v1.00: Initial model scaffold for OAuthCredential
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from src.models.base import Base  # Assumes you have a common declarative base


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

    client = relationship("Client", back_populates="oauth_credentials")

"""
Module/Script Name: src/models/__init__.py
Path: E:/projects/rank_rocket_calendar_stacker/src/models/__init__.py

Description:
Model package initializer. Exposes the canonical SQLAlchemy models for the application.

Author(s):
Skippy the Code Slayer with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
17-07-2025

Last Modified Date:
17-07-2025

Version:
v1.00

Comments:
- Imports only the definitive model definitions to avoid stale or redundant references
- Removed legacy `oauth.py` import to prevent ModuleNotFoundError
"""

from .client import Client
from .oauth_credential import OAuthCredential

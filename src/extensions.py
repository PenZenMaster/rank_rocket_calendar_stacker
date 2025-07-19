"""
Module/Script Name: src/extensions.py

Description:
Flask extensions initialization: custom SQLAlchemy to suppress deprecation and legacy-API warnings, CORS, and database migrations.

Author(s):
George Penzenik - Rank Rocket Co

Created Date:
13-07-2025

Last Modified Date:
19-07-2025

Version:
v1.04

Comments:
- Overridden get_engine to return .engine directly and avoid DeprecationWarning
- Switch to CustomSQLAlchemy for `db` instance
"""

from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate


class CustomSQLAlchemy(SQLAlchemy):
    def get_engine(self, app=None):
        """
        Return the underlying SQLAlchemy engine directly to avoid deprecated API usage.
        """
        return self.engine


# Initialize Flask extensions
# Use CustomSQLAlchemy to suppress deprecation and legacy-API warnings
db = CustomSQLAlchemy()
cors = CORS()
migrate = Migrate()

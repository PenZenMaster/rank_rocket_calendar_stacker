"""
Module/Script Name: base.py

Description:
Defines declarative base for SQLAlchemy models.

Author(s):
Skippy the Magnificent with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
2025-07-12

Last Modified Date:
2025-07-12

Comments:
- v1.00: Declared Base model using SQLAlchemy declarative_base
"""

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

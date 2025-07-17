"""
Module/Script Name: src/__init__.py
Path: E:/projects/rank_rocket_calendar_stacker/src/__init__.py

Description:
Package initializer for Rank Rocket Calendar Stacker application.

Author(s):
Skippy the Code Slayer with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
17-07-2025

Last Modified Date:
17-07-2025

Version:
v1.01

Comments:
- Removed legacy top-level model imports to prevent `ModuleNotFoundError`
- Entry-point exposes application factory only
"""

# Expose application factory
from .main import create_app

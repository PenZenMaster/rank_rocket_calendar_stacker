"""
Module/Script Name: src/__init__.py

Description:
Package initializer for the src application, exposing factory function.

Author(s):
Skippy the Code Slayer

Created Date:
10-07-2025

Last Modified Date:
19-07-2025

Version:
v1.01

Comments:
- Removed top-level import of `create_app` to avoid circular import
"""

# `src` is now a namespace package. Create app via `python -m src.main`.
# No direct imports here to avoid circular dependencies.

# Optional: expose public API
# __all__ = ['main']

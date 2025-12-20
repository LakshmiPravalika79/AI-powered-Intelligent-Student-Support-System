# Package marker for app module
"""
================================================================================
UniAssist Pro - AI-Powered Student Support System
================================================================================

Application package initialization.

PACKAGE STRUCTURE:
-----------------
app/
├── __init__.py          # This file
├── main.py              # FastAPI application entry point
├── models/
│   ├── __init__.py
│   └── schemas.py       # Pydantic models
├── services/
│   ├── __init__.py
│   ├── auth_service.py  # Authentication & JWT
│   ├── ai_service.py    # AI/NLP processing
│   ├── esb_service.py   # ESB integration layer
│   └── analytics_service.py  # Metrics & logging
└── data/
    ├── __init__.py
    └── mock_database.py # In-memory mock data

VERSION: 1.0.0-MVP
================================================================================
"""

__version__ = "1.0.0-mvp"
__author__ = "DBIM Team"

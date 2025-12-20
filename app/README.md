# App Folder - Backend Application 🔧

This folder contains the **FastAPI backend** that powers UniAssist Pro.

## Structure

```
app/
├── __init__.py          # Package initializer
├── main.py              # 🚀 Application entry point & all API routes
│
├── data/                # 📊 Data Layer (Mock Databases)
│   ├── __init__.py
│   ├── mock_database.py # Student records, users, knowledge base
│   └── legacy_systems.py# 6 simulated enterprise systems
│
├── models/              # 📋 Data Models (Pydantic Schemas)
│   ├── __init__.py
│   └── schemas.py       # Request/Response validation models
│
└── services/            # ⚙️ Business Logic Layer
    ├── __init__.py
    ├── ai_service.py    # Intent classification & response generation
    ├── auth_service.py  # JWT authentication & RBAC
    ├── esb_service.py   # Enterprise Service Bus integration
    └── escalation_service.py # Ticket management system
```

## Key Files Explained

### `main.py` - Application Core
- FastAPI application setup
- All REST API endpoints
- CORS configuration
- Startup banner

### `data/mock_database.py` - Mock Data
- Student profiles (Sarah Johnson, Mike Chen)
- User credentials (students, staff, admin)
- Knowledge base for AI responses
- Query history storage

### `data/legacy_systems.py` - Legacy System Simulators
Simulates 6 enterprise systems:
| System | Class | Protocol |
|--------|-------|----------|
| Banner | `AdmissionsSystem` | SOAP/XML |
| PeopleSoft | `AcademicSystem` | JDBC |
| PowerFAIDS | `FinancialAidSystem` | REST |
| StarRez | `HousingSystem` | REST |
| Active Directory | `DirectoryService` | LDAP |
| Ex Libris | `LibrarySystem` | REST |

### `services/ai_service.py` - AI Logic
- **Intent Classification**: Keyword-based matching (no API keys needed)
- **Response Generation**: Template-based with personalization
- **Confidence Scoring**: Determines when to suggest human support

### `services/auth_service.py` - Authentication
- JWT token generation & validation
- Password hashing (bcrypt)
- Role-based access control (Student/Staff/Admin)

### `services/esb_service.py` - ESB Integration
- Aggregates data from all 6 legacy systems
- Returns unified student profile
- Handles system health checks

### `services/escalation_service.py` - Ticket System
- Create/update support tickets
- Message threading
- Status management (open → in_progress → resolved)

## Why This Architecture?

1. **Separation of Concerns**: Each service has a single responsibility
2. **Testable**: Services can be unit tested independently
3. **Swappable**: Easy to replace mock data with real databases
4. **Production-Ready**: Same structure works for enterprise deployment

## No External Dependencies

- ❌ No OpenAI API key required
- ❌ No database server needed
- ❌ No external services
- ✅ Everything runs locally in memory

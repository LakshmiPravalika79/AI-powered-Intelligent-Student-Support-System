# Services Layer - Business Logic ⚙️

This folder contains the **core business logic** of the application, separated by domain.

## Files

### `ai_service.py` - AI/NLP Processing 🤖

**Purpose**: Handle natural language understanding and response generation.

**Key Features**:
- Intent classification (financial_aid, registration, housing, etc.)
- Template-based response generation
- Personalization using student data
- Confidence scoring for escalation decisions

**Implementation**: Rule-based (no API keys required)

```python
# How intent classification works (simplified)
def classify_intent(query):
    if "financial" in query.lower():
        return "financial_aid", 0.95
    elif "course" in query.lower():
        return "registration", 0.90
    # ... etc
```

**Production Upgrade**: Swap keyword matching for OpenAI GPT-4 API call.

---

### `auth_service.py` - Authentication & Authorization 🔐

**Purpose**: Handle user login, JWT tokens, and role-based access.

**Key Features**:
- JWT token generation (24-hour expiry)
- Password hashing with bcrypt
- Role-based access control (RBAC)
- Permission checking for API endpoints

**Roles**:
| Role | Permissions |
|------|-------------|
| Student | View own data, create tickets |
| Staff | View all tickets, reply to students |
| Admin | Full access, analytics, user management |

---

### `esb_service.py` - Enterprise Service Bus 🔌

**Purpose**: Aggregate data from multiple legacy systems into unified profile.

**Key Features**:
- Connects to 6 simulated legacy systems
- Returns unified student profile
- Health check for all systems
- Error handling for system failures

**Architecture**:
```
Student Query
     │
     ▼
┌─────────────┐
│ ESB Service │
└──────┬──────┘
       │
       ├──▶ Banner (Admissions)
       ├──▶ PeopleSoft (Academic)
       ├──▶ PowerFAIDS (Financial)
       ├──▶ StarRez (Housing)
       ├──▶ Active Directory
       └──▶ Library System
       │
       ▼
Unified Student Profile
```

---

### `escalation_service.py` - Ticket Management 🎫

**Purpose**: Handle support ticket lifecycle when AI cannot resolve queries.

**Key Features**:
- Create tickets from chat
- Assign to support staff
- Message threading (student ↔ staff)
- Status management (open → in_progress → resolved)
- Priority levels (low, medium, high, urgent)

**Ticket Flow**:
```
Student asks question
        │
        ▼
   AI Responds
        │
   Confidence < 85%?
        │
    ┌───┴───┐
    │  Yes  │──▶ Show "Talk to Support" button
    └───────┘           │
                        ▼
                Create Ticket ──▶ Staff Dashboard
                        │
                Staff Replies ──▶ Student sees in "My Tickets"
```

## Design Principles

1. **Single Responsibility**: Each service handles one domain
2. **Dependency Injection**: Services don't depend on each other directly
3. **Testable**: Can be unit tested in isolation
4. **Swappable**: Easy to replace mock implementations with real ones

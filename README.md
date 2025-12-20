# UniAssist Pro - AI-Powered Student Support System

## 🎓 DBIM MVP Implementation

An intelligent student support chatbot demonstrating enterprise-grade architecture for a hackathon MVP.

---

## 📋 Quick Start (30 seconds)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the server
uvicorn app.main:app --reload

# 3. Open in browser
# API Docs: http://localhost:8000/docs
```

**Demo Login:**
- Username: `sarah.johnson@techedu.edu`
- Password: `demo123`

---

## 🎯 What This MVP Does

| Feature | Description | Status |
|---------|-------------|--------|
| ✅ Student Authentication | JWT-based login system | Mocked (demo users) |
| ✅ Submit Queries | Natural language questions | Working |
| ✅ AI Response | Intent classification + response | Rule-based (mocked) |
| ✅ Unified Student Data | Aggregated from multiple systems | Mocked (ESB pattern) |
| ✅ Query Logging | Track all interactions | In-memory |
| ✅ Admin Analytics | View metrics and KPIs | Working |
| ✅ ESB Integration | Enterprise service bus demo | Simulated |

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           CLOUD LAYER                                    │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐               │
│  │  API Gateway  │  │  AI Service   │  │   Analytics   │               │
│  │   (FastAPI)   │  │ (Rule-based)  │  │   Dashboard   │               │
│  └───────┬───────┘  └───────┬───────┘  └───────┬───────┘               │
└──────────┼──────────────────┼──────────────────┼────────────────────────┘
           │                  │                  │
           └──────────────────┼──────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────────────┐
│                    ENTERPRISE SERVICE BUS (ESB)                          │
│         • Message Routing  • Data Transformation  • Security            │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
    ┌─────────────┬───────────┼───────────┬─────────────┐
    │             │           │           │             │
┌───▼───┐   ┌─────▼─────┐ ┌───▼───┐ ┌─────▼─────┐ ┌─────▼─────┐
│Admiss-│   │ Academic  │ │Financ-│ │  Housing  │ │ Directory │
│ ions  │   │  Records  │ │  ial  │ │  System   │ │ Services  │
│(SOAP) │   │  (JDBC)   │ │(REST) │ │  (REST)   │ │  (LDAP)   │
└───────┘   └───────────┘ └───────┘ └───────────┘ └───────────┘
           [============ ON-PREMISE SYSTEMS ============]
```

---

## 📁 Project Structure

```
student-support-system/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application & routes
│   ├── models/
│   │   └── schemas.py          # Pydantic data models
│   ├── services/
│   │   ├── auth_service.py     # JWT authentication
│   │   ├── ai_service.py       # Intent classification & responses
│   │   ├── esb_service.py      # ESB integration layer
│   │   └── analytics_service.py # Metrics & logging
│   └── data/
│       └── mock_database.py    # In-memory mock data
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Optional container build
└── README.md                   # This file
```

---

## 🔍 What is Mocked (and Why)

| Component | MVP Implementation | Production Implementation |
|-----------|-------------------|---------------------------|
| **AI/NLP** | Keyword matching + templates | GPT-4 / Azure OpenAI |
| **Database** | In-memory Python dicts | PostgreSQL + Snowflake |
| **Authentication** | JWT with mock users | Azure AD / Okta SSO |
| **ESB** | Simulated integration | MuleSoft / Azure Service Bus |
| **Analytics** | In-memory logging | Azure Event Hubs + Power BI |

**Why Mock?**
- ✅ No API keys required
- ✅ Zero cost for demo
- ✅ Instant setup
- ✅ Predictable behavior for presentation
- ✅ Focus on architecture, not external services

---

## 🚀 How It Scales to Enterprise

### Horizontal Scaling
```
Load Balancer
     │
     ├── API Instance 1 (Azure App Service)
     ├── API Instance 2 (Azure App Service)
     └── API Instance N (Auto-scaled)
            │
         Redis Cache (Azure Cache)
            │
         ESB Gateway (MuleSoft)
            │
    ┌───────┴───────┐
    │               │
On-Premise      Cloud Data
Systems         Warehouse
```

### Key Scaling Strategies
1. **API Layer**: Azure App Service with auto-scaling (0-100+ instances)
2. **AI Processing**: Azure OpenAI with rate limiting and queuing
3. **Data**: Read replicas for queries, write to primary
4. **Cache**: Redis for frequently accessed student profiles
5. **ESB**: Message queues for async processing

---

## 🔌 ESB (Enterprise Service Bus) Explained

The ESB decouples cloud services from on-premise legacy systems:

### Why ESB?
- **Protocol Translation**: Convert SOAP/XML to REST/JSON
- **Security**: Single authentication point
- **Reliability**: Retry logic, circuit breakers
- **Monitoring**: Centralized logging
- **Compliance**: Data masking for FERPA/PCI

### Data Flow Example
```
Student asks: "When is my financial aid disbursement?"

1. API receives query → JWT validated
2. ESB routes to Financial Aid system (on-premise)
3. ESB transforms response (XML → JSON)
4. AI service generates personalized response
5. Analytics logs the interaction
6. Response returned to student
```

---

## ☁️ Hybrid Infrastructure

### Cloud Components (Azure/AWS)
- API Gateway & Load Balancers
- AI/ML Processing
- Analytics & Dashboards
- Caching (Redis)
- CDN for static assets

### On-Premise Components (Must remain local)
- **Admissions System** - FERPA compliance
- **Academic Records** - FERPA compliance  
- **Financial Aid** - PCI-DSS compliance
- **Housing System** - Institutional data
- **Active Directory** - Identity management

### Why Hybrid?
1. **Compliance**: FERPA requires educational records on-premise
2. **Legacy Systems**: Can't easily migrate mainframe systems
3. **Security**: Sensitive financial data stays local
4. **Latency**: Some operations need local speed

---

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info and status |
| `/health` | GET | Health check |
| `/token` | POST | Login (OAuth2) |
| `/api/chat` | POST | Submit query to AI |
| `/api/students/{id}` | GET | Get student profile |
| `/api/analytics` | GET | System metrics |
| `/api/esb/status` | GET | ESB integration status |
| `/api/knowledge-base` | GET | View FAQ content |
| `/docs` | GET | Swagger documentation |

---

## 🧪 Test the MVP

### 1. Login
```bash
curl -X POST "http://localhost:8000/token" \
  -d "username=sarah.johnson@techedu.edu&password=demo123"
```

### 2. Ask a Question
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"student_id": "STU2024001", "message": "When is my financial aid disbursement?"}'
```

### 3. View Analytics
```bash
curl "http://localhost:8000/api/analytics" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🎤 DBIM Presentation Talking Points

### 1. Business Problem
> "Students spend 15+ minutes per query navigating multiple systems. This costs universities $25 per human-handled inquiry."

### 2. Solution
> "UniAssist provides an AI-powered chatbot that integrates with legacy systems through an ESB, answering 73% of queries automatically."

### 3. Architecture Value
> "Our hybrid architecture keeps sensitive data on-premise for compliance while leveraging cloud AI for scalability."

### 4. ROI Metrics
> "At 73% automation, we project $91,000 monthly savings with 85% ROI in year one."

### 5. Technical Feasibility
> "The MVP demonstrates the complete architecture. Production deployment uses the same patterns with real AI and databases."

---

## 📝 Running with Docker (Optional)

```bash
# Build image
docker build -t uniassist-pro .

# Run container
docker run -p 8000:8000 uniassist-pro

# Access at http://localhost:8000
```

---

## 👥 Demo Users

| Username | Password | Role | Student ID |
|----------|----------|------|------------|
| sarah.johnson@techedu.edu | demo123 | Student | STU2024001 |
| michael.chen@techedu.edu | demo123 | Student | STU2024002 |
| emily.rodriguez@techedu.edu | demo123 | Student | STU2024003 |
| admin@techedu.edu | admin123 | Admin | - |

---

## ⚡ Quick Demo Script

1. **Open** http://localhost:8000/docs
2. **Click** "Authorize" → Enter demo credentials
3. **Try** POST `/api/chat` with:
   ```json
   {
     "student_id": "STU2024001",
     "message": "What's my GPA?"
   }
   ```
4. **Show** GET `/api/analytics` for metrics
5. **Show** GET `/api/esb/status` for architecture demo

---

## 🏆 Why This Architecture Wins

✅ **Correct Thinking** - Hybrid cloud with ESB is industry standard  
✅ **Feasibility** - Runs locally in 30 seconds, production-ready patterns  
✅ **Clean Explanation** - Every file has architecture comments  
✅ **Low Risk** - No external APIs, no secrets, no complex setup  
✅ **High Clarity** - Clear separation of concerns, documented flows

---

*Built for DBIM Hackathon - December 2024*

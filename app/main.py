"""
================================================================================
TechEdu University - Student Support Portal 
DBIM (Digital Business Innovation Methodology) MVP Implementation
================================================================================

ARCHITECTURE OVERVIEW:
----------------------
This is the main FastAPI application entry point that orchestrates all services.

KEY ARCHITECTURAL DECISIONS (MVP):
- Monolithic structure for simplicity (enterprise would be microservices)
- In-memory mock data (enterprise would use PostgreSQL/Snowflake)
- Rule-based AI (enterprise would use GPT-4/Azure OpenAI)
- Simulated ESB integration (enterprise would use MuleSoft/Azure Service Bus)

HYBRID INFRASTRUCTURE STRATEGY:
------------------------------
CLOUD (Azure/AWS):
- API Gateway & Load Balancers
- AI/ML Processing Services
- Analytics & Reporting
- Caching Layer (Redis)

ON-PREMISE:
- Legacy Student Information Systems
- Financial Aid Database (compliance requirements)
- Housing Management System
- Academic Records (FERPA compliance)

ESB (Enterprise Service Bus) ROLE:
- Decouples cloud services from on-premise systems
- Provides unified API interface
- Handles data transformation between systems
- Manages message routing and orchestration
================================================================================
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Dict
from datetime import datetime
import os

# Import all service modules (separation of concerns)
from app.services.auth_service import AuthService, oauth2_scheme
from app.services.ai_service import AIService
from app.services.esb_service import ESBService
from app.services.analytics_service import AnalyticsService
from app.services.rbac_service import RBACService, Role, Permission
from app.services.escalation_service import EscalationService, TicketStatus
from app.data.mock_database import MockDatabase
from app.data.legacy_systems import get_all_legacy_systems
from app.models.schemas import (
    Token, QueryRequest, QueryResponse, 
    StudentModel, AnalyticsMetrics
)

# ================================================================================
# APPLICATION INITIALIZATION
# ================================================================================

app = FastAPI(
    title="TechEdu University  API",
    description="""
    ## AI-Powered Intelligent Student Support System
    
    ### DBIM MVP Implementation
    
    This API demonstrates an intelligent student support system that:
    - **Authenticates** students via JWT tokens
    - **Processes queries** using AI-powered intent classification
    - **Integrates data** from multiple legacy systems via ESB
    - **Provides analytics** for administrative oversight
    
    ### Architecture Highlights
    - **Hybrid Infrastructure**: Cloud + On-Premise integration
    - **ESB Pattern**: Decoupled system integration
    - **Mock AI**: Rule-based for MVP, ready for GPT-4 integration
    
    ### Demo Credentials
    - Username: `sarah.johnson@techedu.edu`
    - Password: `demo123`
    """,
    version="1.0.0-MVP",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ================================================================================
# MIDDLEWARE CONFIGURATION
# ================================================================================
"""
CORS is configured to allow all origins for MVP demonstration.
PRODUCTION NOTE: Restrict origins to specific frontend domains.
"""
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # PRODUCTION: ["https://uniassist.techedu.edu"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================================================================================
# SERVICE INITIALIZATION
# ================================================================================
"""
Services are initialized as singletons for this MVP.
PRODUCTION: Use dependency injection with proper lifecycle management.
SCALING: Each service would be a separate microservice with its own scaling.
"""

# Initialize mock database (simulates multiple legacy systems)
db = MockDatabase()

# Initialize services with database reference
auth_service = AuthService(db)
ai_service = AIService(db)
esb_service = ESBService(db)
analytics_service = AnalyticsService(db)
rbac_service = RBACService(db)
escalation_service = EscalationService(db)

# Mount static files for frontend
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# ================================================================================
# HEALTH & STATUS ENDPOINTS
# ================================================================================

@app.get("/", include_in_schema=False)
def serve_frontend():
    """
    Always serve the frontend UI at root.
    """
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    # Otherwise return API info
    return {
        "name": "UniAssist Pro API",
        "version": "1.0.0-MVP",
        "description": "AI-Powered Intelligent Student Support System",
        "architecture": "DBIM Hybrid Cloud + On-Premise",
        "status": "operational",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        },
        "demo_credentials": {
            "username": "sarah.johnson@techedu.edu",
            "password": "demo123"
        }
    }


@app.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    
    PRODUCTION DEPLOYMENT:
    - Kubernetes liveness/readiness probes would call this
    - Azure App Service health checks
    - AWS ALB health checks
    
    MONITORING:
    - Cloud: Azure Monitor / AWS CloudWatch
    - Alerts: PagerDuty / Slack integration
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0-MVP",
        "environment": "development",  # PRODUCTION: Read from env var
        "services": {
            "api": "operational",
            "esb_gateway": "operational (mocked)",
            "ai_service": "operational (rule-based)",
            "data_layer": "operational (in-memory)"
        },
        "infrastructure": {
            "note": "MVP uses in-memory data; production uses hybrid cloud"
        }
    }


# ================================================================================
# AUTHENTICATION ENDPOINTS
# ================================================================================

@app.post("/token", response_model=Token, tags=["Authentication"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token login endpoint.
    
    AUTHENTICATION FLOW:
    1. Client submits username/password
    2. Server validates against user store
    3. JWT token issued with expiration
    4. Client uses token in Authorization header
    
    PRODUCTION ENHANCEMENTS:
    - Azure AD / SAML integration for SSO
    - Multi-factor authentication
    - Token refresh mechanism
    - Rate limiting (prevent brute force)
    
    SECURITY NOTES:
    - JWT secret should be in Azure Key Vault / AWS Secrets Manager
    - Passwords hashed with bcrypt (already implemented)
    - Token expiration: 30 minutes (configurable)
    """
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth_service.create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}


# ================================================================================
# CHAT/QUERY ENDPOINTS - Core AI Functionality
# ================================================================================

@app.post("/api/chat", response_model=QueryResponse, tags=["AI Chat"])
async def chat(
    query: QueryRequest,
    current_user: Dict = Depends(auth_service.get_current_user)
):
    """
    Process student query and return AI-generated response.
    
    ╔══════════════════════════════════════════════════════════════════╗
    ║                    REQUEST PROCESSING FLOW                        ║
    ╠══════════════════════════════════════════════════════════════════╣
    ║  1. AUTHENTICATION                                                ║
    ║     └─> JWT token validated                                       ║
    ║                                                                   ║
    ║  2. ESB DATA AGGREGATION (Simulated)                             ║
    ║     ├─> Admissions System (ON-PREMISE)                           ║
    ║     ├─> Academic Records (ON-PREMISE - FERPA)                    ║
    ║     ├─> Financial Aid (ON-PREMISE - PCI)                         ║
    ║     └─> Housing System (ON-PREMISE)                              ║
    ║                                                                   ║
    ║  3. AI PROCESSING (CLOUD)                                        ║
    ║     ├─> Intent Classification                                    ║
    ║     ├─> Context Enrichment                                       ║
    ║     └─> Response Generation                                      ║
    ║                                                                   ║
    ║  4. ANALYTICS LOGGING (CLOUD)                                    ║
    ║     └─> Query logged for metrics & improvement                   ║
    ╚══════════════════════════════════════════════════════════════════╝
    
    MVP IMPLEMENTATION:
    - Rule-based intent classification (keyword matching)
    - Template-based response generation
    - In-memory analytics logging
    
    PRODUCTION IMPLEMENTATION:
    - GPT-4 / Azure OpenAI for NLU
    - Vector embeddings for semantic search
    - Real-time analytics pipeline (Azure Event Hubs)
    """
    try:
        # Step 1: Get unified student data via ESB
        # ESB aggregates data from multiple on-premise systems
        student_data = esb_service.get_unified_student_profile(query.student_id)
        
        if not student_data:
            raise HTTPException(
                status_code=404,
                detail=f"Student {query.student_id} not found in any integrated system"
            )
        
        # Step 2: AI Service processes the query
        # In MVP: Rule-based classification
        # In Production: GPT-4 with RAG (Retrieval Augmented Generation)
        category = ai_service.classify_intent(query.message)
        
        # Step 3: Generate personalized response
        response = ai_service.generate_response(
            message=query.message,
            student_data=student_data,
            category=category
        )
        
        # Step 4: Log for analytics (async in production)
        analytics_service.log_query(
            student_id=query.student_id,
            query=query.message,
            response=response
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        # PRODUCTION: Log to Azure Application Insights
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


# ================================================================================
# STUDENT DATA ENDPOINTS - ESB Integration Demo
# ================================================================================

@app.get("/api/students/{student_id}", response_model=StudentModel, tags=["Student Data"])
async def get_student_profile(
    student_id: str,
    current_user: Dict = Depends(auth_service.get_current_user)
):
    """
    Get unified student profile aggregated from all systems.
    
    ╔══════════════════════════════════════════════════════════════════╗
    ║                    ESB DATA INTEGRATION                           ║
    ╠══════════════════════════════════════════════════════════════════╣
    ║  This endpoint demonstrates ESB-style data aggregation:          ║
    ║                                                                   ║
    ║  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐        ║
    ║  │  Admissions │     │  Academic   │     │  Financial  │        ║
    ║  │   System    │     │   Records   │     │     Aid     │        ║
    ║  └──────┬──────┘     └──────┬──────┘     └──────┬──────┘        ║
    ║         │                   │                   │               ║
    ║         └───────────────────┼───────────────────┘               ║
    ║                             │                                    ║
    ║                    ┌────────▼────────┐                          ║
    ║                    │   ESB Gateway   │                          ║
    ║                    │ (Data Transform)│                          ║
    ║                    └────────┬────────┘                          ║
    ║                             │                                    ║
    ║                    ┌────────▼────────┐                          ║
    ║                    │ Unified Profile │                          ║
    ║                    └─────────────────┘                          ║
    ╚══════════════════════════════════════════════════════════════════╝
    
    ON-PREMISE SYSTEMS (Simulated):
    - Banner/Ellucian for Admissions
    - PeopleSoft for Academic Records
    - PowerFAIDS for Financial Aid
    - StarRez for Housing
    
    ESB FUNCTIONS:
    - Protocol translation (SOAP → REST)
    - Data transformation (XML → JSON)
    - Error handling & retry logic
    - Caching for performance
    """
    student_data = esb_service.get_unified_student_profile(student_id)
    
    if not student_data:
        raise HTTPException(
            status_code=404,
            detail=f"Student {student_id} not found"
        )
    
    return student_data


@app.get("/api/esb/status", tags=["ESB Integration"])
async def get_esb_status(
    current_user: Dict = Depends(auth_service.get_current_user)
):
    """
    Get ESB integration status and connected systems.
    
    DEMONSTRATES:
    - Which legacy systems are connected via ESB
    - Current connectivity status
    - Data flow patterns
    
    PRODUCTION:
    - Real-time system health from MuleSoft/Azure Service Bus
    - Circuit breaker status
    - Message queue depths
    """
    return esb_service.get_integration_status()


# ================================================================================
# ANALYTICS ENDPOINTS - Admin Dashboard
# ================================================================================

@app.get("/api/analytics", response_model=AnalyticsMetrics, tags=["Analytics"])
async def get_analytics(
    current_user: Dict = Depends(auth_service.get_current_user)
):
    """
    Get real-time system analytics and metrics.
    
    METRICS PROVIDED:
    - Total queries processed
    - Automated resolution rate (vs human escalation)
    - Average response time
    - Student satisfaction score
    - Active user count
    - Query volume trends
    - Top query categories
    - System health indicators
    - ROI metrics
    
    MVP: Simulated metrics with some real query logging
    PRODUCTION: 
    - Azure Data Factory for ETL
    - Snowflake for data warehouse
    - Power BI for dashboards
    - Real-time streaming analytics
    """
    return analytics_service.get_metrics()


@app.get("/api/analytics/queries", tags=["Analytics"])
async def get_query_log(
    limit: int = 50,
    current_user: Dict = Depends(auth_service.get_current_user)
):
    """
    Get recent query log for analysis and debugging.
    
    USE CASES:
    - Admin monitoring of AI performance
    - Training data collection for AI improvement
    - Compliance auditing
    - Escalation pattern analysis
    
    PRODUCTION:
    - Stored in Azure Cosmos DB / AWS DynamoDB
    - 90-day retention policy
    - PII masking for compliance
    """
    return analytics_service.get_query_log(limit)


# ================================================================================
# KNOWLEDGE BASE ENDPOINTS
# ================================================================================

@app.get("/api/knowledge-base", tags=["Knowledge Base"])
async def get_knowledge_base(
    current_user: Dict = Depends(auth_service.get_current_user)
):
    """
    Get all knowledge base entries.
    
    MVP: Static JSON knowledge base
    PRODUCTION:
    - Vector database (Pinecone/Azure Cognitive Search)
    - Semantic search with embeddings
    - Regular updates from content management
    """
    return {"knowledge_base": db.knowledge_base}


@app.get("/api/knowledge-base/search", tags=["Knowledge Base"])
async def search_knowledge_base(
    query: str,
    limit: int = 5,
    current_user: Dict = Depends(auth_service.get_current_user)
):
    """
    Search knowledge base.
    
    MVP: Keyword-based search
    PRODUCTION: 
    - Vector similarity search
    - GPT-4 embeddings
    - Contextual ranking
    """
    return ai_service.search_knowledge_base(query, limit)


# ================================================================================
# ADMIN ENDPOINTS - Role-Based Access Control
# ================================================================================

@app.get("/api/admin/users", tags=["Admin"])
async def get_all_users(
    current_user: Dict = Depends(auth_service.get_current_user)
):
    """
    Get all users (Admin only).
    
    RBAC: Requires ADMIN role
    
    Returns list of all users with their roles and status.
    Passwords are never returned.
    """
    # Check admin permission
    if not rbac_service.has_permission(current_user["username"], Permission.MANAGE_USERS):
        raise HTTPException(
            status_code=403,
            detail="Access denied: Admin role required"
        )
    
    # Return users without sensitive data
    users = []
    for username, user_data in db.users.items():
        users.append({
            "username": username,
            "name": user_data.get("name", "Unknown"),
            "role": user_data.get("role", "student"),
            "department": user_data.get("department"),
            "student_id": user_data.get("student_id"),
            "is_active": user_data.get("is_active", True),
            "created_at": user_data.get("created_at"),
            "last_login": user_data.get("last_login")
        })
    
    return {
        "total_users": len(users),
        "users": users,
        "role_summary": {
            "students": len([u for u in users if u["role"] == "student"]),
            "staff": len([u for u in users if u["role"] == "staff"]),
            "admins": len([u for u in users if u["role"] == "admin"])
        }
    }


@app.get("/api/admin/legacy-systems", tags=["Admin"])
async def get_legacy_systems_status(
    current_user: Dict = Depends(auth_service.get_current_user)
):
    """
    Get status of all integrated legacy systems (Admin/Staff only).
    
    RBAC: Requires ADMIN or STAFF role
    
    ╔════════════════════════════════════════════════════════════════════════╗
    ║                    ON-PREMISE LEGACY SYSTEMS                           ║
    ╠════════════════════════════════════════════════════════════════════════╣
    ║  1. ADMISSIONS SYSTEM (Banner/Ellucian)                               ║
    ║     - Student enrollments, demographics                               ║
    ║     - Location: ON-PREMISE                                            ║
    ║                                                                        ║
    ║  2. ACADEMIC RECORDS (PeopleSoft/Colleague)                           ║
    ║     - Courses, grades, transcripts                                    ║
    ║     - Location: ON-PREMISE (FERPA compliance)                         ║
    ║                                                                        ║
    ║  3. FINANCIAL AID (PowerFAIDS)                                        ║
    ║     - Aid packages, disbursements                                     ║
    ║     - Location: ON-PREMISE (PCI-DSS compliance)                       ║
    ║                                                                        ║
    ║  4. HOUSING MANAGEMENT (StarRez)                                      ║
    ║     - Room assignments, meal plans                                    ║
    ║     - Location: ON-PREMISE                                            ║
    ║                                                                        ║
    ║  5. DIRECTORY SERVICES (Active Directory)                             ║
    ║     - User authentication, groups                                     ║
    ║     - Location: ON-PREMISE                                            ║
    ║                                                                        ║
    ║  6. LIBRARY SYSTEM (Alma/Ex Libris)                                   ║
    ║     - Book checkouts, fines                                           ║
    ║     - Location: HYBRID (on-prem DB, cloud interface)                  ║
    ╚════════════════════════════════════════════════════════════════════════╝
    """
    # Check permission
    if not rbac_service.has_permission(current_user["username"], Permission.VIEW_ANALYTICS):
        raise HTTPException(
            status_code=403,
            detail="Access denied: Staff or Admin role required"
        )
    
    # Get all legacy systems info
    legacy_systems = get_all_legacy_systems()
    
    return {
        "integration_type": "Enterprise Service Bus (ESB)",
        "total_systems": len(legacy_systems),
        "systems": legacy_systems,
        "architecture_notes": {
            "esb_platform": "Simulated (Production: MuleSoft/Azure Service Bus)",
            "data_flow": "On-Premise → ESB → Cloud API → Client",
            "compliance": {
                "FERPA": "Academic records kept on-premise",
                "PCI-DSS": "Financial data kept on-premise",
                "GDPR": "PII data with proper access controls"
            }
        }
    }


@app.get("/api/admin/roles", tags=["Admin"])
async def get_roles_and_permissions(
    current_user: Dict = Depends(auth_service.get_current_user)
):
    """
    Get all roles and their permissions (Admin only).
    
    RBAC: Requires ADMIN role
    
    Returns the complete RBAC matrix showing what each role can do.
    """
    if not rbac_service.has_permission(current_user["username"], Permission.MANAGE_USERS):
        raise HTTPException(
            status_code=403,
            detail="Access denied: Admin role required"
        )
    
    return {
        "roles": [role.value for role in Role],
        "permissions": [perm.value for perm in Permission],
        "role_permissions": {
            Role.STUDENT.value: [p.value for p in rbac_service.ROLE_PERMISSIONS[Role.STUDENT]],
            Role.STAFF.value: [p.value for p in rbac_service.ROLE_PERMISSIONS[Role.STAFF]],
            Role.ADMIN.value: [p.value for p in rbac_service.ROLE_PERMISSIONS[Role.ADMIN]]
        },
        "description": {
            "student": "Can view own profile, use chat, access knowledge base",
            "staff": "Can view student data, analytics, manage escalations",
            "admin": "Full system access including user management and system config"
        }
    }


@app.get("/api/me", tags=["User Profile"])
async def get_current_user_profile(
    current_user: Dict = Depends(auth_service.get_current_user)
):
    """
    Get current authenticated user's profile and permissions.
    
    Returns user info along with their role and available permissions.
    """
    user_data = db.users.get(current_user["username"], {})
    role_str = user_data.get("role", "student")
    role = Role(role_str)
    
    # Get permissions for this user
    permissions = rbac_service.get_permissions(current_user["username"])
    
    return {
        "username": current_user["username"],
        "name": user_data.get("name", "Unknown"),
        "role": role_str,
        "department": user_data.get("department"),
        "student_id": user_data.get("student_id"),
        "permissions": [p.value for p in permissions],
        "is_admin": role == Role.ADMIN,
        "is_staff": role in [Role.STAFF, Role.ADMIN],
        "last_login": user_data.get("last_login"),
        "ui_capabilities": {
            "can_view_admin_panel": role in [Role.STAFF, Role.ADMIN],
            "can_manage_users": role == Role.ADMIN,
            "can_view_all_students": role in [Role.STAFF, Role.ADMIN],
            "can_view_legacy_systems": role in [Role.STAFF, Role.ADMIN],
            "can_view_analytics": role in [Role.STAFF, Role.ADMIN],
            "can_export_data": role == Role.ADMIN
        }
    }


@app.get("/api/students", tags=["Student Data"])
async def list_students(
    current_user: Dict = Depends(auth_service.get_current_user)
):
    """
    List all students (Staff/Admin only).
    
    RBAC: Requires VIEW_ALL_STUDENTS permission
    
    Students can only view their own profile via /api/students/{student_id}
    """
    if not rbac_service.has_permission(current_user["username"], Permission.VIEW_ALL_STUDENTS):
        raise HTTPException(
            status_code=403,
            detail="Access denied: Staff or Admin role required to view all students"
        )
    
    students = []
    for student_id, data in db.students.items():
        students.append({
            "id": student_id,
            "name": data.get("name"),
            "email": data.get("email"),
            "program": data.get("program"),
            "year": data.get("year"),
            "gpa": data.get("gpa")
        })
    
    return {
        "total_students": len(students),
        "students": students
    }


# ================================================================================
# SUPPORT STAFF PORTAL - Escalation & Ticketing
# ================================================================================

@app.get("/api/tickets", tags=["Support Tickets"])
async def get_tickets(
    status: str = None,
    current_user: Dict = Depends(auth_service.get_current_user)
):
    """
    Get all support tickets (Staff/Admin only).
    
    ESCALATION FLOW:
    ┌──────────────┐     ┌───────────────┐     ┌──────────────┐
    │ AI Response  │────►│ Low Confidence│────►│ Create Ticket│
    │ Confidence   │     │   < 70%       │     │ for Staff    │
    └──────────────┘     └───────────────┘     └──────────────┘
    
    Query params:
    - status: Filter by ticket status (open, in_progress, resolved, etc.)
    """
    user_role = rbac_service.get_user_role(current_user["username"])
    
    # Students can only see their own tickets
    if user_role == Role.STUDENT:
        student_id = current_user.get("student_id")
        if student_id:
            return {
                "tickets": escalation_service.get_student_tickets(student_id),
                "can_manage": False
            }
        return {"tickets": [], "can_manage": False}
    
    # Staff/Admin can see all tickets
    tickets = escalation_service.get_all_tickets(status)
    stats = escalation_service.get_escalation_stats()
    
    return {
        "tickets": tickets,
        "stats": stats,
        "can_manage": True
    }


@app.get("/api/tickets/my", tags=["Support Tickets"])
async def get_my_tickets(
    current_user: Dict = Depends(auth_service.get_current_user)
):
    """
    Get tickets assigned to the current staff member.
    
    For staff: Returns tickets assigned to them
    For students: Returns their submitted tickets
    """
    user_role = rbac_service.get_user_role(current_user["username"])
    
    if user_role == Role.STUDENT:
        student_id = current_user.get("student_id")
        return {"tickets": escalation_service.get_student_tickets(student_id) if student_id else []}
    
    return {"tickets": escalation_service.get_staff_tickets(current_user["username"])}


@app.post("/api/tickets/create", tags=["Support Tickets"])
async def create_ticket(
    ticket_data: Dict,
    current_user: Dict = Depends(auth_service.get_current_user)
):
    """
    Create a new support ticket (Student can manually escalate).
    
    This allows students to manually request human support even if
    the AI provided an answer. Useful when:
    - Student needs more detailed help
    - AI answer wasn't satisfactory
    - Complex situation requiring human judgment
    
    Request body:
    - query: The student's question/issue
    - category: Query category (optional)
    - ai_confidence: AI's confidence score (optional)
    """
    student_id = current_user.get("student_id")
    
    if not student_id:
        raise HTTPException(
            status_code=400, 
            detail="Only students can create support tickets"
        )
    
    query = ticket_data.get("query", "")
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")
    
    # Create the ticket
    ticket = escalation_service.create_ticket(
        student_id=student_id,
        query=query,
        ai_response="Student requested human support",
        ai_confidence=ticket_data.get("ai_confidence", 0.5),
        category=ticket_data.get("category", "general")
    )
    
    return {
        "message": "Ticket created successfully",
        "ticket": ticket
    }


@app.get("/api/tickets/{ticket_id}", tags=["Support Tickets"])
async def get_ticket_detail(
    ticket_id: str,
    current_user: Dict = Depends(auth_service.get_current_user)
):
    """Get detailed ticket information including message history."""
    ticket = escalation_service.get_ticket(ticket_id)
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    user_role = rbac_service.get_user_role(current_user["username"])
    
    # Students can only view their own tickets
    if user_role == Role.STUDENT:
        if ticket.get("student_id") != current_user.get("student_id"):
            raise HTTPException(status_code=403, detail="Access denied")
    
    return ticket


@app.post("/api/tickets/{ticket_id}/assign", tags=["Support Tickets"])
async def assign_ticket(
    ticket_id: str,
    current_user: Dict = Depends(auth_service.get_current_user)
):
    """
    Assign a ticket to yourself (Staff/Admin only).
    
    Staff members can claim open tickets to work on them.
    """
    user_role = rbac_service.get_user_role(current_user["username"])
    
    if user_role == Role.STUDENT:
        raise HTTPException(status_code=403, detail="Only staff can assign tickets")
    
    ticket = escalation_service.assign_ticket(ticket_id, current_user["username"])
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    return {"message": "Ticket assigned successfully", "ticket": ticket}


@app.post("/api/tickets/{ticket_id}/message", tags=["Support Tickets"])
async def add_ticket_message(
    ticket_id: str,
    message: Dict,
    current_user: Dict = Depends(auth_service.get_current_user)
):
    """
    Add a message to a ticket.
    
    Both students and staff can add messages to tickets they have access to.
    This enables back-and-forth communication for issue resolution.
    """
    ticket = escalation_service.get_ticket(ticket_id)
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    user_role = rbac_service.get_user_role(current_user["username"])
    
    # Determine sender type
    if user_role == Role.STUDENT:
        if ticket.get("student_id") != current_user.get("student_id"):
            raise HTTPException(status_code=403, detail="Access denied")
        sender_type = "student"
    else:
        sender_type = "staff"
    
    updated_ticket = escalation_service.add_message(
        ticket_id,
        sender_type,
        current_user["username"],
        message.get("text", "")
    )
    
    return {"message": "Message added", "ticket": updated_ticket}


@app.post("/api/tickets/{ticket_id}/resolve", tags=["Support Tickets"])
async def resolve_ticket(
    ticket_id: str,
    resolution: Dict,
    current_user: Dict = Depends(auth_service.get_current_user)
):
    """
    Mark a ticket as resolved (Staff/Admin only).
    
    Resolution notes are required to document how the issue was resolved.
    """
    user_role = rbac_service.get_user_role(current_user["username"])
    
    if user_role == Role.STUDENT:
        raise HTTPException(status_code=403, detail="Only staff can resolve tickets")
    
    ticket = escalation_service.resolve_ticket(
        ticket_id,
        resolution.get("notes", "Resolved by support staff")
    )
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    return {"message": "Ticket resolved", "ticket": ticket}


@app.get("/api/escalation/stats", tags=["Support Tickets"])
async def get_escalation_stats(
    current_user: Dict = Depends(auth_service.get_current_user)
):
    """
    Get escalation statistics for dashboard (Staff/Admin only).
    
    Shows metrics like:
    - Total tickets
    - Open vs resolved
    - Average resolution time
    - Escalation rate
    """
    user_role = rbac_service.get_user_role(current_user["username"])
    
    if user_role == Role.STUDENT:
        raise HTTPException(status_code=403, detail="Staff access required")
    
    return escalation_service.get_escalation_stats()


# ================================================================================
# ARCHITECTURE DOCUMENTATION ENDPOINT
# ================================================================================

@app.get("/api/architecture", tags=["Documentation"])
async def get_architecture_docs():
    """
    Get system architecture documentation.
    
    This endpoint explains how the MVP simulates enterprise legacy systems
    and the overall hybrid cloud architecture.
    
    NO AUTHENTICATION REQUIRED - This is public documentation.
    """
    return {
        "title": "TechEdu University - System Architecture",
        "version": "1.0.0-MVP",
        "overview": {
            "description": "AI-Powered Intelligent Student Support System demonstrating enterprise integration patterns",
            "methodology": "DBIM (Digital Business Innovation Methodology)",
            "purpose": "Hackathon MVP demonstrating how AI can integrate with legacy university systems"
        },
        "data_architecture": {
            "explanation": """
            This MVP uses IN-MEMORY data structures to SIMULATE what would be separate 
            on-premise legacy systems in a real university deployment.
            
            WHY IN-MEMORY FOR MVP:
            - Zero setup required (no database installation)
            - Instant deployment for demo
            - Focus on architecture patterns, not infrastructure
            - All data resets on restart (safe for demo)
            
            PRODUCTION WOULD USE:
            - PostgreSQL/Oracle for transactional data
            - Snowflake/BigQuery for analytics warehouse
            - Redis for caching layer
            - Elasticsearch for search
            """,
            "simulated_systems": [
                {
                    "name": "Admissions System",
                    "real_world": "Ellucian Banner",
                    "data_simulated": ["Student demographics", "Enrollment status", "Application data"],
                    "why_on_premise": "Contains sensitive PII, institutional data governance"
                },
                {
                    "name": "Academic Records",
                    "real_world": "PeopleSoft Campus Solutions",
                    "data_simulated": ["Courses", "Grades", "GPA", "Transcripts"],
                    "why_on_premise": "FERPA compliance requires strict data residency"
                },
                {
                    "name": "Financial Aid",
                    "real_world": "PowerFAIDS / Banner Financial Aid",
                    "data_simulated": ["Aid packages", "Disbursements", "FAFSA status"],
                    "why_on_premise": "PCI-DSS compliance, sensitive financial data"
                },
                {
                    "name": "Housing System",
                    "real_world": "StarRez",
                    "data_simulated": ["Room assignments", "Building info", "Move-in dates"],
                    "why_on_premise": "Integrated with physical access control systems"
                },
                {
                    "name": "Directory Services",
                    "real_world": "Active Directory / LDAP",
                    "data_simulated": ["User authentication", "Role assignments", "Group memberships"],
                    "why_on_premise": "Core identity infrastructure, security requirements"
                },
                {
                    "name": "Library System",
                    "real_world": "Ex Libris Alma",
                    "data_simulated": ["Checkouts", "Fines", "Research access"],
                    "why_on_premise": "Licensing agreements, patron privacy"
                }
            ]
        },
        "esb_pattern": {
            "what_is_esb": """
            Enterprise Service Bus (ESB) is a middleware architecture that allows 
            different systems to communicate through a central hub rather than 
            point-to-point integrations.
            """,
            "why_esb": [
                "Decouples systems - changes to one don't break others",
                "Protocol translation - SOAP, REST, file-based all work together",
                "Data transformation - XML to JSON, different schemas",
                "Security - centralized authentication and authorization",
                "Monitoring - single place to see all integrations"
            ],
            "mvp_simulation": """
            Our ESBService class SIMULATES what MuleSoft, Azure Service Bus, 
            or IBM Integration Bus would do:
            - Aggregates data from multiple 'systems' (our mock databases)
            - Transforms data into unified format
            - Handles errors gracefully
            - Provides integration status monitoring
            """,
            "production_implementation": {
                "options": ["MuleSoft Anypoint", "Azure Service Bus", "AWS EventBridge", "Apache Camel"],
                "features": ["Message queuing", "Event-driven architecture", "Circuit breakers", "Retry policies"]
            }
        },
        "hybrid_cloud_architecture": {
            "diagram": """
            ┌─────────────────────────────────────────────────────────────────┐
            │                         CLOUD (Azure/AWS)                        │
            │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
            │  │ Frontend │  │ API      │  │ AI/ML    │  │ Analytics│        │
            │  │ (React)  │  │ Gateway  │  │ Service  │  │ (Cloud)  │        │
            │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘        │
            │       └──────────────┴──────────────┴──────────────┘            │
            │                              │                                   │
            │                    ┌─────────▼─────────┐                        │
            │                    │   ESB GATEWAY     │                        │
            │                    │ (MuleSoft/Azure)  │                        │
            │                    └─────────┬─────────┘                        │
            └──────────────────────────────┼──────────────────────────────────┘
                                           │
                            ═══════════════╪═══════════════  (Secure VPN)
                                           │
            ┌──────────────────────────────┼──────────────────────────────────┐
            │                              │     ON-PREMISE DATACENTER        │
            │  ┌───────────┐  ┌───────────▼───┐  ┌───────────┐  ┌──────────┐ │
            │  │ Admissions│  │ Academic     │  │ Financial │  │ Housing  │ │
            │  │ (Banner)  │  │ (PeopleSoft) │  │ (PowerFAIDS)│ │(StarRez) │ │
            │  │           │  │              │  │           │  │          │ │
            │  │ [FERPA]   │  │ [FERPA]      │  │ [PCI-DSS] │  │ [Privacy]│ │
            │  └───────────┘  └──────────────┘  └───────────┘  └──────────┘ │
            └─────────────────────────────────────────────────────────────────┘
            """,
            "cloud_components": {
                "what_goes_in_cloud": [
                    "API Gateway - handles all external traffic",
                    "AI/ML Processing - GPT-4, intent classification",
                    "Analytics Dashboard - aggregated, anonymized metrics",
                    "Frontend Application - React/Vue hosted on CDN",
                    "Caching Layer - Redis for performance"
                ],
                "benefits": ["Scalability", "Global availability", "Managed services", "Cost efficiency"]
            },
            "on_premise_components": {
                "what_stays_on_premise": [
                    "Student Information System - core institutional data",
                    "Financial Systems - compliance requirements",
                    "Academic Records - FERPA data residency",
                    "Identity Services - security infrastructure"
                ],
                "reasons": ["Compliance (FERPA, PCI-DSS)", "Data sovereignty", "Existing investments", "Security policies"]
            }
        },
        "ai_architecture": {
            "mvp_approach": """
            For this MVP, we use RULE-BASED AI:
            - Keyword matching for intent classification
            - Template-based responses with personalization
            - Simple confidence scoring
            
            This demonstrates the CONCEPT without API costs or complexity.
            """,
            "production_approach": {
                "components": [
                    "GPT-4 / Azure OpenAI for natural language understanding",
                    "Vector embeddings for semantic search (Pinecone/Weaviate)",
                    "RAG (Retrieval Augmented Generation) for accurate responses",
                    "Fine-tuned models for university-specific terminology"
                ],
                "why_not_in_mvp": "API costs, setup complexity, demo reliability"
            }
        },
        "security_model": {
            "authentication": "JWT tokens with role-based claims",
            "authorization": "RBAC with Student/Staff/Admin roles",
            "production_additions": [
                "Azure AD / SAML SSO integration",
                "Multi-factor authentication",
                "OAuth 2.0 with refresh tokens",
                "API rate limiting",
                "Audit logging"
            ]
        }
    }


# ================================================================================
# APPLICATION ENTRY POINT
# ================================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("""
    ╔════════════════════════════════════════════════════════════════════════╗
    ║           TechEdu University - Student Support Portal             ║
    ║                     DBIM MVP Implementation                            ║
    ╠════════════════════════════════════════════════════════════════════════╣
    ║                                                                        ║
    ║  🌐 API URL:     http://localhost:8000                                 ║
    ║  📚 Swagger:     http://localhost:8000/docs                            ║
    ║  📖 ReDoc:       http://localhost:8000/redoc                           ║
    ║                                                                        ║
    ╠════════════════════════════════════════════════════════════════════════╣
    ║  Demo Credentials:                                                     ║
    ║    👤 Username: sarah.johnson@techedu.edu                              ║
    ║    🔑 Password: demo123                                                ║
    ╠════════════════════════════════════════════════════════════════════════╣
    ║  Quick Test:                                                           ║
    ║    1. Open http://localhost:8000/docs                                  ║
    ║    2. Click 'Authorize' and login                                      ║
    ║    3. Try POST /api/chat with a question                               ║
    ╠════════════════════════════════════════════════════════════════════════╣
    ║  Architecture:                                                         ║
    ║    • Hybrid Cloud (Azure/AWS) + On-Premise                            ║
    ║    • ESB Integration Layer (Simulated)                                 ║
    ║    • Rule-based AI (Ready for GPT-4)                                   ║
    ║    • In-memory Data (Ready for PostgreSQL/Snowflake)                   ║
    ╚════════════════════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

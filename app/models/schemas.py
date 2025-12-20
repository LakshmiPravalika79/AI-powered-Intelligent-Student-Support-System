"""
================================================================================
DATA MODELS & SCHEMAS
================================================================================

Pydantic models for request/response validation and serialization.

ARCHITECTURE NOTE:
These schemas define the contract between:
- Frontend ↔ API
- API ↔ Services
- ESB ↔ Legacy Systems (data transformation)

PRODUCTION:
- Schemas would be versioned for backward compatibility
- OpenAPI spec auto-generated from these models
- Client SDKs can be generated from OpenAPI spec
================================================================================
"""

from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


# ================================================================================
# AUTHENTICATION MODELS
# ================================================================================

class Token(BaseModel):
    """JWT Token response model."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Data extracted from JWT token."""
    username: Optional[str] = None


# ================================================================================
# STUDENT DATA MODELS
# ================================================================================
"""
These models represent the UNIFIED view of student data.
In production, data comes from multiple ON-PREMISE systems:
- Admissions: Banner/Ellucian
- Academic: PeopleSoft
- Financial: PowerFAIDS
- Housing: StarRez

ESB transforms and aggregates data into this unified format.
"""

class CourseModel(BaseModel):
    """Individual course enrollment."""
    code: str
    name: str
    credits: int
    grade: Optional[str] = None


class FinancialAidModel(BaseModel):
    """
    Financial aid information.
    
    COMPLIANCE: PCI-DSS and FERPA requirements
    ON-PREMISE: Stored in secure financial systems
    ESB: Data masked/transformed before cloud transmission
    """
    status: str
    amount: float
    disbursement_date: str


class HousingModel(BaseModel):
    """Student housing assignment."""
    building: str
    room: str
    move_in_date: str


class StudentModel(BaseModel):
    """
    Unified Student Profile - Aggregated from all systems.
    
    ╔═══════════════════════════════════════════════════════════════╗
    ║  DATA SOURCE MAPPING                                          ║
    ╠═══════════════════════════════════════════════════════════════╣
    ║  Field          │ Source System    │ Location                ║
    ╠═══════════════════════════════════════════════════════════════╣
    ║  id, name       │ Admissions       │ ON-PREMISE              ║
    ║  email          │ Directory Svcs   │ ON-PREMISE (LDAP/AD)    ║
    ║  program, year  │ Academic Records │ ON-PREMISE              ║
    ║  gpa, courses   │ Registrar        │ ON-PREMISE              ║
    ║  financial_aid  │ Financial Aid    │ ON-PREMISE (Secure)     ║
    ║  housing        │ Housing System   │ ON-PREMISE              ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    id: str
    name: str
    email: EmailStr
    program: str
    year: int
    gpa: float
    financial_aid: FinancialAidModel
    courses: List[CourseModel]
    housing: HousingModel


# ================================================================================
# CHAT/QUERY MODELS
# ================================================================================

class MessageRole(str, Enum):
    """Chat message role identifier."""
    USER = "user"
    ASSISTANT = "assistant"


class ChatMessage(BaseModel):
    """Individual chat message."""
    role: MessageRole
    content: str
    timestamp: datetime = datetime.now()


class QueryRequest(BaseModel):
    """
    Incoming chat query request.
    
    EXAMPLE REQUEST:
    {
        "student_id": "STU2024001",
        "message": "When is my next financial aid disbursement?",
        "history": [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi! How can I help?"}
        ]
    }
    """
    student_id: str
    message: str
    history: Optional[List[Dict[str, str]]] = None


class QueryResponse(BaseModel):
    """
    AI-generated response to student query.
    
    FIELDS:
    - text: The response message
    - category: Classified intent category
    - confidence: AI confidence score (0-1)
    - automated: True if handled by AI, False if escalated
    - sources: Knowledge base sources used
    - timestamp: Response generation time
    
    PRODUCTION ADDITIONS:
    - trace_id: For distributed tracing
    - model_version: AI model used
    - latency_ms: Processing time
    """
    text: str
    category: str
    confidence: float
    automated: bool
    timestamp: datetime = datetime.now()
    sources: List[str] = []


# ================================================================================
# ANALYTICS MODELS
# ================================================================================

class AnalyticsMetrics(BaseModel):
    """
    System analytics and KPI metrics.
    
    BUSINESS VALUE:
    - ROI calculation for AI investment
    - Workload reduction quantification
    - Student satisfaction tracking
    - System health monitoring
    
    PRODUCTION:
    - Aggregated from Azure Data Factory
    - Stored in Snowflake data warehouse
    - Visualized in Power BI dashboards
    """
    total_queries: int
    automated_resolution: float  # Percentage
    avg_response_time: float  # Seconds
    satisfaction_score: float  # Percentage
    active_users: int
    queries_last_24h: int
    top_categories: List[Dict[str, Any]]
    system_health: Dict[str, Any]
    roi_metrics: Dict[str, Any]


# ================================================================================
# ESB INTEGRATION MODELS
# ================================================================================

class SystemStatus(BaseModel):
    """Status of an integrated legacy system."""
    name: str
    status: str  # operational, degraded, offline
    location: str  # cloud, on-premise
    last_sync: Optional[datetime] = None


class ESBStatus(BaseModel):
    """
    Enterprise Service Bus integration status.
    
    DEMONSTRATES:
    - Connected legacy systems
    - Data flow health
    - Integration patterns
    """
    esb_status: str
    connected_systems: List[Dict[str, Any]]
    message_flow: Dict[str, Any]

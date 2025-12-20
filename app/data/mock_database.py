"""
================================================================================
MOCK DATABASE - Unified Data Layer
================================================================================

PURPOSE:
This module provides a unified view of data aggregated from multiple legacy
systems. In production, this would be the caching/data aggregation layer
that sits between the API and the ESB.

ARCHITECTURE:
                    ┌─────────────────────┐
                    │    API Layer        │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   Mock Database     │  ◄── You are here (Caching Layer)
                    │   (Data Cache)      │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │    ESB Service      │
                    └──────────┬──────────┘
                               │
        ┌──────────┬──────────┴──────────┬──────────┐
        │          │                     │          │
   ┌────▼────┐ ┌───▼────┐ ┌─────────▼────┐ ┌───▼────┐
   │Admissions│ │Academic│ │  Financial   │ │Housing │
   │ System   │ │Records │ │     Aid      │ │ System │
   └──────────┘ └────────┘ └──────────────┘ └────────┘
            [ON-PREMISE LEGACY SYSTEMS]

================================================================================
"""

from datetime import datetime
from typing import Dict, List, Optional
import hashlib

# Import legacy system connectors
from app.data.legacy_systems import (
    admissions_system,
    academic_system,
    financial_system,
    housing_system,
    directory_services,
    get_all_legacy_systems
)

# Simple password hashing for MVP (no external dependencies)
def simple_hash(password: str) -> str:
    """Simple SHA-256 hash for MVP demo. NOT for production use."""
    return hashlib.sha256(password.encode()).hexdigest()

def simple_verify(password: str, hashed: str) -> bool:
    """Verify password against simple hash."""
    return simple_hash(password) == hashed


class MockDatabase:
    """
    In-memory mock database simulating multiple legacy systems.
    
    ARCHITECTURE NOTE:
    In production, each data source below would be a separate system
    accessed via ESB (Enterprise Service Bus) integration.
    
    ╔════════════════════════════════════════════════════════════════╗
    ║  MOCK DATA SOURCES (What they simulate)                        ║
    ╠════════════════════════════════════════════════════════════════╣
    ║  self.students     → Banner/Admissions DB (ON-PREMISE)        ║
    ║  self.users        → Active Directory/LDAP (ON-PREMISE)       ║
    ║  self.query_log    → Analytics DB (CLOUD - Azure Cosmos)      ║
    ║  self.knowledge_base → CMS/Vector DB (CLOUD)                  ║
    ╚════════════════════════════════════════════════════════════════╝
    """
    
    def __init__(self):
        """Initialize all mock data stores."""
        self._init_students()
        self._init_users()
        self._init_knowledge_base()
        self.query_log: List[Dict] = []
    
    def _init_students(self):
        """
        Initialize student data.
        
        SIMULATES: Aggregated view from multiple legacy systems
        PRODUCTION: ESB would call each system and merge results
        """
        self.students: Dict[str, Dict] = {
            # Primary demo student
            "STU2024001": {
                "id": "STU2024001",
                "name": "Sarah Johnson",
                "email": "sarah.johnson@techedu.edu",
                "program": "Computer Science",
                "year": 3,
                "gpa": 3.7,
                # From Financial Aid System (ON-PREMISE)
                "financial_aid": {
                    "status": "Active",
                    "amount": 15000,
                    "disbursement_date": "2025-01-15"
                },
                # From Academic Records System (ON-PREMISE)
                "courses": [
                    {
                        "code": "CS301",
                        "name": "Data Structures",
                        "credits": 4,
                        "grade": "A"
                    },
                    {
                        "code": "CS302",
                        "name": "Algorithms",
                        "credits": 4,
                        "grade": "A-"
                    },
                    {
                        "code": "MATH301",
                        "name": "Linear Algebra",
                        "credits": 3,
                        "grade": "B+"
                    }
                ],
                # From Housing System (ON-PREMISE)
                "housing": {
                    "building": "West Hall",
                    "room": "204B",
                    "move_in_date": "2024-08-15"
                }
            },
            # Additional demo students for testing
            "STU2024002": {
                "id": "STU2024002",
                "name": "Michael Chen",
                "email": "michael.chen@techedu.edu",
                "program": "Data Science",
                "year": 2,
                "gpa": 3.5,
                "financial_aid": {
                    "status": "Pending Review",
                    "amount": 12000,
                    "disbursement_date": "2025-02-01"
                },
                "courses": [
                    {
                        "code": "DS201",
                        "name": "Statistics for Data Science",
                        "credits": 4,
                        "grade": "A"
                    },
                    {
                        "code": "CS201",
                        "name": "Python Programming",
                        "credits": 3,
                        "grade": "A"
                    }
                ],
                "housing": {
                    "building": "North Tower",
                    "room": "512A",
                    "move_in_date": "2024-08-20"
                }
            },
            "STU2024003": {
                "id": "STU2024003",
                "name": "Emily Rodriguez",
                "email": "emily.rodriguez@techedu.edu",
                "program": "Business Administration",
                "year": 4,
                "gpa": 3.9,
                "financial_aid": {
                    "status": "Active",
                    "amount": 18000,
                    "disbursement_date": "2025-01-10"
                },
                "courses": [
                    {
                        "code": "BUS401",
                        "name": "Strategic Management",
                        "credits": 3,
                        "grade": "A"
                    },
                    {
                        "code": "BUS402",
                        "name": "Corporate Finance",
                        "credits": 3,
                        "grade": "A-"
                    }
                ],
                "housing": {
                    "building": "Graduate Commons",
                    "room": "301",
                    "move_in_date": "2024-08-10"
                }
            }
        }
    
    def _init_users(self):
        """
        Initialize authentication users with roles.
        
        SIMULATES: Active Directory / LDAP user store
        PRODUCTION: Azure AD / Okta integration via SAML/OAuth
        
        ROLES:
        - student: Can view own data, use chat
        - staff: Can view student data, manage tickets
        - admin: Full system access, user management
        
        NOTE: Password "demo123" is pre-hashed for all demo users
        """
        self.users: Dict[str, Dict] = {
            # Student Users
            "sarah.johnson@techedu.edu": {
                "username": "sarah.johnson@techedu.edu",
                "hashed_password": simple_hash("demo123"),
                "student_id": "STU2024001",
                "role": "student",
                "name": "Sarah Johnson",
                "department": None,
                "created_at": "2024-08-01T00:00:00",
                "last_login": "2025-01-15T10:30:00",
                "is_active": True
            },
            "michael.chen@techedu.edu": {
                "username": "michael.chen@techedu.edu",
                "hashed_password": simple_hash("demo123"),
                "student_id": "STU2024002",
                "role": "student",
                "name": "Michael Chen",
                "department": None,
                "created_at": "2024-08-15T00:00:00",
                "last_login": "2025-01-14T14:20:00",
                "is_active": True
            },
            "emily.rodriguez@techedu.edu": {
                "username": "emily.rodriguez@techedu.edu",
                "hashed_password": simple_hash("demo123"),
                "student_id": "STU2024003",
                "role": "student",
                "name": "Emily Rodriguez",
                "department": None,
                "created_at": "2024-08-10T00:00:00",
                "last_login": "2025-01-13T09:15:00",
                "is_active": True
            },
            # Staff Users
            "advisor.smith@techedu.edu": {
                "username": "advisor.smith@techedu.edu",
                "hashed_password": simple_hash("staff123"),
                "student_id": None,
                "role": "staff",
                "name": "Dr. James Smith",
                "department": "Academic Advising",
                "created_at": "2023-01-15T00:00:00",
                "last_login": "2025-01-15T08:00:00",
                "is_active": True
            },
            "finaid.jones@techedu.edu": {
                "username": "finaid.jones@techedu.edu",
                "hashed_password": simple_hash("staff123"),
                "student_id": None,
                "role": "staff",
                "name": "Maria Jones",
                "department": "Financial Aid Office",
                "created_at": "2022-06-01T00:00:00",
                "last_login": "2025-01-15T09:30:00",
                "is_active": True
            },
            # Admin Users
            "admin@techedu.edu": {
                "username": "admin@techedu.edu",
                "hashed_password": simple_hash("admin123"),
                "student_id": None,
                "role": "admin",
                "name": "System Administrator",
                "department": "IT Services",
                "created_at": "2021-01-01T00:00:00",
                "last_login": "2025-01-15T07:00:00",
                "is_active": True
            },
            "director@techedu.edu": {
                "username": "director@techedu.edu",
                "hashed_password": simple_hash("admin123"),
                "student_id": None,
                "role": "admin",
                "name": "Dr. Patricia Wilson",
                "department": "Student Services",
                "created_at": "2020-08-15T00:00:00",
                "last_login": "2025-01-14T16:45:00",
                "is_active": True
            }
        }
    
    def _init_knowledge_base(self):
        """
        Initialize FAQ/Knowledge Base content.
        
        SIMULATES: CMS content + Vector database for semantic search
        
        PRODUCTION ARCHITECTURE:
        - Content stored in Contentful/SharePoint (CLOUD)
        - Embeddings generated via Azure OpenAI
        - Vector search via Pinecone/Azure Cognitive Search
        - Real-time sync from content updates
        
        MVP: Simple keyword matching against this data
        """
        self.knowledge_base: List[Dict] = [
            {
                "category": "admissions",
                "keywords": ["admission", "apply", "application", "deadline", "requirements", "transfer", "enrolled"],
                "responses": [
                    "Hi {first_name}! 🎓 You were admitted as a {year}-year student in {program}.\n\n📅 **Application Deadlines (for referrals):**\n• Fall Semester: March 1\n• Spring Semester: October 1\n• Summer Session: March 1\n\n📋 **Requirements:** High school transcript, SAT/ACT scores, two recommendation letters, and personal essay.",
                    "Welcome back, {first_name}! 📚 You're currently enrolled in {program} (Year {year}).\n\nThe average GPA for admitted students is 3.5. We use holistic review considering academics, extracurriculars, and essays.",
                    "Hi {first_name}! For transfer students, we require a minimum 2.5 GPA and transcripts from all institutions. Contact admissions@techedu.edu for more info."
                ]
            },
            {
                "category": "financial_aid",
                "keywords": ["financial aid", "scholarship", "loan", "fafsa", "tuition", "payment", "cost", "fee", "money", "pay", "grant", "disbursement"],
                "responses": [
                    "Hi {first_name}! 💰 Here's your **Financial Aid Summary:**\n\n📊 **Aid Package ({aid_status}):**\n• 🎁 Grants: {grants_total}\n• 🏆 Scholarships: {scholarships_total}\n• 📝 Loans: {loans_total}\n• **Total Aid: {total_aid}**\n\n💳 **Balance Due: {remaining_balance}**\n📅 **Next Disbursement: {next_disbursement}**\n\nNeed more aid? Complete FAFSA by March 1 at financialaid.techedu.edu",
                    "Your financial aid status: **{aid_status}** ✅\n\n📈 **Cost Breakdown:**\n• Total Cost of Attendance: {cost_of_attendance}\n• Your Financial Need: {financial_need}\n• Aid Awarded: {total_aid}\n• Remaining Balance: {remaining_balance}\n\n💵 Next disbursement ({next_disbursement}) will be applied directly to your student account.",
                    "Payment plans are available, {first_name}! Contact the Bursar's Office at bursar@techedu.edu.\n\nYour current balance is {remaining_balance} after {total_aid} in financial aid."
                ]
            },
            {
                "category": "registration",
                "keywords": ["register", "enroll", "course", "class", "schedule", "drop", "add", "waitlist", "credit", "semester"],
                "responses": [
                    "Hi {first_name}! 📚 **Your Current Enrollment:**\n\n📅 Semester: {semester}\n📖 Courses: {courseCount} enrolled\n📊 Credits in Progress: {credits_in_progress}\n✅ Credits Completed: {credits_completed}\n\n**Registration Opens:**\n• Seniors: Nov 1\n• Juniors: Nov 8\n• Sophomores: Nov 15\n• Freshmen: Nov 22",
                    "To add/drop courses, go to Student Portal > Academic Records > Registration.\n\n⚠️ **Important:** Drop deadline is end of Week 2.\n📊 Maximum load: 18 credits (overload needs advisor approval)\n\nYou currently have {credits_in_progress} credits in progress.",
                    "Hey {first_name}! You're enrolled in {courseCount} courses this semester ({credits_in_progress} credits).\n\nFor waitlist questions, contact your department advisor or visit registration.techedu.edu."
                ]
            },
            {
                "category": "grades",
                "keywords": ["grade", "gpa", "transcript", "academic record", "score", "exam", "final", "dean", "standing"],
                "responses": [
                    "Hi {first_name}! 📊 **Your Academic Record:**\n\n🎯 **Cumulative GPA: {gpa}**\n📈 Semester GPA: {gpa_semester}\n✅ Credits Completed: {credits_completed}\n📚 Current Courses: {courseCount}\n\n🏆 Academic Standing: {academic_standing}\n⭐ Dean's List: {dean_list}\n\nOfficial transcripts: registrar.techedu.edu (3-5 business days)",
                    "Great news, {first_name}! Your GPA is **{gpa}** 🎉\n\n📋 **This Semester:**\n• Semester GPA: {gpa_semester}\n• Courses: {courseCount}\n• Credits: {credits_in_progress}\n\n📍 Academic Standing: {academic_standing}\n\nGrades posted within 72 hours after finals.",
                    "For grade appeals, submit within 30 days to Academic Affairs.\n\nYour current record:\n• GPA: {gpa}\n• Standing: {academic_standing}\n• Dean's List: {dean_list}"
                ]
            },
            {
                "category": "housing",
                "keywords": ["housing", "dorm", "residence", "room", "roommate", "apartment", "move", "meal", "dining", "food"],
                "responses": [
                    "Hi {first_name}! 🏠 **Your Housing Assignment:**\n\n📍 **Location:** {building}, Room {room}\n🛏️ Room Type: {room_type} (Floor {floor})\n📅 Move-in: {move_in_date}\n📅 Move-out: {move_out_date}\n\n🍽️ **Meal Plan: {meal_plan}**\n• Meals/Week: {meals_per_week}\n• Flex $ Remaining: {flex_remaining}\n\nFor maintenance: housing.techedu.edu or call (555) 123-4567",
                    "You're in **{building}**, Room **{room}** ({room_type})! 🏠\n\n🍽️ Meal Plan: {meal_plan}\n💵 Flex Balance: {flex_remaining}\n\nRoom changes can be requested in the first 2 weeks of semester.",
                    "Housing applications for next year open February 1.\n\nYour current assignment:\n• {building}, Room {room}\n• Move-out date: {move_out_date}\n\nPriority given to returning students who apply early!"
                ]
            },
            {
                "category": "support",
                "keywords": ["help", "support", "counseling", "health", "wellness", "emergency", "safety"],
                "responses": [
                    "Hi {first_name}! 💙 **Support Services Available:**\n\n🏢 Student Support: Student Center, Room 200 (M-F 8am-6pm)\n🧠 Counseling: (555) 123-4568 or counseling.techedu.edu\n🚨 Campus Emergency: (555) 123-4569\n🏥 Health Services: Health Center (M-F 8am-5pm)\n\nYou're not alone - we're here to help!",
                    "For mental health support, contact the Counseling Center at (555) 123-4568.\n\n24/7 Crisis Line: (555) 999-HELP\n\nYour wellbeing matters, {first_name}! 💚",
                    "Campus Safety: Use the SafeWalk app or call (555) 123-4569.\n\nHealth Services hours: M-F 8am-5pm\nAfter-hours urgent care info: techedu.edu/health"
                ]
            },
            {
                "category": "career",
                "keywords": ["career", "job", "internship", "resume", "interview", "employer", "hire", "work"],
                "responses": [
                    "Hi {first_name}! 💼 **Career Services for {program} Students:**\n\n📝 Resume Reviews: Book at careers.techedu.edu\n🎤 Mock Interviews: Available weekly\n💼 Job Board: Check Handshake for {program}-related positions\n\n📅 **Next Career Fair:** Spring Career Expo - February 15\n\nYour {gpa} GPA will look great to employers!",
                    "The Career Center is here to help, {first_name}!\n\n• Resume workshops every Tuesday\n• {program} industry networking events monthly\n• 1-on-1 career counseling available\n\nCall (555) 123-4570 or visit careers.techedu.edu",
                    "Looking for internships in {program}? Check Handshake!\n\nWith your {gpa} GPA and {credits_completed} credits completed, you're well-positioned for competitive opportunities."
                ]
            },
            {
                "category": "library",
                "keywords": ["library", "book", "research", "study", "borrow", "return", "fine", "overdue"],
                "responses": [
                    "Hi {first_name}! 📚 **Your Library Account:**\n\n📖 Books Checked Out: {library_items}\n⚠️ Overdue Items: {library_overdue}\n💰 Fines Owed: {library_fines}\n\n🕐 Library Hours: M-Th 7am-12am, F 7am-9pm, Sat-Sun 10am-10pm\n\nRenew books online at library.techedu.edu",
                    "Need research help for {program}? Visit the Research Help Desk on the 2nd floor.\n\nYour account: {library_items} items checked out, {library_fines} in fines.",
                    "Study rooms can be booked at library.techedu.edu/rooms (2-hour max).\n\n📚 Your library status: {library_items} books out, {library_overdue} overdue."
                ]
            }
        ]
    
    def get_student(self, student_id: str) -> Optional[Dict]:
        """Get student by ID."""
        return self.students.get(student_id)
    
    def get_user(self, username: str) -> Optional[Dict]:
        """Get user by username/email."""
        return self.users.get(username)
    
    def log_query(self, log_entry: Dict):
        """Add entry to query log."""
        self.query_log.append(log_entry)
    
    def get_query_log(self, limit: int = 50) -> List[Dict]:
        """Get recent query log entries."""
        return self.query_log[-limit:] if self.query_log else []

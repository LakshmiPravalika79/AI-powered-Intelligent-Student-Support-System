"""
================================================================================
LEGACY SYSTEMS SIMULATION - On-Premise System Connectors
================================================================================

This module simulates the ON-PREMISE legacy systems that exist in a typical
university IT infrastructure. In production, each class would be a real
connector to the actual legacy system via ESB.

ARCHITECTURE:
============

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                    ON-PREMISE DATA CENTER                                │
    ├─────────────────────────────────────────────────────────────────────────┤
    │                                                                          │
    │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐      │
    │  │   ADMISSIONS     │  │    ACADEMIC      │  │   FINANCIAL      │      │
    │  │    SYSTEM        │  │    RECORDS       │  │      AID         │      │
    │  │                  │  │                  │  │                  │      │
    │  │  Vendor: Banner  │  │ Vendor: PeopleSoft│ │ Vendor: PowerFAIDS│     │
    │  │  Protocol: SOAP  │  │  Protocol: JDBC  │  │  Protocol: REST  │      │
    │  │  Port: 8443      │  │  Port: 1521      │  │  Port: 443       │      │
    │  └──────────────────┘  └──────────────────┘  └──────────────────┘      │
    │                                                                          │
    │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐      │
    │  │    HOUSING       │  │    DIRECTORY     │  │    LIBRARY       │      │
    │  │    SYSTEM        │  │    SERVICES      │  │    SYSTEM        │      │
    │  │                  │  │                  │  │                  │      │
    │  │  Vendor: StarRez │  │  Vendor: MS AD   │  │  Vendor: Ex Libris│     │
    │  │  Protocol: REST  │  │  Protocol: LDAP  │  │  Protocol: REST  │      │
    │  │  Port: 443       │  │  Port: 636       │  │  Port: 443       │      │
    │  └──────────────────┘  └──────────────────┘  └──────────────────┘      │
    │                                                                          │
    └─────────────────────────────────────────────────────────────────────────┘

WHY ON-PREMISE?
===============
These systems remain on-premise due to:
- FERPA compliance (student educational records)
- PCI-DSS compliance (financial data)
- State data residency laws
- Legacy system limitations (no cloud support)
- Institutional security policies

PRODUCTION IMPLEMENTATION:
=========================
Each connector class would:
1. Establish secure connection to legacy system
2. Handle authentication (service accounts, certificates)
3. Transform data formats (XML→JSON, etc.)
4. Implement retry logic and circuit breakers
5. Cache responses for performance
6. Log all transactions for audit
================================================================================
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import random


class AdmissionsSystem:
    """
    BANNER/ELLUCIAN ADMISSIONS SYSTEM CONNECTOR
    
    Location: ON-PREMISE
    Protocol: SOAP/XML over HTTPS
    Port: 8443
    Authentication: X.509 Certificate + Service Account
    
    Data Owned:
    - Student biographical data
    - Application status
    - Admission decisions
    - Enrollment status
    
    Compliance: FERPA
    """
    
    SYSTEM_INFO = {
        "name": "Student Admissions System",
        "vendor": "Ellucian Banner",
        "version": "9.17",
        "protocol": "SOAP/XML",
        "location": "on-premise",
        "datacenter": "Main Campus DC-1",
        "port": 8443,
        "status": "operational",
        "compliance": ["FERPA"],
        "data_classification": "Confidential"
    }
    
    def __init__(self):
        # Mock data store - in production, this connects to Banner DB
        self._students = {
            "STU2024001": {
                "student_id": "STU2024001",
                "first_name": "Sarah",
                "last_name": "Johnson",
                "email": "sarah.johnson@techedu.edu",
                "date_of_birth": "2003-05-15",
                "admission_date": "2022-08-01",
                "admission_type": "Freshman",
                "status": "Active",
                "program_code": "CS-BS",
                "program_name": "Computer Science",
                "expected_graduation": "2026-05"
            },
            "STU2024002": {
                "student_id": "STU2024002",
                "first_name": "Michael",
                "last_name": "Chen",
                "email": "michael.chen@techedu.edu",
                "date_of_birth": "2004-02-20",
                "admission_date": "2023-08-01",
                "admission_type": "Freshman",
                "status": "Active",
                "program_code": "DS-BS",
                "program_name": "Data Science",
                "expected_graduation": "2027-05"
            },
            "STU2024003": {
                "student_id": "STU2024003",
                "first_name": "Emily",
                "last_name": "Rodriguez",
                "email": "emily.rodriguez@techedu.edu",
                "date_of_birth": "2002-11-08",
                "admission_date": "2021-08-01",
                "admission_type": "Transfer",
                "status": "Active",
                "program_code": "BA-BS",
                "program_name": "Business Administration",
                "expected_graduation": "2025-05"
            }
        }
    
    def get_student(self, student_id: str) -> Optional[Dict]:
        """
        Retrieve student record from Banner.
        
        PRODUCTION: Would execute SOAP call:
        <soapenv:Envelope>
            <soapenv:Body>
                <ban:GetStudentRequest>
                    <ban:StudentId>{student_id}</ban:StudentId>
                </ban:GetStudentRequest>
            </soapenv:Body>
        </soapenv:Envelope>
        """
        return self._students.get(student_id)
    
    def get_all_students(self) -> List[Dict]:
        """Get all student records."""
        return list(self._students.values())
    
    def search_students(self, query: str) -> List[Dict]:
        """Search students by name or email."""
        query_lower = query.lower()
        results = []
        for student in self._students.values():
            if (query_lower in student["first_name"].lower() or
                query_lower in student["last_name"].lower() or
                query_lower in student["email"].lower()):
                results.append(student)
        return results


class AcademicRecordsSystem:
    """
    PEOPLESOFT ACADEMIC RECORDS SYSTEM CONNECTOR
    
    Location: ON-PREMISE
    Protocol: JDBC/SQL
    Port: 1521 (Oracle)
    Authentication: Database Service Account
    
    Data Owned:
    - Course enrollments
    - Grades and GPA
    - Academic standing
    - Degree progress
    - Transcripts
    
    Compliance: FERPA
    """
    
    SYSTEM_INFO = {
        "name": "Academic Records System",
        "vendor": "Oracle PeopleSoft Campus Solutions",
        "version": "9.2",
        "protocol": "JDBC/SQL",
        "location": "on-premise",
        "datacenter": "Main Campus DC-1",
        "port": 1521,
        "database": "Oracle 19c",
        "status": "operational",
        "compliance": ["FERPA"],
        "data_classification": "Confidential"
    }
    
    def __init__(self):
        self._records = {
            "STU2024001": {
                "student_id": "STU2024001",
                "academic_year": "2024-2025",
                "semester": "Fall 2024",
                "year_level": 3,
                "gpa_cumulative": 3.7,
                "gpa_semester": 3.8,
                "credits_completed": 75,
                "credits_in_progress": 15,
                "academic_standing": "Good Standing",
                "dean_list": True,
                "courses": [
                    {"code": "CS301", "name": "Data Structures", "credits": 4, "grade": "A", "status": "Completed"},
                    {"code": "CS302", "name": "Algorithms", "credits": 4, "grade": "A-", "status": "Completed"},
                    {"code": "MATH301", "name": "Linear Algebra", "credits": 3, "grade": "B+", "status": "Completed"},
                    {"code": "CS350", "name": "Software Engineering", "credits": 3, "grade": None, "status": "In Progress"},
                    {"code": "CS360", "name": "Database Systems", "credits": 3, "grade": None, "status": "In Progress"}
                ]
            },
            "STU2024002": {
                "student_id": "STU2024002",
                "academic_year": "2024-2025",
                "semester": "Fall 2024",
                "year_level": 2,
                "gpa_cumulative": 3.5,
                "gpa_semester": 3.6,
                "credits_completed": 45,
                "credits_in_progress": 16,
                "academic_standing": "Good Standing",
                "dean_list": False,
                "courses": [
                    {"code": "DS201", "name": "Statistics for Data Science", "credits": 4, "grade": "A", "status": "Completed"},
                    {"code": "CS201", "name": "Python Programming", "credits": 3, "grade": "A", "status": "Completed"},
                    {"code": "DS250", "name": "Machine Learning Basics", "credits": 4, "grade": None, "status": "In Progress"}
                ]
            },
            "STU2024003": {
                "student_id": "STU2024003",
                "academic_year": "2024-2025",
                "semester": "Fall 2024",
                "year_level": 4,
                "gpa_cumulative": 3.9,
                "gpa_semester": 4.0,
                "credits_completed": 105,
                "credits_in_progress": 12,
                "academic_standing": "Good Standing",
                "dean_list": True,
                "courses": [
                    {"code": "BUS401", "name": "Strategic Management", "credits": 3, "grade": "A", "status": "Completed"},
                    {"code": "BUS402", "name": "Corporate Finance", "credits": 3, "grade": "A-", "status": "Completed"},
                    {"code": "BUS450", "name": "Business Capstone", "credits": 4, "grade": None, "status": "In Progress"}
                ]
            }
        }
    
    def get_academic_record(self, student_id: str) -> Optional[Dict]:
        """
        Retrieve academic record.
        
        PRODUCTION: Would execute SQL:
        SELECT * FROM PS_STDNT_ACAD_REC 
        WHERE EMPLID = :student_id
        """
        return self._records.get(student_id)
    
    def get_transcript(self, student_id: str) -> Optional[Dict]:
        """Get official transcript data."""
        record = self._records.get(student_id)
        if record:
            return {
                "student_id": student_id,
                "courses": record["courses"],
                "gpa": record["gpa_cumulative"],
                "generated_at": datetime.now().isoformat()
            }
        return None


class FinancialAidSystem:
    """
    POWERFAIDS FINANCIAL AID SYSTEM CONNECTOR
    
    Location: ON-PREMISE (Secure Zone)
    Protocol: REST/JSON over HTTPS
    Port: 443
    Authentication: OAuth2 Client Credentials
    
    Data Owned:
    - Financial aid packages
    - Scholarships
    - Loans
    - Disbursements
    - FAFSA data
    
    Compliance: FERPA, PCI-DSS, GLBA
    """
    
    SYSTEM_INFO = {
        "name": "Financial Aid Management",
        "vendor": "Ellucian PowerFAIDS",
        "version": "27.0",
        "protocol": "REST/JSON",
        "location": "on-premise",
        "datacenter": "Secure Zone DC-2",
        "port": 443,
        "status": "operational",
        "compliance": ["FERPA", "PCI-DSS", "GLBA"],
        "data_classification": "Highly Confidential"
    }
    
    def __init__(self):
        self._financial_aid = {
            "STU2024001": {
                "student_id": "STU2024001",
                "aid_year": "2024-2025",
                "status": "Active",
                "total_cost_of_attendance": 52000,
                "expected_family_contribution": 12000,
                "financial_need": 40000,
                "package": {
                    "grants": [
                        {"name": "Federal Pell Grant", "amount": 7395, "status": "Awarded"},
                        {"name": "State Grant", "amount": 3000, "status": "Awarded"},
                        {"name": "Institutional Grant", "amount": 4605, "status": "Awarded"}
                    ],
                    "scholarships": [
                        {"name": "Merit Scholarship", "amount": 5000, "status": "Awarded"},
                        {"name": "CS Department Award", "amount": 2000, "status": "Awarded"}
                    ],
                    "loans": [
                        {"name": "Federal Direct Subsidized", "amount": 3500, "status": "Accepted"},
                        {"name": "Federal Direct Unsubsidized", "amount": 2000, "status": "Accepted"}
                    ],
                    "work_study": {"amount": 2500, "status": "Eligible"}
                },
                "total_aid": 30000,
                "remaining_balance": 10000,
                "disbursements": [
                    {"date": "2024-08-15", "amount": 15000, "status": "Completed"},
                    {"date": "2025-01-15", "amount": 15000, "status": "Scheduled"}
                ],
                "next_disbursement": "2025-01-15",
                "satisfactory_academic_progress": True
            },
            "STU2024002": {
                "student_id": "STU2024002",
                "aid_year": "2024-2025",
                "status": "Pending Review",
                "total_cost_of_attendance": 52000,
                "expected_family_contribution": 18000,
                "financial_need": 34000,
                "package": {
                    "grants": [
                        {"name": "Federal Pell Grant", "amount": 5000, "status": "Awarded"}
                    ],
                    "scholarships": [
                        {"name": "Data Science Scholarship", "amount": 7000, "status": "Awarded"}
                    ],
                    "loans": [
                        {"name": "Federal Direct Subsidized", "amount": 3500, "status": "Pending"}
                    ],
                    "work_study": {"amount": 0, "status": "Not Eligible"}
                },
                "total_aid": 15500,
                "remaining_balance": 18500,
                "disbursements": [
                    {"date": "2024-08-20", "amount": 6000, "status": "Completed"},
                    {"date": "2025-02-01", "amount": 6000, "status": "Scheduled"}
                ],
                "next_disbursement": "2025-02-01",
                "satisfactory_academic_progress": True
            },
            "STU2024003": {
                "student_id": "STU2024003",
                "aid_year": "2024-2025",
                "status": "Active",
                "total_cost_of_attendance": 52000,
                "expected_family_contribution": 8000,
                "financial_need": 44000,
                "package": {
                    "grants": [
                        {"name": "Federal Pell Grant", "amount": 7395, "status": "Awarded"},
                        {"name": "State Grant", "amount": 4000, "status": "Awarded"},
                        {"name": "Institutional Grant", "amount": 6605, "status": "Awarded"}
                    ],
                    "scholarships": [
                        {"name": "Dean's Scholarship", "amount": 8000, "status": "Awarded"},
                        {"name": "Business Excellence Award", "amount": 3000, "status": "Awarded"}
                    ],
                    "loans": [],
                    "work_study": {"amount": 3000, "status": "Active"}
                },
                "total_aid": 32000,
                "remaining_balance": 12000,
                "disbursements": [
                    {"date": "2024-08-10", "amount": 18000, "status": "Completed"},
                    {"date": "2025-01-10", "amount": 14000, "status": "Scheduled"}
                ],
                "next_disbursement": "2025-01-10",
                "satisfactory_academic_progress": True
            }
        }
    
    def get_financial_aid(self, student_id: str) -> Optional[Dict]:
        """
        Retrieve financial aid package.
        
        PRODUCTION: Would call REST API:
        GET /api/v1/students/{student_id}/financial-aid
        Authorization: Bearer {oauth_token}
        """
        return self._financial_aid.get(student_id)
    
    def get_disbursement_schedule(self, student_id: str) -> List[Dict]:
        """Get disbursement schedule for student."""
        aid = self._financial_aid.get(student_id)
        if aid:
            return aid.get("disbursements", [])
        return []


class HousingSystem:
    """
    STARREZ HOUSING SYSTEM CONNECTOR
    
    Location: ON-PREMISE
    Protocol: REST/JSON
    Port: 443
    Authentication: API Key + HMAC
    
    Data Owned:
    - Room assignments
    - Building information
    - Meal plans
    - Roommate matching
    - Maintenance requests
    
    Compliance: Institutional Policy
    """
    
    SYSTEM_INFO = {
        "name": "Housing Management System",
        "vendor": "StarRez",
        "version": "8.5",
        "protocol": "REST/JSON",
        "location": "on-premise",
        "datacenter": "Main Campus DC-1",
        "port": 443,
        "status": "operational",
        "compliance": ["Institutional Policy"],
        "data_classification": "Internal"
    }
    
    def __init__(self):
        self._housing = {
            "STU2024001": {
                "student_id": "STU2024001",
                "assignment_status": "Assigned",
                "building": "West Hall",
                "building_code": "WH",
                "room_number": "204B",
                "room_type": "Double",
                "floor": 2,
                "bed_space": "B",
                "roommate_id": "STU2024050",
                "move_in_date": "2024-08-15",
                "move_out_date": "2025-05-15",
                "meal_plan": {
                    "name": "Gold Plan",
                    "meals_per_week": 14,
                    "flex_dollars": 200,
                    "flex_remaining": 145
                },
                "access_card": "AC-2024-0892",
                "parking_permit": None
            },
            "STU2024002": {
                "student_id": "STU2024002",
                "assignment_status": "Assigned",
                "building": "North Tower",
                "building_code": "NT",
                "room_number": "512A",
                "room_type": "Single",
                "floor": 5,
                "bed_space": "A",
                "roommate_id": None,
                "move_in_date": "2024-08-20",
                "move_out_date": "2025-05-15",
                "meal_plan": {
                    "name": "Silver Plan",
                    "meals_per_week": 10,
                    "flex_dollars": 150,
                    "flex_remaining": 98
                },
                "access_card": "AC-2024-1205",
                "parking_permit": "P-2024-0456"
            },
            "STU2024003": {
                "student_id": "STU2024003",
                "assignment_status": "Assigned",
                "building": "Graduate Commons",
                "building_code": "GC",
                "room_number": "301",
                "room_type": "Studio",
                "floor": 3,
                "bed_space": "A",
                "roommate_id": None,
                "move_in_date": "2024-08-10",
                "move_out_date": "2025-05-20",
                "meal_plan": {
                    "name": "Flex Only",
                    "meals_per_week": 0,
                    "flex_dollars": 500,
                    "flex_remaining": 320
                },
                "access_card": "AC-2024-0654",
                "parking_permit": "P-2024-0123"
            }
        }
    
    def get_housing(self, student_id: str) -> Optional[Dict]:
        """
        Retrieve housing assignment.
        
        PRODUCTION: Would call REST API:
        GET /api/housing/assignments/{student_id}
        X-API-Key: {api_key}
        X-Signature: {hmac_signature}
        """
        return self._housing.get(student_id)


class DirectoryServices:
    """
    MICROSOFT ACTIVE DIRECTORY CONNECTOR
    
    Location: ON-PREMISE
    Protocol: LDAPS
    Port: 636
    Authentication: Service Account (Kerberos)
    
    Data Owned:
    - User accounts
    - Authentication
    - Group memberships
    - Email addresses
    
    Compliance: Institutional Security Policy
    """
    
    SYSTEM_INFO = {
        "name": "Directory Services",
        "vendor": "Microsoft Active Directory",
        "version": "Windows Server 2022",
        "protocol": "LDAPS",
        "location": "on-premise",
        "datacenter": "Main Campus DC-1",
        "port": 636,
        "status": "operational",
        "compliance": ["Security Policy", "NIST 800-171"],
        "data_classification": "Confidential"
    }
    
    def __init__(self):
        self._users = {
            "sarah.johnson@techedu.edu": {
                "username": "sarah.johnson@techedu.edu",
                "employee_id": "STU2024001",
                "display_name": "Sarah Johnson",
                "user_type": "student",
                "groups": ["students", "cs-majors", "west-hall-residents"],
                "account_status": "active",
                "last_login": "2024-12-19T08:30:00Z",
                "mfa_enabled": True
            },
            "michael.chen@techedu.edu": {
                "username": "michael.chen@techedu.edu",
                "employee_id": "STU2024002",
                "display_name": "Michael Chen",
                "user_type": "student",
                "groups": ["students", "ds-majors", "north-tower-residents"],
                "account_status": "active",
                "last_login": "2024-12-19T09:15:00Z",
                "mfa_enabled": True
            },
            "emily.rodriguez@techedu.edu": {
                "username": "emily.rodriguez@techedu.edu",
                "employee_id": "STU2024003",
                "display_name": "Emily Rodriguez",
                "user_type": "student",
                "groups": ["students", "business-majors", "grad-commons-residents"],
                "account_status": "active",
                "last_login": "2024-12-18T14:45:00Z",
                "mfa_enabled": True
            },
            "admin@techedu.edu": {
                "username": "admin@techedu.edu",
                "employee_id": "EMP001",
                "display_name": "System Administrator",
                "user_type": "admin",
                "groups": ["administrators", "it-staff", "system-admins"],
                "account_status": "active",
                "last_login": "2024-12-19T07:00:00Z",
                "mfa_enabled": True
            },
            "advisor@techedu.edu": {
                "username": "advisor@techedu.edu",
                "employee_id": "EMP002",
                "display_name": "Academic Advisor",
                "user_type": "staff",
                "groups": ["staff", "academic-advisors", "student-services"],
                "account_status": "active",
                "last_login": "2024-12-19T08:00:00Z",
                "mfa_enabled": True
            }
        }
    
    def authenticate(self, username: str, password: str) -> Optional[Dict]:
        """
        Authenticate user against AD.
        
        PRODUCTION: Would perform LDAP bind:
        ldap.simple_bind_s(username, password)
        """
        user = self._users.get(username)
        if user and user["account_status"] == "active":
            return user
        return None
    
    def get_user(self, username: str) -> Optional[Dict]:
        """Get user from directory."""
        return self._users.get(username)
    
    def get_user_groups(self, username: str) -> List[str]:
        """Get user's group memberships."""
        user = self._users.get(username)
        if user:
            return user.get("groups", [])
        return []


class LibrarySystem:
    """
    EX LIBRIS ALMA LIBRARY SYSTEM CONNECTOR
    
    Location: CLOUD (Vendor Hosted)
    Protocol: REST/JSON
    Port: 443
    Authentication: API Key
    
    Data Owned:
    - Library accounts
    - Borrowed items
    - Fines
    - Resource access
    """
    
    SYSTEM_INFO = {
        "name": "Library Management System",
        "vendor": "Ex Libris Alma",
        "version": "Cloud",
        "protocol": "REST/JSON",
        "location": "cloud",
        "datacenter": "Ex Libris Cloud (AWS)",
        "port": 443,
        "status": "operational",
        "compliance": ["Institutional Policy"],
        "data_classification": "Internal"
    }
    
    def __init__(self):
        self._accounts = {
            "STU2024001": {
                "student_id": "STU2024001",
                "library_id": "LIB-2024-001",
                "items_checked_out": 3,
                "items_overdue": 0,
                "fines_owed": 0.00,
                "hold_requests": 1
            }
        }
    
    def get_library_account(self, student_id: str) -> Optional[Dict]:
        """Get library account info."""
        return self._accounts.get(student_id)


# Singleton instances for the legacy systems
admissions_system = AdmissionsSystem()
academic_system = AcademicRecordsSystem()
financial_system = FinancialAidSystem()
housing_system = HousingSystem()
directory_services = DirectoryServices()
library_system = LibrarySystem()


def get_all_legacy_systems() -> List[Dict]:
    """Get status of all legacy systems for ESB dashboard."""
    return [
        AdmissionsSystem.SYSTEM_INFO,
        AcademicRecordsSystem.SYSTEM_INFO,
        FinancialAidSystem.SYSTEM_INFO,
        HousingSystem.SYSTEM_INFO,
        DirectoryServices.SYSTEM_INFO,
        LibrarySystem.SYSTEM_INFO
    ]

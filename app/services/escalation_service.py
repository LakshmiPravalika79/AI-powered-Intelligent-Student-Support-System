"""
================================================================================
ESCALATION & TICKETING SERVICE
================================================================================

Handles escalation of queries that cannot be resolved by AI to human support staff.

ESCALATION FLOW:
---------------
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Student Query  │────►│  AI Processing   │────►│  Confidence     │
└─────────────────┘     └──────────────────┘     │  Check          │
                                                  └────────┬────────┘
                                                           │
                            ┌──────────────────────────────┴──────────┐
                            │                                         │
                    ┌───────▼───────┐                        ┌────────▼────────┐
                    │ Confidence    │                        │ Confidence      │
                    │ >= 0.7        │                        │ < 0.7           │
                    │               │                        │                 │
                    │ ✓ Auto-Reply  │                        │ ⚠ ESCALATE      │
                    └───────────────┘                        └────────┬────────┘
                                                                      │
                                                            ┌─────────▼─────────┐
                                                            │  Create Ticket    │
                                                            │  Assign to Staff  │
                                                            │  Notify Student   │
                                                            └───────────────────┘

TICKET STATUSES:
---------------
- OPEN: New ticket, awaiting staff assignment
- IN_PROGRESS: Staff is working on it
- PENDING_STUDENT: Waiting for student response
- RESOLVED: Issue resolved
- CLOSED: Ticket closed (with or without resolution)

PRODUCTION NOTES:
----------------
- Integrate with email/SMS notifications
- Add SLA tracking and alerts
- Connect to CRM systems (Salesforce, ServiceNow)
- Implement skill-based routing
================================================================================
"""

from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
import uuid


class TicketStatus(str, Enum):
    """Ticket lifecycle statuses."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    PENDING_STUDENT = "pending_student"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketPriority(str, Enum):
    """Ticket priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class EscalationService:
    """
    Service for managing query escalations and support tickets.
    
    Handles the handoff from AI to human support staff when
    queries cannot be resolved automatically.
    """
    
    # Confidence threshold for auto-escalation
    ESCALATION_THRESHOLD = 0.70
    
    def __init__(self, db):
        """
        Initialize escalation service.
        
        Args:
            db: MockDatabase instance
        """
        self.db = db
        
        # Initialize tickets storage if not exists
        if not hasattr(db, 'tickets'):
            db.tickets = {}
        
        # Initialize with some sample escalated tickets for demo
        self._init_sample_tickets()
    
    def _init_sample_tickets(self):
        """Create sample tickets for demonstration."""
        sample_tickets = [
            {
                "id": "TKT-2025-001",
                "student_id": "STU2024001",
                "student_name": "Sarah Johnson",
                "student_email": "sarah.johnson@techedu.edu",
                "subject": "Financial Aid Appeal",
                "original_query": "I need to appeal my financial aid decision because my family circumstances have changed significantly.",
                "ai_response": "I understand you need to appeal your financial aid. Let me connect you with a financial aid specialist who can help you through this process.",
                "ai_confidence": 0.45,
                "category": "financial_aid",
                "status": TicketStatus.IN_PROGRESS.value,
                "priority": TicketPriority.HIGH.value,
                "assigned_to": "finaid.jones@techedu.edu",
                "created_at": "2025-01-15T09:30:00",
                "updated_at": "2025-01-16T14:20:00",
                "messages": [
                    {
                        "sender": "student",
                        "message": "I need to appeal my financial aid decision because my family circumstances have changed significantly.",
                        "timestamp": "2025-01-15T09:30:00"
                    },
                    {
                        "sender": "system",
                        "message": "Your query has been escalated to our Financial Aid support team. A specialist will respond within 24 hours.",
                        "timestamp": "2025-01-15T09:30:05"
                    },
                    {
                        "sender": "system",
                        "message": "Ticket assigned to Maria Jones.",
                        "timestamp": "2025-01-15T10:00:00"
                    },
                    {
                        "sender": "staff",
                        "sender_name": "Maria Jones",
                        "message": "Hi Sarah! Thank you for reaching out. I'm sorry to hear about the changes in your family's circumstances. I'd be happy to help you with the financial aid appeal process.\n\nTo proceed, please provide:\n1. A brief explanation letter describing the changes\n2. Any supporting documentation (medical bills, layoff notice, etc.)\n\nYou can email these to finaid@techedu.edu or upload them through the Student Portal.\n\nDo you have any questions about the process?",
                        "timestamp": "2025-01-15T14:30:00"
                    },
                    {
                        "sender": "student",
                        "message": "Thank you! My father lost his job last month. I'll send the layoff notice and updated income information.",
                        "timestamp": "2025-01-16T09:15:00"
                    },
                    {
                        "sender": "staff",
                        "sender_name": "Maria Jones",
                        "message": "Thank you Sarah. I received your documents and have started processing your appeal. Given the circumstances, I'm also checking if you qualify for emergency aid. I'll update you within 2-3 business days.",
                        "timestamp": "2025-01-16T14:20:00"
                    }
                ],
                "resolution_notes": None
            },
            {
                "id": "TKT-2025-002",
                "student_id": "STU2024001",
                "student_name": "Sarah Johnson",
                "student_email": "sarah.johnson@techedu.edu",
                "subject": "Course Registration Issue",
                "original_query": "I'm trying to register for CS401 but it says I don't have the prerequisites, but I do!",
                "ai_response": "I see you're having a prerequisite issue. Let me connect you with an academic advisor.",
                "ai_confidence": 0.52,
                "category": "registration",
                "status": TicketStatus.RESOLVED.value,
                "priority": TicketPriority.MEDIUM.value,
                "assigned_to": "advisor.smith@techedu.edu",
                "created_at": "2025-01-10T11:20:00",
                "updated_at": "2025-01-11T16:00:00",
                "messages": [
                    {
                        "sender": "student",
                        "message": "I'm trying to register for CS401 but it says I don't have the prerequisites, but I do!",
                        "timestamp": "2025-01-10T11:20:00"
                    },
                    {
                        "sender": "system",
                        "message": "Your query has been escalated to Academic Advising.",
                        "timestamp": "2025-01-10T11:20:05"
                    },
                    {
                        "sender": "staff",
                        "sender_name": "Dr. James Smith",
                        "message": "Hi Sarah, I checked your records and found the issue. Your CS302 grade was posted late and the system hadn't updated. I've manually added the prerequisite override for CS401. You should be able to register now!",
                        "timestamp": "2025-01-10T15:45:00"
                    },
                    {
                        "sender": "student",
                        "message": "It worked! Thank you so much Dr. Smith!",
                        "timestamp": "2025-01-10T16:30:00"
                    },
                    {
                        "sender": "staff",
                        "sender_name": "Dr. James Smith",
                        "message": "You're welcome! Good luck with CS401 - it's a great course. I'm marking this as resolved. Feel free to reach out if you have any other issues.",
                        "timestamp": "2025-01-11T16:00:00"
                    }
                ],
                "resolution_notes": "Added prerequisite override for CS401. Grade posting delay caused system issue."
            },
            {
                "id": "TKT-2025-003",
                "student_id": "STU2024002",
                "student_name": "Michael Chen",
                "student_email": "michael.chen@techedu.edu",
                "subject": "Course Override Request",
                "original_query": "I need a prerequisite override for CS401 Advanced Machine Learning. I have relevant work experience.",
                "ai_response": "Prerequisite overrides require department approval. I'm connecting you with an academic advisor.",
                "ai_confidence": 0.52,
                "category": "registration",
                "status": TicketStatus.IN_PROGRESS.value,
                "priority": TicketPriority.MEDIUM.value,
                "assigned_to": "advisor.smith@techedu.edu",
                "created_at": "2025-01-14T14:20:00",
                "updated_at": "2025-01-15T10:15:00",
                "messages": [
                    {
                        "sender": "student",
                        "message": "I need a prerequisite override for CS401 Advanced Machine Learning. I have relevant work experience.",
                        "timestamp": "2025-01-14T14:20:00"
                    },
                    {
                        "sender": "system",
                        "message": "Your query has been escalated to Academic Advising. An advisor will review your request.",
                        "timestamp": "2025-01-14T14:20:05"
                    },
                    {
                        "sender": "staff",
                        "sender_name": "Dr. James Smith",
                        "message": "Hi Michael, I've reviewed your request. Could you please provide documentation of your work experience? A letter from your employer or relevant certifications would help.",
                        "timestamp": "2025-01-15T10:15:00"
                    }
                ],
                "resolution_notes": None
            },
            {
                "id": "TKT-2025-003",
                "student_id": "STU2024003",
                "student_name": "Emily Rodriguez",
                "student_email": "emily.rodriguez@techedu.edu",
                "subject": "Housing Accommodation Request",
                "original_query": "I need to request a housing accommodation due to a medical condition. What forms do I need?",
                "ai_response": "Housing accommodations require documentation from the Disability Services office. Let me connect you with Housing Services.",
                "ai_confidence": 0.61,
                "category": "housing",
                "status": TicketStatus.RESOLVED.value,
                "priority": TicketPriority.MEDIUM.value,
                "assigned_to": "finaid.jones@techedu.edu",
                "created_at": "2025-01-13T11:00:00",
                "updated_at": "2025-01-14T16:30:00",
                "messages": [
                    {
                        "sender": "student",
                        "message": "I need to request a housing accommodation due to a medical condition. What forms do I need?",
                        "timestamp": "2025-01-13T11:00:00"
                    },
                    {
                        "sender": "system",
                        "message": "Your query has been escalated to Housing Services.",
                        "timestamp": "2025-01-13T11:00:05"
                    },
                    {
                        "sender": "staff",
                        "sender_name": "Maria Jones",
                        "message": "Hi Emily, for housing accommodations you'll need: 1) Medical documentation from your healthcare provider, 2) Completed Accommodation Request Form (available at housing.techedu.edu/forms), 3) Registration with Disability Services. Would you like me to send you direct links?",
                        "timestamp": "2025-01-13T15:30:00"
                    },
                    {
                        "sender": "student",
                        "message": "Yes please, that would be very helpful!",
                        "timestamp": "2025-01-14T09:00:00"
                    },
                    {
                        "sender": "staff",
                        "sender_name": "Maria Jones",
                        "message": "I've emailed you all the forms and instructions. Please let me know if you have any questions!",
                        "timestamp": "2025-01-14T16:30:00"
                    }
                ],
                "resolution_notes": "Provided student with accommodation forms and process information."
            }
        ]
        
        for ticket in sample_tickets:
            self.db.tickets[ticket["id"]] = ticket
    
    def should_escalate(self, confidence: float, category: str = None) -> bool:
        """
        Determine if a query should be escalated to human support.
        
        Args:
            confidence: AI confidence score (0-1)
            category: Query category for special handling
            
        Returns:
            True if should escalate
        """
        # Always escalate low confidence queries
        if confidence < self.ESCALATION_THRESHOLD:
            return True
        
        # Categories that should always have human review option
        sensitive_categories = ["financial_aid_appeal", "complaint", "emergency"]
        if category in sensitive_categories:
            return True
        
        return False
    
    def create_ticket(
        self,
        student_id: str,
        query: str,
        ai_response: str,
        ai_confidence: float,
        category: str
    ) -> Dict:
        """
        Create a new support ticket for escalated query.
        
        Args:
            student_id: Student's ID
            query: Original student query
            ai_response: AI's attempted response
            ai_confidence: AI confidence score
            category: Query category
            
        Returns:
            Created ticket dict
        """
        # Get student info
        student = self.db.students.get(student_id, {})
        
        # Generate ticket ID
        ticket_count = len(self.db.tickets) + 1
        ticket_id = f"TKT-2025-{ticket_count:03d}"
        
        # Determine priority based on category and confidence
        if ai_confidence < 0.3:
            priority = TicketPriority.HIGH.value
        elif category in ["financial_aid", "emergency"]:
            priority = TicketPriority.HIGH.value
        else:
            priority = TicketPriority.MEDIUM.value
        
        now = datetime.now().isoformat()
        
        ticket = {
            "id": ticket_id,
            "student_id": student_id,
            "student_name": student.get("name", "Unknown"),
            "student_email": student.get("email", "unknown@techedu.edu"),
            "subject": f"{category.replace('_', ' ').title()} Query",
            "original_query": query,
            "ai_response": ai_response,
            "ai_confidence": ai_confidence,
            "category": category,
            "status": TicketStatus.OPEN.value,
            "priority": priority,
            "assigned_to": None,
            "created_at": now,
            "updated_at": now,
            "messages": [
                {
                    "sender": "student",
                    "message": query,
                    "timestamp": now
                },
                {
                    "sender": "system",
                    "message": f"Your query has been escalated to our support team. A specialist will respond within 24 hours. Your ticket number is {ticket_id}.",
                    "timestamp": now
                }
            ],
            "resolution_notes": None
        }
        
        self.db.tickets[ticket_id] = ticket
        return ticket
    
    def get_all_tickets(self, status_filter: str = None) -> List[Dict]:
        """
        Get all tickets, optionally filtered by status.
        
        Args:
            status_filter: Optional status to filter by
            
        Returns:
            List of tickets
        """
        tickets = list(self.db.tickets.values())
        
        if status_filter:
            tickets = [t for t in tickets if t["status"] == status_filter]
        
        # Sort by created_at descending (newest first)
        tickets.sort(key=lambda x: x["created_at"], reverse=True)
        
        return tickets
    
    def get_ticket(self, ticket_id: str) -> Optional[Dict]:
        """Get a specific ticket by ID."""
        return self.db.tickets.get(ticket_id)
    
    def get_staff_tickets(self, staff_email: str) -> List[Dict]:
        """Get tickets assigned to a specific staff member."""
        return [
            t for t in self.db.tickets.values()
            if t.get("assigned_to") == staff_email
        ]
    
    def get_student_tickets(self, student_id: str) -> List[Dict]:
        """Get tickets for a specific student."""
        return [
            t for t in self.db.tickets.values()
            if t.get("student_id") == student_id
        ]
    
    def assign_ticket(self, ticket_id: str, staff_email: str) -> Optional[Dict]:
        """
        Assign a ticket to a staff member.
        
        Args:
            ticket_id: Ticket to assign
            staff_email: Staff member's email
            
        Returns:
            Updated ticket or None
        """
        ticket = self.db.tickets.get(ticket_id)
        if not ticket:
            return None
        
        ticket["assigned_to"] = staff_email
        ticket["status"] = TicketStatus.IN_PROGRESS.value
        ticket["updated_at"] = datetime.now().isoformat()
        
        # Add system message
        staff_name = self.db.users.get(staff_email, {}).get("name", "Staff")
        ticket["messages"].append({
            "sender": "system",
            "message": f"Ticket assigned to {staff_name}.",
            "timestamp": datetime.now().isoformat()
        })
        
        return ticket
    
    def add_message(
        self,
        ticket_id: str,
        sender_type: str,
        sender_email: str,
        message: str
    ) -> Optional[Dict]:
        """
        Add a message to a ticket.
        
        Args:
            ticket_id: Ticket ID
            sender_type: "student" or "staff"
            sender_email: Sender's email
            message: Message content
            
        Returns:
            Updated ticket or None
        """
        ticket = self.db.tickets.get(ticket_id)
        if not ticket:
            return None
        
        # Get sender name
        sender_info = self.db.users.get(sender_email, {})
        sender_name = sender_info.get("name", "Unknown")
        
        msg = {
            "sender": sender_type,
            "sender_name": sender_name if sender_type == "staff" else None,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        
        ticket["messages"].append(msg)
        ticket["updated_at"] = datetime.now().isoformat()
        
        # Update status based on who sent
        if sender_type == "staff":
            ticket["status"] = TicketStatus.PENDING_STUDENT.value
        elif sender_type == "student":
            ticket["status"] = TicketStatus.IN_PROGRESS.value
        
        return ticket
    
    def resolve_ticket(
        self,
        ticket_id: str,
        resolution_notes: str
    ) -> Optional[Dict]:
        """
        Mark a ticket as resolved.
        
        Args:
            ticket_id: Ticket to resolve
            resolution_notes: Notes about the resolution
            
        Returns:
            Updated ticket or None
        """
        ticket = self.db.tickets.get(ticket_id)
        if not ticket:
            return None
        
        ticket["status"] = TicketStatus.RESOLVED.value
        ticket["resolution_notes"] = resolution_notes
        ticket["updated_at"] = datetime.now().isoformat()
        
        ticket["messages"].append({
            "sender": "system",
            "message": f"Ticket resolved. Resolution: {resolution_notes}",
            "timestamp": datetime.now().isoformat()
        })
        
        return ticket
    
    def get_escalation_stats(self) -> Dict:
        """Get escalation statistics for dashboard."""
        tickets = list(self.db.tickets.values())
        
        open_tickets = len([t for t in tickets if t["status"] == TicketStatus.OPEN.value])
        in_progress = len([t for t in tickets if t["status"] == TicketStatus.IN_PROGRESS.value])
        resolved = len([t for t in tickets if t["status"] == TicketStatus.RESOLVED.value])
        
        # Category breakdown
        categories = {}
        for t in tickets:
            cat = t.get("category", "other")
            categories[cat] = categories.get(cat, 0) + 1
        
        # Average confidence of escalated queries
        confidences = [t.get("ai_confidence", 0) for t in tickets]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        return {
            "total_tickets": len(tickets),
            "open": open_tickets,
            "in_progress": in_progress,
            "resolved": resolved,
            "pending_student": len([t for t in tickets if t["status"] == TicketStatus.PENDING_STUDENT.value]),
            "by_category": categories,
            "avg_escalation_confidence": round(avg_confidence, 2),
            "escalation_rate": "27%",  # Simulated
            "avg_resolution_time": "4.2 hours"  # Simulated
        }

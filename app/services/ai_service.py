"""
================================================================================
AI SERVICE - Intent Classification & Response Generation
================================================================================

PURPOSE:
This service handles the "AI" functionality of the student support system.

MVP IMPLEMENTATION (Rule-Based):
--------------------------------
- Keyword-based intent classification
- Template-based response generation
- Personalization using student data
- No external API calls

WHY MOCK AI:
- No API keys required
- No cost for demo
- Predictable behavior for presentation
- Demonstrates the ARCHITECTURE, not AI capability

PRODUCTION IMPLEMENTATION:
--------------------------
The same interface would be used with real AI:

1. INTENT CLASSIFICATION:
   - Azure OpenAI GPT-4 for NLU
   - Fine-tuned classifier model
   - Confidence thresholds for escalation

2. RESPONSE GENERATION:
   - RAG (Retrieval Augmented Generation)
   - Vector search for relevant content
   - GPT-4 for natural response synthesis

3. KNOWLEDGE BASE:
   - Pinecone / Azure Cognitive Search
   - OpenAI embeddings (ada-002)
   - Real-time content updates

SCALING CONSIDERATIONS:
-----------------------
CLOUD DEPLOYMENT:
- Azure Cognitive Services for hosted models
- Auto-scaling based on query volume
- Response caching for common queries
- Async processing for high throughput

COST OPTIMIZATION:
- Cache frequent query responses
- Use smaller models for classification
- Batch embedding generation
- Tier responses by complexity
================================================================================
"""

import random
from datetime import datetime
from typing import Dict, List, Optional
from app.models.schemas import QueryResponse


class AIService:
    """
    AI Service for natural language processing and response generation.
    
    ARCHITECTURE DIAGRAM:
    
    ┌─────────────────────────────────────────────────────────────────┐
    │                        AI SERVICE                                │
    ├─────────────────────────────────────────────────────────────────┤
    │                                                                  │
    │  ┌───────────────┐    ┌───────────────┐    ┌───────────────┐   │
    │  │    Intent     │    │   Knowledge   │    │   Response    │   │
    │  │ Classifier    │───▶│    Search     │───▶│  Generator    │   │
    │  │  (Keywords)   │    │  (Keywords)   │    │  (Templates)  │   │
    │  └───────────────┘    └───────────────┘    └───────────────┘   │
    │         │                    │                    │             │
    │         │    PRODUCTION:     │    PRODUCTION:     │             │
    │         │    GPT-4 NLU       │    Vector DB       │             │
    │         │    Fine-tuned      │    Pinecone        │             │
    │         │    Classifier      │    Embeddings      │             │
    │                                                                  │
    └─────────────────────────────────────────────────────────────────┘
    """
    
    def __init__(self, db):
        """
        Initialize AI service with database reference.
        
        Args:
            db: MockDatabase instance containing knowledge base
        """
        self.db = db
        
        # Confidence thresholds
        self.HIGH_CONFIDENCE = 0.85
        self.LOW_CONFIDENCE = 0.45
        
        # Escalation keywords that should go to human support
        self.escalation_keywords = [
            "complaint", "angry", "upset", "urgent", "emergency",
            "speak to human", "real person", "manager", "sue", "lawyer",
            "discrimination", "harassment", "unfair"
        ]
    
    def classify_intent(self, message: str) -> str:
        """
        Classify the intent of a user message.
        
        MVP: Keyword matching against knowledge base categories
        PRODUCTION: GPT-4 or fine-tuned BERT classifier
        
        INTENT CATEGORIES:
        - admissions: Application questions
        - financial_aid: Money, payments, scholarships
        - registration: Course enrollment, scheduling
        - grades: Academic records, GPA, transcripts
        - housing: Dorms, roommates, facilities
        - support: Counseling, health, emergencies
        - career: Jobs, internships, career advice
        - escalation: Needs human intervention
        - general: Unclassified queries
        
        Args:
            message: User's query text
            
        Returns:
            Category string
        """
        message_lower = message.lower()
        
        # Check for escalation triggers first
        if any(keyword in message_lower for keyword in self.escalation_keywords):
            return "escalation"
        
        # Match against knowledge base categories
        for kb_item in self.db.knowledge_base:
            if any(keyword in message_lower for keyword in kb_item["keywords"]):
                return kb_item["category"]
        
        return "general"
    
    def generate_response(
        self, 
        message: str, 
        student_data: Dict, 
        category: str
    ) -> QueryResponse:
        """
        Generate AI response based on intent and student context.
        
        MVP FLOW:
        1. Find knowledge base entry for category
        2. Select appropriate response template
        3. Personalize with student data
        4. Return structured response
        
        PRODUCTION FLOW:
        1. Vector search for relevant content
        2. Retrieve top-k similar documents
        3. Build context with student data
        4. GPT-4 generates natural response
        5. Post-process for accuracy
        
        PERSONALIZATION:
        - Student's name, GPA, courses
        - Financial aid amounts and dates
        - Housing assignment details
        - Enrollment status
        
        Args:
            message: Original user query
            student_data: Student profile for personalization
            category: Classified intent category
            
        Returns:
            QueryResponse with text, category, confidence, etc.
        """
        
        # Handle escalation category
        if category == "escalation":
            return self._create_escalation_response(message)
        
        # Find knowledge base entry
        kb_item = self._find_knowledge_entry(category)
        
        if kb_item:
            # Select and personalize response
            response_text = self._personalize_response(
                kb_item["responses"],
                student_data
            )
            
            return QueryResponse(
                text=response_text,
                category=category,
                confidence=self.HIGH_CONFIDENCE + random.uniform(-0.05, 0.05),
                automated=True,
                timestamp=datetime.now(),
                sources=[f"{category}.techedu.edu", "knowledge-base"]
            )
        
        # Fallback for unmatched queries
        return self._create_fallback_response(message, student_data)
    
    def _find_knowledge_entry(self, category: str) -> Optional[Dict]:
        """Find knowledge base entry by category."""
        for item in self.db.knowledge_base:
            if item["category"] == category:
                return item
        return None
    
    def _personalize_response(
        self, 
        responses: List[str], 
        student_data: Dict
    ) -> str:
        """
        Select and personalize a response template.
        
        TEMPLATE VARIABLES (Now using full legacy system data):
        Basic Info:
        - {name}: Student full name
        - {first_name}: Student first name
        - {program}: Academic program
        - {year}: Class year
        
        Academic (from PeopleSoft):
        - {gpa}: Cumulative GPA
        - {gpa_semester}: Current semester GPA
        - {credits_completed}: Total credits completed
        - {credits_in_progress}: Current credits
        - {academic_standing}: Academic standing
        - {dean_list}: Dean's list status
        - {courseCount}: Number of current courses
        - {semester}: Current semester
        
        Financial Aid (from PowerFAIDS):
        - {total_aid}: Total aid amount
        - {remaining_balance}: Balance due
        - {next_disbursement}: Next payment date
        - {grants_total}: Total grants
        - {scholarships_total}: Total scholarships
        - {loans_total}: Total loans
        - {aid_status}: Aid status
        
        Housing (from StarRez):
        - {building}: Building name
        - {room}: Room number
        - {room_type}: Room type
        - {meal_plan}: Meal plan name
        - {flex_remaining}: Remaining flex dollars
        - {move_in_date}: Move-in date
        
        Library (from Ex Libris):
        - {library_items}: Items checked out
        - {library_fines}: Library fines
        """
        # Select random response from options
        template = random.choice(responses)
        
        # Extract nested data safely (now from legacy systems)
        financial_aid = student_data.get("financial_aid", {})
        housing = student_data.get("housing", {})
        library = student_data.get("library", {})
        courses = student_data.get("courses", [])
        meal_plan = housing.get("meal_plan", {})
        
        # Calculate totals from detailed aid breakdown
        grants_total = sum(g.get("amount", 0) for g in financial_aid.get("grants", []))
        scholarships_total = sum(s.get("amount", 0) for s in financial_aid.get("scholarships", []))
        loans_total = sum(l.get("amount", 0) for l in financial_aid.get("loans", []))
        
        # Personalize template with rich data
        try:
            response = template.format(
                # Basic info
                name=student_data.get("name", "Student"),
                first_name=student_data.get("first_name", student_data.get("name", "Student").split()[0]),
                program=student_data.get("program", "N/A"),
                year=student_data.get("year", "N/A"),
                
                # Academic data (from PeopleSoft)
                gpa=student_data.get("gpa", "N/A"),
                gpa_semester=student_data.get("gpa_semester", "N/A"),
                credits_completed=student_data.get("credits_completed", 0),
                credits_in_progress=student_data.get("credits_in_progress", 0),
                academic_standing=student_data.get("academic_standing", "N/A"),
                dean_list="Yes ⭐" if student_data.get("dean_list") else "No",
                courseCount=len(courses),
                semester=student_data.get("semester", "N/A"),
                
                # Financial aid (from PowerFAIDS) - detailed
                amount=f"${financial_aid.get('total_aid', financial_aid.get('amount', 0)):,}",
                total_aid=f"${financial_aid.get('total_aid', 0):,}",
                remaining_balance=f"${financial_aid.get('remaining_balance', 0):,}",
                date=financial_aid.get("next_disbursement", financial_aid.get("disbursement_date", "N/A")),
                next_disbursement=financial_aid.get("next_disbursement", "N/A"),
                grants_total=f"${grants_total:,}",
                scholarships_total=f"${scholarships_total:,}",
                loans_total=f"${loans_total:,}",
                aid_status=financial_aid.get("status", "N/A"),
                cost_of_attendance=f"${financial_aid.get('total_cost_of_attendance', 0):,}",
                financial_need=f"${financial_aid.get('financial_need', 0):,}",
                
                # Housing (from StarRez) - detailed
                building=housing.get("building", "N/A"),
                room=housing.get("room", "N/A"),
                room_type=housing.get("room_type", "N/A"),
                floor=housing.get("floor", "N/A"),
                meal_plan=meal_plan.get("name", "None"),
                meals_per_week=meal_plan.get("meals_per_week", 0),
                flex_remaining=f"${meal_plan.get('flex_remaining', 0)}",
                move_in_date=housing.get("move_in_date", "N/A"),
                move_out_date=housing.get("move_out_date", "N/A"),
                
                # Library (from Ex Libris)
                library_items=library.get("items_checked_out", 0),
                library_fines=f"${library.get('fines_owed', 0):.2f}",
                library_overdue=library.get("items_overdue", 0)
            )
        except KeyError as e:
            # If template uses a variable we don't have, use the template as-is
            response = template
        
        return response
    
    def _create_escalation_response(self, message: str) -> QueryResponse:
        """
        Create response for queries needing human intervention.
        
        ESCALATION TRIGGERS:
        - Complaints or frustration detected
        - Complex issues outside FAQ scope
        - Legal or sensitive matters
        - Low AI confidence
        
        PRODUCTION:
        - Create support ticket automatically
        - Route to appropriate department
        - Provide wait time estimates
        - Offer callback option
        """
        return QueryResponse(
            text=(
                "I understand this is an important matter that needs personal attention. "
                "I've detected that your query may require human assistance.\n\n"
                "**I can:**\n"
                "• 🎫 Create a support ticket so our staff can help you personally\n"
                "• 📞 Provide contact info: (555) 123-4567\n"
                "• 📧 Email: support@techedu.edu\n\n"
                "Click 'Talk to Support' below to create a ticket and connect with a staff member. "
                "Average response time: 4-24 hours."
            ),
            category="escalation",
            confidence=self.LOW_CONFIDENCE,  # Low confidence triggers "Talk to Support" link
            automated=False,
            timestamp=datetime.now(),
            sources=["support.techedu.edu"]
        )
    
    def _create_fallback_response(
        self, 
        message: str, 
        student_data: Dict
    ) -> QueryResponse:
        """
        Create fallback response for unclassified queries.
        
        PRODUCTION IMPROVEMENT:
        - Use GPT-4 to attempt answering anyway
        - Log for training data collection
        - Suggest similar questions that can be answered
        """
        student_name = student_data.get("name", "").split()[0]  # First name
        
        return QueryResponse(
            text=(
                f"Hi {student_name}! I'm not quite sure I understood your question correctly. "
                "Here are some things I can help you with:\n\n"
                "• 💰 **Financial Aid** - Scholarships, payments, FAFSA\n"
                "• 📚 **Registration** - Courses, enrollment, schedules\n"
                "• 📊 **Grades & GPA** - Transcripts, academic records\n"
                "• 🏠 **Housing** - Dorms, room assignments, maintenance\n"
                "• 🎓 **Admissions** - Applications, requirements\n"
                "• 💼 **Career Services** - Jobs, internships, resume help\n\n"
                "Could you rephrase your question? Or if you need human assistance, click 'Talk to Support' below."
            ),
            category="general",
            confidence=0.30,  # Low confidence triggers "Talk to Support" link
            automated=True,
            timestamp=datetime.now(),
            sources=["help.techedu.edu"]
        )
    
    def search_knowledge_base(self, query: str, limit: int = 5) -> Dict:
        """
        Search knowledge base for relevant entries.
        
        MVP: Simple keyword matching
        PRODUCTION: Vector similarity search with embeddings
        
        Args:
            query: Search query text
            limit: Maximum results to return
            
        Returns:
            Dict with query, results, and count
        """
        query_lower = query.lower()
        results = []
        
        for item in self.db.knowledge_base:
            # Check if any keywords match
            matching_keywords = [
                kw for kw in item["keywords"] 
                if kw in query_lower
            ]
            
            if matching_keywords:
                results.append({
                    "category": item["category"],
                    "matched_keywords": matching_keywords,
                    "sample_response": item["responses"][0] if item["responses"] else None
                })
                
                if len(results) >= limit:
                    break
        
        return {
            "query": query,
            "results": results,
            "count": len(results),
            "search_type": "keyword"  # PRODUCTION: "semantic"
        }
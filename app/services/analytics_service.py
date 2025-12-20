"""
================================================================================
ANALYTICS SERVICE - Metrics, Logging, and Business Intelligence
================================================================================

PURPOSE:
Provides real-time analytics, query logging, and business metrics for:
- Administrative dashboard
- AI performance monitoring
- ROI calculation
- System health tracking

MVP IMPLEMENTATION:
-------------------
- In-memory query logging
- Simulated baseline metrics
- Real-time query count updates

PRODUCTION ARCHITECTURE:
------------------------

┌─────────────────────────────────────────────────────────────────────────────┐
│                        ANALYTICS PIPELINE (CLOUD)                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌───────────┐     ┌───────────┐     ┌───────────┐     ┌───────────┐       │
│  │   Query   │────▶│  Event    │────▶│   Data    │────▶│  Data     │       │
│  │   Event   │     │   Hub     │     │  Factory  │     │ Warehouse │       │
│  │           │     │ (Kafka)   │     │  (ETL)    │     │(Snowflake)│       │
│  └───────────┘     └───────────┘     └───────────┘     └───────────┘       │
│                                                              │               │
│                                                              ▼               │
│                                                      ┌───────────┐          │
│                                                      │  Power BI │          │
│                                                      │ Dashboard │          │
│                                                      └───────────┘          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

PRODUCTION TECHNOLOGIES:
- Azure Event Hubs / AWS Kinesis for streaming
- Azure Data Factory / AWS Glue for ETL
- Snowflake / Azure Synapse for data warehouse
- Power BI / Tableau for dashboards
- Azure Monitor / CloudWatch for infrastructure

KEY METRICS TRACKED:
-------------------
1. OPERATIONAL
   - Query volume (total, per hour, per day)
   - Response times
   - Error rates
   - System uptime

2. AI PERFORMANCE
   - Automated resolution rate
   - Intent classification accuracy
   - Escalation rate
   - Confidence score distribution

3. BUSINESS VALUE (ROI)
   - Cost per query
   - Workload reduction %
   - Monthly savings
   - Student satisfaction

4. CATEGORY DISTRIBUTION
   - Top query categories
   - Trending topics
   - Emerging issues
================================================================================
"""

from datetime import datetime
from typing import Dict, List
from app.models.schemas import QueryResponse, AnalyticsMetrics


class AnalyticsService:
    """
    Analytics and metrics service.
    
    Handles:
    - Query logging for analysis
    - Real-time metrics calculation
    - Business intelligence data
    - Performance monitoring
    """
    
    def __init__(self, db):
        """
        Initialize analytics service.
        
        Args:
            db: MockDatabase instance
        """
        self.db = db
        
        # Baseline metrics (simulated historical data)
        # In production, these come from data warehouse
        self._baseline_metrics = {
            "total_queries": 1247,
            "automated_resolution": 73.0,
            "avg_response_time": 3.2,
            "satisfaction_score": 87.0,
            "active_users": 342,
            "queries_last_24h": 156
        }
    
    def log_query(
        self, 
        student_id: str, 
        query: str, 
        response: QueryResponse
    ) -> None:
        """
        Log a query for analytics tracking.
        
        LOGGED DATA:
        - Timestamp: When query was made
        - Student ID: Who asked (anonymized in production)
        - Query text: What was asked
        - Response: What AI answered
        - Category: Classified intent
        - Automated: Was it AI-resolved or escalated
        - Confidence: AI confidence score
        
        PRODUCTION CONSIDERATIONS:
        - Async logging (don't block response)
        - PII masking/anonymization
        - Retention policies (90 days typical)
        - GDPR compliance for EU students
        
        Args:
            student_id: Student who made query
            query: Original query text
            response: Generated response object
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "student_id": student_id,
            "query": query,
            "response_text": response.text[:200] + "..." if len(response.text) > 200 else response.text,
            "category": response.category,
            "automated": response.automated,
            "confidence": response.confidence,
            "sources": response.sources
        }
        
        # Store in mock database
        self.db.log_query(log_entry)
    
    def get_metrics(self) -> AnalyticsMetrics:
        """
        Get current system analytics metrics.
        
        METRICS CALCULATION:
        - Total queries = baseline + logged queries
        - Automated % = (automated queries / total) * 100
        - Other metrics simulated for MVP
        
        PRODUCTION:
        These would be calculated from:
        - Real-time streaming data (last hour)
        - Data warehouse aggregations (historical)
        - Cached for performance (1 min TTL)
        
        Returns:
            AnalyticsMetrics model with all KPIs
        """
        # Get logged queries
        query_log = self.db.get_query_log()
        logged_count = len(query_log)
        
        # Calculate automated resolution from logged queries
        if logged_count > 0:
            automated_count = sum(1 for q in query_log if q.get("automated", False))
            recent_automated_rate = (automated_count / logged_count) * 100
        else:
            recent_automated_rate = self._baseline_metrics["automated_resolution"]
        
        # Blend baseline with recent data
        total_queries = self._baseline_metrics["total_queries"] + logged_count
        
        # Category distribution from logged queries
        category_counts = self._calculate_category_distribution(query_log)
        
        return AnalyticsMetrics(
            total_queries=total_queries,
            automated_resolution=round(recent_automated_rate, 1),
            avg_response_time=self._baseline_metrics["avg_response_time"],
            satisfaction_score=self._baseline_metrics["satisfaction_score"],
            active_users=self._baseline_metrics["active_users"],
            queries_last_24h=self._baseline_metrics["queries_last_24h"] + logged_count,
            top_categories=category_counts,
            system_health=self._get_system_health(),
            roi_metrics=self._get_roi_metrics(total_queries)
        )
    
    def _calculate_category_distribution(self, query_log: List[Dict]) -> List[Dict]:
        """
        Calculate query distribution by category.
        
        Returns list of categories with counts and percentages.
        """
        # Start with baseline distribution
        categories = {
            "Financial Aid": 423,
            "Registration": 361,
            "Grades": 298,
            "Housing": 165,
            "Admissions": 89,
            "Support": 45,
            "Career": 32,
            "General": 28
        }
        
        # Add logged queries
        category_mapping = {
            "financial_aid": "Financial Aid",
            "registration": "Registration",
            "grades": "Grades",
            "housing": "Housing",
            "admissions": "Admissions",
            "support": "Support",
            "career": "Career",
            "general": "General",
            "escalation": "Support"  # Escalations count as support
        }
        
        for query in query_log:
            cat = query.get("category", "general")
            display_name = category_mapping.get(cat, "General")
            categories[display_name] = categories.get(display_name, 0) + 1
        
        # Calculate percentages
        total = sum(categories.values())
        result = []
        
        for name, count in sorted(categories.items(), key=lambda x: -x[1]):
            percentage = round((count / total) * 100) if total > 0 else 0
            result.append({
                "name": name,
                "count": count,
                "percentage": percentage
            })
        
        return result[:5]  # Top 5 categories
    
    def _get_system_health(self) -> Dict:
        """
        Get current system health indicators.
        
        PRODUCTION: Would query actual infrastructure:
        - Azure Monitor metrics
        - Application Insights
        - Database connection pools
        - Cache hit rates
        """
        return {
            "api_status": "operational",
            "api_response_time": "124ms",
            "database_status": "operational (mock)",
            "database_query_time": "45ms",
            "ai_service_status": "operational (rule-based)",
            "esb_status": "operational (simulated)",
            "cache_hit_rate": "78%",
            "uptime": "99.7%",
            "last_incident": "None in last 30 days"
        }
    
    def _get_roi_metrics(self, total_queries: int) -> Dict:
        """
        Calculate ROI metrics for the AI system.
        
        BUSINESS VALUE CALCULATION:
        
        Assumptions (for demo):
        - Human support cost: $25/query (15 min @ $100/hr)
        - AI cost: $0.38/query (infrastructure + mock AI)
        - Automated resolution: 73%
        
        Savings = (Automated Queries) × (Human Cost - AI Cost)
        
        PRODUCTION:
        - Pull from financial systems
        - Track actual support ticket costs
        - Measure real AI processing costs
        """
        # Cost assumptions
        human_cost_per_query = 25.00  # $25 per human-handled query
        ai_cost_per_query = 0.38  # $0.38 per AI query
        automated_rate = 0.73  # 73% automated
        
        # Calculations
        automated_queries = int(total_queries * automated_rate)
        cost_savings_per_query = human_cost_per_query - ai_cost_per_query
        total_savings = automated_queries * cost_savings_per_query
        
        # Annual projection (assuming current volume continues)
        monthly_projection = total_savings * 30 / max(total_queries, 1)
        annual_projection = monthly_projection * 12
        
        # ROI calculation
        implementation_cost = 150000  # Assumed initial investment
        roi_year1 = ((annual_projection - implementation_cost) / implementation_cost) * 100
        
        return {
            "cost_per_query_human": f"${human_cost_per_query:.2f}",
            "cost_per_query_ai": f"${ai_cost_per_query:.2f}",
            "automated_queries": automated_queries,
            "workload_reduction_percent": round(automated_rate * 100),
            "cost_savings_to_date": f"${total_savings:,.2f}",
            "monthly_savings_projected": f"${monthly_projection:,.2f}",
            "annual_savings_projected": f"${annual_projection:,.2f}",
            "implementation_cost": f"${implementation_cost:,}",
            "roi_year1_percent": round(roi_year1, 1),
            "break_even_months": round(implementation_cost / monthly_projection) if monthly_projection > 0 else "N/A",
            "notes": "Values simulated for MVP demonstration. Production would use actual cost data."
        }
    
    def get_query_log(self, limit: int = 50) -> Dict:
        """
        Get recent query log for analysis.
        
        USE CASES:
        - Admin review of AI performance
        - Training data collection
        - Debugging response issues
        - Compliance auditing
        
        PRODUCTION:
        - Paginated results
        - Date range filters
        - Category filters
        - Export to CSV/Excel
        
        Args:
            limit: Maximum entries to return
            
        Returns:
            Dict with query log entries and metadata
        """
        queries = self.db.get_query_log(limit)
        
        return {
            "total_logged": len(self.db.query_log),
            "returned": len(queries),
            "limit": limit,
            "queries": queries,
            "note": "MVP: In-memory storage. Production: Azure Cosmos DB with 90-day retention."
        }
    
    def get_trend_data(self, days: int = 7) -> Dict:
        """
        Get query volume trends over time.
        
        MVP: Returns simulated trend data
        PRODUCTION: Query from data warehouse with actual timestamps
        
        Args:
            days: Number of days to include
            
        Returns:
            Dict with daily query volumes
        """
        # Simulated trend data
        import random
        from datetime import timedelta
        
        trends = []
        base_volume = 150
        
        for i in range(days, 0, -1):
            date = datetime.now() - timedelta(days=i)
            # Add some variance
            volume = base_volume + random.randint(-30, 50)
            trends.append({
                "date": date.strftime("%Y-%m-%d"),
                "queries": volume,
                "automated": int(volume * 0.73),
                "escalated": int(volume * 0.27)
            })
        
        return {
            "period_days": days,
            "data": trends,
            "summary": {
                "total_queries": sum(t["queries"] for t in trends),
                "avg_daily": sum(t["queries"] for t in trends) // days,
                "trend": "stable"
            }
        }

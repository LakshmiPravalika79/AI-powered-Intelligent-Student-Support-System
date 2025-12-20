# Data Layer - Mock Databases & Legacy Systems 📊

This folder contains **simulated data** that mimics real university databases and legacy systems.

## Files

### `mock_database.py` - Core Application Data

Contains all the mock data for the MVP:

```python
# Student Records
STUDENTS = {
    "STU2024001": {
        "name": "Sarah Johnson",
        "program": "Computer Science",
        "gpa": 3.75,
        ...
    }
}

# User Authentication
USERS = {
    "sarah.johnson@techedu.edu": {...},  # Student
    "advisor.smith@techedu.edu": {...},  # Staff
    "admin@techedu.edu": {...}           # Admin
}

# AI Knowledge Base
KNOWLEDGE_BASE = {
    "financial_aid": [...],
    "registration": [...],
    "housing": [...]
}
```

### `legacy_systems.py` - Enterprise System Simulators

Simulates 6 university legacy systems with realistic data:

| Class | Real System | Data Provided |
|-------|-------------|---------------|
| `AdmissionsSystem` | Ellucian Banner | Enrollment status, admission date |
| `AcademicSystem` | Oracle PeopleSoft | GPA, credits, courses, grades |
| `FinancialAidSystem` | PowerFAIDS | Aid packages, scholarships, loans |
| `HousingSystem` | StarRez | Room assignments, meal plans |
| `DirectoryService` | Active Directory | Contact info, emergency contacts |
| `LibrarySystem` | Ex Libris Alma | Books checked out, fines |

## Why Mock Data?

1. **Zero Setup**: No database installation required
2. **Consistent Demos**: Same data every time you restart
3. **Easy Testing**: Predictable values for testing
4. **FERPA Safe**: No real student data involved

## Production Migration

To move to real databases, replace function calls:

```python
# Current (Mock)
student = STUDENTS.get(student_id)

# Production (PostgreSQL)
student = db.query(Student).filter(Student.id == student_id).first()
```

The architecture is already designed for this swap!

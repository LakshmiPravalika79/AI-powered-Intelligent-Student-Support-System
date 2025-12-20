# Models Layer - Data Schemas 📋

This folder contains **Pydantic models** for request/response validation.

## File

### `schemas.py` - All Data Models

Defines the shape of data flowing through the API.

## Key Models

### Authentication
```python
class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    email: str
    role: str  # "student", "staff", "admin"
    student_id: Optional[str]
```

### Chat
```python
class ChatRequest(BaseModel):
    student_id: str
    message: str

class QueryResponse(BaseModel):
    text: str
    category: str      # "financial_aid", "registration", etc.
    confidence: float  # 0.0 - 1.0
    sources: List[str]
```

### Students
```python
class Student(BaseModel):
    id: str
    name: str
    email: str
    program: str
    gpa: float
    year: int
```

### Tickets
```python
class TicketCreate(BaseModel):
    query: str
    category: str
    ai_confidence: float

class TicketMessage(BaseModel):
    sender: str       # "student", "staff"
    sender_name: str
    message: str
    timestamp: datetime
```

## Why Pydantic?

1. **Automatic Validation**: Invalid data rejected with clear errors
2. **Documentation**: Auto-generates OpenAPI/Swagger docs
3. **Type Safety**: IDE autocomplete and error checking
4. **Serialization**: Easy JSON conversion

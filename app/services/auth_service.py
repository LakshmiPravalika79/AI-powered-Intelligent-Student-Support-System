"""
================================================================================
AUTHENTICATION SERVICE
================================================================================

Handles user authentication, JWT token management, and authorization.

MVP IMPLEMENTATION:
- JWT tokens with configurable expiration
- Password hashing with bcrypt
- In-memory user store

PRODUCTION ENHANCEMENTS:
- Azure AD / Okta integration (SAML/OAuth2)
- Multi-factor authentication
- Token refresh mechanism
- Session management
- Audit logging

SECURITY NOTES:
- Secret key should be in Azure Key Vault / AWS Secrets Manager
- Use HTTPS in production
- Implement rate limiting for login attempts
================================================================================
"""

import os
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

# ================================================================================
# CONFIGURATION
# ================================================================================
"""
PRODUCTION: These values should come from:
- Azure Key Vault
- AWS Secrets Manager
- Environment variables (loaded via Azure App Configuration)

NEVER commit real secrets to source control!
"""

SECRET_KEY = os.getenv("SECRET_KEY", "mvp-demo-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("TOKEN_EXPIRE_MINUTES", "30"))

# Simple password functions for MVP (avoiding bcrypt compatibility issues)
# PRODUCTION: Use proper bcrypt via passlib with compatible versions
def simple_hash(password: str) -> str:
    """Simple SHA-256 hash for MVP demo. NOT for production use."""
    return hashlib.sha256(password.encode()).hexdigest()

def simple_verify(password: str, hashed: str) -> bool:
    """Verify password against simple hash."""
    return simple_hash(password) == hashed

# OAuth2 scheme for token extraction from request headers
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class AuthService:
    """
    Authentication service handling login, tokens, and user validation.
    
    ARCHITECTURE:
    ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
    │   Client    │────▶│  AuthService│────▶│  User Store │
    │  (Browser)  │     │   (JWT)     │     │ (Mock/LDAP) │
    └─────────────┘     └─────────────┘     └─────────────┘
          │                   │
          │   Bearer Token    │
          ◀───────────────────┘
    
    PRODUCTION:
    - Replace mock user store with LDAP/Active Directory
    - Add Azure AD B2C for external identity
    - Implement OAuth2 flows for third-party apps
    """
    
    def __init__(self, db):
        """
        Initialize auth service with database reference.
        
        Args:
            db: MockDatabase instance (or real DB in production)
        """
        self.db = db
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        MVP: Uses simple SHA-256 hash.
        PRODUCTION: Use bcrypt for secure password comparison.
        """
        return simple_verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """
        Hash a password for storage.
        
        MVP: Uses simple SHA-256 hash.
        PRODUCTION: Use bcrypt with automatic salt generation.
        """
        return simple_hash(password)
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """
        Authenticate user with username and password.
        
        FLOW:
        1. Lookup user by username (email)
        2. Verify password hash
        3. Return user data or None
        
        PRODUCTION ENHANCEMENTS:
        - Lock account after N failed attempts
        - Log authentication events for security audit
        - Check if account is disabled/suspended
        - Verify email is confirmed
        
        Args:
            username: User's email address
            password: Plain-text password
            
        Returns:
            User dict if authenticated, None otherwise
        """
        user = self.db.get_user(username)
        
        if not user:
            # User not found
            return None
        
        if not self.verify_password(password, user["hashed_password"]):
            # Wrong password
            return None
        
        return user
    
    def create_access_token(
        self, 
        data: dict, 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT access token.
        
        TOKEN STRUCTURE:
        {
            "sub": "user@email.com",  # Subject (username)
            "exp": 1234567890,        # Expiration timestamp
            "iat": 1234567000,        # Issued at
            "type": "access"          # Token type
        }
        
        PRODUCTION ENHANCEMENTS:
        - Add refresh token mechanism
        - Include user roles/permissions in token
        - Add audience claim for multi-tenant
        - Sign with RS256 (asymmetric) for microservices
        
        Args:
            data: Payload data (must include 'sub' for subject)
            expires_delta: Optional custom expiration time
            
        Returns:
            Encoded JWT string
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    async def get_current_user(self, token: str = Depends(oauth2_scheme)) -> Dict:
        """
        Dependency to get current authenticated user from token.
        
        Use as FastAPI dependency:
        ```python
        @app.get("/protected")
        async def protected_route(user: Dict = Depends(auth_service.get_current_user)):
            return {"user": user["username"]}
        ```
        
        FLOW:
        1. Extract token from Authorization header
        2. Decode and validate JWT
        3. Lookup user from token subject
        4. Return user data or raise 401
        
        PRODUCTION:
        - Cache user lookups (Redis)
        - Validate token against revocation list
        - Check user status (active, suspended, etc.)
        
        Args:
            token: JWT from Authorization header (injected by FastAPI)
            
        Returns:
            User dict
            
        Raises:
            HTTPException 401 if token invalid or user not found
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            # Decode token
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            
            if username is None:
                raise credentials_exception
                
            # Check token type
            if payload.get("type") != "access":
                raise credentials_exception
                
        except JWTError:
            raise credentials_exception
        
        # Lookup user
        user = self.db.get_user(username)
        
        if user is None:
            raise credentials_exception
        
        return user
    
    def get_user_role(self, user: Dict) -> str:
        """
        Get user's role for authorization checks.
        
        ROLES:
        - student: Regular student access
        - admin: Full administrative access
        - staff: Limited admin access
        
        PRODUCTION:
        - Role-based access control (RBAC)
        - Permission-based access
        - Resource-level authorization
        """
        return user.get("role", "student")

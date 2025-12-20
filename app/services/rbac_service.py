"""
================================================================================
ROLE-BASED ACCESS CONTROL (RBAC) SERVICE
================================================================================

Implements role-based authorization for the UniAssist Pro system.

ROLES:
------
1. STUDENT - Regular student users
   - View own profile
   - Submit queries
   - View own query history

2. STAFF - University staff (advisors, support)
   - View assigned students
   - View student profiles (assigned)
   - Handle escalations
   - View analytics

3. ADMIN - System administrators
   - Full system access
   - View all students
   - System configuration
   - Analytics access
   - ESB monitoring
   - User management

PERMISSIONS MODEL:
-----------------
┌────────────────────┬─────────┬─────────┬─────────┐
│ Permission         │ Student │ Staff   │ Admin   │
├────────────────────┼─────────┼─────────┼─────────┤
│ view_own_profile   │    ✓    │    ✓    │    ✓    │
│ submit_query       │    ✓    │    ✓    │    ✓    │
│ view_own_history   │    ✓    │    ✓    │    ✓    │
│ view_any_student   │    ✗    │    ✓    │    ✓    │
│ view_all_students  │    ✗    │    ✗    │    ✓    │
│ view_analytics     │    ✗    │    ✓    │    ✓    │
│ view_esb_status    │    ✗    │    ✗    │    ✓    │
│ manage_users       │    ✗    │    ✗    │    ✓    │
│ system_config      │    ✗    │    ✗    │    ✓    │
│ view_all_queries   │    ✗    │    ✗    │    ✓    │
└────────────────────┴─────────┴─────────┴─────────┘
================================================================================
"""

from enum import Enum
from typing import List, Dict, Optional, Set
from fastapi import HTTPException, status


class Role(str, Enum):
    """User roles in the system."""
    STUDENT = "student"
    STAFF = "staff"
    ADMIN = "admin"


class Permission(str, Enum):
    """System permissions."""
    # Profile permissions
    VIEW_OWN_PROFILE = "view_own_profile"
    VIEW_ANY_STUDENT = "view_any_student"
    VIEW_ALL_STUDENTS = "view_all_students"
    
    # Query permissions
    SUBMIT_QUERY = "submit_query"
    VIEW_OWN_HISTORY = "view_own_history"
    VIEW_ALL_QUERIES = "view_all_queries"
    
    # Analytics permissions
    VIEW_ANALYTICS = "view_analytics"
    VIEW_DETAILED_ANALYTICS = "view_detailed_analytics"
    
    # System permissions
    VIEW_ESB_STATUS = "view_esb_status"
    VIEW_LEGACY_SYSTEMS = "view_legacy_systems"
    MANAGE_USERS = "manage_users"
    SYSTEM_CONFIG = "system_config"


# Role to Permission mapping
ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.STUDENT: {
        Permission.VIEW_OWN_PROFILE,
        Permission.SUBMIT_QUERY,
        Permission.VIEW_OWN_HISTORY,
    },
    Role.STAFF: {
        Permission.VIEW_OWN_PROFILE,
        Permission.SUBMIT_QUERY,
        Permission.VIEW_OWN_HISTORY,
        Permission.VIEW_ANY_STUDENT,
        Permission.VIEW_ANALYTICS,
    },
    Role.ADMIN: {
        Permission.VIEW_OWN_PROFILE,
        Permission.SUBMIT_QUERY,
        Permission.VIEW_OWN_HISTORY,
        Permission.VIEW_ANY_STUDENT,
        Permission.VIEW_ALL_STUDENTS,
        Permission.VIEW_ALL_QUERIES,
        Permission.VIEW_ANALYTICS,
        Permission.VIEW_DETAILED_ANALYTICS,
        Permission.VIEW_ESB_STATUS,
        Permission.VIEW_LEGACY_SYSTEMS,
        Permission.MANAGE_USERS,
        Permission.SYSTEM_CONFIG,
    }
}


class RBACService:
    """
    Role-Based Access Control service.
    
    Handles authorization checks for all system operations.
    """
    
    # Class-level reference to role permissions for external access
    ROLE_PERMISSIONS = ROLE_PERMISSIONS
    
    def __init__(self, db):
        """
        Initialize RBAC service with database reference.
        
        Args:
            db: MockDatabase instance
        """
        self.db = db
    
    def get_user_role(self, username: str) -> Role:
        """
        Get user's role by username.
        
        Args:
            username: User's email/username
            
        Returns:
            Role enum value
        """
        user = self.db.users.get(username, {})
        role_str = user.get("role", "student")
        try:
            return Role(role_str)
        except ValueError:
            return Role.STUDENT
    
    def get_permissions(self, username: str) -> Set[Permission]:
        """
        Get all permissions for a user.
        
        Args:
            username: User's email/username
            
        Returns:
            Set of Permission values
        """
        role = self.get_user_role(username)
        return ROLE_PERMISSIONS.get(role, set())
    
    def has_permission(self, username: str, permission: Permission) -> bool:
        """
        Check if user has a specific permission.
        
        Args:
            username: User's email/username
            permission: Permission to check
            
        Returns:
            True if user has permission
        """
        permissions = self.get_permissions(username)
        return permission in permissions
    
    def check_permission(self, username: str, permission: Permission) -> None:
        """
        Check permission and raise exception if denied.
        
        Args:
            username: User's email/username
            permission: Required permission
            
        Raises:
            HTTPException: If permission denied
        """
        if not self.has_permission(username, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission.value} required"
            )
    
    def can_view_student(self, username: str, target_student_id: str) -> bool:
        """
        Check if user can view a specific student's data.
        
        Rules:
        - Students can only view their own data
        - Staff can view any student
        - Admin can view all students
        
        Args:
            username: Requesting user's email
            target_student_id: Student ID to access
            
        Returns:
            True if access allowed
        """
        user = self.db.users.get(username, {})
        role = self.get_user_role(username)
        
        # Admin can view all
        if role == Role.ADMIN:
            return True
        
        # Staff can view any student
        if role == Role.STAFF:
            return True
        
        # Students can only view themselves
        if role == Role.STUDENT:
            return user.get("student_id") == target_student_id
        
        return False
    
    def is_admin(self, username: str) -> bool:
        """Check if user is admin."""
        return self.get_user_role(username) == Role.ADMIN
    
    def is_staff_or_admin(self, username: str) -> bool:
        """Check if user is staff or admin."""
        role = self.get_user_role(username)
        return role in [Role.STAFF, Role.ADMIN]
    
    @staticmethod
    def get_role_from_dict(user: Dict) -> Role:
        """
        Get user's role from user data dictionary.
        
        Args:
            user: User dictionary from auth
            
        Returns:
            Role enum value
        """
        role_str = user.get("role", "student")
        try:
            return Role(role_str)
        except ValueError:
            return Role.STUDENT

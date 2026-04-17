"""
Data models for the Enterprise Device Replacement System.
Simplified to use basic types and enumerations only.
"""
from enum import Enum


class EmployeeStatus(str, Enum):
    """Employee status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    TERMINATED = "terminated"


class DeviceCategory(str, Enum):
    """Device category enumeration."""
    STANDARD = "Standard"
    MAC = "Mac"
    HIGH_SPEC = "High-Spec"
    WORKSTATION = "Workstation"


class ApprovalStatus(str, Enum):
    """Approval status enumeration."""
    PENDING = "Pending"
    APPROVED = "Approved"
    DENIED = "Denied"
    EXPIRED = "Expired"


class TicketStatus(str, Enum):
    """ServiceNow ticket status enumeration."""
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    PENDING_APPROVAL = "Pending Approval"
    APPROVED = "Approved"
    ORDERED = "Ordered"
    SHIPPED = "Shipped"
    DELIVERED = "Delivered"
    CLOSED = "Closed"
    CANCELLED = "Cancelled"


class TicketPriority(str, Enum):
    """ServiceNow ticket priority enumeration."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class RequestType(str, Enum):
    """Request type enumeration."""
    NEW_EMPLOYEE = "new_employee"
    REFRESH = "refresh"
    MANAGER_REQUEST = "manager_request"
    REPLACEMENT = "replacement"


# Made with Bob

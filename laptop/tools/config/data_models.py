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


class CatalogItemCategory(str, Enum):
    """Catalog item category enumeration."""
    ACCESS = "Access"
    SOFTWARE = "Software"
    HARDWARE = "Hardware"
    SERVICE = "Service"
    TEMPLATE = "Template"


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
    CATALOG_ORDER = "catalog_order"
    MANAGER_REQUEST = "manager_request"
    SELF_SERVICE = "self_service"


# Made with Bob

"""
Utility tools for common operations across the system.
Provides helper functions for validation, formatting, and ID generation.
"""
import re
import uuid
from typing import Optional, Dict, Any
from datetime import datetime
import logging

from ibm_watsonx_orchestrate.agent_builder.tools import tool

logger = logging.getLogger(__name__)


@tool
def validate_business_justification(justification: str) -> Dict[str, Any]:
    """
    Validate business justification text for device requests.
    
    This tool validates that a business justification meets minimum requirements
    including length constraints, content quality, and appropriateness. Returns
    detailed validation results with suggestions for improvement if invalid.
    
    Parameters:
        justification (str): The business justification text to validate (e.g., "Need Mac for iOS development")
        
    Returns:
        dict: Validation result dictionary containing:
            - valid (bool): Whether the justification is valid
            - reason (str): Explanation of validation result
            - suggestions (list, optional): Suggestions for improvement if invalid
            - character_count (int, optional): Character count if valid
        
    Example:
        result = validate_business_justification("Need Mac for iOS development")
        if result['valid']:
            print("Valid justification")
        else:
            print(f"Invalid: {result['reason']}")
            for suggestion in result.get('suggestions', []):
                print(f"- {suggestion}")
    """
    if not justification or not justification.strip():
        return {
            "valid": False,
            "reason": "Justification cannot be empty",
            "suggestions": ["Please provide a clear business reason for this request"]
        }
    
    # Check minimum length
    if len(justification.strip()) < 10:
        return {
            "valid": False,
            "reason": "Justification too short",
            "suggestions": ["Please provide more detail (at least 10 characters)"]
        }
    
    # Check maximum length
    if len(justification) > 500:
        return {
            "valid": False,
            "reason": "Justification too long",
            "suggestions": ["Please keep justification under 500 characters"]
        }
    
    # Check for inappropriate content (basic check)
    inappropriate_patterns = [
        r'\b(test|testing|asdf|qwerty)\b',
        r'^[a-z]{1,3}$',  # Very short words
    ]
    
    for pattern in inappropriate_patterns:
        if re.search(pattern, justification.lower()):
            return {
                "valid": False,
                "reason": "Justification appears incomplete or invalid",
                "suggestions": ["Please provide a meaningful business justification"]
            }
    
    return {
        "valid": True,
        "reason": "Justification is valid",
        "character_count": len(justification)
    }


@tool
def format_confirmation_summary(
    employee_name: str,
    employee_title: str,
    employee_email: str,
    device_model_name: str,
    device_sys_id: str,
    requestor_name: str,
    justification: str,
    manager_email: Optional[str] = None,
    approval_required: bool = False
) -> str:
    """
    Format a human-readable confirmation summary for device requests.
    
    This tool creates a formatted text summary of a device request including
    employee details, selected device name with sys_id, and justification for the request.
    
    Parameters:
        employee_name (str): Full name of the employee (e.g., "John Smith")
        employee_title (str): Employee's job title (e.g., "Software Engineer")
        employee_email (str): Employee's email address (e.g., "john.smith@company.com")
        device_model_name (str): Name of the device model (e.g., "MacBook Pro 14in")
        device_sys_id (str): ServiceNow sys_id of the selected device (e.g., "abc123def456")
        requestor_name (str): Full name of the person making the request (e.g., "Jane Doe")
        justification (str): Reason for the device request (user-provided or auto-generated from eligibility)
        manager_email (str, optional): Manager's email address if approval required. Default: None
        approval_required (bool, optional): Whether manager approval is needed. Default: False
        
    Returns:
        str: Multi-line formatted summary text with emoji indicators and clear sections
        
    Example:
        summary = format_confirmation_summary(
            employee_name="John Smith",
            employee_title="Software Engineer",
            employee_email="john.smith@company.com",
            device_model_name="MacBook Pro 14in",
            device_sys_id="abc123def456",
            requestor_name="Jane Doe",
            justification="Device is over 3 years old and eligible for refresh",
            manager_email="manager@company.com",
            approval_required=False
        )
        print(summary)
    """
    summary_lines = [
        "📋 Request Summary",
        "=" * 50,
        "",
        f"Employee: {employee_name}",
        f"Title: {employee_title}",
        f"Email: {employee_email}",
        "",
        f"Device: {device_model_name}",
        f"Device ID: {device_sys_id}",
        "",
        f"Requested by: {requestor_name}",
        "",
        "Justification:",
        f"  {justification}"
    ]
    
    if approval_required:
        summary_lines.extend([
            "",
            "⚠️  Manager approval required",
            f"Approval will be sent to: {manager_email}"
        ])
    else:
        summary_lines.extend([
            "",
            "✅ No approval required - proceeding with request"
        ])
    
    return "\n".join(summary_lines)


@tool
def generate_request_id(prefix: str = "REQ") -> str:
    """
    Generate a unique identifier for device requests.
    
    This tool creates a unique request ID combining a prefix, timestamp,
    and random UUID component. Ensures uniqueness across all requests.
    
    Parameters:
        prefix (str, optional): Prefix for the ID (e.g., "REQ", "APPROVAL"). Default: "REQ"
        
    Returns:
        str: Unique request ID in format: PREFIX-YYYYMMDD-XXXXXXXX
        
    Example:
        request_id = generate_request_id("REQ")
        print(request_id)  # Output: REQ-20260213-A1B2C3D4
        
        approval_id = generate_request_id("APPROVAL")
        print(approval_id)  # Output: APPROVAL-20260213-D4E5F6G7
    """
    unique_part = uuid.uuid4().hex[:8].upper()
    timestamp = datetime.now().strftime("%Y%m%d")
    return f"{prefix}-{timestamp}-{unique_part}"

# Made with Bob

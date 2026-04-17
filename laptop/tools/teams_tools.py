"""
Microsoft Teams notification tools for sending messages and adaptive cards.
Provides functions for Teams integration including approval notifications.
"""
import requests
from typing import Optional, Dict, Any
from functools import wraps
import time
import logging

from ibm_watsonx_orchestrate.agent_builder.tools import tool

logger = logging.getLogger(__name__)


def retry_with_backoff(max_retries: int = 3, backoff_factor: int = 2):
    """Decorator for retrying failed API calls with exponential backoff."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.RequestException as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Max retries reached for {func.__name__}: {str(e)}")
                        raise
                    wait_time = backoff_factor ** attempt
                    logger.warning(f"Retry {attempt + 1}/{max_retries} after {wait_time}s")
                    time.sleep(wait_time)
        return wrapper
    return decorator


# ============================================================================
# LEGACY TEAMS API TOOLS - PRESERVED FOR FUTURE INTEGRATION
# These tools use Microsoft Graph API and are currently commented out
# Uncomment when Teams API credentials are configured
# ============================================================================

# def get_teams_token() -> str:
#     """
#     Get OAuth token for Microsoft Teams API.
#
#     Returns:
#         str: Bearer token
#     """
#     response = requests.post(
#         settings["teams"]["token_endpoint"],
#         data={
#             "grant_type": "client_credentials",
#             "client_id": settings["teams"]["client_id"],
#             "client_secret": settings["teams"]["client_secret"],
#             "scope": "https://graph.microsoft.com/.default"
#         }
#     )
#     response.raise_for_status()
#     return response.json()["access_token"]


# def get_user_id_by_email(email: str) -> Optional[str]:
#     """
#     Get Teams user ID by email address.
#
#     Args:
#         email: User email address
#
#     Returns:
#         User ID if found, None otherwise
#     """
#     try:
#         token = get_teams_token()
#         headers = {
#             "Authorization": f"Bearer {token}",
#             "Content-Type": "application/json"
#         }
#
#         response = requests.get(
#             f"{settings['teams']['api_url']}/users/{email}",
#             headers=headers
#         )
#
#         if response.status_code == 404:
#             logger.warning(f"User not found in Teams: {email}")
#             return None
#
#         response.raise_for_status()
#         return response.json()["id"]
#
#     except Exception as e:
#         logger.error(f"Error getting Teams user ID for {email}: {str(e)}")
#         return None


# @tool
# @retry_with_backoff()
# def send_teams_message(
#     recipient_email: str,
#     subject: str,
#     body: str
# ) -> bool:
#     """
#     Send a text message to a user via Microsoft Teams chat.
#
#     This tool sends a direct message to a user in Microsoft Teams. It creates
#     a one-on-one chat if needed and delivers the message with the specified
#     subject and body content. Supports both plain text and HTML formatting.
#
#     Parameters:
#         recipient_email (str): Email address of the message recipient (e.g., "user@company.com")
#         subject (str): Subject line for the message (e.g., "Device Request Update")
#         body (str): Message content - supports plain text or HTML formatting (e.g., "Your device request has been approved.")
#
#     Returns:
#         bool: True if message was sent successfully, False if recipient not found
#
#     Example:
#         success = send_teams_message(
#             recipient_email="user@company.com",
#             subject="Device Request Update",
#             body="Your device request has been approved and will be delivered in 5 days."
#         )
#         if success:
#             print("Message sent successfully")
#     """
#     try:
#         token = get_teams_token()
#         headers = {
#             "Authorization": f"Bearer {token}",
#             "Content-Type": "application/json"
#         }
#
#         user_id = get_user_id_by_email(recipient_email)
#         if not user_id:
#             logger.error(f"Cannot send message: user not found {recipient_email}")
#             return False
#
#         # Create chat with user
#         chat_data = {
#             "chatType": "oneOnOne",
#             "members": [
#                 {
#                     "@odata.type": "#microsoft.graph.aadUserConversationMember",
#                     "roles": ["owner"],
#                     "user@odata.bind": f"{settings['teams']['api_url']}/users('{user_id}')"
#                 }
#             ]
#         }
#
#         response = requests.post(
#             f"{settings['teams']['api_url']}/chats",
#             headers=headers,
#             json=chat_data
#         )
#         response.raise_for_status()
#         chat_id = response.json()["id"]
#
#         # Send message to chat
#         message_data = {
#             "body": {
#                 "contentType": "html",
#                 "content": f"<h3>{subject}</h3><p>{body}</p>"
#             }
#         }
#
#         response = requests.post(
#             f"{settings['teams']['api_url']}/chats/{chat_id}/messages",
#             headers=headers,
#             json=message_data
#         )
#         response.raise_for_status()
#
#         logger.info(f"Sent Teams message to {recipient_email}")
#         return True
#
#     except Exception as e:
#         logger.error(f"Error sending Teams message to {recipient_email}: {str(e)}")
#         raise


# def send_teams_adaptive_card(
#     recipient_email: str,
#     card_data: Dict[str, Any]
# ) -> bool:
#     """
#     Send an interactive adaptive card to a user via Microsoft Teams.
#
#     This tool sends a rich, interactive adaptive card to a user in Microsoft Teams.
#     Adaptive cards can include formatted text, images, buttons, and interactive
#     elements. Commonly used for approval requests and notifications.
#
#     Parameters:
#         recipient_email (str): Email address of the card recipient (e.g., "manager@company.com")
#         card_data (dict): Adaptive card JSON structure following Microsoft Adaptive Card schema v1.4
#
#     Returns:
#         bool: True if card was sent successfully, False if recipient not found
#
#     Example:
#         card = {
#             "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
#             "type": "AdaptiveCard",
#             "version": "1.4",
#             "body": [{"type": "TextBlock", "text": "Hello!"}]
#         }
#         success = send_teams_adaptive_card("user@company.com", card)
#     """
#     try:
#         token = get_teams_token()
#         headers = {
#             "Authorization": f"Bearer {token}",
#             "Content-Type": "application/json"
#         }
#
#         user_id = get_user_id_by_email(recipient_email)
#         if not user_id:
#             logger.error(f"Cannot send card: user not found {recipient_email}")
#             return False
#
#         # Create chat with user
#         chat_data = {
#             "chatType": "oneOnOne",
#             "members": [
#                 {
#                     "@odata.type": "#microsoft.graph.aadUserConversationMember",
#                     "roles": ["owner"],
#                     "user@odata.bind": f"{settings['teams']['api_url']}/users('{user_id}')"
#                 }
#             ]
#         }
#
#         response = requests.post(
#             f"{settings['teams']['api_url']}/chats",
#             headers=headers,
#             json=chat_data
#         )
#         response.raise_for_status()
#         chat_id = response.json()["id"]
#
#         # Send adaptive card to chat
#         message_data = {
#             "body": {
#                 "contentType": "html",
#                 "content": "<attachment id=\"1\"></attachment>"
#             },
#             "attachments": [
#                 {
#                     "id": "1",
#                     "contentType": "application/vnd.microsoft.card.adaptive",
#                     "content": card_data
#                 }
#             ]
#         }
#
#         response = requests.post(
#             f"{settings['teams']['api_url']}/chats/{chat_id}/messages",
#             headers=headers,
#             json=message_data
#         )
#         response.raise_for_status()
#
#         logger.info(f"Sent Teams adaptive card to {recipient_email}")
#         return True
#
#     except Exception as e:
#         logger.error(f"Error sending Teams adaptive card to {recipient_email}: {str(e)}")
#         raise


# def create_approval_card(
#     employee_name: str,
#     employee_id: str,
#     device_model: str,
#     requestor_name: str,
#     requestor_email: str,
#     approval_id: str,
#     approval_url: str,
#     business_justification: Optional[str] = None
# ) -> Dict[str, Any]:
#     """
#     Create a formatted adaptive card for device approval requests.
#
#     This tool generates a Microsoft Teams adaptive card with approval request
#     details and action buttons. The card includes employee information, device
#     details, business justification, and approve/deny buttons.
#
#     Parameters:
#         employee_name (str): Name of employee requesting device (e.g., "John Smith")
#         employee_id (str): Employee ID (e.g., "EMP12345")
#         device_model (str): Device model name (e.g., "MacBook Pro 14in")
#         requestor_name (str): Name of person making request (e.g., "Jane Doe")
#         requestor_email (str): Email of requestor (e.g., "jane.doe@company.com")
#         approval_id (str): Unique approval identifier (e.g., "APPROVAL-20260213-A1B2C3D4")
#         approval_url (str): URL for approval actions (e.g., "https://approval.company.com/approve/123")
#         business_justification (str, optional): Reason for request. Default: None
#
#     Returns:
#         dict: Adaptive card JSON structure ready to send via Teams
#
#     Example:
#         card = create_approval_card(
#             employee_name="John Smith",
#             employee_id="EMP12345",
#             device_model="MacBook Pro 14in",
#             requestor_name="Jane Doe",
#             requestor_email="jane.doe@company.com",
#             approval_id="APPROVAL-20260213-A1B2C3D4",
#             approval_url="https://approval.company.com/approve/123",
#             business_justification="iOS development work"
#         )
#         send_teams_adaptive_card(manager_email, card)
#     """
#     card = {
#         "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
#         "type": "AdaptiveCard",
#         "version": "1.4",
#         "body": [
#             {
#                 "type": "TextBlock",
#                 "text": "Device Approval Request",
#                 "weight": "Bolder",
#                 "size": "Large",
#                 "color": "Accent"
#             },
#             {
#                 "type": "FactSet",
#                 "facts": [
#                     {
#                         "title": "Employee:",
#                         "value": f"{employee_name} ({employee_id})"
#                     },
#                     {
#                         "title": "Device:",
#                         "value": device_model
#                     },
#                     {
#                         "title": "Requested by:",
#                         "value": f"{requestor_name} ({requestor_email})"
#                     },
#                     {
#                         "title": "Approval ID:",
#                         "value": approval_id
#                     }
#                 ]
#             }
#         ],
#         "actions": [
#             {
#                 "type": "Action.OpenUrl",
#                 "title": "Approve",
#                 "url": f"{approval_url}?action=approve",
#                 "style": "positive"
#             },
#             {
#                 "type": "Action.OpenUrl",
#                 "title": "Deny",
#                 "url": f"{approval_url}?action=deny",
#                 "style": "destructive"
#             }
#         ]
#     }
#
#     # Add business justification if provided
#     if business_justification:
#         card["body"].insert(2, {
#             "type": "TextBlock",
#             "text": "Business Justification:",
#             "weight": "Bolder",
#             "spacing": "Medium"
#         })
#         card["body"].insert(3, {
#             "type": "TextBlock",
#             "text": business_justification,
#             "wrap": True,
#             "spacing": "Small"
#         })
#
#     return card


# @tool
# @retry_with_backoff()
# def send_approval_notification(
#     manager_email: str,
#     employee_name: str,
#     employee_id: str,
#     device_model: str,
#     requestor_name: str,
#     requestor_email: str,
#     approval_id: str,
#     approval_url: str,
#     business_justification: Optional[str] = None
# ) -> bool:
#     """
#     Send device approval request notification to manager via Teams.
#
#     This tool creates and sends an interactive approval card to the employee's
#     manager via Microsoft Teams. The card includes all request details and
#     approve/deny action buttons for quick decision-making.
#
#     Parameters:
#         manager_email (str): Manager's email address (recipient, e.g., "manager@company.com")
#         employee_name (str): Name of employee requesting device (e.g., "John Smith")
#         employee_id (str): Employee ID (e.g., "EMP12345")
#         device_model (str): Device model being requested (e.g., "MacBook Pro 14in")
#         requestor_name (str): Name of person making request (e.g., "Jane Doe")
#         requestor_email (str): Email of requestor (e.g., "jane.doe@company.com")
#         approval_id (str): Unique approval identifier (e.g., "APPROVAL-20260213-A1B2C3D4")
#         approval_url (str): URL for approval actions (e.g., "https://approval.company.com/approve/123")
#         business_justification (str, optional): Reason for request. Default: None
#
#     Returns:
#         bool: True if notification was sent successfully, False otherwise
#
#     Example:
#         success = send_approval_notification(
#             manager_email="manager@company.com",
#             employee_name="John Smith",
#             employee_id="EMP12345",
#             device_model="MacBook Pro 14in",
#             requestor_name="Jane Doe",
#             requestor_email="jane.doe@company.com",
#             approval_id="APPROVAL-20260213-A1B2C3D4",
#             approval_url="https://approval.company.com/approve/123",
#             business_justification="iOS development work"
#         )
#         if success:
#             print("Approval request sent to manager")
#     """
#     try:
#         card = create_approval_card(
#             employee_name=employee_name,
#             employee_id=employee_id,
#             device_model=device_model,
#             requestor_name=requestor_name,
#             requestor_email=requestor_email,
#             approval_id=approval_id,
#             approval_url=approval_url,
#             business_justification=business_justification
#         )
#         return send_teams_adaptive_card(manager_email, card)
#
#     except Exception as e:
#         logger.error(f"Error sending approval notification: {str(e)}")
#         raise


# ============================================================================
# ACTIVE NOTIFICATION TOOLS - MOCK IMPLEMENTATION
# These tools simulate Teams notifications until API is configured
# ============================================================================

@tool
def send_employee_confirmation(
    employee_email: str,
    employee_name: str,
    ticket_number: str,
    device_model: str
) -> Dict[str, Any]:
    """
    Send device request confirmation to employee via Teams.
    
    This tool sends a confirmation message to the employee who will receive
    the device, including ticket details.
    
    Parameters:
        employee_email (str): Employee's email address (e.g., "john.smith@pnc.com")
        employee_name (str): Employee's full name (e.g., "John Smith")
        ticket_number (str): ServiceNow ticket number (e.g., "REQ0012345")
        device_model (str): Device model name (e.g., "Lenovo ThinkPad X1 Carbon")
        
    Returns:
        dict: Status with success flag, recipient, and message details
        
    Example:
        result = send_employee_confirmation(
            employee_email="john.smith@pnc.com",
            employee_name="John Smith",
            ticket_number="REQ0012345",
            device_model="Lenovo ThinkPad X1 Carbon"
        )
    """
    try:
        message = f"""Hi {employee_name},

Your device request has been submitted successfully!

📋 Ticket Number: {ticket_number}
💻 Device: {device_model}

You will receive updates as your request is processed.

Thank you,
IT Support Team"""
        
        logger.info(f"[MOCK] Employee confirmation sent to {employee_email}")
        logger.info(f"[MOCK] Message: {message}")
        
        return {
            "success": True,
            "notification_type": "employee_confirmation",
            "recipient": employee_email,
            "ticket_number": ticket_number,
            "message": message
        }
        
    except Exception as e:
        logger.error(f"Error sending employee confirmation: {str(e)}")
        return {
            "success": False,
            "notification_type": "employee_confirmation",
            "recipient": employee_email,
            "error": str(e)
        }


@tool
def send_manager_confirmation(
    manager_email: str,
    employee_name: str,
    employee_id: str,
    ticket_number: str,
    device_model: str
) -> Dict[str, Any]:
    """
    Send device request confirmation to manager via Teams.
    
    This tool sends a confirmation message to the manager when an employee
    makes a self-service device request (NOT for manager-initiated requests).
    
    Parameters:
        manager_email (str): Manager's email address (e.g., "jane.doe@pnc.com")
        employee_name (str): Employee's full name (e.g., "John Smith")
        employee_id (str): Employee ID (e.g., "E12345")
        ticket_number (str): ServiceNow ticket number (e.g., "REQ0012345")
        device_model (str): Device model name (e.g., "Lenovo ThinkPad X1 Carbon")
        
    Returns:
        dict: Status with success flag, recipient, and message details
        
    Example:
        result = send_manager_confirmation(
            manager_email="jane.doe@pnc.com",
            employee_name="John Smith",
            employee_id="E12345",
            ticket_number="REQ0012345",
            device_model="Lenovo ThinkPad X1 Carbon"
        )
    """
    try:
        message = f"""Hi,

Your team member has submitted a device request.

👤 Employee: {employee_name} ({employee_id})
📋 Ticket Number: {ticket_number}
💻 Device: {device_model}

The employee will receive their confirmation and updates separately.

Thank you,
IT Support Team"""
        
        logger.info(f"[MOCK] Manager confirmation sent to {manager_email}")
        logger.info(f"[MOCK] Message: {message}")
        
        return {
            "success": True,
            "notification_type": "manager_confirmation",
            "recipient": manager_email,
            "ticket_number": ticket_number,
            "message": message
        }
        
    except Exception as e:
        logger.error(f"Error sending manager confirmation: {str(e)}")
        return {
            "success": False,
            "notification_type": "manager_confirmation",
            "recipient": manager_email,
            "error": str(e)
        }


@tool
def send_procurement_approval(
    employee_name: str,
    employee_id: str,
    employee_title: str,
    employee_email: str,
    device_model: str,
    device_sys_id: str,
    ticket_number: str,
    requestor_name: str,
    requestor_email: str,
    business_justification: str,
    procurement_email: str = "alice.barns@pnc.com"
) -> Dict[str, Any]:
    """
    Send device request approval notification to procurement team via Teams.
    
    This tool sends a comprehensive approval request to the procurement team
    (hardcoded to Alice Barns) with all details needed for processing.
    
    Parameters:
        employee_name (str): Employee's full name (e.g., "John Smith")
        employee_id (str): Employee ID (e.g., "E12345")
        employee_title (str): Employee's job title (e.g., "Senior Data Engineer")
        employee_email (str): Employee's email (e.g., "john.smith@pnc.com")
        device_model (str): Device model name (e.g., "Lenovo ThinkPad X1 Carbon")
        device_sys_id (str): ServiceNow device sys_id (e.g., "abc123def456")
        ticket_number (str): ServiceNow ticket number (e.g., "REQ0012345")
        requestor_name (str): Name of person who made request (e.g., "Jane Doe")
        requestor_email (str): Requestor's email (e.g., "jane.doe@pnc.com")
        business_justification (str): Reason for request (e.g., "Standard 3-year refresh")
        procurement_email (str): Procurement team email (default: "alice.barns@pnc.com")
        
    Returns:
        dict: Status with success flag, recipient, and message details
        
    Example:
        result = send_procurement_approval(
            employee_name="John Smith",
            employee_id="E12345",
            employee_title="Senior Data Engineer",
            employee_email="john.smith@pnc.com",
            device_model="Lenovo ThinkPad X1 Carbon",
            device_sys_id="abc123def456",
            ticket_number="REQ0012345",
            requestor_name="Jane Doe",
            requestor_email="jane.doe@pnc.com",
            business_justification="Standard 3-year refresh cycle"
        )
    """
    try:
        message = f"""🔔 NEW DEVICE REQUEST FOR APPROVAL

📋 TICKET DETAILS
Ticket Number: {ticket_number}
Device sys_id: {device_sys_id}

👤 EMPLOYEE INFORMATION
Name: {employee_name}
Employee ID: {employee_id}
Title: {employee_title}
Email: {employee_email}

💻 DEVICE INFORMATION
Device Model: {device_model}

📝 REQUEST DETAILS
Requested By: {requestor_name} ({requestor_email})
Justification: {business_justification}

⚡ ACTION REQUIRED
Please review and process this device request in ServiceNow.

---
IT Support System"""
        
        logger.info(f"[MOCK] Procurement approval sent to {procurement_email}")
        logger.info(f"[MOCK] Message: {message}")
        
        return {
            "success": True,
            "notification_type": "procurement_approval",
            "recipient": procurement_email,
            "ticket_number": ticket_number,
            "message": message
        }
        
    except Exception as e:
        logger.error(f"Error sending procurement approval: {str(e)}")
        return {
            "success": False,
            "notification_type": "procurement_approval",
            "recipient": procurement_email,
            "error": str(e)
        }

# Made with Bob

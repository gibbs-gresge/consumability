"""
Employee profile tools for Workday integration.
Provides functions to retrieve and validate employee information.
"""
from typing import Optional, Dict, Any
import logging

from ibm_watsonx_orchestrate.agent_builder.tools import tool

logger = logging.getLogger(__name__)

# Hard-coded employee data
EMPLOYEES = [
    {
        "employeeId": "E1001",
        "name": "Tom Brady",
        "title": "Director of Data Engineering",
        "organization": "Enterprise Data Platform",
        "email": "tom.brady@pnc.com",
        "startDate": "2016-04-18",
        "manager": {
            "name": "Sandra Lopez",
            "employeeId": "E0900",
            "email": "sandra.lopez@pnc.com"
        },
        "direct_reports": [
            {
                "name": "Maya Chen",
                "employeeId": "E1002"
            },
            {
                "name": "Liam Patel",
                "employeeId": "E1003"
            },
            {
                "name": "Noah Brooks",
                "employeeId": "E1004"
            }
        ]
    },
    {
        "employeeId": "E1002",
        "name": "Maya Chen",
        "title": "Senior Data Engineer",
        "organization": "Enterprise Data Platform",
        "email": "maya.chen@pnc.com",
        "startDate": "2019-07-22",
        "manager": {
            "name": "Tom Brady",
            "employeeId": "E1001",
            "email": "tom.brady@pnc.com"
        },
        "direct_reports": []
    },
    {
        "employeeId": "E1003",
        "name": "Liam Patel",
        "title": "Data Engineer II",
        "organization": "Enterprise Data Platform",
        "email": "liam.patel@pnc.com",
        "startDate": "2021-02-15",
        "manager": {
            "name": "Tom Brady",
            "employeeId": "E1001",
            "email": "tom.brady@pnc.com"
        },
        "direct_reports": []
    },
    {
        "employeeId": "E1004",
        "name": "Noah Brooks",
        "title": "Sales Person",
        "organization": "Enterprise Sales",
        "email": "noah.brooks@pnc.com",
        "startDate": "2022-10-03",
        "manager": {
            "name": "Tom Brady",
            "employeeId": "E1001",
            "email": "tom.brady@pnc.com"
        },
        "direct_reports": []
    }
]

def transform_employee_data(employee_data: Dict[str, Any]) -> Dict[str, Any]:
    """Transform employee data from JSON format to expected profile format."""
    return {
        "employee_id": employee_data.get("employeeId"),
        "email": employee_data.get("email"),
        "full_name": employee_data.get("name"),
        "title": employee_data.get("title"),
        "role": "Standard",  # Default role
        "department": employee_data.get("organization"),
        "cost_center": None,  # Not provided in data
        "manager_id": employee_data.get("manager", {}).get("employeeId"),
        "manager_name": employee_data.get("manager", {}).get("name"),
        "manager_email": employee_data.get("manager", {}).get("email"),
        "start_date": employee_data.get("startDate"),
        "status": "Active",  # Default status
        "direct_reports": employee_data.get("direct_reports", [])
    }


@tool
def get_employee_by_id(employee_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve employee profile by employee ID from Workday.
    
    This tool retrieves detailed employee information including name, title,
    department, manager details, and employment status from the Workday system.
    
    Parameters:
        employee_id (str): The unique employee identifier (e.g., "E1001")
        
    Returns:
        dict: Employee profile dictionary containing all employee details, or None if not found
        
    Example:
        profile = get_employee_by_id("E1001")
        if profile:
            print(f"Employee: {profile['full_name']}, Title: {profile['title']}")
    """
    try:
        # Search for employee by ID
        for employee in EMPLOYEES:
            if employee.get("employeeId") == employee_id:
                profile = transform_employee_data(employee)
                logger.info(f"Retrieved employee profile: {employee_id}")
                return profile
        
        logger.info(f"Employee not found: {employee_id}")
        return None
        
    except Exception as e:
        logger.error(f"Error retrieving employee {employee_id}: {str(e)}")
        raise


@tool
def get_employee_by_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve employee profile by email address from Workday.
    
    This tool searches for an employee using their email address and returns
    their complete profile information including employee ID, title, department,
    and manager details.
    
    Parameters:
        email (str): The employee's email address (e.g., "Kai.Duty@ibm.com")
        
    Returns:
        dict: Employee profile dictionary containing all employee details, or None if not found
        
    Example:
        profile = get_employee_by_email("Kai.Duty@ibm.com")
        if profile:
            print(f"Employee ID: {profile['employee_id']}")
    """
    try:
        # Search for employee by email
        for employee in EMPLOYEES:
            if employee.get("email") == email:
                profile = transform_employee_data(employee)
                logger.info(f"Retrieved employee profile by email: {email}")
                return profile
        
        logger.info(f"Employee not found with email: {email}")
        return None
        
    except Exception as e:
        logger.error(f"Error retrieving employee by email {email}: {str(e)}")
        raise

# Made with Bob

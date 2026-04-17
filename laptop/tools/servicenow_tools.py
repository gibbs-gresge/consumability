"""
ServiceNow integration tools for catalog ordering and ticket management.
Provides functions for creating catalog item requests.
"""
import requests
from typing import Dict, Any
import logging

from ibm_watsonx_orchestrate.agent_builder.tools import tool
from ibm_watsonx_orchestrate.agent_builder.connections import ConnectionType
from ibm_watsonx_orchestrate.run import connections

logger = logging.getLogger(__name__)

# ServiceNow connection app ID
SERVICENOW_APP_ID = 'test_token'


@tool(
    expected_credentials=[
        {"app_id": SERVICENOW_APP_ID, "type": ConnectionType.BEARER_TOKEN}
    ]
)
def create_a_request(
    employee_id: str,
    item_name: str,
    comment: str
) -> Dict[str, Any]:
    """
    Create a ServiceNow catalog request.
    
    This tool creates a request in ServiceNow on behalf of an employee.
    The short_description will be formatted as "Name: [item_name]. Comment: [comment]"
    
    Args:
        employee_id (str): The employee ID for whom the request is being made
        item_name (str): The name of the catalog item being requested
        comment (str): User's comment about the request
    
    Returns:
        Dict[str, Any]: Dictionary containing:
            - request_number: The ServiceNow request number (e.g., "REQ0010153")
            - sys_id: The system ID of the created request
            - status: Status of the request
    
    Example:
        >>> result = create_a_request(
        ...     employee_id="E1001",
        ...     item_name="Grant SharePoint Access",
        ...     comment="Need SharePoint access for new project"
        ... )
        >>> print(result['request_number'])
        REQ0010153
    """
    try:
        # Get credentials from watsonx Orchestrate connection
        creds = connections.bearer_token(SERVICENOW_APP_ID)
        base_url = creds.url
        bearer_token = creds.token
        
        # Construct the API endpoint
        endpoint = f"{base_url}/api/now/table/sc_request"
        
        # Format short_description as "Name: [item_name]. Comment: [comment]"
        short_description = f"Name: {item_name}. Comment: {comment}"
        
        # Build request body
        request_body = {
            "short_description": short_description,
            "requested_for": employee_id
        }
        
        # Set headers
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {bearer_token}'
        }
        
        # Make the API request
        logger.info(f"Creating ServiceNow request for employee {employee_id}")
        response = requests.post(endpoint, headers=headers, json=request_body, timeout=30)
        
        # Check for successful response
        if response.status_code not in [200, 201]:
            error_msg = f"ServiceNow API returned status {response.status_code}"
            logger.error(f"{error_msg}: {response.text}")
            raise Exception(error_msg)
        
        # Parse response
        data = response.json()
        result = data.get('result', {})
        
        # Extract request details
        request_number = result.get('request_number', 'Unknown')
        sys_id = result.get('sys_id', 'Unknown')
        status = result.get('request_state', 'Submitted')
        
        logger.info(f"Successfully created request {request_number}")
        
        return {
            'request_number': request_number,
            'sys_id': sys_id,
            'status': status
        }
        
    except requests.exceptions.Timeout:
        logger.error("ServiceNow API request timed out")
        raise Exception("Request to ServiceNow timed out. Please try again.")
    
    except requests.exceptions.RequestException as e:
        logger.error(f"ServiceNow API request failed: {str(e)}")
        raise Exception(f"Failed to connect to ServiceNow: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error creating ServiceNow request: {str(e)}")
        raise Exception(f"Error creating request: {str(e)}")

# Made with Bob

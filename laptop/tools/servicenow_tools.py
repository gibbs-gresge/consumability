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
    item_sys_id: str,
    employee_id: str,
    short_description: str
) -> Dict[str, Any]:
    """
    Create a ServiceNow catalog item request.
    
    This tool submits an order for a catalog item on behalf of an employee.
    It creates a request in ServiceNow with the specified item and details.
    
    Args:
        item_sys_id (str): The sys_id of the catalog item to order
        employee_id (str): The employee ID for whom the request is being made
        short_description (str): A short description/comment about the request
    
    Returns:
        Dict[str, Any]: Dictionary containing:
            - request_number: The ServiceNow request number (e.g., "REQ0010153")
            - sys_id: The system ID of the created request
            - status: Status of the request
    
    Example:
        >>> result = create_a_request(
        ...     item_sys_id="011f117a9f3002002920bde8132e7020",
        ...     employee_id="E1001",
        ...     short_description="Need SharePoint access for new project"
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
        endpoint = f"{base_url}/api/sn_sc/servicecatalog/items/{item_sys_id}/order_now"
        
        # Build request body
        request_body = {
            "variables": {
                "site_url": "https://example.sharepoint.com/sites/demo",
                "old_title": "Old Site Title",
                "new_title": "New Site Title",
                "reason_for_title_change": short_description
            }
        }
        
        # Set headers
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {bearer_token}'
        }
        
        # Make the API request
        logger.info(f"Creating ServiceNow request for item {item_sys_id}, employee {employee_id}")
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

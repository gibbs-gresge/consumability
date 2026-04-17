"""
ServiceNow Catalog Item Retrieval Tool

Queries the ServiceNow catalog to retrieve items based on search criteria.
Uses bearer token authentication and returns filtered catalog items.
"""

from typing import Optional, List, Dict, Any
import requests
import logging

from ibm_watsonx_orchestrate.agent_builder.tools import tool
from ibm_watsonx_orchestrate.agent_builder.connections import ConnectionType
from ibm_watsonx_orchestrate.run import connections

logger = logging.getLogger(__name__)

# ServiceNow connection app ID
SERVICENOW_APP_ID = 'test_token'

# Hardcoded catalog ID as specified
CATALOG_ID = 'e0d08b13c3330100c8b837659bba8fb4'


@tool(
    expected_credentials=[
        {"app_id": SERVICENOW_APP_ID, "type": ConnectionType.BEARER_TOKEN}
    ]
)
def get_records(search_query: str = "sharepoint") -> List[Dict[str, str]]:
    """
    Query ServiceNow catalog items based on search criteria.
    
    This tool retrieves catalog items from ServiceNow that match the search query.
    Results are filtered to a maximum of 15 items and include the item name and sys_id.
    
    Args:
        search_query (str): Search term to filter catalog items (default: "sharepoint").
                           This will be used in a LIKE query against item names.
    
    Returns:
        List[Dict[str, str]]: List of catalog items, each containing:
            - name: The catalog item name
            - sys_id: The ServiceNow system ID for the item
        Maximum of 15 items will be returned.
    
    Examples:
        >>> items = get_records("sharepoint")
        >>> print(items[0])
        {'name': 'Grant SharePoint Access', 'sys_id': '011f117a9f3002002920bde8132e7020'}
        
        >>> items = get_records("access")
        >>> for item in items:
        ...     print(f"{item['name']} - {item['sys_id']}")
    """
    try:
        # Get credentials from watsonx Orchestrate connection
        creds = connections.bearer_token(SERVICENOW_APP_ID)
        base_url = creds.url
        bearer_token = creds.token
        
        # Construct the API endpoint
        endpoint = f"{base_url}/api/now/table/sc_cat_item"
        
        # Build query parameters
        params = {
            'sysparm_fields': 'name,sys_id',
            'sysparm_query': f'sc_catalogs={CATALOG_ID}^nameLIKE{search_query}',
            'sysparm_display_value': 'true'
        }
        
        # Set headers
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {bearer_token}'
        }
        
        # Make the API request
        logger.info(f"Querying ServiceNow catalog with search_query: {search_query}")
        response = requests.get(endpoint, headers=headers, params=params, timeout=30)
        
        # Check for successful response
        if response.status_code != 200:
            error_msg = f"ServiceNow API returned status {response.status_code}"
            logger.error(f"{error_msg}: {response.text}")
            raise Exception(error_msg)
        
        # Parse response
        data = response.json()
        result = data.get('result', [])
        
        if not result:
            logger.info(f"No catalog items found for search_query: {search_query}")
            return []
        
        # Extract name and sys_id from each item
        items = []
        for item in result:
            if 'name' in item and 'sys_id' in item:
                items.append({
                    'name': item['name'],
                    'sys_id': item['sys_id']
                })
        
        # Limit to maximum 15 items
        items = items[:15]
        
        logger.info(f"Retrieved {len(items)} catalog items")
        return items
        
    except requests.exceptions.Timeout:
        logger.error("ServiceNow API request timed out")
        raise Exception("Request to ServiceNow timed out. Please try again.")
    
    except requests.exceptions.RequestException as e:
        logger.error(f"ServiceNow API request failed: {str(e)}")
        raise Exception(f"Failed to connect to ServiceNow: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error retrieving catalog items: {str(e)}")
        raise Exception(f"Error retrieving catalog items: {str(e)}")


# Made with Bob

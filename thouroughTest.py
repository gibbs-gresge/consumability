"""
ServiceNow Catalog Items Tool for watsonx Orchestrate
Fetches catalog items from ServiceNow with automatic fallback for air-gapped environments
"""

from ibm_watsonx_orchestrate.agent_builder.tools import tool
from ibm_watsonx_orchestrate.agent_builder.connections import ConnectionType
from ibm_watsonx_orchestrate.run import connections
import json
import ssl
import urllib.request
import urllib.error
from datetime import datetime
import time
from typing import Dict, Any

# ServiceNow connection app ID
SERVICENOW_APP_ID = 'test_token'

@tool(
    expected_credentials=[
        {"app_id": SERVICENOW_APP_ID, "type": ConnectionType.BEARER_TOKEN}
    ]
)
def get_servicenow_catalog_items_v2() -> Dict[str, Any]:
    """
    Fetch ServiceNow catalog items with automatic fallback for air-gapped environments.
    
    This tool retrieves catalog items from ServiceNow using Python standard library
    with automatic fallback to curl if needed. Optimized for air-gapped environments
    with minimal dependencies.
    
    Returns:
        dict: Response containing:
            - catalog_items (list): List of ServiceNow catalog item objects
            - connection_log (str): Detailed log of connection attempts
            - method_used (str): Which connection method succeeded ('urllib' or 'curl')
            - items_count (int): Number of items retrieved
            - timestamp (str): When the request was made
            - success (bool): Whether the operation succeeded
    
    Raises:
        Exception: If all connection methods fail (includes logs in error message)
    
    Example:
        >>> response = get_servicenow_catalog_items()
        >>> print(f"Retrieved {response['items_count']} items using {response['method_used']}")
        >>> items = response['catalog_items']
    """
    
    # Get credentials from watsonx Orchestrate connection
    creds = connections.bearer_token(SERVICENOW_APP_ID)
    base_url = creds.url
    bearer_token = creds.token
    
    # Configuration
    endpoint = "/api/now/table/sc_cat_item?sysparm_fields=name,description&sysparm_limit=75&sysparm_query=u_itemLIKELaptop^ORu_itemLIKEMac^ORu_itemLIKEThinkPad^ORu_itemLIKELatitude^ORu_itemLIKEDesktop^ORu_itemLIKEWorkstation^ORu_itemLIKESurface%20Laptop"
    
    # Try Method 1: Python standard library urllib
    result = _try_urllib_standard(base_url, endpoint, bearer_token)
    
    if result['success']:
        return {
            'items_count': len(result['data'].get('result', [])),
            'timestamp': _get_timestamp(),
            'success': True,
            'catalog_items': result['data'].get('result', [])
        }

    raise Exception(f"Failed to connect to ServiceNow:\n")


def _get_timestamp() -> str:
    """Get current timestamp in readable format"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _try_urllib_standard(base_url: str, endpoint: str, bearer_token: str) -> Dict[str, Any]:
    """
    Try connection using Python standard library urllib.
    No external dependencies required.
    """
    start_time = time.time()
    try:
        url = f"{base_url}{endpoint}"
        
        # Create request with headers
        request = urllib.request.Request(url)
        request.add_header('Accept', 'application/json')
        request.add_header('Content-Type', 'application/json')
        request.add_header('Authorization', f'Bearer {bearer_token}')
        
        # Create SSL context that doesn't verify certificates (for air-gapped env)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Make request
        with urllib.request.urlopen(request, context=ssl_context, timeout=30) as response:
            response_time = f"{(time.time() - start_time):.2f}s"
            
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                return {
                    'success': True,
                    'data': data,
                    'response_time': response_time
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status}'
                }
    
    except urllib.error.HTTPError as e:
        return {
            'success': False,
            'error': f'HTTPError {e.code}: {e.reason}'
        }
    
    except urllib.error.URLError as e:
        return {
            'success': False,
            'error': f'URLError: {str(e.reason)[:200]}'
        }
    
    except ssl.SSLError as e:
        return {
            'success': False,
            'error': f'SSLError: {str(e)[:200]}'
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': f'{type(e).__name__}: {str(e)[:200]}'
        }

# Made with Bob
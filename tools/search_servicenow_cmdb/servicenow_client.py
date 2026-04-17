"""
ServiceNow CMDB API Client

This module provides functions to fetch CMDB business application data from ServiceNow
using Bearer Token authentication. Based on the pattern from thouroughTest.py.

Uses Python standard library (urllib) for air-gapped environment compatibility.
"""

import json
import ssl
import urllib.request
import urllib.error
from typing import Dict, List, Any


def fetch_cmdb_applications(base_url: str, bearer_token: str) -> List[Dict[str, Any]]:
    """
    Fetch CMDB business applications from ServiceNow.
    
    Retrieves application data from the cmdb_ci_business_app table with all
    required fields for ownership and management information.
    
    Args:
        base_url: ServiceNow instance base URL (e.g., "https://pncbankdev5.service-now.com")
        bearer_token: Bearer token for authentication
        
    Returns:
        List of application records as dictionaries
        
    Raises:
        Exception: If the API request fails
        
    Example:
        >>> apps = fetch_cmdb_applications(base_url, token)
        >>> print(f"Retrieved {len(apps)} applications")
        Retrieved 150 applications
    """
    # ServiceNow CMDB endpoint with all required fields
    endpoint = (
        "/api/now/table/cmdb_ci_business_app"
        "?sysparm_fields=name,u_mnemonic_id,short_description,"
        "owned_by.name,owned_by.email,owned_by.user_name,"
        "managed_by.name,managed_by.email,managed_by.user_name,"
        "it_application_owner.name,it_application_owner.email,it_application_owner.user_name,"
        "business_criticality,data_classification,"
        "application_manager.name,application_manager.email,application_manager.user_name"
        "&sysparm_limit=300&sysparm_display_value=true"
        "&sysparm_query="
    )
    
    url = f"{base_url}{endpoint}"
    
    try:
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
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                return data.get('result', [])
            else:
                raise Exception(f'HTTP {response.status}: Failed to fetch CMDB data')
    
    except urllib.error.HTTPError as e:
        raise Exception(f'HTTPError {e.code}: {e.reason}')
    
    except urllib.error.URLError as e:
        raise Exception(f'URLError: {str(e.reason)[:200]}')
    
    except ssl.SSLError as e:
        raise Exception(f'SSLError: {str(e)[:200]}')
    
    except json.JSONDecodeError as e:
        raise Exception(f'Failed to parse JSON response: {str(e)}')
    
    except Exception as e:
        raise Exception(f'Failed to fetch CMDB applications: {str(e)[:200]}')


def parse_servicenow_record(record: Dict[str, Any]) -> Dict[str, str]:
    """
    Parse a ServiceNow CMDB record into a flat dictionary structure.
    
    ServiceNow returns most fields as flat strings, but u_mnemonic_id is an object
    with display_value and link properties. This function extracts the display_value.
    
    Args:
        record: Raw ServiceNow record dictionary
        
    Returns:
        Flattened dictionary with all fields as strings
        
    Example:
        >>> record = {
        ...     "name": "FEE GENERATOR SYSTEM",
        ...     "u_mnemonic_id": {"display_value": "FGS", "link": "..."},
        ...     "owned_by.name": "Martin Fabian"
        ... }
        >>> parsed = parse_servicenow_record(record)
        >>> print(parsed['u_mnemonic_id'])
        FGS
    """
    parsed = {}
    
    # Direct string fields
    parsed['name'] = record.get('name', '')
    parsed['short_description'] = record.get('short_description', '')
    parsed['business_criticality'] = record.get('business_criticality', '')
    parsed['data_classification'] = record.get('data_classification', '')
    
    # u_mnemonic_id is an object with display_value - extract it
    # Try display_value first, then value, then the whole object as string
    u_mnemonic_id = record.get('u_mnemonic_id', '')
    if isinstance(u_mnemonic_id, dict):
        # Try display_value first
        app_code = u_mnemonic_id.get('display_value', '')
        # If empty, try value as fallback
        if not app_code:
            app_code = u_mnemonic_id.get('value', '')
        parsed['u_mnemonic_id'] = app_code
    else:
        parsed['u_mnemonic_id'] = str(u_mnemonic_id) if u_mnemonic_id else ''
    
    # Owned by (Product Owner) - flat fields with dot notation
    parsed['owned_by.name'] = record.get('owned_by.name', '')
    parsed['owned_by.email'] = record.get('owned_by.email', '')
    parsed['owned_by.user_name'] = record.get('owned_by.user_name', '')
    
    # Managed by (RTB_ASM) - flat fields with dot notation
    parsed['managed_by.name'] = record.get('managed_by.name', '')
    parsed['managed_by.email'] = record.get('managed_by.email', '')
    parsed['managed_by.user_name'] = record.get('managed_by.user_name', '')
    
    # IT Application Owner - flat fields with dot notation
    parsed['it_application_owner.name'] = record.get('it_application_owner.name', '')
    parsed['it_application_owner.email'] = record.get('it_application_owner.email', '')
    parsed['it_application_owner.user_name'] = record.get('it_application_owner.user_name', '')
    
    # Application Manager (CIO) - flat fields with dot notation
    parsed['application_manager.name'] = record.get('application_manager.name', '')
    parsed['application_manager.email'] = record.get('application_manager.email', '')
    parsed['application_manager.user_name'] = record.get('application_manager.user_name', '')
    
    return parsed


# Made with Bob
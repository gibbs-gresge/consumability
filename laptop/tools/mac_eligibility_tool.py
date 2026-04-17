"""
Mac eligibility classification tool for determining device access based on job title.
Provides deterministic classification and pre-built ServiceNow queries.
"""
from typing import Dict, Any
import logging

from ibm_watsonx_orchestrate.agent_builder.tools import tool

logger = logging.getLogger(__name__)


@tool
def classify_mac_eligibility(title: str) -> Dict[str, Any]:
    """
    Determine if an employee's job title qualifies them for Mac devices.
    
    This tool performs deterministic classification based on job title keywords
    and returns a pre-built ServiceNow search query for device catalog filtering.
    This eliminates ambiguity and ensures consistent Mac eligibility decisions.
    
    Parameters:
        title (str): The employee's job title (e.g., "Senior Data Engineer", "Sales Person")
        
    Returns:
        dict: Classification result containing:
            - is_mac_eligible (bool): Whether the employee qualifies for Mac devices
            - reason (str): Explanation of the classification decision
            - search_query (str): Pre-built ServiceNow query string for get_records_7be86
            - matched_keywords (list): List of keywords that matched (if eligible)
            
    Example:
        result = classify_mac_eligibility("Senior Data Engineer")
        # Returns:
        # {
        #     "is_mac_eligible": True,
        #     "reason": "Title 'Senior Data Engineer' contains Mac-eligible keyword: 'engineer'",
        #     "search_query": "u_itemLIKELaptop^ORu_itemLIKEMac^OR...",
        #     "matched_keywords": ["engineer"]
        # }
    """
    # Define Mac-eligible keywords (case-insensitive matching)
    mac_keywords = [
        "developer",
        "engineer", 
        "architect",
        "programmer",
        "marketing",
        "creative",
        "designer",
        "content"
    ]
    
    # Normalize title for comparison
    title_lower = title.lower()
    
    # Find matching keywords
    matched_keywords = [keyword for keyword in mac_keywords if keyword in title_lower]
    
    # Determine eligibility
    is_eligible = len(matched_keywords) > 0
    
    # Build appropriate ServiceNow query
    if is_eligible:
        # Mac-eligible: Include Mac devices in results
        search_query = (
            "u_itemLIKELaptop^ORu_itemLIKEMac^ORu_itemLIKEThinkPad^OR"
            "u_itemLIKELatitude^ORu_itemLIKEDesktop^ORu_itemLIKEWorkstation^OR"
            "u_itemLIKESurface Laptop"
        )
        reason = (
            f"Title '{title}' contains Mac-eligible keyword(s): "
            f"{', '.join(matched_keywords)}. Employee can select Mac devices."
        )
    else:
        # Not Mac-eligible: Exclude Mac devices from results
        search_query = (
            "u_itemLIKELaptop^ORu_itemLIKEThinkPad^ORu_itemLIKELatitude^OR"
            "u_itemLIKEDesktop^ORu_itemLIKEWorkstation^ORu_itemLIKESurface Laptop^"
            "u_itemNOT LIKEMac"
        )
        reason = (
            f"Title '{title}' does not contain Mac-eligible keywords. "
            f"Employee cannot select Mac devices."
        )
    
    result = {
        "is_mac_eligible": is_eligible,
        "reason": reason,
        "search_query": search_query,
        "matched_keywords": matched_keywords
    }
    
    logger.info(f"Mac eligibility classification: {title} -> {is_eligible}")
    return result


# Made with Bob
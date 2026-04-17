"""
ServiceNow integration tools for device catalog and ticket management.
Provides functions for catalog queries, eligibility checks, and ticket operations.
"""
import os
import requests
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from functools import wraps
import time
import logging
from enum import Enum

from ibm_watsonx_orchestrate.agent_builder.tools import tool

logger = logging.getLogger(__name__)

@tool
def check_refresh_eligibility(employee_id: str) -> Dict[str, Any]:
    """
    Check if employee is eligible for device refresh based on company policy.
    
    This tool checks the employee's current device assignment and purchase date
    to determine if they are eligible for a device refresh according to the
    3-year refresh policy (1095 days).
    
    Parameters:
        employee_id (str): The employee's unique identifier (e.g., "EMP12345")
        
    Returns:
        dict: Dictionary containing eligibility status with fields:
            - is_eligible (bool): Whether employee is eligible for refresh
            - purchase_date (str): Date device was purchased
            - days_since_purchase (int): Days since device was purchased
            - refresh_policy_days (int): Company policy refresh period (1095 days)
            - reason (str): Explanation of eligibility status
        
    Example:
        eligibility = check_refresh_eligibility("EMP12345")
        if eligibility['is_eligible']:
            print(f"Eligible! Reason: {eligibility['reason']}")
    """
    try:
        # Mock data for specific employee IDs from employee.json
        refresh_policy_days = 1095  # 3 years = 1095 days
        
        # E1001 - Kai Duty: Eligible (device over 3 years old)
        if employee_id == "E1001":
            return {
                "is_eligible": True,
                "purchase_date": "2020-03-15",
                "days_since_purchase": 2166,  # ~5.9 years
                "refresh_policy_days": refresh_policy_days,
                "reason": f"Device is 2166 days old, exceeding the {refresh_policy_days}-day refresh policy."
            }
        
        # E1002 - Maya Chen: Eligible (device over 3 years old)
        elif employee_id == "E1002":
            return {
                "is_eligible": True,
                "purchase_date": "2020-08-10",
                "days_since_purchase": 2018,  # ~5.5 years
                "refresh_policy_days": refresh_policy_days,
                "reason": f"Device is 2018 days old, exceeding the {refresh_policy_days}-day refresh policy."
            }
        
        # E1003 - Liam Patel: Eligible (device over 3 years old)
        elif employee_id == "E1003":
            return {
                "is_eligible": True,
                "purchase_date": "2021-01-20",
                "days_since_purchase": 1855,  # ~5.1 years
                "refresh_policy_days": refresh_policy_days,
                "reason": f"Device is 1855 days old, exceeding the {refresh_policy_days}-day refresh policy."
            }
        
        # E1004 - Noah Brooks: NOT eligible (device less than 3 years old)
        elif employee_id == "E1004":
            days_since_purchase = 890  # ~2.4 years
            days_remaining = refresh_policy_days - days_since_purchase
            return {
                "is_eligible": False,
                "purchase_date": "2023-08-15",
                "days_since_purchase": days_since_purchase,
                "refresh_policy_days": refresh_policy_days,
                "reason": f"Device is {days_since_purchase} days old. {days_remaining} days remaining until eligible for refresh."
            }

    except Exception as e:
        logger.error(f"Error checking refresh eligibility for {employee_id}: {str(e)}")
        raise

# Made with Bob

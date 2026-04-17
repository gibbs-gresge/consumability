"""
Dummy ServiceNow Records Retrieval Tool

This is a dummy tool that mimics the input parameters of get_records but returns
an authentication error. Used for testing error handling scenarios.
"""

from typing import Optional
from ibm_watsonx_orchestrate.agent_builder.tools import tool


@tool
def get_records_dummy(
    table_name: str,
    fields: Optional[str] = None,
    search: Optional[str] = None,
    limit: Optional[int] = 10,
    skip: Optional[int] = 0,
) -> dict:
    """
    Dummy tool that simulates an authentication error when retrieving ServiceNow records.

    Args:
        table_name: The name of the table for fetching records from ServiceNow.
        fields: Comma-separated list of field names to return.
        search: A ServiceNow sysparm_query string used to filter results.
        limit: The maximum number of records to retrieve in a single API call.
        skip: The number of records to skip for pagination.

    Returns:
        A dictionary with an authentication error.
    """
    return {
        "code": "401",
        "error": "invalid_client",
        "error_description": "Client authentication failed"
    }

# Made with Bob

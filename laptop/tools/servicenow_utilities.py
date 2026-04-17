"""
ServiceNow Utilities Module

This module provides utility functions for interacting with ServiceNow table metadata
and field information. It enables validation and discovery of ServiceNow table structures,
which is essential for dynamic query building and field validation in ServiceNow integrations.

The utilities handle table inheritance (super_class relationships) and provide comprehensive
field information for ServiceNow tables, supporting both standard and custom tables.

Note:
    This module is designed to work with the agent_ready_tools framework and
    requires proper ServiceNow client configuration and credentials.
"""

from typing import Optional

from pydantic.dataclasses import dataclass

from agent_ready_tools.clients.error_handling import ErrorDetails
from agent_ready_tools.clients.servicenow_client_refactored import get_servicenow_client


@dataclass
class TableResponse:
    """Represents the table details in ServiceNow."""

    name: Optional[str]
    label: Optional[str]
    super_class: Optional[str]


def get_tables(search: str) -> TableResponse | ErrorDetails:
    """
    Gets a table details in ServiceNow.

    Args:
        search: A query string used to filter ServiceNow tables, passed to the API as `sysparm_query` (e.g., name=incident).

    Returns:
        A TableResponse containing a table details, or an ErrorDetails object if an error occurs during the fetch operation.
    """

    client = get_servicenow_client()
    if isinstance(client, ErrorDetails):
        return client

    params = {
        "sysparm_query": search,
        "sysparm_display_value": True,
        "sysparm_fields": "name,label,sys_id,sys_name,super_class",
    }

    response = client.get_request(entity="sys_db_object", params=params)
    if isinstance(response, ErrorDetails):
        return response

    result_list = response.get("result")
    if not result_list:
        return ErrorDetails(
            status_code=None,
            reason=f"No table details found with query '{search}'.",
            recommendation="Please check the query and try again.",
            details=result_list,
            url=None,
        )

    result = result_list[0]
    super_class_value = result.get("super_class")
    return TableResponse(
        name=result.get("name", ""),
        label=result.get("label", ""),
        super_class=(
            super_class_value.get("display_value")
            if isinstance(super_class_value, dict)
            else None
        ),
    )


def get_table_fields(table_name: str) -> set | ErrorDetails:
    """
    Gets a table field details in ServiceNow.

    Args:
        table_name: The name of the table for fetching table field details from ServiceNow.

    Returns:
        A set containing a table field elements, or an ErrorDetails object if an error occurs during the fetch operation.
    """

    client = get_servicenow_client()
    if isinstance(client, ErrorDetails):
        return client

    params = {
        "sysparm_display_value": True,
        "sysparm_fields": "name,element,column_label,mandatory,sys_id,sys_name,max_length",
    }

    # Calls the get_tables method to validate the provided table_name. If the table is invalid or the response contains error_details, the function returns those error details.
    table_response = get_tables(search=f"name={table_name}")
    if isinstance(table_response, ErrorDetails):
        return table_response

    # If get_tables returns valid table details and the table's super_class is not None and equals "task", then the query parameters are adjusted accordingly. In ServiceNow, a table with super_class = task indicates it extends the core Task table, inheriting its fields and functionality.
    if (
        table_response.super_class
        and table_response.super_class is not None
        and table_response.super_class.lower() == "task"
    ):
        params["sysparm_query"] = f"nameIN{table_name},task^active=true"
    else:
        params["sysparm_query"] = f"name={table_name}^active=true"

    # After finalizing the parameters, the API call is executed.
    response = client.get_request(entity="sys_dictionary", params=params)
    if isinstance(response, ErrorDetails):
        return response

    result_list = response.get("result")
    if not result_list:
        return ErrorDetails(
            status_code=None,
            reason=f"No field details found for '{table_name}' table.",
            recommendation="Please check the table name and try again.",
            details=result_list,
            url=None,
        )

    valid_fields: set[str] = set()
    for result in result_list:
        valid_fields.add(result.get("element", ""))

    return valid_fields

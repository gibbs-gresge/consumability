"""
ServiceNow CMDB Search Tool Package

This package provides semantic search capabilities for ServiceNow CMDB business applications
with automatic PII obfuscation and IBM Granite embeddings.
"""

from .search_servicenow_cmdb import search_servicenow_cmdb

__all__ = ['search_servicenow_cmdb']

# Made with Bob
"""
Search ServiceNow CMDB Tool for watsonx Orchestrate.

Performs semantic search using IBM Granite embeddings via HTTP endpoint and cosine similarity.
Fetches live data from ServiceNow CMDB and obfuscates PII before embedding generation.
"""
from ibm_watsonx_orchestrate.agent_builder.tools import tool
from ibm_watsonx_orchestrate.agent_builder.connections import ConnectionType
from ibm_watsonx_orchestrate.run import connections
import os
import json
import sys

# Handle both relative and absolute imports
try:
    from .servicenow_client import fetch_cmdb_applications, parse_servicenow_record
    from .obfuscation_utils import obfuscate_person_fields
    from .embedding_utils import get_granite_embedding, get_granite_embeddings_batch
    from .search_utils import cosine_similarity_search, format_search_results
except ImportError:
    # Add parent directory to path for absolute imports
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from servicenow_client import fetch_cmdb_applications, parse_servicenow_record
    from obfuscation_utils import obfuscate_person_fields
    from embedding_utils import get_granite_embedding, get_granite_embeddings_batch
    from search_utils import cosine_similarity_search, format_search_results


# ServiceNow connection app ID
SERVICENOW_APP_ID = 'test_token'


def transform_and_obfuscate_record(record: dict) -> dict:
    """
    Transform ServiceNow record and obfuscate PII fields.
    
    Args:
        record: Parsed ServiceNow record dictionary
        
    Returns:
        Metadata dictionary with obfuscated person information
    """
    # Step 1: Extract raw metadata (non-PII fields)
    # Get u_mnemonic_id - should already be extracted as display_value by parse_servicenow_record
    app_code = record.get('u_mnemonic_id', '')
    if not app_code or app_code == '':
        app_code = 'N/A'
    
    metadata = {
        'app_code': app_code,
        'application_name': record.get('name', 'Unknown'),
        'description': record.get('short_description', ''),
        'business_criticality': record.get('business_criticality', ''),
        'data_classification': record.get('data_classification', ''),
    }
    
    # Step 2: Extract person data (to be obfuscated)
    person_fields = {
        'product_owner': {
            'name': record.get('owned_by.name', ''),
            'id': record.get('owned_by.user_name', ''),
            'email': record.get('owned_by.email', '')
        },
        'rtb_asm': {
            'name': record.get('managed_by.name', ''),
            'id': record.get('managed_by.user_name', ''),
            'email': record.get('managed_by.email', '')
        },
        'it_app_owner': {
            'name': record.get('it_application_owner.name', ''),
            'id': record.get('it_application_owner.user_name', ''),
            'email': record.get('it_application_owner.email', '')
        },
        'cio': {
            'name': record.get('application_manager.name', ''),
            'id': record.get('application_manager.user_name', ''),
            'email': record.get('application_manager.email', '')
        }
    }
    
    # Step 3: Obfuscate person data using Faker
    obfuscated_persons = obfuscate_person_fields(person_fields)
    
    # Step 4: Merge obfuscated data into metadata
    metadata.update({
        'product_owner': obfuscated_persons['product_owner']['name'],
        'owner_id': obfuscated_persons['product_owner']['id'],
        'owner_email': obfuscated_persons['product_owner']['email'],
        
        'rtb_asm_name': obfuscated_persons['rtb_asm']['name'],
        'rtb_asm_id': obfuscated_persons['rtb_asm']['id'],
        'rtb_asm_email': obfuscated_persons['rtb_asm']['email'],
        
        'it_app_owner_name': obfuscated_persons['it_app_owner']['name'],
        'it_app_owner_id': obfuscated_persons['it_app_owner']['id'],
        'it_app_owner_email': obfuscated_persons['it_app_owner']['email'],
        
        'cio_name': obfuscated_persons['cio']['name'],
        'cio_id': obfuscated_persons['cio']['id'],
        'cio_email': obfuscated_persons['cio']['email'],
    })
    
    return metadata


def create_searchable_content(metadata: dict) -> str:
    """
    Create comprehensive text for embedding generation using OBFUSCATED data.
    
    Args:
        metadata: Metadata dictionary with obfuscated person information
        
    Returns:
        Searchable text string for embedding
    """
    parts = [
        f"Application: {metadata['application_name']}",
        f"App Code: {metadata['app_code']}",
        f"Description: {metadata['description']}",
        # All person data below is OBFUSCATED
        f"Product Owner: {metadata['product_owner']} ({metadata['owner_email']})",
        f"RTB ASM: {metadata['rtb_asm_name']} ({metadata['rtb_asm_email']})",
        f"IT Application Owner: {metadata['it_app_owner_name']} ({metadata['it_app_owner_email']})",
        f"CIO: {metadata['cio_name']} ({metadata['cio_email']})",
        f"Business Criticality: {metadata['business_criticality']}",
        f"Data Classification: {metadata['data_classification']}"
    ]
    return "\n".join(parts)


@tool(
    expected_credentials=[
        {"app_id": SERVICENOW_APP_ID, "type": ConnectionType.BEARER_TOKEN}
    ]
)
def search_servicenow_cmdb(query: str, top_k: int = 3) -> str:
    """
    Search the ServiceNow CMDB for business applications using semantic similarity.
    
    This tool fetches live data from ServiceNow, obfuscates PII, generates embeddings,
    and performs semantic search to find the most relevant applications based on the query.
    
    Args:
        query (str): The search query. Examples:
            - "Who owns the FBAR application?"
            - "Find applications owned by a specific person"
            - "What is the RADIUS application?"
            - "Show me RTB_ASM contact for FBAR"
        top_k (int): Number of top results to return (default: 3, max: 20)
    
    Returns:
        str: Formatted search results with application details, ownership information,
             and similarity scores in markdown format. All personal information is obfuscated.
    
    Examples:
        >>> search_servicenow_cmdb("Who owns FBAR?")
        # Search Results for: 'Who owns FBAR?'
        Found 1 relevant application(s):
        
        ## 1. FBAR (Similarity: 0.892)
        **App Code:** `FBAR`
        **Product Owner:** John Doe
        **Email:** john.doe@pnc.com
        **Owner ID:** ID12345
    """
    # Validate and constrain top_k
    top_k = min(max(1, top_k), 20)
    
    try:
        # Get credentials from watsonx Orchestrate connection
        creds = connections.bearer_token(SERVICENOW_APP_ID)
        base_url = creds.url
        bearer_token = creds.token
        
        # Fetch live data from ServiceNow
        try:
            raw_records = fetch_cmdb_applications(base_url, bearer_token)
        except Exception as e:
            return (
                f"❌ **Error fetching data from ServiceNow**\n\n"
                f"Details: {str(e)}\n\n"
                "Please verify the ServiceNow connection is configured correctly."
            )
        
        if not raw_records:
            return (
                "⚠️ **No applications found in ServiceNow CMDB**\n\n"
                "The query returned no results. Please check the ServiceNow configuration."
            )
        
        # Transform and obfuscate each record
        chunks = []
        for raw_record in raw_records:
            try:
                # Parse ServiceNow record
                parsed_record = parse_servicenow_record(raw_record)
                
                # Transform and obfuscate
                metadata = transform_and_obfuscate_record(parsed_record)
                
                # Create searchable content
                content = create_searchable_content(metadata)
                
                chunks.append({
                    'metadata': metadata,
                    'content': content
                })
            except Exception as e:
                # Skip records that fail to process
                continue
        
        if not chunks:
            return (
                "❌ **Error processing ServiceNow data**\n\n"
                "Failed to process any application records. Please check the data format."
            )
        
        # Generate embeddings for all obfuscated chunks (batch processing)
        try:
            contents = [chunk['content'] for chunk in chunks]
            embeddings = get_granite_embeddings_batch(contents, batch_size=32)
        except Exception as e:
            return (
                f"❌ **Error generating embeddings for applications**\n\n"
                f"Details: {str(e)}\n\n"
                "Please verify the Granite embedding endpoint is accessible."
            )
        
        # Generate query embedding
        try:
            query_embedding = get_granite_embedding(text=query)
        except Exception as e:
            return (
                f"❌ **Error generating query embedding**\n\n"
                f"Details: {str(e)}\n\n"
                "Please verify the Granite embedding endpoint is accessible and configured correctly."
            )
        
        # Perform cosine similarity search
        try:
            results = cosine_similarity_search(
                query_embedding=query_embedding,
                kb_embeddings=embeddings,
                kb_metadata=[chunk['metadata'] for chunk in chunks],
                top_k=top_k,
                min_score=0.0  # No minimum threshold
            )
        except Exception as e:
            return f"❌ **Error during search**\n\nDetails: {str(e)}"
        
        # Format and return results
        return format_search_results(results, query)
        
    except Exception as e:
        return (
            f"❌ **Unexpected error**\n\n"
            f"Details: {str(e)}\n\n"
            "Please contact support if this issue persists."
        )


# Made with Bob
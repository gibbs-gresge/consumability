"""
Search Knowledge Base Tool for watsonx Orchestrate.
Performs semantic search using IBM Granite embeddings via HTTP endpoint and cosine similarity.
"""
from ibm_watsonx_orchestrate.agent_builder.tools import tool
import os
import json
import sys

# Handle both relative and absolute imports
try:
    from .embedding_utils import get_granite_embedding
    from .search_utils import cosine_similarity_search, format_search_results
except ImportError:
    # Add parent directory to path for absolute imports
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from embedding_utils import get_granite_embedding
    from search_utils import cosine_similarity_search, format_search_results


@tool()
def search_knowledge_base(query: str, top_k: int = 3) -> str:
    """
    Search the product ownership knowledge base using semantic similarity.
    
    This tool uses IBM Granite embeddings to perform semantic search across
    application ownership data. It returns the most relevant applications
    based on the query, including product owner information and contact details.
    
    Args:
        query (str): The search query. Examples:
            - "Who owns the AAA application?"
            - "Find applications owned by Michelle Davis"
            - "What is the RADIUS application?"
            - "Show me CIO contact for AAA"
        top_k (int): Number of top results to return (default: 5, max: 20)
    
    Returns:
        str: Formatted search results with application details, product owners,
             and similarity scores in markdown format
    
    Examples:
        >>> search_knowledge_base("Who owns AAA?")
        # Search Results for: 'Who owns AAA?'
        Found 1 relevant application(s):
        
        ## 1. AAA - Enterprise RADIUS (Similarity: 0.892)
        **App Code:** `AAA`
        **Product Owner:** Michelle Davis MD
        **Email:** michelle.davis.md@pnc.com
        **Owner ID:** ID69501
    """
    # Validate and constrain top_k
    top_k = min(max(1, top_k), 20)
    
    # Load pre-computed embeddings
    base_path = os.path.dirname(os.path.abspath(__file__))
    embeddings_path = os.path.join(base_path, 'embeddings_data.json')
    
    try:
        with open(embeddings_path, 'r') as f:
            kb_data = json.load(f)
    except FileNotFoundError:
        return (
            "❌ **Error: Embeddings data file not found**\n\n"
            f"Expected location: `{embeddings_path}`\n\n"
            "Please run the embedding generation script:\n"
            "```bash\n"
            "python scripts/generate_embeddings_json.py\n"
            "```"
        )
    except json.JSONDecodeError as e:
        return f"❌ **Error: Invalid embeddings data file**\n\nDetails: {str(e)}"
    
    # Validate data structure
    if 'embeddings' not in kb_data or 'metadata' not in kb_data:
        return (
            "❌ **Error: Invalid embeddings data structure**\n\n"
            "The embeddings file must contain 'embeddings' and 'metadata' keys."
        )
    
    # Generate query embedding using Granite endpoint
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
            kb_embeddings=kb_data['embeddings'],
            kb_metadata=kb_data['metadata'],
            top_k=top_k,
            min_score=0.0  # No minimum threshold
        )
    except Exception as e:
        return f"❌ **Error during search**\n\nDetails: {str(e)}"
    
    # Format and return results
    return format_search_results(results, query)

# Made with Bob

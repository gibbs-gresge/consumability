"""
Search utilities for cosine similarity-based semantic search.
Adapted for ServiceNow CMDB data with corrected field mappings.
"""
import numpy as np
from typing import List, Dict, Tuple, Any


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors.
    
    Args:
        vec1: First vector
        vec2: Second vector
    
    Returns:
        Cosine similarity score (0 to 1, where 1 is most similar)
    """
    vec1 = np.array(vec1, dtype=np.float32)
    vec2 = np.array(vec2, dtype=np.float32)
    
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return float(dot_product / (norm1 * norm2))


def cosine_similarity_search(
    query_embedding: List[float],
    kb_embeddings: List[List[float]],
    kb_metadata: List[Dict[str, Any]],
    top_k: int = 5,
    min_score: float = 0.0
) -> List[Dict[str, Any]]:
    """
    Perform cosine similarity search against knowledge base.
    
    Args:
        query_embedding: Query vector
        kb_embeddings: List of knowledge base vectors
        kb_metadata: List of metadata dicts (one per embedding)
        top_k: Number of top results to return
        min_score: Minimum similarity score threshold (0 to 1)
    
    Returns:
        List of top_k results with metadata and similarity scores,
        sorted by score descending
    
    Raises:
        ValueError: If embeddings and metadata lists have different lengths
    """
    if len(kb_embeddings) != len(kb_metadata):
        raise ValueError(
            f"Embeddings ({len(kb_embeddings)}) and metadata ({len(kb_metadata)}) "
            "lists must have same length"
        )
    
    if not kb_embeddings:
        return []
    
    # Calculate similarities
    similarities = []
    for idx, kb_emb in enumerate(kb_embeddings):
        score = cosine_similarity(query_embedding, kb_emb)
        
        # Apply minimum score threshold
        if score >= min_score:
            similarities.append({
                'score': score,
                'metadata': kb_metadata[idx],
                'index': idx
            })
    
    # Sort by score descending
    similarities.sort(key=lambda x: x['score'], reverse=True)
    
    # Return top_k results
    return similarities[:top_k]


def format_search_results(results: List[Dict[str, Any]], query: str) -> str:
    """
    Format search results as markdown for display.
    Updated with corrected ServiceNow CMDB field mappings.
    
    Args:
        results: List of search results with 'score' and 'metadata' keys
        query: Original search query
    
    Returns:
        Formatted markdown string
    """
    if not results:
        return f"No results found for query: **'{query}'**"
    
    output = [f"# Search Results for: '{query}'\n"]
    output.append(f"Found {len(results)} relevant application(s):\n")
    
    for idx, result in enumerate(results, 1):
        meta = result['metadata']
        score = result['score']
        
        # Header with app name and score
        output.append(f"## {idx}. {meta.get('application_name', 'Unknown')} (Similarity: {score:.3f})")
        
        # App code
        output.append(f"**App Code:** `{meta.get('app_code', 'N/A')}`")
        
        # Description
        if meta.get('description'):
            output.append(f"**Description:** {meta['description']}")
        
        # Product Owner (OWNED_BY) - OBFUSCATED DATA
        if meta.get('product_owner'):
            output.append(f"\n**Product Owner (OWNED_BY):**")
            output.append(f"- Name: {meta['product_owner']}")
            if meta.get('owner_id'):
                output.append(f"- ID: {meta['owner_id']}")
            if meta.get('owner_email'):
                output.append(f"- Email: {meta['owner_email']}")
        
        # RTB_ASM (MANAGED_BY - Run The Bank) - OBFUSCATED DATA
        if meta.get('rtb_asm_name'):
            output.append(f"\n**RTB_ASM (Run The Bank - MANAGED_BY):**")
            output.append(f"- Name: {meta['rtb_asm_name']}")
            if meta.get('rtb_asm_id'):
                output.append(f"- ID: {meta['rtb_asm_id']}")
            if meta.get('rtb_asm_email'):
                output.append(f"- Email: {meta['rtb_asm_email']}")
        
        # IT Application Owner (IT_APPLICATION_OWNER) - OBFUSCATED DATA
        if meta.get('it_app_owner_name'):
            output.append(f"\n**IT Application Owner (IT_APPLICATION_OWNER):**")
            output.append(f"- Name: {meta['it_app_owner_name']}")
            if meta.get('it_app_owner_id'):
                output.append(f"- ID: {meta['it_app_owner_id']}")
            if meta.get('it_app_owner_email'):
                output.append(f"- Email: {meta['it_app_owner_email']}")
        
        # CIO (APPLICATION_MANAGER) - OBFUSCATED DATA
        if meta.get('cio_name'):
            output.append(f"\n**CIO (APPLICATION_MANAGER):**")
            output.append(f"- Name: {meta['cio_name']}")
            if meta.get('cio_id'):
                output.append(f"- ID: {meta['cio_id']}")
            if meta.get('cio_email'):
                output.append(f"- Email: {meta['cio_email']}")
        
        # Additional fields (NOT obfuscated)
        if meta.get('business_criticality'):
            output.append(f"\n**Business Criticality:** {meta['business_criticality']}")
        if meta.get('data_classification'):
            output.append(f"**Data Classification:** {meta['data_classification']}")
        
        # Add separator between results
        output.append("")
    
    # Add footer note about obfuscation
    output.append("---")
    output.append("*Source: ServiceNow CMDB*")
    output.append("*Note: Personal information is obfuscated for privacy*")
    
    return "\n".join(output)


# Made with Bob
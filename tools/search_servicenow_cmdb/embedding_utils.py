"""
Embedding utilities for IBM Granite embedding model via OpenAI-compatible endpoint.
Uses HTTP requests to remote embedding service instead of local model execution.
"""
import requests
import numpy as np
from typing import List, Dict, Any

# ─────────────────────────────────────────────
# CONFIG — Granite embedding via RHOAI (OpenAI-compatible)
# ─────────────────────────────────────────────
EMBEDDING_ENDPOINT = "http://granite-embedding-wxo.pnc-rhoai.svc.cluster.local/v1/embeddings"
MODEL_ID = "granite-embedding"
HEADERS = {"Content-Type": "application/json"}
REQUEST_TIMEOUT = 30  # seconds


def get_granite_embedding(text: str) -> List[float]:
    """
    Get embedding from IBM Granite model via OpenAI-compatible HTTP endpoint.
    
    Args:
        text: Text to embed
    
    Returns:
        List of embedding values
    
    Raises:
        requests.exceptions.RequestException: If HTTP request fails
        KeyError: If response format is unexpected
        Exception: For other embedding generation failures
    """
    try:
        payload = {
            "model": MODEL_ID,
            "input": text
        }
        
        response = requests.post(
            EMBEDDING_ENDPOINT,
            headers=HEADERS,
            json=payload,
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        
        # OpenAI-compatible response shape:
        # {"data": [{"embedding": [...], "index": 0, "object": "embedding"}], ...}
        embedding_data = response.json()
        values = embedding_data["data"][0]["embedding"]
        
        return values
        
    except requests.exceptions.Timeout:
        raise Exception(f"Embedding request timed out after {REQUEST_TIMEOUT} seconds")
    except requests.exceptions.ConnectionError:
        raise Exception(f"Failed to connect to embedding endpoint: {EMBEDDING_ENDPOINT}")
    except requests.exceptions.HTTPError as e:
        raise Exception(f"HTTP error from embedding endpoint: {e.response.status_code} - {e.response.text}")
    except KeyError as e:
        raise Exception(f"Unexpected response format from embedding endpoint: missing key {e}")
    except Exception as e:
        raise Exception(f"Failed to generate embedding: {str(e)}")


def get_granite_embeddings_batch(texts: List[str], batch_size: int = 1) -> List[List[float]]:
    """
    Get embeddings for multiple texts with automatic batching.
    
    Note: This function processes texts in batches but makes separate requests
    for each batch. For the search tool, single-text embedding is typically used.
    This is mainly for compatibility with batch processing scripts.
    
    Args:
        texts: List of texts to embed
        batch_size: Number of texts to process at once (default: 32)
    
    Returns:
        List of embeddings (one per input text)
    
    Raises:
        Exception: If encoding fails
    """
    all_embeddings = []
    
    try:
        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            payload = {
                "model": MODEL_ID,
                "input": batch  # OpenAI spec allows list of strings
            }
            
            response = requests.post(
                EMBEDDING_ENDPOINT,
                headers=HEADERS,
                json=payload,
                timeout=REQUEST_TIMEOUT * 2  # Longer timeout for batches
            )
            response.raise_for_status()
            
            # Extract embeddings in order
            embedding_data = response.json()
            batch_embeddings = [item["embedding"] for item in embedding_data["data"]]
            all_embeddings.extend(batch_embeddings)
        
        return all_embeddings
        
    except Exception as e:
        raise Exception(f"Failed to generate batch embeddings: {str(e)}")


def verify_model() -> Dict[str, Any]:
    """
    Verify endpoint connectivity and get embedding dimension.
    
    Returns:
        Dict with 'success', 'dimension', 'model_name', and 'message' keys
    """
    try:
        # Test with simple text
        test_embedding = get_granite_embedding("test")
        
        return {
            'success': True,
            'dimension': len(test_embedding),
            'model_name': MODEL_ID,
            'endpoint': EMBEDDING_ENDPOINT,
            'message': f"Endpoint accessible. Embedding dimension: {len(test_embedding)}"
        }
    except Exception as e:
        return {
            'success': False,
            'dimension': None,
            'model_name': MODEL_ID,
            'endpoint': EMBEDDING_ENDPOINT,
            'message': f"Endpoint verification failed: {str(e)}"
        }


# Backward compatibility aliases (for code that might still reference old names)
get_granite_embedding_rest = get_granite_embedding
get_granite_embeddings_batch_rest = get_granite_embeddings_batch

# Made with Bob

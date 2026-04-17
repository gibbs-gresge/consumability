#!/usr/bin/env python3
"""
Standalone test script for search_knowledge_base tool.
Tests the tool logic without deploying to watsonx Orchestrate.
"""
import os
import sys
import json
from pathlib import Path

# Add the tools directory to the path so we can import the modules
tools_dir = Path(__file__).parent
sys.path.insert(0, str(tools_dir))

from embedding_utils import get_granite_embedding
from search_utils import cosine_similarity_search, format_search_results


def test_search(query: str, top_k: int = 5):
    """
    Test the search functionality with a given query.
    
    Args:
        query: Search query string
        top_k: Number of results to return
    
    Returns:
        Formatted search results
    """
    print(f"\n{'='*80}")
    print(f"Testing query: '{query}'")
    print(f"{'='*80}\n")
    
    # Load embeddings data
    embeddings_path = Path(__file__).parent / 'embeddings_data.json'
    try:
        with open(embeddings_path, 'r') as f:
            kb_data = json.load(f)
        print(f"✓ Loaded embeddings data: {kb_data['count']} entries")
        print(f"  Model: {kb_data['model']}")
        print(f"  Dimension: {kb_data['dimension']}")
    except FileNotFoundError:
        return f"❌ Error: embeddings_data.json not found at {embeddings_path}"
    except Exception as e:
        return f"❌ Error loading embeddings: {str(e)}"
    
    # Generate query embedding using local model
    try:
        print(f"\n⏳ Generating embedding for query using local Granite model...")
        query_embedding = get_granite_embedding(text=query)
        print(f"✓ Generated query embedding (dimension: {len(query_embedding)})")
    except Exception as e:
        return f"❌ Error generating query embedding: {str(e)}"
    
    # Perform search
    try:
        print(f"\n⏳ Searching knowledge base...")
        results = cosine_similarity_search(
            query_embedding=query_embedding,
            kb_embeddings=kb_data['embeddings'],
            kb_metadata=kb_data['metadata'],
            top_k=top_k,
            min_score=0.0
        )
        print(f"✓ Found {len(results)} results")
    except Exception as e:
        return f"❌ Error during search: {str(e)}"
    
    # Format results
    formatted_results = format_search_results(results, query)
    
    return formatted_results


def main():
    """Run tests with the specified prompts."""
    test_prompts = ["AAA", "SMTP", "ASC"]
    
    print("\n" + "="*80)
    print("SEARCH KNOWLEDGE BASE TOOL - STANDALONE TEST")
    print("="*80)
    print(f"\nTesting with prompts: {test_prompts}")
    
    all_results = []
    
    for prompt in test_prompts:
        result = test_search(prompt, top_k=3)
        all_results.append({
            'query': prompt,
            'result': result
        })
        print(f"\n{result}")
        print("\n" + "-"*80)
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    for i, test in enumerate(all_results, 1):
        status = "✓ PASS" if not test['result'].startswith("❌") else "✗ FAIL"
        print(f"{i}. Query: '{test['query']}' - {status}")
    
    print("\n" + "="*80)
    print("All tests completed!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()

# Made with Bob

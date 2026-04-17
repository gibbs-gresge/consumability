"""
Generate embeddings_data.json for the search_knowledge_base tool.

This script:
1. Reads all application files from data/kb_data/
2. Generates embeddings via OpenAI-compatible HTTP endpoint
3. Uses batch processing for efficiency (32 files per request)
4. Extracts metadata from each file
5. Saves embeddings and metadata to JSON file

Usage:
    python scripts/generate_embeddings_json.py
"""
import os
import json
from datetime import datetime
from typing import List, Dict
import sys
import requests

# ─────────────────────────────────────────────
# CONFIG — Granite embedding via RHOAI (OpenAI-compatible)
# ─────────────────────────────────────────────
EMBEDDING_ENDPOINT = "http://granite-embedding-wxo.pnc-rhoai.svc.cluster.local/v1/embeddings"
MODEL_ID = "granite-embedding"
HEADERS = {"Content-Type": "application/json"}
REQUEST_TIMEOUT = 120  # seconds (longer for batch requests)
BATCH_SIZE = 32  # Number of texts to embed per request


def get_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """
    Get embeddings for multiple texts via OpenAI-compatible HTTP endpoint.
    
    Args:
        texts: List of texts to embed (up to BATCH_SIZE recommended)
    
    Returns:
        List of embeddings (one per input text, in same order)
    
    Raises:
        Exception: If HTTP request fails or response is invalid
    """
    try:
        payload = {
            "model": MODEL_ID,
            "input": texts  # OpenAI spec allows list of strings
        }
        
        response = requests.post(
            EMBEDDING_ENDPOINT,
            headers=HEADERS,
            json=payload,
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        
        # OpenAI-compatible response shape:
        # {"data": [{"embedding": [...], "index": 0, "object": "embedding"}, ...], ...}
        embedding_data = response.json()
        embeddings = [item["embedding"] for item in embedding_data["data"]]
        
        return embeddings
        
    except requests.exceptions.Timeout:
        raise Exception(f"Embedding request timed out after {REQUEST_TIMEOUT} seconds")
    except requests.exceptions.ConnectionError:
        raise Exception(f"Failed to connect to embedding endpoint: {EMBEDDING_ENDPOINT}")
    except requests.exceptions.HTTPError as e:
        raise Exception(f"HTTP error from embedding endpoint: {e.response.status_code} - {e.response.text}")
    except KeyError as e:
        raise Exception(f"Unexpected response format from embedding endpoint: missing key {e}")
    except Exception as e:
        raise Exception(f"Failed to generate embeddings: {str(e)}")


def verify_endpoint() -> tuple[bool, str, int]:
    """
    Verify endpoint is accessible and get embedding dimension.
    
    Returns:
        Tuple of (success: bool, message: str, dimension: int)
    """
    try:
        test_embeddings = get_embeddings_batch(["test"])
        dimension = len(test_embeddings[0])
        return True, f"Endpoint accessible. Embedding dimension: {dimension}", dimension
    except Exception as e:
        return False, f"Endpoint verification failed: {str(e)}", 0


def extract_metadata(content: str, app_code: str) -> Dict:
    """
    Extract structured metadata from kb_data file content.
    
    Args:
        content: Full file content
        app_code: Application code (filename without .txt)
    
    Returns:
        Dict with extracted metadata fields
    """
    lines = content.split('\n')
    metadata = {
        'app_code': app_code,
        'content': content,
        'application_name': app_code  # Default fallback
    }
    
    # Parse structured fields
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Application name
        if line.startswith('APPLICATION:'):
            metadata['application_name'] = line.replace('APPLICATION:', '').strip()
        
        # Product Owner section
        elif 'PRODUCT OWNER' in line and 'OWNED_BY' in line:
            # Look for Name, ID, Email in next few lines
            for j in range(i + 1, min(i + 5, len(lines))):
                next_line = lines[j].strip()
                if next_line.startswith('- Name:'):
                    metadata['product_owner'] = next_line.replace('- Name:', '').strip()
                elif next_line.startswith('- ID:'):
                    metadata['owner_id'] = next_line.replace('- ID:', '').strip()
                elif next_line.startswith('- Email:'):
                    metadata['owner_email'] = next_line.replace('- Email:', '').strip()
        
        # RTB_ASM section
        elif 'RTB_ASM' in line and 'Run The Bank' in line:
            # Look for Name, ID, Email in next few lines
            for j in range(i + 1, min(i + 5, len(lines))):
                next_line = lines[j].strip()
                if next_line.startswith('- Name:'):
                    metadata['rtb_asm_name'] = next_line.replace('- Name:', '').strip()
                elif next_line.startswith('- ID:'):
                    metadata['rtb_asm_id'] = next_line.replace('- ID:', '').strip()
                elif next_line.startswith('- Email:'):
                    metadata['rtb_asm_email'] = next_line.replace('- Email:', '').strip()
        
        # CTB_ASM section
        elif 'CTB_ASM' in line and 'Change The Bank' in line:
            # Look for Name, ID, Email in next few lines
            for j in range(i + 1, min(i + 5, len(lines))):
                next_line = lines[j].strip()
                if next_line.startswith('- Name:'):
                    metadata['ctb_asm_name'] = next_line.replace('- Name:', '').strip()
                elif next_line.startswith('- ID:'):
                    metadata['ctb_asm_id'] = next_line.replace('- ID:', '').strip()
                elif next_line.startswith('- Email:'):
                    metadata['ctb_asm_email'] = next_line.replace('- Email:', '').strip()
        
        # Description
        elif line.startswith('DESCRIPTION:'):
            metadata['description'] = line.replace('DESCRIPTION:', '').strip()
        
        # CIO section
        elif line.startswith('CIO:'):
            for j in range(i + 1, min(i + 5, len(lines))):
                next_line = lines[j].strip()
                if next_line.startswith('- Name:'):
                    metadata['cio_name'] = next_line.replace('- Name:', '').strip()
                elif next_line.startswith('- ID:'):
                    metadata['cio_id'] = next_line.replace('- ID:', '').strip()
                elif next_line.startswith('- Email:'):
                    metadata['cio_email'] = next_line.replace('- Email:', '').strip()
    
    return metadata


def generate_embeddings_data():
    """Main function to generate embeddings data file."""
    
    # Configuration
    KB_DATA_DIR = "data/kb_data"
    OUTPUT_FILE = "tools/search_knowledge_base/embeddings_data.json"
    
    # Print header
    print("=" * 80)
    print("GENERATING EMBEDDINGS DATA FOR SEARCH TOOL")
    print("=" * 80)
    print(f"Model: {MODEL_ID}")
    print(f"Endpoint: {EMBEDDING_ENDPOINT}")
    print(f"Source: {KB_DATA_DIR}")
    print(f"Output: {OUTPUT_FILE}")
    print(f"Batch Size: {BATCH_SIZE}")
    print()
    
    # Verify endpoint
    print("Verifying embedding endpoint...")
    success, message, embedding_dim = verify_endpoint()
    if not success:
        print(f"❌ {message}")
        return False
    print(f"✓ {message}")
    print()
    
    # Load all kb_data files
    if not os.path.exists(KB_DATA_DIR):
        print(f"❌ Error: Directory not found: {KB_DATA_DIR}")
        return False
    
    files = sorted([f for f in os.listdir(KB_DATA_DIR) if f.endswith('.txt')])
    
    if not files:
        print(f"❌ Error: No .txt files found in {KB_DATA_DIR}")
        return False
    
    print(f"Found {len(files)} application files")
    print()
    
    # Read all files first
    print("Reading application files...")
    file_data = []
    failed_reads = []
    
    for filename in files:
        app_code = filename.replace('.txt', '')
        filepath = os.path.join(KB_DATA_DIR, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            metadata = extract_metadata(content, app_code)
            file_data.append({
                'app_code': app_code,
                'content': content,
                'metadata': metadata
            })
        except Exception as e:
            print(f"  ❌ Failed to read {app_code}: {str(e)}")
            failed_reads.append((app_code, str(e)))
    
    print(f"✓ Successfully read {len(file_data)} files")
    if failed_reads:
        print(f"⚠ Failed to read {len(failed_reads)} files")
    print()
    
    # Generate embeddings in batches
    print(f"Generating embeddings in batches of {BATCH_SIZE}...")
    embeddings = []
    metadata_list = []
    failed_embeddings = []
    
    total_batches = (len(file_data) + BATCH_SIZE - 1) // BATCH_SIZE
    
    for batch_idx in range(0, len(file_data), BATCH_SIZE):
        batch_data = file_data[batch_idx:batch_idx + BATCH_SIZE]
        batch_num = (batch_idx // BATCH_SIZE) + 1
        
        try:
            # Extract content for batch
            batch_contents = [item['content'] for item in batch_data]
            
            # Generate embeddings for batch
            batch_embeddings = get_embeddings_batch(batch_contents)
            
            # Store results
            for item, embedding in zip(batch_data, batch_embeddings):
                embeddings.append(embedding)
                metadata_list.append(item['metadata'])
            
            # Progress update
            print(f"  Batch {batch_num}/{total_batches}: Processed {len(batch_data)} applications")
        
        except Exception as e:
            print(f"  ❌ Failed batch {batch_num}: {str(e)}")
            for item in batch_data:
                failed_embeddings.append((item['app_code'], str(e)))
    
    print()
    print(f"✓ Successfully generated {len(embeddings)} embeddings")
    
    if failed_embeddings:
        print(f"⚠ Failed to process {len(failed_embeddings)} files:")
        for app_code, error in failed_embeddings[:10]:  # Show first 10
            print(f"  - {app_code}: {error}")
        if len(failed_embeddings) > 10:
            print(f"  ... and {len(failed_embeddings) - 10} more")
        print()
    
    # Save to JSON
    output_data = {
        'model': MODEL_ID,
        'endpoint': EMBEDDING_ENDPOINT,
        'dimension': embedding_dim,
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'count': len(embeddings),
        'embeddings': embeddings,
        'metadata': metadata_list
    }
    
    # Create output directory if needed
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    # Write JSON file
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    # Report file size
    file_size_mb = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)
    
    print(f"✓ Saved to {OUTPUT_FILE}")
    print(f"  File size: {file_size_mb:.2f} MB")
    print(f"  Embedding dimension: {embedding_dim}")
    print(f"  Total applications: {len(embeddings)}")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. Import the tool to watsonx Orchestrate:")
    print("   orchestrate tools import \\")
    print("     -k python \\")
    print("     -p tools/search_knowledge_base \\")
    print("     -f tools/search_knowledge_base/search_knowledge_base.py \\")
    print("     -r tools/search_knowledge_base/requirements.txt \\")
    print("     -a watsonx_ai")
    print()
    
    return True


if __name__ == "__main__":
    try:
        success = generate_embeddings_data()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

# Made with Bob

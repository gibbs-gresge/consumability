"""
Load Victor Apps data into Milvus
This script loads the prepared application data into a Milvus collection
with proper indexing for optimal search performance.
"""

import os
import json
from pymilvus import (
    connections,
    Collection,
    FieldSchema,
    CollectionSchema,
    DataType,
    utility
)
import requests

# Configuration - Update these with your Milvus details
MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT = int(os.getenv("MILVUS_PORT", "19530"))
MILVUS_USER = os.getenv("MILVUS_USER", "")
MILVUS_PASSWORD = os.getenv("MILVUS_PASSWORD", "")
COLLECTION_NAME = os.getenv("MILVUS_COLLECTION", "default")  # Updated to match embedding model
KB_DATA_DIR = "data/kb_data"

# IBM Slate embedding configuration via watsonx.ai REST API
EMBEDDING_MODEL = "ibm/slate-30m-english-rtrvr-v2"
EMBEDDING_DIM = 768  # Will be verified on first API call
WATSONX_API_KEY = os.getenv("WATSONX_API_KEY")
WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID")
WATSONX_URL = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")


def connect_to_milvus():
    """Connect to Milvus instance"""
    print("=" * 80)
    print("CONNECTING TO MILVUS")
    print("=" * 80)
    print(f"Host: {MILVUS_HOST}")
    print(f"Port: {MILVUS_PORT}")
    
    try:
        if MILVUS_USER and MILVUS_PASSWORD:
            connections.connect(
                alias="default",
                host=MILVUS_HOST,
                port=MILVUS_PORT,
                user=MILVUS_USER,
                password=MILVUS_PASSWORD,
                secure=True
            )
        else:
            connections.connect(
                alias="default",
                host=MILVUS_HOST,
                port=MILVUS_PORT
            )
        print("✓ Connected to Milvus successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to connect to Milvus: {str(e)}")
        return False


def create_collection():
    """Create Milvus collection with proper schema"""
    print("\n" + "=" * 80)
    print("CREATING COLLECTION")
    print("=" * 80)
    
    # Define schema
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="app_code", dtype=DataType.VARCHAR, max_length=10),
        FieldSchema(name="application_name", dtype=DataType.VARCHAR, max_length=500),
        FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=5000),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=EMBEDDING_DIM)
    ]
    
    schema = CollectionSchema(
        fields=fields,
        description="Victor Apps Product Ownership Information"
    )
    
    # Check if collection exists
    if utility.has_collection(COLLECTION_NAME):
        print(f"Collection '{COLLECTION_NAME}' already exists")
        response = input("Do you want to drop and recreate it? (yes/no): ")
        if response.lower() == 'yes':
            utility.drop_collection(COLLECTION_NAME)
            print(f"✓ Dropped existing collection '{COLLECTION_NAME}'")
        else:
            print("Using existing collection")
            return Collection(COLLECTION_NAME)
    
    # Create collection
    collection = Collection(name=COLLECTION_NAME, schema=schema)
    print(f"✓ Created collection '{COLLECTION_NAME}'")
    
    return collection


def verify_slate_api_connection():
    """Verify watsonx.ai API connection and get embedding dimension"""
    print("\n" + "=" * 80)
    print("VERIFYING WATSONX.AI SLATE API CONNECTION")
    print("=" * 80)
    print(f"Model: {EMBEDDING_MODEL}")
    print(f"Endpoint: {WATSONX_URL}")
    
    if not WATSONX_API_KEY or not WATSONX_PROJECT_ID:
        print("✗ WATSONX_API_KEY and WATSONX_PROJECT_ID must be set")
        return None
    
    try:
        # Support both API key and IAM token
        # IAM tokens contain special characters like +, =, :
        # API keys are typically alphanumeric
        auth_value = WATSONX_API_KEY
        if any(c in WATSONX_API_KEY for c in ['+', '=', ':']):
            # This looks like an IAM token
            if not auth_value.startswith("Bearer "):
                auth_value = f"Bearer {auth_value}"
        else:
            # This looks like an API key
            auth_value = f"Bearer {auth_value}"
        
        endpoint = f"{WATSONX_URL}/ml/v1/text/embeddings?version=2023-05-29"
        headers = {
            "Authorization": auth_value,
            "Content-Type": "application/json"
        }
        payload = {
            "model_id": EMBEDDING_MODEL,
            "inputs": ["test"],
            "project_id": WATSONX_PROJECT_ID
        }
        
        response = requests.post(endpoint, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        test_embedding = result['results'][0]['embedding']
        actual_dim = len(test_embedding)
        
        print(f"✓ API connection successful")
        print(f"✓ Embedding dimension: {actual_dim}")
        
        global EMBEDDING_DIM
        if actual_dim != EMBEDDING_DIM:
            print(f"⚠ Updating EMBEDDING_DIM from {EMBEDDING_DIM} to {actual_dim}")
            EMBEDDING_DIM = actual_dim
        
        return {
            'api_key': WATSONX_API_KEY,
            'project_id': WATSONX_PROJECT_ID,
            'url': WATSONX_URL,
            'dimension': actual_dim
        }
    except Exception as e:
        print(f"✗ API connection failed: {str(e)}")
        return None


def load_data_from_files():
    """Load application data from prepared text files"""
    print("\n" + "=" * 80)
    print("LOADING DATA FROM FILES")
    print("=" * 80)
    print(f"Directory: {KB_DATA_DIR}")
    
    if not os.path.exists(KB_DATA_DIR):
        print(f"✗ Directory '{KB_DATA_DIR}' not found")
        print("Please run 'python prepare_kb_data.py' first")
        return None
    
    files = sorted([f for f in os.listdir(KB_DATA_DIR) if f.endswith('.txt')])
    
    if not files:
        print(f"✗ No .txt files found in '{KB_DATA_DIR}'")
        return None
    
    print(f"Found {len(files)} application files")
    
    app_codes = []
    application_names = []
    contents = []
    
    for filename in files:
        app_code = filename.replace('.txt', '')
        filepath = os.path.join(KB_DATA_DIR, filename)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract application name from content (first line)
        lines = content.split('\n')
        app_name = lines[0].replace('APPLICATION: ', '').strip() if lines else app_code
        
        app_codes.append(app_code)
        application_names.append(app_name)
        contents.append(content)
        
        if len(app_codes) % 50 == 0:
            print(f"  Loaded {len(app_codes)} applications...")
    
    print(f"✓ Loaded {len(app_codes)} applications")
    
    return {
        'app_codes': app_codes,
        'application_names': application_names,
        'contents': contents
    }


def generate_embeddings(api_config, contents):
    """Generate embeddings using IBM Slate model via watsonx.ai REST API"""
    print("\n" + "=" * 80)
    print("GENERATING EMBEDDINGS WITH IBM SLATE (REST API)")
    print("=" * 80)
    print(f"Processing {len(contents)} documents...")
    
    embeddings = []
    batch_size = 10
    
    # Support both API key and IAM token
    auth_value = api_config['api_key']
    if any(c in api_config['api_key'] for c in ['+', '=', ':']):
        # This looks like an IAM token
        if not auth_value.startswith("Bearer "):
            auth_value = f"Bearer {auth_value}"
    else:
        # This looks like an API key
        auth_value = f"Bearer {auth_value}"
    
    endpoint = f"{api_config['url']}/ml/v1/text/embeddings?version=2023-05-29"
    headers = {
        "Authorization": auth_value,
        "Content-Type": "application/json"
    }
    
    for i in range(0, len(contents), batch_size):
        batch = contents[i:i + batch_size]
        
        payload = {
            "model_id": EMBEDDING_MODEL,
            "inputs": batch,
            "project_id": api_config['project_id']
        }
        
        try:
            response = requests.post(endpoint, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            batch_embeddings = [r['embedding'] for r in result['results']]
            embeddings.extend(batch_embeddings)
            
            if (i + batch_size) % 50 == 0 or (i + batch_size) >= len(contents):
                print(f"  Generated embeddings for {min(i + batch_size, len(contents))} documents...")
        
        except requests.exceptions.RequestException as e:
            print(f"✗ Failed to generate embeddings for batch {i//batch_size + 1}: {str(e)}")
            return None
    
    print(f"✓ Generated {len(embeddings)} embeddings")
    return embeddings


def insert_data(collection, data, embeddings):
    """Insert data into Milvus collection"""
    print("\n" + "=" * 80)
    print("INSERTING DATA INTO MILVUS")
    print("=" * 80)
    
    try:
        entities = [
            data['app_codes'],
            data['application_names'],
            data['contents'],
            embeddings
        ]
        
        print(f"Inserting {len(data['app_codes'])} records...")
        collection.insert(entities)
        collection.flush()
        
        print(f"✓ Inserted {len(data['app_codes'])} records successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to insert data: {str(e)}")
        return False


def create_index(collection):
    """Create index on embedding field for fast search"""
    print("\n" + "=" * 80)
    print("CREATING INDEX")
    print("=" * 80)
    
    try:
        index_params = {
            "metric_type": "L2",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 128}
        }
        
        print("Creating index on 'embedding' field...")
        collection.create_index(
            field_name="embedding",
            index_params=index_params
        )
        
        print("✓ Index created successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to create index: {str(e)}")
        return False


def load_collection(collection):
    """Load collection into memory"""
    print("\n" + "=" * 80)
    print("LOADING COLLECTION")
    print("=" * 80)
    
    try:
        collection.load()
        print("✓ Collection loaded into memory")
        return True
    except Exception as e:
        print(f"✗ Failed to load collection: {str(e)}")
        return False


def verify_data(collection):
    """Verify data was loaded correctly"""
    print("\n" + "=" * 80)
    print("VERIFYING DATA")
    print("=" * 80)
    
    try:
        num_entities = collection.num_entities
        print(f"Total entities in collection: {num_entities}")
        
        # Sample query to verify
        print("\nTesting sample query...")
        results = collection.query(
            expr="app_code == 'AAA'",
            output_fields=["app_code", "application_name"]
        )
        
        if results:
            print(f"✓ Sample query successful")
            print(f"  Found: {results[0]['application_name']} ({results[0]['app_code']})")
        else:
            print("⚠ Sample query returned no results")
        
        return True
    except Exception as e:
        print(f"✗ Verification failed: {str(e)}")
        return False


def main():
    """Main execution function"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  LOAD VICTOR APPS DATA INTO MILVUS (IBM SLATE)".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")
    
    # Step 1: Connect to Milvus
    if not connect_to_milvus():
        return False
    
    # Step 2: Verify Slate API connection
    api_config = verify_slate_api_connection()
    if not api_config:
        return False
    
    # Step 3: Create collection (with updated EMBEDDING_DIM)
    collection = create_collection()
    if not collection:
        return False
    
    # Step 4: Load data from files
    data = load_data_from_files()
    if not data:
        return False
    
    # Step 5: Generate embeddings via REST API
    embeddings = generate_embeddings(api_config, data['contents'])
    if not embeddings:
        return False
    
    # Step 6: Insert data
    if not insert_data(collection, data, embeddings):
        return False
    
    # Step 7: Create index
    if not create_index(collection):
        return False
    
    # Step 8: Load collection
    if not load_collection(collection):
        return False
    
    # Step 9: Verify data
    if not verify_data(collection):
        return False
    
    # Success!
    print("\n" + "=" * 80)
    print("SUCCESS!")
    print("=" * 80)
    print(f"✓ Successfully loaded {len(data['app_codes'])} applications into Milvus")
    print(f"  Collection: {COLLECTION_NAME}")
    print(f"  Host: {MILVUS_HOST}:{MILVUS_PORT}")
    print(f"  Embedding Model: {EMBEDDING_MODEL}")
    print(f"  Embedding Dimension: {EMBEDDING_DIM}")
    print("\nNext steps:")
    print("1. Test the search_knowledge_base tool")
    print("2. Deploy the tool to watsonx Orchestrate")
    print("=" * 80)
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        exit(1)
    except Exception as e:
        print(f"\n\n✗ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)

# Made with Bob

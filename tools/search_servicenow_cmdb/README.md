# ServiceNow CMDB Search Tool

This tool provides semantic search capabilities for ServiceNow CMDB business applications with automatic PII obfuscation and IBM Granite embeddings.

## Overview

The tool:
1. Fetches live data from ServiceNow CMDB (`cmdb_ci_business_app` table)
2. Obfuscates all PII (names, IDs, emails) using deterministic Faker generation
3. Generates embeddings for each application using IBM Granite embedding model
4. Performs cosine similarity search to find top_k matching applications
5. Returns formatted results with obfuscated contact information

## Architecture

### Files

- **`search_servicenow_cmdb.py`** - Main tool entry point with `@tool` decorator
- **`servicenow_client.py`** - ServiceNow API client using urllib (air-gapped compatible)
- **`obfuscation_utils.py`** - Faker-based deterministic PII obfuscation
- **`embedding_utils.py`** - IBM Granite embedding generation via HTTP endpoint
- **`search_utils.py`** - Cosine similarity search and result formatting
- **`requirements.txt`** - Dependencies (requests, numpy, faker)
- **`__init__.py`** - Package initialization

### Data Flow

```
User Query
    ↓
search_servicenow_cmdb()
    ↓
ServiceNow API (fetch_cmdb_applications)
    ↓
Parse & Transform Records
    ↓
Obfuscate PII (obfuscate_person_fields)
    ↓
Generate Embeddings (get_granite_embeddings_batch)
    ↓
Cosine Similarity Search
    ↓
Format Results
    ↓
Return to User
```

## Field Mappings

### ServiceNow → Metadata

| ServiceNow Field | Metadata Field | Role | Obfuscated? |
|-----------------|----------------|------|-------------|
| `name` | `application_name` | Application Name | No |
| `u_mnemonic_id` | `app_code` | App Code | No |
| `short_description` | `description` | Description | No |
| `owned_by.name` | `product_owner` | Product Owner | **Yes** |
| `owned_by.user_name` | `owner_id` | Owner ID | **Yes** |
| `owned_by.email` | `owner_email` | Owner Email | **Yes** |
| `managed_by.name` | `rtb_asm_name` | RTB_ASM | **Yes** |
| `managed_by.user_name` | `rtb_asm_id` | RTB_ASM ID | **Yes** |
| `managed_by.email` | `rtb_asm_email` | RTB_ASM Email | **Yes** |
| `it_application_owner.name` | `it_app_owner_name` | IT App Owner | **Yes** |
| `it_application_owner.user_name` | `it_app_owner_id` | IT App Owner ID | **Yes** |
| `it_application_owner.email` | `it_app_owner_email` | IT App Owner Email | **Yes** |
| `application_manager.name` | `cio_name` | CIO | **Yes** |
| `application_manager.user_name` | `cio_id` | CIO ID | **Yes** |
| `application_manager.email` | `cio_email` | CIO Email | **Yes** |
| `business_criticality` | `business_criticality` | Criticality | No |
| `data_classification` | `data_classification` | Classification | No |

## Configuration

### ServiceNow Connection

- **App ID:** `test_token`
- **Type:** Bearer Token
- **Endpoint:** `/api/now/table/cmdb_ci_business_app`
- **Limit:** 300 records
- **SSL Verification:** Disabled (air-gapped environment)

### Embedding Configuration

- **Endpoint:** `http://granite-embedding-wxo.pnc-rhoai.svc.cluster.local/v1/embeddings`
- **Model:** `granite-embedding`
- **Batch Size:** 32 records per request
- **Timeout:** 30 seconds (single), 60 seconds (batch)

## Usage

### Tool Function

```python
search_servicenow_cmdb(query: str, top_k: int = 3) -> str
```

**Parameters:**
- `query` (str): Search query (e.g., "Who owns FBAR?")
- `top_k` (int): Number of results to return (default: 3, max: 20)

**Returns:**
- Formatted markdown string with search results

### Example Queries

```python
# By application code
search_servicenow_cmdb("Who owns FBAR?")

# By application name
search_servicenow_cmdb("Find the FBAR application")

# By role
search_servicenow_cmdb("Who is the RTB_ASM for FBAR?")

# By keyword
search_servicenow_cmdb("Financial reporting applications")
```

## Deployment

### Prerequisites

1. ServiceNow connection configured in watsonx Orchestrate with app_id `test_token`
2. IBM Granite embedding endpoint accessible
3. Python dependencies installed (requests, numpy, faker)

### Import to watsonx Orchestrate

```bash
orchestrate tools import \
  -k python \
  -p tools/search_servicenow_cmdb \
  -f tools/search_servicenow_cmdb/search_servicenow_cmdb.py \
  -r tools/search_servicenow_cmdb/requirements.txt
```

### Agent Configuration

The agent is configured in `src/product_ownership_agent.py` with:
- Tool reference: `tools=["search_servicenow_cmdb"]`
- Updated instructions for ServiceNow CMDB fields
- Corrected role mappings (OWNED_BY, MANAGED_BY, IT_APPLICATION_OWNER, APPLICATION_MANAGER)

## Privacy & Security

### PII Obfuscation

All personal information is obfuscated using deterministic Faker generation:

- **Input:** Real ID (e.g., "P067926")
- **Process:** MD5 hash → Faker seed → Generate fake identity
- **Output:** Fake ID (e.g., "ID12345"), Name (e.g., "John Doe"), Email (e.g., "john.doe@pnc.com")

**Key Properties:**
- Same real ID always generates same fake identity (consistency)
- No real PII appears in embeddings, cache, or responses
- Safe for development, testing, and sharing

### Security Considerations

- SSL verification disabled for air-gapped environment
- Bearer token authentication for ServiceNow
- No credentials stored in code
- All PII obfuscated before embedding generation

## Testing

### Manual Testing

1. **Test ServiceNow Connection:**
   ```python
   from servicenow_client import fetch_cmdb_applications
   apps = fetch_cmdb_applications(base_url, token)
   print(f"Retrieved {len(apps)} applications")
   ```

2. **Test Obfuscation:**
   ```python
   from obfuscation_utils import generate_fake_identity
   fake_id, fake_name, fake_email = generate_fake_identity("P067926")
   print(f"{fake_id}, {fake_name}, {fake_email}")
   # Should always produce same output for same input
   ```

3. **Test Embedding Generation:**
   ```python
   from embedding_utils import get_granite_embedding
   embedding = get_granite_embedding("test query")
   print(f"Embedding dimension: {len(embedding)}")
   ```

4. **Test Full Tool:**
   ```python
   result = search_servicenow_cmdb("Who owns FBAR?", top_k=3)
   print(result)
   ```

### Expected Behavior

- Tool should fetch live data from ServiceNow
- All PII should be obfuscated in results
- Semantic search should return relevant applications
- Results should include all role information with correct field names

## Troubleshooting

### Common Issues

1. **ServiceNow Connection Failed**
   - Verify Bearer Token is valid
   - Check base_url is correct
   - Ensure network connectivity

2. **Embedding Generation Failed**
   - Verify Granite endpoint is accessible
   - Check endpoint URL and model ID
   - Ensure sufficient timeout

3. **No Results Found**
   - Check ServiceNow query returns data
   - Verify embedding generation succeeded
   - Try different search queries

4. **Import Errors**
   - Ensure all dependencies installed (requests, numpy, faker)
   - Check Python version compatibility
   - Verify file structure is correct

## Differences from Previous Implementation

### Old Tool (search_knowledge_base)
- Static file-based knowledge base
- Pre-computed embeddings from text files
- No PII obfuscation
- Fields: product_owner, rtb_asm, ctb_asm, cio

### New Tool (search_servicenow_cmdb)
- Live ServiceNow CMDB data
- On-demand embedding generation
- Automatic PII obfuscation
- Corrected fields: owned_by, managed_by, it_application_owner, application_manager
- Additional fields: business_criticality, data_classification

## Made with Bob
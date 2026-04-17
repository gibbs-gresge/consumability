# Product Ownership Agent for watsonx Orchestrate

A helpful AI agent that provides accurate, knowledge base-grounded responses about PNC product ownership and management roles.

## 🎯 Overview

This agent helps developers and architects find information about:
- **Product Owners (OWNED_BY)** - Primary application owners
- **RTB_ASM (RUN THE BANK APPLICATION SYSTEM MANAGER)** - Sev1 type response personnel
- **CTB_ASM (CHANGE THE BANK ASM)** - Tech Leaders overseeing change requests, new versions, and bug fixes

### Key Features

✅ **Knowledge Base Grounded** - Uses PNC Apps document as source of truth
✅ **Flexible Search** - Search by code, name, description, or keywords
✅ **Helpful Responses** - Clear, complete information with guidance
✅ **Multiple Search Methods** - Supports exact matching and semantic search
✅ **Clear "Not Found" Handling** - Helpful suggestions when information is unavailable
✅ **Complete Contact Information** - Returns name, employee ID, and email for all roles
✅ **Precise Chunking** - Optional Milvus setup for one-application-per-chunk accuracy

## 📁 Project Structure

```
.
├── config/                          # Configuration files
│   ├── .env.example               # Environment variables template (Milvus credentials)
│   └── excel_schema.md            # Excel file schema documentation
├── data/                           # Data files
│   ├── kb_data/                   # Knowledge base data (individual app files)
│   └── source/                    # Source data files
│       ├── Victor Apps (Products and Services) - Updated.xlsx
│       ├── EXPORT SNOW Business App.xlsx
│       └── victor_apps_consolidated.txt
├── docs/                           # Documentation
│   ├── DEPLOYMENT.md              # Deployment guide
│   ├── MILVUS_SETUP.md           # Milvus setup guide
│   └── README.md                  # Detailed documentation
├── scripts/                        # Utility scripts
│   ├── prepare_kb_data.py         # Data preparation
│   └── load_to_milvus.py          # Load data to Milvus
├── src/                            # Source code (agent/KB definitions)
│   ├── product_ownership_agent.py
│   ├── pnc_catalog_replica.html
│   └── product_ownership_kb_milvus.py
├── .gitignore                      # Git ignore rules
└── README.md                       # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

Install required Python packages:
- `ibm-watsonx-orchestrate`
- `pymilvus` (for Milvus setup)
- `sentence-transformers` (for embeddings)
- `pandas`, `openpyxl` (for data processing)

### 2. Configure Environment (for Milvus setup)

```bash
# Copy the example environment file
cp config/.env.example config/.env

# Edit config/.env with your Milvus credentials
```

### 3. Authenticate to watsonx Orchestrate

```bash
orchestrate login
```

### 4. Prepare and Deploy

```bash
# Prepare knowledge base data
python scripts/prepare_kb_data.py

# For Milvus setup: Load data to Milvus
python scripts/load_to_milvus.py

# Export and import knowledge base and agent using watsonx Orchestrate CLI
```

## 📖 Documentation

- **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** - Complete deployment guide with troubleshooting
- **[docs/MILVUS_SETUP.md](docs/MILVUS_SETUP.md)** - External Milvus setup guide

## 🔍 Query Examples

### By Application Code
```
User: "Who owns AAA?"
Agent: Returns complete ownership info for AAA - Enterprise RADIUS
```

### By Application Name (Full or Partial)
```
User: "Who is the Product Owner for Enterprise RADIUS?"
Agent: Returns ownership info for AAA application
```

### By Description or Keywords
```
User: "Who manages the RADIUS authentication system?"
Agent: Finds AAA based on description and returns complete info
```

### By Role
```
User: "Who is the RTB_ASM for ABR?"
Agent: Returns RTB_ASM contact details for ABR
```

## 🔄 Updating the Knowledge Base

### Option 1: Built-in Knowledge Base

```bash
# 1. Replace the Excel file in data/source/
cp "new-victor-apps.xlsx" "data/source/Victor Apps (Products and Services) - Updated.xlsx"

# 2. Prepare data for better chunking
python scripts/prepare_kb_data.py

# 3. Delete old knowledge base and re-import
orchestrate knowledge-bases delete product_ownership_kb
orchestrate knowledge-bases import -f product_ownership_kb.yaml
```

### Option 2: External Milvus (Recommended)

```bash
# 1. Update Excel file
cp "new-victor-apps.xlsx" "data/source/Victor Apps (Products and Services) - Updated.xlsx"

# 2. Prepare data
python scripts/prepare_kb_data.py

# 3. Reload into Milvus
python scripts/load_to_milvus.py

# 4. Re-deploy knowledge base
orchestrate knowledge-bases delete product_ownership_kb
orchestrate knowledge-bases import -f product_ownership_kb_milvus.yaml -a milvus_credentials
```

See [docs/MILVUS_SETUP.md](docs/MILVUS_SETUP.md) for detailed Milvus configuration.

**Note:** The embedding model used is `sentence-transformers/all-MiniLM-L6-v2` for optimal performance.

## 🐛 Troubleshooting

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for complete troubleshooting guide.

## 🔒 Security Considerations

- PNC Apps document contains employee information
- Ensure proper access controls in watsonx Orchestrate
- Follow PNC data handling policies
- Enable audit logging
- Regularly review access permissions

## 📝 License

Internal PNC use only. Not for external distribution.

---

**Version:** 1.0.0  
**Last Updated:** 2026-02-10  
**Maintained By:** AI Agent Development Team
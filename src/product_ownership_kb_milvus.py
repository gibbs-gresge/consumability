"""
Product Ownership Knowledge Base Configuration - External Milvus
This configuration uses an external Milvus instance for better chunking control.
Each application is stored as a separate document/chunk.
"""

from ibm_watsonx_orchestrate.agent_builder.knowledge_bases.knowledge_base import KnowledgeBase
from ibm_watsonx_orchestrate.agent_builder.knowledge_bases.types import (
    ConversationalSearchConfig,
    IndexConnection,
    MilvusConnection
)

# External Milvus knowledge base with precise chunking control
product_ownership_kb_milvus = KnowledgeBase(
    name="product_ownership_kb",
    description="""
    Knowledge base containing comprehensive information about PNC product ownership and management roles.
    This includes:
    - Product Owners (OWNED_BY) - Primary application owners
    - RTB_ASM (RUN THE BANK APPLICATION SYSTEM MANAGER) - Sev1 type response personnel
    - CTB_ASM (CHANGE THE BANK ASM) - Tech Leaders overseeing change requests, new versions, and bug fixes
    
    The knowledge base can be queried by:
    - Application name (e.g., "AAA - Enterprise RADIUS", "Enterprise RADIUS")
    - Three-letter application code (e.g., "AAA", "ABA", "ABR")
    - Application description or keywords (e.g., "RADIUS authentication", "database management")
    - Technology or function (e.g., "Kubernetes", "email services")
    
    Each application is stored as a separate document for precise retrieval.
    All information is sourced from the PNC Apps (Products and Services).
    """,
    conversational_search_tool=ConversationalSearchConfig(
        index_config=[
            IndexConnection(
                milvus=MilvusConnection(
                    # Connection details - update with your Milvus credentials
                    host="${MILVUS_HOST}",  # e.g., "your-milvus-instance.com"
                    port="${MILVUS_PORT}",  # e.g., 19530
                    collection_name="${MILVUS_COLLECTION}",
                    
                    # Authentication
                    user="${MILVUS_USER}",
                    password="${MILVUS_PASSWORD}",
                    
                    # Field mapping for search results
                    field_mapping={
                        "title": "application_name",  # Maps to application name
                        "body": "content",            # Maps to full application details
                        "url": "app_code"             # Maps to application code
                    },
                    
                    # Embedding configuration
                    embeddings_model_name="sentence-transformers/all-MiniLM-L6-v2"
                )
            )
        ]
    )
)

# Note: Before deploying, replace ${MILVUS_*} placeholders with actual values
# or set them as environment variables

# Made with Bob

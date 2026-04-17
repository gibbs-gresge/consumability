"""
Application configuration settings.
Loads environment variables and provides configuration dictionaries.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# Workday API configuration
workday = {
    "client_id": os.getenv("WORKDAY_CLIENT_ID", ""),
    "client_secret": os.getenv("WORKDAY_CLIENT_SECRET", ""),
    "api_url": os.getenv("WORKDAY_API_URL", "https://api.workday.com/v1"),
    "token_endpoint": os.getenv("WORKDAY_TOKEN_ENDPOINT", ""),
    "scope": "employee:read manager:read"
}


# ServiceNow API configuration
servicenow = {
    "client_id": os.getenv("SNOW_CLIENT_ID", ""),
    "client_secret": os.getenv("SNOW_CLIENT_SECRET", ""),
    "api_url": os.getenv("SNOW_API_URL", ""),
    "token_endpoint": os.getenv("SNOW_TOKEN_ENDPOINT", ""),
    "scope": "useraccount"
}


# Microsoft Teams API configuration
teams = {
    "client_id": os.getenv("TEAMS_CLIENT_ID", ""),
    "client_secret": os.getenv("TEAMS_CLIENT_SECRET", ""),
    "tenant_id": os.getenv("TEAMS_TENANT_ID", ""),
    "api_url": os.getenv("TEAMS_API_URL", "https://graph.microsoft.com/v1.0"),
    "auth_endpoint": os.getenv("TEAMS_AUTH_ENDPOINT", ""),
    "token_endpoint": os.getenv("TEAMS_TOKEN_ENDPOINT", ""),
    "scope": "Chat.ReadWrite ChannelMessage.Send"
}


# Approval System API configuration
approval = {
    "api_key": os.getenv("APPROVAL_API_KEY", ""),
    "api_url": os.getenv("APPROVAL_API_URL", "")
}


# watsonx Orchestrate configuration
watsonx = {
    "api_key": os.getenv("WXO_API_KEY", ""),
    "project_id": os.getenv("WXO_PROJECT_ID", ""),
    "region": os.getenv("WXO_REGION", "us-south")
}


# Groq LLM configuration
groq = {
    "api_key": os.getenv("GROQ_API_KEY", ""),
    "model": "gpt-oss-120b",
    "temperature": 0.7,
    "max_tokens": 2000
}


# Milvus vector database configuration
milvus = {
    "host": os.getenv("MILVUS_HOST", "localhost"),
    "port": int(os.getenv("MILVUS_PORT", "19530")),
    "user": os.getenv("MILVUS_USER", "root"),
    "password": os.getenv("MILVUS_PASSWORD", "")
}


# Elasticsearch configuration
elasticsearch = {
    "host": os.getenv("ELASTICSEARCH_HOST", "localhost"),
    "port": int(os.getenv("ELASTICSEARCH_PORT", "9200")),
    "user": os.getenv("ELASTICSEARCH_USER", "elastic"),
    "password": os.getenv("ELASTICSEARCH_PASSWORD", "")
}


# Application configuration
app = {
    "env": os.getenv("APP_ENV", "development"),
    "log_level": os.getenv("LOG_LEVEL", "INFO"),
    "debug": os.getenv("DEBUG", "false").lower() == "true",
    "session_timeout": int(os.getenv("SESSION_TIMEOUT", "3600")),
    "max_concurrent_sessions": int(os.getenv("MAX_CONCURRENT_SESSIONS", "100"))
}


# Monitoring configuration
monitoring = {
    "prometheus_port": int(os.getenv("PROMETHEUS_PORT", "9090")),
    "metrics_enabled": os.getenv("METRICS_ENABLED", "true").lower() == "true"
}


# Main settings dictionary containing all configuration
settings = {
    "workday": workday,
    "servicenow": servicenow,
    "teams": teams,
    "approval": approval,
    "watsonx": watsonx,
    "groq": groq,
    "milvus": milvus,
    "elasticsearch": elasticsearch,
    "app": app,
    "monitoring": monitoring
}

# Made with Bob

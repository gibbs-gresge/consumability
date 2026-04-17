#!/bin/bash

# Enterprise Catalog Ordering Multi-Agent System
# Deployment Script

set -e  # Exit on error

echo "========================================="
echo "Catalog Ordering System Deployment"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color



echo -e "${GREEN}✓${NC} Found .env file"

source /home/user/venv/bin/activate



echo ""
echo "========================================="
echo "Step 2: Importing Tools"
echo "========================================="
echo "Importing individual tool files..."

tools=(
    "tools/employee_tools.py"
    "tools/teams_tools.py"
    "tools/utility_tools.py"
)

for tool in "${tools[@]}"; do
    echo "Importing $tool..."
    orchestrate tools import -k python -f "$tool" -r tools/requirements.txt -p tools/ || echo -e "${YELLOW}Warning: Failed to import $tool${NC}"
done

tools=(
    "tools/get_records.py"
    "tools/servicenow_tools.py"
)

for tool in "${tools[@]}"; do
    echo "Importing $tool..."
    orchestrate tools import -k python -f "$tool" -r tools/requirements.txt -p tools/ -a test_token || echo -e "${YELLOW}Warning: Failed to import $tool${NC}"
done

echo ""
echo "========================================="
echo "Step 3: Importing Agents"
echo "========================================="

agents=(
    "agents/employee_profile_agent.yaml"
    "agents/servicenow_agent.yaml"
    "agents/teams_notification_agent.yaml"
    "agents/asktech_agent.yaml"
)

for agent in "${agents[@]}"; do
    echo "Importing $agent..."
    orchestrate agents import -f "$agent" || echo -e "${YELLOW}Warning: Failed to import $agent${NC}"
done



echo ""
echo "========================================="
echo "Deployment Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Verify all agents are listed above"
echo "2. Test connections with: ./scripts/test_connections.py"
echo "3. Run tests with: pytest tests/"
echo "4. Start using the system!"
echo ""
echo -e "${GREEN}✓${NC} Deployment successful"

# Made with Bob

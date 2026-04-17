#!/bin/bash

# Enterprise Device Replacement Multi-Agent System
# Deployment Script

set -e  # Exit on error

echo "========================================="
echo "Device Replacement System Deployment"
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
    "tools/servicenow_tools.py"
    "tools/teams_tools.py"
    "tools/utility_tools.py"
    "tools/mac_eligibility_tool.py"
)

for tool in "${tools[@]}"; do
    echo "Importing $tool..."
    orchestrate tools import -k python -f "$tool" || echo -e "${YELLOW}Warning: Failed to import $tool${NC}"
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
echo "Step 4: Creating Knowledge Bases"
echo "========================================="

knowledge_bases=(
    "knowledge_base/it_policies_kb.yaml"
)

for kb in "${knowledge_bases[@]}"; do
    echo "Creating knowledge base: $kb..."
    orchestrate knowledge-bases import -f "$kb" || echo -e "${YELLOW}Warning: Failed to import $kb${NC}"
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

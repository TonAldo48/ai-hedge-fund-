#!/bin/bash

# Test Chat Agents via curl
# Uses the provided API key for authentication

API_KEY="Pb9RPNoA1neVLA6teD-GFTbUh8EI9TFe5QK9aN3z_Aw"
API_BASE_URL="http://localhost:8000"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}AI Hedge Fund Chat Agents Test (curl)${NC}"
echo "======================================"

# Test health endpoint
echo -e "\n${YELLOW}Testing health check...${NC}"
curl -s -X GET "$API_BASE_URL/health" \
  -H "Authorization: Bearer $API_KEY" | jq '.'

# Function to test an agent
test_agent() {
    local agent_id=$1
    local agent_name=$2
    local question=$3
    
    echo -e "\n${YELLOW}Testing $agent_name ($agent_id)...${NC}"
    echo "Question: $question"
    echo "---"
    
    response=$(curl -s -X POST "$API_BASE_URL/api/agents/$agent_id/chat" \
      -H "Authorization: Bearer $API_KEY" \
      -H "Content-Type: application/json" \
      -d "{
        \"message\": \"$question\",
        \"conversation_id\": \"test-$agent_id-$(date +%s)\"
      }")
    
    # Check if response is valid JSON
    if echo "$response" | jq empty 2>/dev/null; then
        echo -e "${GREEN}✓ Success${NC}"
        echo "$response" | jq -r '.response' | head -c 200
        echo "..."
        
        # Show metadata if available
        metadata=$(echo "$response" | jq '.metadata // empty')
        if [ ! -z "$metadata" ] && [ "$metadata" != "null" ]; then
            echo -e "\n${BLUE}Metadata:${NC}"
            echo "$metadata" | jq '.'
        fi
    else
        echo -e "${RED}✗ Failed${NC}"
        echo "$response"
    fi
}

# Test each agent
echo -e "\n${BLUE}Testing Individual Agents${NC}"
echo "========================="

test_agent "warren-buffett" "Warren Buffett" "What are your thoughts on value investing?"
sleep 1

test_agent "peter-lynch" "Peter Lynch" "How do you find growth stocks?"
sleep 1

test_agent "charlie-munger" "Charlie Munger" "What mental models do you recommend?"
sleep 1

test_agent "ben-graham" "Ben Graham" "How do you calculate intrinsic value?"
sleep 1

test_agent "technical-analyst" "Technical Analyst" "What indicators show a bullish trend?"

# Test streaming (optional)
echo -e "\n${BLUE}Testing Streaming Response${NC}"
echo "=========================="
echo "Testing Warren Buffett with streaming..."

curl -N -X POST "$API_BASE_URL/api/agents/warren-buffett/chat" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain value investing briefly",
    "conversation_id": "test-stream-'$(date +%s)'",
    "stream": true
  }' 2>/dev/null | head -20

echo -e "\n\n${GREEN}Test completed!${NC}" 
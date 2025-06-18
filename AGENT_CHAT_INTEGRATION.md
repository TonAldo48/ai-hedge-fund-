# Agent Chat Integration Guide

## Overview

This guide explains how the AI hedge fund agent chat system works, connecting the frontend chat interface with the backend agent services.

## Architecture

```
Frontend (Next.js)          Backend (FastAPI)
    │                           │
    ├─ Agent Chat Pages        ├─ Agent Routes
    │   └─ AgentChat Component │   └─ /api/agents/{agent}/analyze
    │                           │
    ├─ useAgentChat Hook       ├─ Agent Services
    │   └─ API calls           │   └─ Process queries
    │                           │
    └─ Visual Indicators       └─ Individual Agents
        ├─ Agent Icon              ├─ Warren Buffett
        ├─ Agent Name              ├─ Peter Lynch
        ├─ Expertise Tags          ├─ Charlie Munger
        └─ Custom Greeting         ├─ Ben Graham
                                   └─ Technical Analyst
```

## Key Components

### Frontend Components

1. **AgentChat Component** (`app/frontend/components/agent-chat.tsx`)
   - Main chat interface for agent interactions
   - Displays agent header with visual indicators
   - Handles message display and input
   - Shows loading states and errors

2. **useAgentChat Hook** (`app/frontend/hooks/use-agent-chat.ts`)
   - Manages chat state and API communication
   - Handles message sending and receiving
   - Manages loading and error states

3. **Agent Pages** (`app/frontend/app/(chat)/chat/agent/[agent-name]/page.tsx`)
   - Individual pages for each agent
   - Configure agent-specific data
   - Render AgentChat component

### Backend Components

1. **Agent Routes** (`app/backend/routes/agents_chat.py`)
   - RESTful API endpoints for agent interactions
   - Authentication via API key
   - Route: `/api/agents/{agent_name}/analyze`

2. **Agent Services** (`app/backend/services/*_chat_agent.py`)
   - Individual agent implementations
   - Process user queries with agent-specific logic
   - Return formatted responses

## Visual Indicators

Each agent chat interface includes:

1. **Agent Header**
   - Agent icon (emoji)
   - Agent name
   - Brief description

2. **Expertise Tags**
   - Skills and specialties
   - Displayed in the greeting

3. **Custom Greeting**
   - Agent-specific welcome message
   - Shows expertise areas
   - Prompts user interaction

## API Integration

### Request Format
```json
{
  "message": "User's question",
  "chat_history": [
    {"role": "user", "content": "Previous question"},
    {"role": "assistant", "content": "Previous answer"}
  ]
}
```

### Response Format
```json
{
  "response": "Agent's analysis and recommendations",
  "timestamp": "2024-01-20T10:30:00Z",
  "agent_name": "warren_buffett"
}
```

### Authentication
- API Key: `Pb9RPNoA1neVLA6teD-GFTbUh8EI9TFe5QK9aN3z_Aw`
- Header: `Authorization: Bearer {API_KEY}`

## Follow-up Questions and Chat History

The agent chat system maintains conversation context to enable meaningful follow-up questions:

1. **Frontend State Management**
   - The `useAgentChat` hook maintains all messages in local state
   - Each new message includes the full chat history in the API request

2. **Backend Context Processing**
   - The backend extracts the last 5 messages from chat history (configurable)
   - Creates a context string from previous Q&A pairs
   - Prepends this context to the current question
   
   **Why 5 messages?**
   - **Token limits**: LLMs have context window limits (4k-128k tokens)
   - **Cost efficiency**: More context = more tokens = higher API costs
   - **Relevance decay**: Older messages become less relevant over time
   - **Performance**: Shorter prompts process faster
   - **Focus**: Recent context is usually most relevant for follow-ups

3. **Context-Aware Responses**
   - Agents can reference previous topics discussed
   - Maintains continuity across multiple questions
   - Enables deeper analysis through follow-up queries

### Example Conversation Flow
```
User: "What's Apple's competitive moat?"
Agent: "Apple has a strong moat with..."

User: "How does that compare to Microsoft?"
Agent: "Comparing to Microsoft's moat..." (understands "that" refers to Apple's moat)

User: "Which would you prefer long-term?"
Agent: "Between Apple and Microsoft..." (maintains context of comparison)
```

## Available Agents

1. **Warren Buffett** (`warren_buffett`)
   - Value investing and moat analysis
   - Icon: 🎩

2. **Peter Lynch** (`peter_lynch`)
   - Growth investing and PEG ratios
   - Icon: 📈

3. **Charlie Munger** (`charlie_munger`)
   - Mental models and quality businesses
   - Icon: 🧠

4. **Ben Graham** (`ben_graham`)
   - Margin of safety and intrinsic value
   - Icon: 📚

5. **Technical Analyst** (`technical_analyst`)
   - Chart patterns and technical indicators
   - Icon: 📊

## Testing

### Backend Testing
```bash
# Run the test script
python test_agent_chat_integration.py
```

### Frontend Testing
1. Start the backend server: `cd app/backend && python main.py`
2. Start the frontend: `cd app/frontend && npm run dev`
3. Navigate to agent pages:
   - http://localhost:3000/chat/agent/warren-buffett
   - http://localhost:3000/chat/agent/peter-lynch
   - etc.

## Configuration

### Frontend Configuration
- API proxy in `next.config.ts`
- Rewrites `/api/agents/*` to backend

### Backend Configuration
- CORS enabled for frontend access
- API key authentication required

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure backend is running on port 8000
   - Check CORS configuration

2. **Authentication Failed**
   - Verify API key is correct
   - Check Authorization header format

3. **Agent Not Found**
   - Use correct agent ID (e.g., `warren_buffett` not `warren-buffett`)
   - Check available agents in backend

## Customization

### Adjusting Chat History Context

The default configuration uses the last 5 messages for context. This can be customized:

1. **In BaseChatAgent subclasses**:
```python
class MyCustomAgent(BaseChatAgent):
    def __init__(self):
        super().__init__(
            agent_name="custom_agent",
            max_history_messages=10  # Use last 10 messages
        )
```

2. **Trade-offs to consider**:
   - More history = Better context but higher costs
   - Less history = Faster responses but may lose context
   - Optimal range: 3-10 messages for most use cases

## Future Enhancements

1. **Streaming Responses**
   - Real-time token streaming
   - Progressive response display

2. **Chat History**
   - Persistent conversation storage
   - Resume previous chats

3. **Multi-Agent Conversations**
   - Compare multiple agent perspectives
   - Agent collaboration features

4. **Enhanced Visuals**
   - Agent avatars
   - Rich message formatting
   - Chart/graph support

5. **Dynamic Context Windows**
   - Automatically adjust history based on conversation type
   - Smart context selection (relevant messages only)
   - Token-aware context management 
"""
Base Chat Agent Template for Individual AI Hedge Fund Agents
"""
from typing import Dict, Any, List, AsyncGenerator, Optional
from abc import ABC, abstractmethod
import asyncio
import json
from datetime import datetime

from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import tool
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain.callbacks.base import BaseCallbackHandler
from langchain.callbacks.manager import CallbackManager
from langchain_core.outputs import LLMResult
from langchain.schema import AgentAction, AgentFinish

# Import existing LLM infrastructure
from src.llm.models import get_model


class StreamingCallbackHandler(BaseCallbackHandler):
    """Custom callback handler to stream agent decisions and actions."""
    
    def __init__(self, queue: asyncio.Queue, loop: Optional[asyncio.AbstractEventLoop] = None):
        self.queue = queue
        self.current_step = 0
        self.loop = loop
        
    def _send_event_sync(self, event_type: str, data: Dict[str, Any]):
        """Send an event to the streaming queue (thread-safe)."""
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "step": self.current_step
        }
        
        # If we have a loop, schedule the coroutine
        if self.loop and not self.loop.is_closed():
            try:
                asyncio.run_coroutine_threadsafe(
                    self.queue.put(json.dumps(event)), 
                    self.loop
                )
            except Exception as e:
                # Fallback: just print for debugging
                print(f"📊 {event_type}: {data.get('message', data)}")
        else:
            # Fallback: just print for debugging  
            print(f"📊 {event_type}: {data.get('message', data)}")
    
    def on_agent_action(self, action: AgentAction, **kwargs) -> Any:
        """Called when agent decides to take an action."""
        self._send_event_sync("agent_action", {
            "tool": action.tool,
            "tool_input": action.tool_input,
            "log": action.log,
            "message": f"🔧 Using tool: {action.tool}",
            "details": f"Analyzing {action.tool_input} with {action.tool}"
        })
        
    def on_agent_finish(self, finish: AgentFinish, **kwargs) -> Any:
        """Called when agent finishes."""
        self._send_event_sync("agent_finish", {
            "output": finish.return_values.get("output", ""),
            "message": "✅ Analysis complete",
            "log": finish.log
        })
    
    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs) -> Any:
        """Called when a tool starts."""
        tool_name = serialized.get("name", "Unknown tool")
        self._send_event_sync("tool_start", {
            "tool_name": tool_name,
            "input": input_str,
            "message": f"⚡ Running {tool_name} for {input_str}...",
            "details": f"Performing analysis on {input_str}"
        })
    
    def on_tool_end(self, output: str, **kwargs) -> Any:
        """Called when a tool ends."""
        self._send_event_sync("tool_end", {
            "output": output[:200] + "..." if len(output) > 200 else output,
            "message": "📊 Data received",
            "details": "Processing results..."
        })
    
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs) -> Any:
        """Called when LLM starts thinking."""
        self.current_step += 1
        self._send_event_sync("llm_thinking", {
            "message": f"🤔 Analyzing with {self.__class__.__name__.replace('ChatAgent', '')} principles...",
            "details": "Processing data with investment criteria",
            "step": self.current_step
        })
    
    def on_llm_end(self, response: LLMResult, **kwargs) -> Any:
        """Called when LLM finishes thinking."""
        if response.generations and response.generations[0]:
            content = response.generations[0][0].text
            # Extract the thought process
            if "Thought:" in content:
                thought = content.split("Thought:")[1].split("\n")[0].strip()
                self._send_event_sync("llm_thought", {
                    "thought": thought,
                    "message": f"💭 Thought: {thought}",
                    "details": "Deciding next action..."
                })


class BaseChatAgent(ABC):
    """Base class for all individual agent chat interfaces."""
    
    def __init__(self, agent_name: str, model_name: str = "gpt-4o-mini", model_provider: str = "openai", max_history_messages: int = 5):
        self.agent_name = agent_name
        self.model_name = model_name
        self.model_provider = model_provider
        self.max_history_messages = max_history_messages
        
        # Initialize LLM using existing infrastructure
        self.llm = get_model(model_name, model_provider)
        if self.llm is None:
            raise ValueError(f"Failed to initialize model: {model_name} with provider: {model_provider}")
        
        # These will be set by subclasses
        self.tools = []
        self.prompt_template = ""
        
        # Initialize tools and prompt
        self.setup_tools()
        self.setup_prompt()
        
        # Create the agent
        self.agent = self._create_agent()
        
    @abstractmethod
    def setup_tools(self):
        """Override in subclasses to define agent-specific tools."""
        pass
        
    @abstractmethod
    def setup_prompt(self):
        """Override in subclasses to define agent personality."""
        pass
    
    def _create_agent(self) -> AgentExecutor:
        """Create the React agent with tools and prompt."""
        # Create React prompt with our custom template
        react_prompt = PromptTemplate(
            template=self.prompt_template + """

Question: {input}
Thought: I should analyze this step by step using my available tools.
{agent_scratchpad}""",
            input_variables=["input", "agent_scratchpad"]
        )
        
        # Create the agent
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=react_prompt
        )
        
        # Create executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            return_intermediate_steps=True,
            handle_parsing_errors=True,
            output_parser=ReActSingleInputOutputParser()
        )
        
        return agent_executor
        
    async def analyze(self, query: str, chat_history: List = None) -> Dict[str, Any]:
        """Standard analysis interface."""
        # Create context from chat history if provided
        context = ""
        if chat_history:
            # Use the last N messages, where N is configurable
            relevant_history = chat_history[-self.max_history_messages:] if len(chat_history) > self.max_history_messages else chat_history
            context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in relevant_history])
            query = f"Context from previous conversation:\n{context}\n\nCurrent question: {query}"
        
        # Run the agent
        result = await asyncio.get_event_loop().run_in_executor(
            None,
            self.agent.invoke,
            {"input": query}
        )
        
        # Format the response
        return {
            "agent": self.agent_name,
            "query": query,
            "response": result["output"],
            "intermediate_steps": result.get("intermediate_steps", []),
            "timestamp": datetime.now().isoformat()
        }
        
    async def analyze_streaming(self, query: str, chat_history: List = None) -> AsyncGenerator[str, None]:
        """Streaming analysis interface."""
        # Create a queue for streaming
        event_queue = asyncio.Queue()
        
        # Get current event loop
        loop = asyncio.get_event_loop()
        
        # Create callback handler
        callback_handler = StreamingCallbackHandler(event_queue, loop)
        callback_manager = CallbackManager([callback_handler])
        
        # Update agent with callback manager
        self.agent.callbacks = callback_manager
        
        # Create context from chat history if provided
        context = ""
        if chat_history:
            # Use the last N messages, where N is configurable
            relevant_history = chat_history[-self.max_history_messages:] if len(chat_history) > self.max_history_messages else chat_history
            context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in relevant_history])
            query = f"Context from previous conversation:\n{context}\n\nCurrent question: {query}"
        
        # Run agent in thread
        def run_agent():
            return self.agent.invoke({"input": query})
        
        # Start agent execution in thread
        future = loop.run_in_executor(None, run_agent)
        
        # Stream events while agent runs
        async def stream_events():
            while True:
                try:
                    # Wait for event with timeout
                    event = await asyncio.wait_for(event_queue.get(), timeout=0.5)
                    yield event
                except asyncio.TimeoutError:
                    # Check if agent is done
                    if future.done():
                        break
                    continue
                except Exception as e:
                    print(f"Error in stream_events: {e}")
                    break
            
            # Get final result
            try:
                result = await future
                final_event = {
                    "type": "final_result",
                    "data": {
                        "output": result["output"],
                        "message": "✅ Complete analysis",
                        "intermediate_steps": result.get("intermediate_steps", [])
                    },
                    "timestamp": datetime.now().isoformat()
                }
                yield json.dumps(final_event)
            except Exception as e:
                error_event = {
                    "type": "error",
                    "data": {
                        "error": str(e),
                        "message": "❌ Error during analysis"
                    },
                    "timestamp": datetime.now().isoformat()
                }
                yield json.dumps(error_event)
        
        # Stream the events
        async for event in stream_events():
            yield event


def clean_ticker(ticker: str) -> str:
    """Clean and normalize ticker symbol."""
    return ticker.strip().strip("'\"").upper() 
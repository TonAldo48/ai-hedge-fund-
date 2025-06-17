"""
Peter Lynch Chat Agent for Natural Language Financial Analysis
"""
import os
from typing import Dict, Any, List, AsyncGenerator, Optional
from datetime import datetime, timedelta
import json
import asyncio

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

# Import Peter Lynch analysis functions
from src.agents.peter_lynch import (
    analyze_lynch_growth,
    analyze_lynch_fundamentals,
    analyze_lynch_valuation,
    analyze_sentiment,
    analyze_insider_activity
)

# Import data fetching functions
from src.tools.api import (
    get_financial_metrics,
    get_market_cap,
    search_line_items,
    get_prices,
    get_insider_trades,
    get_company_news
)

# Import existing LLM infrastructure
from src.llm.models import get_model

def clean_ticker(ticker: str) -> str:
    """Clean and normalize ticker symbol."""
    return ticker.strip().strip("'\"").upper()

@tool
def peter_lynch_growth_analysis(ticker: str) -> Dict[str, Any]:
    """
    Analyze a stock's growth potential using Peter Lynch's GARP (Growth at Reasonable Price) approach.
    Evaluates revenue growth, EPS growth trends, and identifies potential 'ten-baggers'.
    
    Args:
        ticker: Stock ticker symbol (e.g., TSLA, AAPL)
    
    Returns:
        Dict containing growth analysis with score, details, and growth metrics
    """
    try:
        ticker = clean_ticker(ticker)
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        financial_line_items = search_line_items(
            ticker,
            ["revenue", "earnings_per_share", "net_income", "outstanding_shares"],
            end_date,
            period="annual",
            limit=5
        )
        
        result = analyze_lynch_growth(financial_line_items)
        
        return {
            "ticker": ticker,
            "analysis_type": "peter_lynch_growth",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "ticker": clean_ticker(ticker) if ticker else "UNKNOWN",
            "analysis_type": "peter_lynch_growth",
            "error": str(e),
            "result": {"score": 0, "details": f"Error: {str(e)}"},
            "timestamp": datetime.now().isoformat()
        }

@tool
def peter_lynch_peg_analysis(ticker: str) -> Dict[str, Any]:
    """
    Calculate and analyze PEG ratio using Lynch's methodology.
    PEG < 1 is attractive, 1-2 is fair, >2 is expensive according to Lynch.
    
    Args:
        ticker: Stock ticker symbol (e.g., TSLA, AAPL)
    
    Returns:
        Dict containing PEG analysis with valuation assessment
    """
    try:
        ticker = clean_ticker(ticker)
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        financial_line_items = search_line_items(
            ticker,
            ["earnings_per_share", "net_income", "book_value_per_share", "outstanding_shares"],
            end_date,
            period="annual",
            limit=5
        )
        
        market_cap = get_market_cap(ticker, end_date)
        result = analyze_lynch_valuation(financial_line_items, market_cap)
        
        return {
            "ticker": ticker,
            "analysis_type": "peter_lynch_peg",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "ticker": clean_ticker(ticker) if ticker else "UNKNOWN",
            "analysis_type": "peter_lynch_peg",
            "error": str(e),
            "result": {"score": 0, "details": f"Error: {str(e)}"},
            "timestamp": datetime.now().isoformat()
        }

@tool
def peter_lynch_fundamentals_analysis(ticker: str) -> Dict[str, Any]:
    """
    Analyze fundamentals using Peter Lynch's criteria.
    Focuses on debt levels, operating margins, and free cash flow.
    Lynch prefers simple, understandable businesses with strong fundamentals.
    
    Args:
        ticker: Stock ticker symbol (e.g., TSLA, AAPL)
    
    Returns:
        Dict containing fundamentals analysis with financial health assessment
    """
    try:
        ticker = clean_ticker(ticker)
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        financial_line_items = search_line_items(
            ticker,
            [
                "total_debt", "shareholders_equity", "operating_margin",
                "gross_margin", "free_cash_flow", "operating_income"
            ],
            end_date,
            period="annual",
            limit=5
        )
        
        result = analyze_lynch_fundamentals(financial_line_items)
        
        return {
            "ticker": ticker,
            "analysis_type": "peter_lynch_fundamentals",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "ticker": clean_ticker(ticker) if ticker else "UNKNOWN",
            "analysis_type": "peter_lynch_fundamentals",
            "error": str(e),
            "result": {"score": 0, "details": f"Error: {str(e)}"},
            "timestamp": datetime.now().isoformat()
        }

@tool
def peter_lynch_sentiment_analysis(ticker: str) -> Dict[str, Any]:
    """
    Analyze market sentiment and news flow for a stock.
    Lynch considers market sentiment as a secondary factor in his analysis.
    
    Args:
        ticker: Stock ticker symbol (e.g., TSLA, AAPL)
    
    Returns:
        Dict containing sentiment analysis from recent news
    """
    try:
        ticker = clean_ticker(ticker)
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        company_news = get_company_news(ticker, end_date, limit=50)
        result = analyze_sentiment(company_news)
        
        return {
            "ticker": ticker,
            "analysis_type": "peter_lynch_sentiment",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "ticker": clean_ticker(ticker) if ticker else "UNKNOWN",
            "analysis_type": "peter_lynch_sentiment",
            "error": str(e),
            "result": {"score": 5, "details": f"Error: {str(e)}"},
            "timestamp": datetime.now().isoformat()
        }

@tool
def peter_lynch_insider_activity_analysis(ticker: str) -> Dict[str, Any]:
    """
    Analyze insider trading activity using Lynch's approach.
    Lynch pays attention to insider buying as a positive signal.
    
    Args:
        ticker: Stock ticker symbol (e.g., TSLA, AAPL)
    
    Returns:
        Dict containing insider activity analysis and signals
    """
    try:
        ticker = clean_ticker(ticker)
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        insider_trades = get_insider_trades(ticker, end_date, limit=50)
        result = analyze_insider_activity(insider_trades)
        
        return {
            "ticker": ticker,
            "analysis_type": "peter_lynch_insider",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "ticker": clean_ticker(ticker) if ticker else "UNKNOWN",
            "analysis_type": "peter_lynch_insider",
            "error": str(e),
            "result": {"score": 5, "details": f"Error: {str(e)}"},
            "timestamp": datetime.now().isoformat()
        }

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
        
        # Create specific messages based on the tool type
        if "growth" in tool_name:
            message = f"📈 Analyzing {input_str} growth potential..."
            details = "Evaluating revenue and EPS growth trends for ten-bagger potential"
        elif "peg" in tool_name:
            message = f"💹 Calculating {input_str} PEG ratio..."
            details = "Assessing growth at reasonable price (GARP) metrics"
        elif "fundamentals" in tool_name:
            message = f"📊 Examining {input_str} business fundamentals..."
            details = "Checking debt levels, margins, and cash flow"
        elif "sentiment" in tool_name:
            message = f"📰 Analyzing {input_str} market sentiment..."
            details = "Reviewing recent news and market perception"
        elif "insider" in tool_name:
            message = f"👥 Checking {input_str} insider activity..."
            details = "Looking for insider buying or selling patterns"
        else:
            message = f"⚡ Running {tool_name} for {input_str}..."
            details = f"Performing analysis on {input_str}"
            
        self._send_event_sync("tool_start", {
            "tool_name": tool_name,
            "input": input_str,
            "message": message,
            "details": details
        })
    
    def on_tool_end(self, output: str, **kwargs) -> Any:
        """Called when a tool ends."""
        
        # Extract key information from the output to make messages more specific
        message = "📊 Data received"
        details = "Processing results..."
        
        try:
            if "growth" in output and "revenue" in output:
                message = "📈 Growth analysis complete"
                details = "Revenue and earnings growth trends evaluated"
            elif "PEG" in output or "P/E" in output:
                message = "💹 Valuation metrics calculated"
                details = "PEG ratio and valuation assessment complete"
            elif "debt" in output and "margin" in output:
                message = "📊 Fundamentals data collected"
                details = "Financial health metrics analyzed"
            elif "sentiment" in output and "news" in output:
                message = "📰 Sentiment analysis done"
                details = "Market perception assessment complete"
            elif "insider" in output and "trades" in output:
                message = "👥 Insider activity reviewed"
                details = "Insider trading patterns analyzed"
        except:
            pass  # Use default message if parsing fails
            
        self._send_event_sync("tool_end", {
            "output": output[:200] + "..." if len(output) > 200 else output,
            "message": message,
            "details": details
        })
    
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs) -> Any:
        """Called when LLM starts thinking."""
        self.current_step += 1
        
        # Vary the thinking messages to be more specific
        thinking_messages = [
            "🤔 Peter Lynch is evaluating the growth story...",
            "🤔 Considering the PEG ratio and valuation...",
            "🤔 Looking for ten-bagger potential...",
            "🤔 Applying GARP principles...",
            "🤔 Analyzing business simplicity...",
            "🤔 Determining investment opportunity..."
        ]
        
        # Use step to rotate through different messages
        message_index = (self.current_step - 1) % len(thinking_messages)
        
        self._send_event_sync("llm_thinking", {
            "message": thinking_messages[message_index],
            "details": "Processing data with Lynch's growth investing criteria",
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

class PeterLynchChatAgent:
    """Peter Lynch specialized chat agent for growth at reasonable price (GARP) analysis."""
    
    def __init__(self, model_name: str = "gpt-4o-mini", model_provider: str = "openai"):
        self.model_name = model_name
        self.model_provider = model_provider
        
        # Initialize LLM using existing infrastructure
        self.llm = get_model(model_name, model_provider)
        if self.llm is None:
            raise ValueError(f"Failed to initialize model: {model_name} with provider: {model_provider}")
        
        # Import the existing tools
        from app.backend.services.peter_lynch_chat_agent import (
            peter_lynch_growth_analysis,
            peter_lynch_peg_analysis,
            peter_lynch_fundamentals_analysis,
            peter_lynch_sentiment_analysis,
            peter_lynch_insider_activity_analysis
        )
        
        self.tools = [
            peter_lynch_growth_analysis,
            peter_lynch_peg_analysis,
            peter_lynch_fundamentals_analysis,
            peter_lynch_sentiment_analysis,
            peter_lynch_insider_activity_analysis
        ]
        
        # Create prompt
        template = """You are Peter Lynch, the legendary fund manager who ran Fidelity's Magellan Fund from 1977 to 1990, achieving an average annual return of 29.2%. You are known for your "invest in what you know" philosophy and ability to find "ten-baggers" (stocks that increase 10x in value).

Your investment philosophy includes:
- Invest in what you know and understand
- Look for growth at a reasonable price (GARP)
- Focus on PEG ratio (P/E to growth rate) - under 1.0 is attractive
- Prefer simple, understandable businesses
- Look for companies with room to grow
- Consider different categories: slow growers, stalwarts, fast growers, cyclicals, turnarounds, asset plays
- Pay attention to insider buying
- Be willing to invest in boring or unpopular companies if fundamentals are strong

When analyzing companies, you consider:
- Revenue and earnings growth consistency
- PEG ratio and valuation metrics
- Business simplicity and competitive position
- Debt levels and financial health
- Insider activity and market sentiment
- Potential for multi-bagger returns

You should respond in Peter Lynch's characteristic style - practical, down-to-earth, using everyday analogies, and focusing on common sense investing principles. Reference your experience managing the Magellan Fund when relevant.

TOOLS:
------
You have access to the following tools:

{tools}

To use a tool, please use the following format:

```
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
```

When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:

```
Thought: Do I need to use a tool? No
Final Answer: [your response here]
```

Begin!

Question: {input}
Thought: {agent_scratchpad}"""

        self.prompt = PromptTemplate.from_template(template)
        
        # Create non-streaming agent for regular use
        self.agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            return_intermediate_steps=True,
            max_iterations=8,
            handle_parsing_errors=True
        )
    
    async def analyze(self, query: str, chat_history: List = None) -> Dict[str, Any]:
        """
        Process a natural language financial analysis query with Peter Lynch's perspective.
        
        Args:
            query: Natural language query (e.g., "Is Apple a good growth stock?")
            chat_history: Previous conversation messages
            
        Returns:
            Dict containing analysis results and Lynch-style response
        """
        try:
            # Execute the agent
            result = await self.executor.ainvoke({
                "input": query,
                "chat_history": chat_history or []
            })
            
            return {
                "response": result["output"],
                "intermediate_steps": result.get("intermediate_steps", []),
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "agent": "peter_lynch"
            }
            
        except Exception as e:
            return {
                "response": f"I apologize, but I encountered an error while analyzing your question: {str(e)}",
                "error": str(e),
                "success": False,
                "timestamp": datetime.now().isoformat(),
                "agent": "peter_lynch"
            }
        
    async def analyze_streaming(self, query: str, chat_history: List = None) -> AsyncGenerator[str, None]:
        """
        Stream the analysis process in real-time.
        
        Args:
            query: Natural language query
            chat_history: Previous conversation messages
            
        Yields:
            JSON strings containing streaming events
        """
        # Create streaming queue
        stream_queue = asyncio.Queue()
        
        # Get current event loop
        current_loop = asyncio.get_running_loop()
        
        # Create callback handler
        callback_handler = StreamingCallbackHandler(stream_queue, current_loop)
        callback_manager = CallbackManager([callback_handler])
        
        # Create agent with streaming callbacks
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            return_intermediate_steps=True,
            max_iterations=8,
            handle_parsing_errors=True,
            callbacks=callback_manager
        )
        
        # Start the analysis in background
        analysis_task = asyncio.create_task(
            executor.ainvoke({
                "input": query,
                "chat_history": chat_history or []
            })
        )
        
        # Send initial event
        initial_event = {
            "type": "start",
            "data": {
                "message": "🎯 Starting Peter Lynch GARP analysis...",
                "query": query,
                "agent": "peter_lynch"
            },
            "timestamp": datetime.now().isoformat()
        }
        yield json.dumps(initial_event)
        
        # Stream events until analysis is complete
        while not analysis_task.done():
            try:
                # Wait for streaming events or timeout
                event_json = await asyncio.wait_for(stream_queue.get(), timeout=1.0)
                yield event_json
            except asyncio.TimeoutError:
                # Send contextual heartbeat to keep connection alive
                heartbeat_messages = [
                    "⏳ Searching for growth opportunities...",
                    "⏳ Calculating PEG ratios...",
                    "⏳ Evaluating business fundamentals...",
                    "⏳ Looking for ten-bagger potential...",
                    "⏳ Checking insider activity...",
                    "⏳ Analyzing growth consistency...",
                    "⏳ Comparing to industry peers..."
                ]
                
                import random
                heartbeat = {
                    "type": "heartbeat",
                    "data": {"message": random.choice(heartbeat_messages)},
                    "timestamp": datetime.now().isoformat()
                }
                yield json.dumps(heartbeat)
        
        # Get final result
        try:
            result = await analysis_task
            final_event = {
                "type": "complete",
                "data": {
                    "response": result["output"],
                    "success": True,
                    "agent": "peter_lynch"
                },
                "timestamp": datetime.now().isoformat()
            }
            yield json.dumps(final_event)
        except Exception as e:
            error_event = {
                "type": "error",
                "data": {
                    "error": str(e),
                    "success": False,
                    "agent": "peter_lynch"
                },
                "timestamp": datetime.now().isoformat()
            }
            yield json.dumps(error_event)

# Global agent instance with lazy initialization
_peter_lynch_agent = None

def get_peter_lynch_agent():
    """Get or create the Peter Lynch chat agent instance."""
    global _peter_lynch_agent
    if _peter_lynch_agent is None:
        _peter_lynch_agent = PeterLynchChatAgent()
    return _peter_lynch_agent

async def process_peter_lynch_query(query: str, chat_history: List = None) -> Dict[str, Any]:
    """
    Process a natural language query using Peter Lynch's GARP approach.
    
    Args:
        query: Natural language query about stocks or investing
        chat_history: Previous conversation messages
        
    Returns:
        Dict containing Peter Lynch's analysis and response
    """
    agent = get_peter_lynch_agent()
    return await agent.analyze(query, chat_history) 
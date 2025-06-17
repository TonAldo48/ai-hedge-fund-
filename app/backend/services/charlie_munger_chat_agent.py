"""
Charlie Munger Chat Agent for Natural Language Financial Analysis
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

# Import Charlie Munger analysis functions
from src.agents.charlie_munger import (
    analyze_moat_strength,
    analyze_management_quality,
    analyze_predictability,
    analyze_news_sentiment
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
def charlie_munger_moat_analysis(ticker: str) -> Dict[str, Any]:
    """
    Analyze a company's competitive moat using Charlie Munger's mental models.
    Evaluates sustainable competitive advantages, pricing power, and barriers to entry.
    
    Args:
        ticker: Stock ticker symbol (e.g., TSLA, AAPL)
    
    Returns:
        Dict containing moat analysis with strength assessment and competitive advantages
    """
    try:
        ticker = clean_ticker(ticker)
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        metrics = get_financial_metrics(ticker, end_date, period="annual", limit=5)
        financial_line_items = search_line_items(
            ticker,
            [
                "return_on_invested_capital", "gross_margin", "operating_margin",
                "capital_expenditure", "revenue", "research_and_development",
                "goodwill_and_intangible_assets"
            ],
            end_date,
            period="annual",
            limit=5
        )
        
        result = analyze_moat_strength(metrics, financial_line_items)
        
        return {
            "ticker": ticker,
            "analysis_type": "charlie_munger_moat",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "ticker": clean_ticker(ticker) if ticker else "UNKNOWN",
            "analysis_type": "charlie_munger_moat",
            "error": str(e),
            "result": {"score": 0, "details": f"Error: {str(e)}"},
            "timestamp": datetime.now().isoformat()
        }

@tool
def charlie_munger_management_quality_analysis(ticker: str) -> Dict[str, Any]:
    """
    Evaluate management quality using Munger's criteria for capital allocation wisdom.
    Focuses on shareholder-friendly actions, debt management, and insider ownership.
    
    Args:
        ticker: Stock ticker symbol (e.g., TSLA, AAPL)
    
    Returns:
        Dict containing management quality assessment with capital allocation analysis
    """
    try:
        ticker = clean_ticker(ticker)
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        financial_line_items = search_line_items(
            ticker,
            [
                "free_cash_flow", "net_income", "total_debt", "shareholders_equity",
                "cash_and_equivalents", "revenue", "outstanding_shares"
            ],
            end_date,
            period="annual",
            limit=5
        )
        
        insider_trades = get_insider_trades(ticker, end_date, limit=50)
        result = analyze_management_quality(financial_line_items, insider_trades)
        
        return {
            "ticker": ticker,
            "analysis_type": "charlie_munger_management",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "ticker": clean_ticker(ticker) if ticker else "UNKNOWN",
            "analysis_type": "charlie_munger_management",
            "error": str(e),
            "result": {"score": 0, "details": f"Error: {str(e)}"},
            "timestamp": datetime.now().isoformat()
        }

@tool
def charlie_munger_predictability_analysis(ticker: str) -> Dict[str, Any]:
    """
    Assess business predictability - Munger strongly prefers predictable businesses.
    Analyzes revenue stability, margin consistency, and cash flow reliability.
    
    Args:
        ticker: Stock ticker symbol (e.g., TSLA, AAPL)
    
    Returns:
        Dict containing predictability analysis with consistency metrics
    """
    try:
        ticker = clean_ticker(ticker)
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        financial_line_items = search_line_items(
            ticker,
            [
                "revenue", "operating_income", "operating_margin",
                "free_cash_flow", "earnings_per_share"
            ],
            end_date,
            period="annual",
            limit=10  # Need more years for predictability analysis
        )
        
        result = analyze_predictability(financial_line_items)
        
        return {
            "ticker": ticker,
            "analysis_type": "charlie_munger_predictability",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "ticker": clean_ticker(ticker) if ticker else "UNKNOWN",
            "analysis_type": "charlie_munger_predictability",
            "error": str(e),
            "result": {"score": 0, "details": f"Error: {str(e)}"},
            "timestamp": datetime.now().isoformat()
        }

@tool
def charlie_munger_mental_models_analysis(ticker: str) -> Dict[str, Any]:
    """
    Apply Munger's mental models framework to analyze a company.
    Combines insights from psychology, economics, and business analysis.
    
    Args:
        ticker: Stock ticker symbol (e.g., TSLA, AAPL)
    
    Returns:
        Dict containing mental models analysis and multidisciplinary insights
    """
    try:
        ticker = clean_ticker(ticker)
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        # Get comprehensive data for mental models analysis
        metrics = get_financial_metrics(ticker, end_date, period="annual", limit=5)
        news = get_company_news(ticker, end_date, limit=20)
        
        # Combine different analyses for mental models perspective
        news_sentiment = analyze_news_sentiment(news)
        
        # Create a mental models summary
        mental_models_insights = {
            "psychology": "Understanding customer behavior and brand loyalty",
            "economics": "Network effects, economies of scale, switching costs",
            "business_strategy": "Competitive positioning and moat durability",
            "news_sentiment": news_sentiment,
            "inversion_principle": "What could destroy this business?"
        }
        
        return {
            "ticker": ticker,
            "analysis_type": "charlie_munger_mental_models",
            "result": mental_models_insights,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "ticker": clean_ticker(ticker) if ticker else "UNKNOWN",
            "analysis_type": "charlie_munger_mental_models",
            "error": str(e),
            "result": {"details": f"Error: {str(e)}"},
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
        if "moat" in tool_name:
            message = f"🏰 Evaluating {input_str} competitive moat..."
            details = "Analyzing sustainable competitive advantages and barriers to entry"
        elif "management" in tool_name:
            message = f"👔 Assessing {input_str} management quality..."
            details = "Evaluating capital allocation wisdom and shareholder orientation"
        elif "predictability" in tool_name:
            message = f"📊 Analyzing {input_str} business predictability..."
            details = "Examining consistency of operations and cash flows"
        elif "mental_models" in tool_name:
            message = f"🧠 Applying mental models to {input_str}..."
            details = "Using multidisciplinary thinking and inversion principles"
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
            if "moat" in output or "ROIC" in output:
                message = "🏰 Moat analysis complete"
                details = "Competitive advantage assessment finished"
            elif "capital allocation" in output or "management" in output:
                message = "👔 Management evaluation done"
                details = "Capital allocation assessment complete"
            elif "predictab" in output or "consistency" in output:
                message = "📊 Predictability assessment complete"
                details = "Business consistency evaluation finished"
            elif "mental model" in output or "psychology" in output:
                message = "🧠 Mental models applied"
                details = "Multidisciplinary analysis complete"
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
            "🤔 Charlie Munger is applying mental models...",
            "🤔 Considering the business moat...",
            "🤔 Evaluating management integrity...",
            "🤔 Inverting the problem...",
            "🤔 Thinking about predictability...",
            "🤔 Applying multidisciplinary thinking..."
        ]
        
        # Use step to rotate through different messages
        message_index = (self.current_step - 1) % len(thinking_messages)
        
        self._send_event_sync("llm_thinking", {
            "message": thinking_messages[message_index],
            "details": "Processing data with Munger's wisdom and mental models",
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

class CharlieMungerChatAgent:
    """Charlie Munger specialized chat agent for mental models and quality business analysis."""
    
    def __init__(self, model_name: str = "gpt-4o-mini", model_provider: str = "openai"):
        self.model_name = model_name
        self.model_provider = model_provider
        
        # Initialize LLM using existing infrastructure
        self.llm = get_model(model_name, model_provider)
        if self.llm is None:
            raise ValueError(f"Failed to initialize model: {model_name} with provider: {model_provider}")
        
        # Import the existing tools
        from app.backend.services.charlie_munger_chat_agent import (
            charlie_munger_moat_analysis,
            charlie_munger_management_quality_analysis,
            charlie_munger_predictability_analysis,
            charlie_munger_mental_models_analysis
        )
        
        self.tools = [
            charlie_munger_moat_analysis,
            charlie_munger_management_quality_analysis,
            charlie_munger_predictability_analysis,
            charlie_munger_mental_models_analysis
        ]
        
        # Create prompt
        template = """You are Charlie Munger, Warren Buffett's long-time partner at Berkshire Hathaway and one of the greatest investors of all time. You are known for your multidisciplinary approach to investing, mental models framework, and wisdom about human psychology and decision-making.

Your investment philosophy includes:
- Mental models from multiple disciplines (psychology, economics, mathematics, physics, biology)
- Focus on high-quality businesses with durable competitive advantages
- Emphasis on competent and honest management
- Preference for simple, predictable businesses
- The importance of patience and rational thinking
- Inversion: "Invert, always invert" - think about what could go wrong
- Circle of competence - stay within what you understand
- Margin of safety in all decisions

Key mental models you often apply:
- Opportunity cost and alternative uses of capital
- Incentive-caused bias and human psychology
- Compound interest and time value
- Network effects and winner-take-all dynamics
- The Lollapalooza effect (multiple forces acting together)

When analyzing companies, you consider:
- Sustainable competitive advantages (moats)
- Management quality and capital allocation
- Business predictability and consistency
- Return on invested capital (ROIC)
- Risks and what could destroy the business
- Psychological factors affecting the business

You should respond in Charlie Munger's characteristic style - philosophical, referencing mental models, using examples from multiple disciplines, emphasizing rationality and wisdom. Be direct and sometimes contrarian. Reference Poor Charlie's Almanack and your speeches when relevant.

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
        Process a natural language financial analysis query with Charlie Munger's perspective.
        
        Args:
            query: Natural language query (e.g., "Does Coca-Cola have a strong moat?")
            chat_history: Previous conversation messages
            
        Returns:
            Dict containing analysis results and Munger-style response
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
                "agent": "charlie_munger"
            }
            
        except Exception as e:
            return {
                "response": f"I apologize, but I encountered an error while analyzing your question: {str(e)}",
                "error": str(e),
                "success": False,
                "timestamp": datetime.now().isoformat(),
                "agent": "charlie_munger"
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
                "message": "🎯 Starting Charlie Munger mental models analysis...",
                "query": query,
                "agent": "charlie_munger"
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
                    "⏳ Applying mental models framework...",
                    "⏳ Evaluating competitive advantages...",
                    "⏳ Analyzing management quality...",
                    "⏳ Checking business predictability...",
                    "⏳ Inverting the problem...",
                    "⏳ Considering psychological factors...",
                    "⏳ Assessing margin of safety..."
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
                    "agent": "charlie_munger"
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
                    "agent": "charlie_munger"
                },
                "timestamp": datetime.now().isoformat()
            }
            yield json.dumps(error_event)

# Global agent instance with lazy initialization
_charlie_munger_agent = None

def get_charlie_munger_agent():
    """Get or create the Charlie Munger chat agent instance."""
    global _charlie_munger_agent
    if _charlie_munger_agent is None:
        _charlie_munger_agent = CharlieMungerChatAgent()
    return _charlie_munger_agent

async def process_charlie_munger_query(query: str, chat_history: List = None) -> Dict[str, Any]:
    """
    Process a natural language query using Charlie Munger's mental models approach.
    
    Args:
        query: Natural language query about stocks or investing
        chat_history: Previous conversation messages
        
    Returns:
        Dict containing Charlie Munger's analysis and response
    """
    agent = get_charlie_munger_agent()
    return await agent.analyze(query, chat_history) 
import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
import pandas as pd
from dataclasses import dataclass, field
from langsmith import traceable

from src.backtester import Backtester
from src.main import run_hedge_fund
from app.backend.models.schemas import BacktestRequest, BacktestResult, PortfolioSnapshot, TradingDecision, PerformanceMetrics
from app.backend.models.events import (
    BacktestStartEvent, BacktestProgressEvent, TradingEvent, 
    PortfolioUpdateEvent, PerformanceUpdateEvent, BacktestCompleteEvent
)


@dataclass
class BacktestSession:
    """Represents an active backtest session"""
    id: str
    request: BacktestRequest
    result: BacktestResult
    backtester: Optional[Backtester] = None
    task: Optional[asyncio.Task] = None
    event_queue: asyncio.Queue = field(default_factory=asyncio.Queue)
    is_running: bool = False
    start_time: datetime = field(default_factory=datetime.now)


class BacktestManager:
    """Manages multiple concurrent backtest sessions"""
    
    def __init__(self):
        self.sessions: Dict[str, BacktestSession] = {}
    
    def create_session(self, request: BacktestRequest) -> str:
        """Create a new backtest session"""
        backtest_id = str(uuid.uuid4())
        
        result = BacktestResult(
            backtest_id=backtest_id,
            status="initialized",
            progress=0.0
        )
        
        session = BacktestSession(
            id=backtest_id,
            request=request,
            result=result
        )
        
        self.sessions[backtest_id] = session
        return backtest_id
    
    def get_session(self, backtest_id: str) -> Optional[BacktestSession]:
        """Get a backtest session by ID"""
        return self.sessions.get(backtest_id)
    
    def cleanup_session(self, backtest_id: str):
        """Clean up a completed backtest session"""
        if backtest_id in self.sessions:
            session = self.sessions[backtest_id]
            if session.task and not session.task.done():
                session.task.cancel()
            del self.sessions[backtest_id]


# Global instance
backtest_manager = BacktestManager()


class StreamingBacktester(Backtester):
    """Extended Backtester that emits streaming events"""
    
    def __init__(self, event_queue: asyncio.Queue, backtest_id: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_queue = event_queue
        self.backtest_id = backtest_id
        self.completed_days = 0
        self.total_days = 0
    
    async def emit_event(self, event):
        """Emit an event to the stream"""
        await self.event_queue.put(event)
    
    def emit_event_sync(self, event):
        """Emit an event to the stream synchronously"""
        self.event_queue.put_nowait(event)
    
    @traceable(
        name="AI Hedge Fund Backtest Streaming",
        metadata_key="backtest_streaming_metadata"
    )
    def run_backtest_streaming(self):
        """Run backtest with streaming events"""
        # Pre-fetch all data at the start
        self.prefetch_data()
        
        dates = pd.date_range(self.start_date, self.end_date, freq="B")
        self.total_days = len(dates)
        
        # Initialize portfolio values list with initial capital
        if len(dates) > 0:
            self.portfolio_values = [{"Date": dates[0], "Portfolio Value": self.initial_capital}]
        else:
            self.portfolio_values = []
        
        performance_metrics = {
            "sharpe_ratio": None, 
            "sortino_ratio": None, 
            "max_drawdown": None,
            "total_return": 0.0
        }
        
        # Emit start event
        self.emit_event_sync(
            BacktestStartEvent(
                backtest_id=self.backtest_id,
                total_days=self.total_days,
                tickers=self.tickers,
                timestamp=datetime.now().isoformat()
            )
        )
        
        for i, current_date in enumerate(dates):
            self.completed_days = i + 1
            progress = self.completed_days / self.total_days if self.total_days > 0 else 0
            
            # Emit progress event
            self.emit_event_sync(
                BacktestProgressEvent(
                    backtest_id=self.backtest_id,
                    current_date=current_date.strftime("%Y-%m-%d"),
                    progress=progress,
                    completed_days=self.completed_days,
                    total_days=self.total_days,
                    message=f"Processing {current_date.strftime('%Y-%m-%d')}",
                    timestamp=datetime.now().isoformat()
                )
            )
            
            # Run the same logic as original backtester but emit events
            current_date_str = current_date.strftime("%Y-%m-%d")
            lookback_start = (current_date - timedelta(days=30)).strftime("%Y-%m-%d")
            previous_date_str = (current_date - timedelta(days=1)).strftime("%Y-%m-%d")
            
            # Skip if there's no prior day to look back
            if lookback_start == current_date_str:
                continue
            
            try:
                # Get current prices for all tickers
                current_prices = {}
                missing_data = False
                
                for ticker in self.tickers:
                    from src.tools.api import get_price_data
                    try:
                        price_data = get_price_data(ticker, previous_date_str, current_date_str)
                        if price_data.empty:
                            missing_data = True
                            break
                        current_prices[ticker] = price_data.iloc[-1]["close"]
                    except Exception as e:
                        missing_data = True
                        break
                
                if missing_data:
                    continue
                
                # Execute the agent's trades
                output = self.agent(
                    tickers=self.tickers,
                    start_date=lookback_start,
                    end_date=current_date_str,
                    portfolio=self.portfolio,
                    model_name=self.model_name,
                    model_provider=self.model_provider,
                    selected_analysts=self.selected_analysts,
                )
                decisions = output["decisions"]
                
                # Execute trades and emit events for each
                for ticker in self.tickers:
                    decision = decisions.get(ticker, {"action": "hold", "quantity": 0})
                    action, quantity = decision.get("action", "hold"), decision.get("quantity", 0)
                    
                    executed_quantity = self.execute_trade(ticker, action, quantity, current_prices[ticker])
                    
                    if executed_quantity > 0 or action != "hold":
                        # Emit trading event
                        self.emit_event_sync(
                            TradingEvent(
                                backtest_id=self.backtest_id,
                                date=current_date_str,
                                ticker=ticker,
                                action=action,
                                quantity=executed_quantity,
                                price=current_prices[ticker],
                                portfolio_value=self.calculate_portfolio_value(current_prices),
                                timestamp=datetime.now().isoformat()
                            )
                        )
                
                # Calculate portfolio value and emit portfolio update
                total_value = self.calculate_portfolio_value(current_prices)
                daily_return = None
                if len(self.portfolio_values) > 0:
                    previous_value = self.portfolio_values[-1]["Portfolio Value"]
                    daily_return = (total_value - previous_value) / previous_value if previous_value > 0 else 0
                
                # Track portfolio value
                self.portfolio_values.append({
                    "Date": current_date, 
                    "Portfolio Value": total_value
                })
                
                # Emit portfolio update
                self.emit_event_sync(
                    PortfolioUpdateEvent(
                        backtest_id=self.backtest_id,
                        date=current_date_str,
                        cash=self.portfolio["cash"],
                        total_value=total_value,
                        daily_return=daily_return,
                        positions=self.portfolio["positions"],
                        timestamp=datetime.now().isoformat()
                    )
                )
                
                # Update performance metrics periodically
                if len(self.portfolio_values) > 3:
                    self._update_performance_metrics(performance_metrics)
                    
                    # Emit performance update every 5 days
                    if self.completed_days % 5 == 0:
                        total_return = (total_value / self.initial_capital - 1) * 100
                        self.emit_event_sync(
                            PerformanceUpdateEvent(
                                backtest_id=self.backtest_id,
                                sharpe_ratio=performance_metrics.get("sharpe_ratio"),
                                sortino_ratio=performance_metrics.get("sortino_ratio"),
                                max_drawdown=performance_metrics.get("max_drawdown"),
                                total_return=total_return,
                                timestamp=datetime.now().isoformat()
                            )
                        )
                
            except Exception as e:
                print(f"Error processing {current_date_str}: {e}")
                continue
        
        # Final performance calculation
        if self.portfolio_values:
            final_value = self.portfolio_values[-1]["Portfolio Value"]
            total_return = (final_value / self.initial_capital - 1) * 100
            
            final_performance = {
                "total_return": total_return,
                "final_value": final_value,
                "initial_capital": self.initial_capital,
                "sharpe_ratio": performance_metrics.get("sharpe_ratio"),
                "sortino_ratio": performance_metrics.get("sortino_ratio"),
                "max_drawdown": performance_metrics.get("max_drawdown")
            }
            
            # Emit completion event
            self.emit_event_sync(
                BacktestCompleteEvent(
                    backtest_id=self.backtest_id,
                    final_performance=final_performance,
                    timestamp=datetime.now().isoformat()
                )
            )
        
        return performance_metrics


@traceable(
    name="AI Hedge Fund Backtest",
    metadata_key="backtest_metadata"
)
async def run_backtest_async(session: BacktestSession):
    """Run backtest asynchronously with streaming events"""
    try:
        session.result.status = "running"
        session.is_running = True
        
        # Add metadata for tracing
        from langsmith import get_current_run_tree
        if get_current_run_tree():
            get_current_run_tree().extra = {
                "backtest_id": session.id,
                "tickers": session.request.tickers,
                "selected_agents": session.request.selected_agents,
                "model_name": session.request.model_name,
                "model_provider": session.request.model_provider.value,
                "date_range": f"{session.request.start_date} to {session.request.end_date}",
                "initial_capital": session.request.initial_capital,
                "margin_requirement": session.request.margin_requirement,
                "backtest_type": "streaming"
            }
        
        # Create streaming backtester
        backtester = StreamingBacktester(
            event_queue=session.event_queue,
            backtest_id=session.id,
            agent=run_hedge_fund,
            tickers=session.request.tickers,
            start_date=session.request.start_date,
            end_date=session.request.end_date,
            initial_capital=session.request.initial_capital,
            model_name=session.request.model_name,
            model_provider=session.request.model_provider.value,
            selected_analysts=session.request.selected_agents,
            initial_margin_requirement=session.request.margin_requirement
        )
        
        session.backtester = backtester
        
        # Run the backtest in a thread executor to avoid blocking the event loop
        import asyncio
        loop = asyncio.get_running_loop()
        performance_metrics = await loop.run_in_executor(
            None, backtester.run_backtest_streaming
        )
        
        # Update final result
        session.result.status = "completed"
        session.result.progress = 1.0
        session.is_running = False
        
        return performance_metrics
        
    except Exception as e:
        session.result.status = "failed"
        session.result.error_message = str(e)
        session.is_running = False
        raise 
from typing import Dict, Optional, Any, Literal, List
from pydantic import BaseModel


class BaseEvent(BaseModel):
    """Base class for all Server-Sent Event events"""

    type: str

    def to_sse(self) -> str:
        """Convert to Server-Sent Event format"""
        event_type = self.type.lower()
        return f"event: {event_type}\ndata: {self.model_dump_json()}\n\n"


class StartEvent(BaseEvent):
    """Event indicating the start of processing"""

    type: Literal["start"] = "start"
    timestamp: Optional[str] = None

class ProgressUpdateEvent(BaseEvent):
    """Event containing an agent's progress update"""

    type: Literal["progress"] = "progress"
    agent: str
    ticker: Optional[str] = None
    status: str
    timestamp: Optional[str] = None
    analysis: Optional[str] = None

class ErrorEvent(BaseEvent):
    """Event indicating an error occurred"""

    type: Literal["error"] = "error"
    message: str
    timestamp: Optional[str] = None


class CompleteEvent(BaseEvent):
    """Event indicating successful completion with results"""

    type: Literal["complete"] = "complete"
    data: Dict[str, Any]
    timestamp: Optional[str] = None


# Backtest-specific events
class BacktestStartEvent(BaseEvent):
    """Event indicating the start of backtesting"""

    type: Literal["backtest_start"] = "backtest_start"
    backtest_id: str
    total_days: int
    tickers: List[str]
    timestamp: Optional[str] = None


class BacktestProgressEvent(BaseEvent):
    """Event containing backtest progress updates"""

    type: Literal["backtest_progress"] = "backtest_progress"
    backtest_id: str
    current_date: str
    progress: float  # 0.0 to 1.0
    completed_days: int
    total_days: int
    message: Optional[str] = None
    timestamp: Optional[str] = None


class TradingEvent(BaseEvent):
    """Event for individual trading decisions"""

    type: Literal["trading"] = "trading"
    backtest_id: str
    date: str
    ticker: str
    action: str
    quantity: int
    price: float
    portfolio_value: float
    timestamp: Optional[str] = None


class PortfolioUpdateEvent(BaseEvent):
    """Event for portfolio value updates"""

    type: Literal["portfolio_update"] = "portfolio_update"
    backtest_id: str
    date: str
    cash: float
    total_value: float
    daily_return: Optional[float] = None
    positions: Dict[str, Dict[str, Any]]
    timestamp: Optional[str] = None


class PerformanceUpdateEvent(BaseEvent):
    """Event for performance metrics updates"""

    type: Literal["performance_update"] = "performance_update"
    backtest_id: str
    sharpe_ratio: Optional[float] = None
    sortino_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None
    total_return: float
    timestamp: Optional[str] = None


class BacktestCompleteEvent(BaseEvent):
    """Event indicating backtest completion"""

    type: Literal["backtest_complete"] = "backtest_complete"
    backtest_id: str
    final_performance: Dict[str, Any]
    timestamp: Optional[str] = None

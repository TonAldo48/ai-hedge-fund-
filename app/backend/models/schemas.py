from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from src.llm.models import ModelProvider


class HedgeFundResponse(BaseModel):
    decisions: dict
    analyst_signals: dict


class ErrorResponse(BaseModel):
    message: str
    error: str | None = None


class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    success: bool
    timestamp: str
    agent: Optional[str] = None


class HedgeFundRequest(BaseModel):
    tickers: List[str]
    selected_agents: List[str]
    end_date: Optional[str] = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    start_date: Optional[str] = None
    model_name: str = "gpt-4o"
    model_provider: ModelProvider = ModelProvider.OPENAI
    initial_cash: float = 100000.0
    margin_requirement: float = 0.0
    show_reasoning: bool = False

    def get_start_date(self) -> str:
        """Calculate start date if not provided"""
        if self.start_date:
            return self.start_date
        return (datetime.strptime(self.end_date, "%Y-%m-%d") - timedelta(days=90)).strftime("%Y-%m-%d")


# New Backtest Schemas
class BacktestRequest(BaseModel):
    tickers: List[str]
    selected_agents: List[str]
    start_date: str
    end_date: str
    model_name: str = "gpt-4o"
    model_provider: ModelProvider = ModelProvider.OPENAI
    initial_capital: float = 100000.0
    margin_requirement: float = 0.0
    show_reasoning: bool = False


class TradingDecision(BaseModel):
    ticker: str
    action: str  # buy, sell, short, cover, hold
    quantity: int
    price: float
    timestamp: str


class PortfolioSnapshot(BaseModel):
    date: str
    cash: float
    positions: Dict[str, Dict[str, Any]]  # ticker -> {long: int, short: int, etc.}
    total_value: float
    daily_return: Optional[float] = None


class PerformanceMetrics(BaseModel):
    total_return: float
    sharpe_ratio: Optional[float] = None
    sortino_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None
    win_rate: Optional[float] = None
    total_trades: Optional[int] = None


class BacktestResult(BaseModel):
    backtest_id: str
    status: str  # running, completed, failed
    progress: float  # 0.0 to 1.0
    current_date: Optional[str] = None
    portfolio_snapshots: List[PortfolioSnapshot] = []
    trading_decisions: List[TradingDecision] = []
    performance_metrics: Optional[PerformanceMetrics] = None
    error_message: Optional[str] = None

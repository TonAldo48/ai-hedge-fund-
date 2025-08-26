from __future__ import annotations

from datetime import datetime, timedelta
import json
from typing_extensions import Literal

from src.graph.state import AgentState, show_agent_reasoning
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from src.tools.api import (
    get_company_news,
    get_financial_metrics,
    get_insider_trades,
    get_market_cap,
    search_line_items,
)
from src.utils.llm import call_llm
from src.utils.progress import progress
from src.utils.weight_manager import get_current_weights, track_agent_weights, weight_tracker
from langsmith import traceable
from src.utils.tracing import create_agent_session_metadata

__all__ = [
    "MichaelBurrySignal",
    "michael_burry_agent",
]

###############################################################################
# Pydantic output model
###############################################################################


class MichaelBurrySignal(BaseModel):
    """Schema returned by the LLM."""

    signal: Literal["bullish", "bearish", "neutral"]
    confidence: float  # 0–100
    reasoning: str


###############################################################################
# Core agent
###############################################################################


@traceable(
    name="michael_burry_agent",
    tags=["hedge_fund", "deep_value", "michael_burry", "contrarian"],
    metadata={"agent_type": "investment_analyst", "style": "deep_value_contrarian"}
)
def michael_burry_agent(state: AgentState):  # noqa: C901  (complexity is fine here)
    """Analyse stocks using Michael Burry's deep‑value, contrarian framework."""

    data = state["data"]
    end_date: str = data["end_date"]  # YYYY‑MM‑DD
    tickers: list[str] = data["tickers"]
    
    # Get or create session ID
    session_id = state.get("session_id")
    if not session_id:
        # Generate a session ID if not provided
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        state["session_id"] = session_id
        
        # Create session in weight tracker
        weight_tracker.create_session(
            session_id=session_id,
            session_type="hedge_fund",
            tickers=tickers,
            start_date=data.get("start_date", end_date),
            end_date=end_date,
            selected_agents=["michael_burry"]
        )

    # Create session metadata for tracing
    model_name = state["metadata"]["model_name"]
    model_provider = state["metadata"]["model_provider"]
    session_metadata = create_agent_session_metadata(
        session_id=session_id,
        agent_name="michael_burry",
        tickers=tickers,
        model_name=model_name,
        model_provider=model_provider,
        metadata={
            "investment_style": "deep_value_contrarian",
            "key_metrics": ["FCF_yield", "EV_EBIT", "debt_equity", "insider_activity", "contrarian_sentiment"]
        }
    )

    # We look one year back for insider trades / news flow
    start_date = (datetime.fromisoformat(end_date) - timedelta(days=365)).date().isoformat()

    analysis_data: dict[str, dict] = {}
    burry_analysis: dict[str, dict] = {}
    
    # Get current weights for this agent
    current_weights = get_current_weights("michael_burry")

    for ticker in tickers:
        # ------------------------------------------------------------------
        # Fetch raw data
        # ------------------------------------------------------------------
        progress.update_status("michael_burry_agent", ticker, "Fetching financial metrics")
        metrics = get_financial_metrics(ticker, end_date, period="ttm", limit=5)

        progress.update_status("michael_burry_agent", ticker, "Fetching line items")
        line_items = search_line_items(
            ticker,
            [
                "free_cash_flow",
                "net_income",
                "total_debt",
                "cash_and_equivalents",
                "total_assets",
                "total_liabilities",
                "outstanding_shares",
                "issuance_or_purchase_of_equity_shares",
            ],
            end_date,
        )

        progress.update_status("michael_burry_agent", ticker, "Fetching insider trades")
        insider_trades = get_insider_trades(ticker, end_date=end_date, start_date=start_date)

        progress.update_status("michael_burry_agent", ticker, "Fetching company news")
        news = get_company_news(ticker, end_date=end_date, start_date=start_date, limit=250)

        progress.update_status("michael_burry_agent", ticker, "Fetching market cap")
        market_cap = get_market_cap(ticker, end_date)

        # ------------------------------------------------------------------
        # Run sub‑analyses
        # ------------------------------------------------------------------
        progress.update_status("michael_burry_agent", ticker, "Analyzing value")
        value_analysis = _analyze_value(metrics, line_items, market_cap)

        progress.update_status("michael_burry_agent", ticker, "Analyzing balance sheet")
        balance_sheet_analysis = _analyze_balance_sheet(metrics, line_items)

        progress.update_status("michael_burry_agent", ticker, "Analyzing insider activity")
        insider_analysis = _analyze_insider_activity(insider_trades)

        progress.update_status("michael_burry_agent", ticker, "Analyzing contrarian sentiment")
        contrarian_analysis = _analyze_contrarian_sentiment(news)

        # ------------------------------------------------------------------
        # Aggregate score & derive preliminary signal
        # ------------------------------------------------------------------
        # Normalize scores to 0-10 and apply weights from registry
        value_score = value_analysis["score"] / value_analysis["max_score"] * 10
        balance_sheet_score = balance_sheet_analysis["score"] / balance_sheet_analysis["max_score"] * 10
        insider_score = insider_analysis["score"] / insider_analysis["max_score"] * 10
        contrarian_score = contrarian_analysis["score"] / contrarian_analysis["max_score"] * 10
        
        total_score = (
            value_score * current_weights["value"] +
            balance_sheet_score * current_weights["balance_sheet"] +
            insider_score * current_weights["insider_activity"] +
            contrarian_score * current_weights["contrarian_sentiment"]
        )
        
        max_score = 10

        if total_score >= 7.0:
            signal = "bullish"
        elif total_score <= 4.0:
            signal = "bearish"
        else:
            signal = "neutral"

        # ------------------------------------------------------------------
        # Collect data for LLM reasoning & output
        # ------------------------------------------------------------------
        analysis_data[ticker] = {
            "signal": signal,
            "score": total_score,
            "max_score": max_score,
            "value_analysis": value_analysis,
            "balance_sheet_analysis": balance_sheet_analysis,
            "insider_analysis": insider_analysis,
            "contrarian_analysis": contrarian_analysis,
            "market_cap": market_cap,
            "weights_used": current_weights  # Store weights used
        }

        progress.update_status("michael_burry_agent", ticker, "Generating LLM output")
        burry_output = _generate_burry_output(
            ticker=ticker,
            analysis_data=analysis_data,
            model_name=state["metadata"]["model_name"],
            model_provider=state["metadata"]["model_provider"],
        )

        burry_analysis[ticker] = {
            "signal": burry_output.signal,
            "confidence": burry_output.confidence,
            "reasoning": burry_output.reasoning,
        }
        
        # Track the weights used for this analysis
        track_agent_weights(
            session_id=session_id,
            agent_name="michael_burry",
            ticker=ticker,
            weights_used=current_weights,
            total_score=total_score,
            signal=signal,
            confidence=burry_output.confidence
        )
        
        # Record function-level analyses
        weight_tracker.record_function_analysis(
            session_id=session_id,
            agent_name="michael_burry",
            ticker=ticker,
            function_name="analyze_value",
            score=value_analysis["score"],
            max_score=value_analysis["max_score"],
            details=value_analysis["details"],
            function_data=value_analysis
        )
        
        weight_tracker.record_function_analysis(
            session_id=session_id,
            agent_name="michael_burry",
            ticker=ticker,
            function_name="analyze_balance_sheet",
            score=balance_sheet_analysis["score"],
            max_score=balance_sheet_analysis["max_score"],
            details=balance_sheet_analysis["details"],
            function_data=balance_sheet_analysis
        )

        progress.update_status("michael_burry_agent", ticker, "Done", analysis=burry_output.reasoning)

    # ----------------------------------------------------------------------
    # Return to the graph
    # ----------------------------------------------------------------------
    message = HumanMessage(content=json.dumps(burry_analysis), name="michael_burry_agent")

    if state["metadata"].get("show_reasoning"):
        show_agent_reasoning(burry_analysis, "Michael Burry Agent")

    state["data"]["analyst_signals"]["michael_burry_agent"] = burry_analysis

    progress.update_status("michael_burry_agent", None, "Done")

    return {"messages": [message], "data": state["data"]}


###############################################################################
# Sub‑analysis helpers
###############################################################################


def _latest_line_item(line_items: list):
    """Return the most recent line‑item object or *None*."""
    return line_items[0] if line_items else None


# ----- Value ----------------------------------------------------------------

@traceable(
    name="analyze_value",
    tags=["michael_burry", "value_analysis", "deep_value"],
    metadata={"analysis_type": "value_metrics"}
)
def _analyze_value(metrics, line_items, market_cap):
    """Free cash‑flow yield, EV/EBIT, other classic deep‑value metrics."""

    max_score = 6  # 4 pts for FCF‑yield, 2 pts for EV/EBIT
    score = 0
    details: list[str] = []

    # Free‑cash‑flow yield
    latest_item = _latest_line_item(line_items)
    fcf = getattr(latest_item, "free_cash_flow", None) if latest_item else None
    if fcf is not None and market_cap:
        fcf_yield = fcf / market_cap
        if fcf_yield >= 0.15:
            score += 4
            details.append(f"Extraordinary FCF yield {fcf_yield:.1%}")
        elif fcf_yield >= 0.12:
            score += 3
            details.append(f"Very high FCF yield {fcf_yield:.1%}")
        elif fcf_yield >= 0.08:
            score += 2
            details.append(f"Respectable FCF yield {fcf_yield:.1%}")
        else:
            details.append(f"Low FCF yield {fcf_yield:.1%}")
    else:
        details.append("FCF data unavailable")

    # EV/EBIT (from financial metrics)
    if metrics:
        ev_ebit = getattr(metrics[0], "ev_to_ebit", None)
        if ev_ebit is not None:
            if ev_ebit < 6:
                score += 2
                details.append(f"EV/EBIT {ev_ebit:.1f} (<6)")
            elif ev_ebit < 10:
                score += 1
                details.append(f"EV/EBIT {ev_ebit:.1f} (<10)")
            else:
                details.append(f"High EV/EBIT {ev_ebit:.1f}")
        else:
            details.append("EV/EBIT data unavailable")
    else:
        details.append("Financial metrics unavailable")

    return {"score": score, "max_score": max_score, "details": "; ".join(details)}


# ----- Balance sheet --------------------------------------------------------

@traceable(
    name="analyze_balance_sheet",
    tags=["michael_burry", "balance_sheet", "financial_strength"],
    metadata={"analysis_type": "balance_sheet"}
)
def _analyze_balance_sheet(metrics, line_items):
    """Leverage and liquidity checks."""

    max_score = 3
    score = 0
    details: list[str] = []

    latest_metrics = metrics[0] if metrics else None
    latest_item = _latest_line_item(line_items)

    debt_to_equity = getattr(latest_metrics, "debt_to_equity", None) if latest_metrics else None
    if debt_to_equity is not None:
        if debt_to_equity < 0.5:
            score += 2
            details.append(f"Low D/E {debt_to_equity:.2f}")
        elif debt_to_equity < 1:
            score += 1
            details.append(f"Moderate D/E {debt_to_equity:.2f}")
        else:
            details.append(f"High leverage D/E {debt_to_equity:.2f}")
    else:
        details.append("Debt‑to‑equity data unavailable")

    # Quick liquidity sanity check (cash vs total debt)
    if latest_item is not None:
        cash = getattr(latest_item, "cash_and_equivalents", None)
        total_debt = getattr(latest_item, "total_debt", None)
        if cash is not None and total_debt is not None:
            if cash > total_debt:
                score += 1
                details.append("Net cash position")
            else:
                details.append("Net debt position")
        else:
            details.append("Cash/debt data unavailable")

    return {"score": score, "max_score": max_score, "details": "; ".join(details)}


# ----- Insider activity -----------------------------------------------------

@traceable(
    name="analyze_insider_activity",
    tags=["michael_burry", "insider_trading", "catalyst"],
    metadata={"analysis_type": "insider_activity"}
)
def _analyze_insider_activity(insider_trades):
    """Net insider buying over the last 12 months acts as a hard catalyst."""

    max_score = 2
    score = 0
    details: list[str] = []

    if not insider_trades:
        details.append("No insider trade data")
        return {"score": score, "max_score": max_score, "details": "; ".join(details)}

    shares_bought = sum(t.transaction_shares or 0 for t in insider_trades if (t.transaction_shares or 0) > 0)
    shares_sold = abs(sum(t.transaction_shares or 0 for t in insider_trades if (t.transaction_shares or 0) < 0))
    net = shares_bought - shares_sold
    if net > 0:
        score += 2 if net / max(shares_sold, 1) > 1 else 1
        details.append(f"Net insider buying of {net:,} shares")
    else:
        details.append("Net insider selling")

    return {"score": score, "max_score": max_score, "details": "; ".join(details)}


# ----- Contrarian sentiment -------------------------------------------------

@traceable(
    name="analyze_contrarian_sentiment",
    tags=["michael_burry", "contrarian", "sentiment_analysis"],
    metadata={"analysis_type": "contrarian_sentiment"}
)
def _analyze_contrarian_sentiment(news):
    """Very rough gauge: a wall of recent negative headlines can be a *positive* for a contrarian."""

    max_score = 1
    score = 0
    details: list[str] = []

    if not news:
        details.append("No recent news")
        return {"score": score, "max_score": max_score, "details": "; ".join(details)}

    # Count negative sentiment articles
    sentiment_negative_count = sum(
        1 for n in news if n.sentiment and n.sentiment.lower() in ["negative", "bearish"]
    )
    
    if sentiment_negative_count >= 5:
        score += 1  # The more hated, the better (assuming fundamentals hold up)
        details.append(f"{sentiment_negative_count} negative headlines (contrarian opportunity)")
    else:
        details.append("Limited negative press")

    return {"score": score, "max_score": max_score, "details": "; ".join(details)}


###############################################################################
# LLM generation
###############################################################################

@traceable(
    name="generate_burry_output",
    tags=["michael_burry", "llm_generation", "deep_value"],
    metadata={"analysis_type": "signal_generation"}
)
def _generate_burry_output(
    ticker: str,
    analysis_data: dict,
    *,
    model_name: str,
    model_provider: str,
) -> MichaelBurrySignal:
    """Call the LLM to craft the final trading signal in Burry's voice."""

    template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are an AI agent emulating Dr. Michael J. Burry. Your mandate:
                - Hunt for deep value in US equities using hard numbers (free cash flow, EV/EBIT, balance sheet)
                - Be contrarian: hatred in the press can be your friend if fundamentals are solid
                - Focus on downside first – avoid leveraged balance sheets
                - Look for hard catalysts such as insider buying, buybacks, or asset sales
                - Communicate in Burry's terse, data‑driven style

                IMPORTANT: Format your reasoning using Markdown with the following structure:

                ## Michael Burry's Deep Value Analysis

                ### Key Valuation Metrics
                - **FCF Yield**: X% (vs benchmark Y%)
                - **EV/EBIT**: X.X (vs industry average)
                - **Book Value**: Trading at X% of book value

                ### Balance Sheet Strength
                - **Debt-to-Equity**: X.X ratio
                - **Current Ratio**: X.X
                - **Cash Position**: Analysis of liquidity

                ### Contrarian Opportunities
                - **Market Sentiment**: Why the market is wrong
                - **Hard Catalysts**: Specific events that could unlock value
                - **Insider Activity**: Recent buying/selling patterns

                ### Risk Assessment
                - **Downside Protection**: What limits losses
                - **Financial Leverage**: Debt concerns or lack thereof

                ### Investment Decision
                - **Signal**: Strong Buy/Buy/Hold/Sell with reasoning
                - **Price Target**: Based on valuation metrics

                Use **bold** for key metrics, *italics* for emphasis, and be terse like Burry.

                When providing your reasoning, be thorough and specific by:
                1. Start with the key metric(s) that drove your decision
                2. Cite concrete numbers (e.g. "FCF yield **14.7%**", "EV/EBIT **5.3**")
                3. Highlight risk factors and why they are acceptable (or not)
                4. Mention relevant insider activity or contrarian opportunities
                5. Use Burry's direct, number-focused communication style with minimal words
                
                For example, if bullish: "**FCF yield 12.8%**. **EV/EBIT 6.2**. Debt-to-equity **0.4**. Net insider buying **25k shares**. Market missing value due to overreaction to recent litigation. **Strong buy**."
                For example, if bearish: "FCF yield only **2.1%**. Debt-to-equity concerning at **2.3**. Management diluting shareholders. **Pass**."
                """,
            ),
            (
                "human",
                """Based on the following data, create a Michael Burry-style trading signal:

                Analysis Data for {ticker}:
                {analysis_data}

                Return the trading signal in the following JSON format exactly:
                {{
                  "signal": "bullish" | "bearish" | "neutral",
                  "confidence": float between 0 and 100,
                  "reasoning": "string with markdown formatting"
                }}
                """,
            ),
        ]
    )

    prompt = template.invoke({"analysis_data": json.dumps(analysis_data, indent=2), "ticker": ticker})

    # Default fallback signal in case parsing fails
    def create_default_michael_burry_signal():
        return MichaelBurrySignal(signal="neutral", confidence=0.0, reasoning="Parsing error – defaulting to neutral")

    return call_llm(
        prompt=prompt,
        model_name=model_name,
        model_provider=model_provider,
        pydantic_model=MichaelBurrySignal,
        agent_name="michael_burry_agent",
        default_factory=create_default_michael_burry_signal,
    )

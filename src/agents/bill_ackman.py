from langchain_openai import ChatOpenAI
from src.graph.state import AgentState, show_agent_reasoning
from src.tools.api import get_financial_metrics, get_market_cap, search_line_items
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from pydantic import BaseModel
import json
from typing_extensions import Literal
from src.utils.progress import progress
from src.utils.llm import call_llm
from src.utils.weight_manager import get_current_weights, track_agent_weights, weight_tracker
from datetime import datetime
from langsmith import traceable
from src.utils.tracing import create_agent_session_metadata


class BillAckmanSignal(BaseModel):
    signal: Literal["bullish", "bearish", "neutral"]
    confidence: float
    reasoning: str


@traceable(
    name="bill_ackman_agent",
    tags=["hedge_fund", "activist_investing", "bill_ackman", "value_investing"],
    metadata={"agent_type": "investment_analyst", "style": "activist_value_investing"}
)
def bill_ackman_agent(state: AgentState):
    """
    Analyzes stocks using Bill Ackman's investing principles and LLM reasoning.
    Fetches multiple periods of data for a more robust long-term view.
    Incorporates brand/competitive advantage, activism potential, and other key factors.
    """
    data = state["data"]
    end_date = data["end_date"]
    tickers = data["tickers"]
    
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
            selected_agents=["bill_ackman"]
        )

    # Create session metadata for tracing
    model_name = state["metadata"]["model_name"]
    model_provider = state["metadata"]["model_provider"]
    session_metadata = create_agent_session_metadata(
        session_id=session_id,
        agent_name="bill_ackman",
        tickers=tickers,
        model_name=model_name,
        model_provider=model_provider,
        metadata={
            "investment_style": "activist_value_investing",
            "key_metrics": ["quality", "balance_sheet", "activism_potential", "valuation"]
        }
    )
    
    analysis_data = {}
    ackman_analysis = {}
    
    # Get current weights for this agent
    current_weights = get_current_weights("bill_ackman")
    
    for ticker in tickers:
        progress.update_status("bill_ackman_agent", ticker, "Fetching financial metrics")
        metrics = get_financial_metrics(ticker, end_date, period="annual", limit=5)
        
        progress.update_status("bill_ackman_agent", ticker, "Gathering financial line items")
        # Request multiple periods of data (annual or TTM) for a more robust long-term view.
        financial_line_items = search_line_items(
            ticker,
            [
                "revenue",
                "operating_margin",
                "debt_to_equity",
                "free_cash_flow",
                "total_assets",
                "total_liabilities",
                "dividends_and_other_cash_distributions",
                "outstanding_shares",
                # Optional: intangible_assets if available
                # "intangible_assets"
            ],
            end_date,
            period="annual",
            limit=5
        )
        
        progress.update_status("bill_ackman_agent", ticker, "Getting market cap")
        market_cap = get_market_cap(ticker, end_date)
        
        progress.update_status("bill_ackman_agent", ticker, "Analyzing business quality")
        quality_analysis = analyze_business_quality(metrics, financial_line_items)
        
        progress.update_status("bill_ackman_agent", ticker, "Analyzing balance sheet and capital structure")
        balance_sheet_analysis = analyze_financial_discipline(metrics, financial_line_items)
        
        progress.update_status("bill_ackman_agent", ticker, "Analyzing activism potential")
        activism_analysis = analyze_activism_potential(financial_line_items)
        
        progress.update_status("bill_ackman_agent", ticker, "Calculating intrinsic value & margin of safety")
        valuation_analysis = analyze_valuation(financial_line_items, market_cap)
        
        # Combine partial scores using weights from registry
        total_score = (
            quality_analysis["score"] * current_weights["quality"] +
            balance_sheet_analysis["score"] * current_weights["balance_sheet"] +
            activism_analysis["score"] * current_weights["activism_potential"] +
            valuation_analysis["score"] * current_weights["valuation"]
        )
        
        # Normalize scores to 0-10 scale
        max_component_scores = {"quality": 7, "balance_sheet": 5, "activism_potential": 2, "valuation": 3}
        normalized_total = sum(
            (score / max_component_scores[component]) * 10 * current_weights[component]
            for component, score in [
                ("quality", quality_analysis["score"]),
                ("balance_sheet", balance_sheet_analysis["score"]),
                ("activism_potential", activism_analysis["score"]),
                ("valuation", valuation_analysis["score"])
            ]
        )
        
        max_possible_score = 10
        
        # Generate a simple buy/hold/sell (bullish/neutral/bearish) signal
        if normalized_total >= 7.0:
            signal = "bullish"
        elif normalized_total <= 4.0:
            signal = "bearish"
        else:
            signal = "neutral"
        
        analysis_data[ticker] = {
            "signal": signal,
            "score": normalized_total,
            "max_score": max_possible_score,
            "quality_analysis": quality_analysis,
            "balance_sheet_analysis": balance_sheet_analysis,
            "activism_analysis": activism_analysis,
            "valuation_analysis": valuation_analysis,
            "weights_used": current_weights  # Store weights used
        }
        
        progress.update_status("bill_ackman_agent", ticker, "Generating Bill Ackman analysis")
        ackman_output = generate_ackman_output(
            ticker=ticker, 
            analysis_data=analysis_data,
            model_name=state["metadata"]["model_name"],
            model_provider=state["metadata"]["model_provider"],
        )
        
        ackman_analysis[ticker] = {
            "signal": ackman_output.signal,
            "confidence": ackman_output.confidence,
            "reasoning": ackman_output.reasoning
        }
        
        # Track the weights used for this analysis
        track_agent_weights(
            session_id=session_id,
            agent_name="bill_ackman",
            ticker=ticker,
            weights_used=current_weights,
            total_score=normalized_total,
            signal=signal,
            confidence=ackman_output.confidence
        )
        
        # Record function-level analyses
        weight_tracker.record_function_analysis(
            session_id=session_id,
            agent_name="bill_ackman",
            ticker=ticker,
            function_name="analyze_business_quality",
            score=quality_analysis["score"],
            max_score=max_component_scores["quality"],
            details=quality_analysis["details"],
            function_data=quality_analysis
        )
        
        weight_tracker.record_function_analysis(
            session_id=session_id,
            agent_name="bill_ackman",
            ticker=ticker,
            function_name="analyze_financial_discipline",
            score=balance_sheet_analysis["score"],
            max_score=max_component_scores["balance_sheet"],
            details=balance_sheet_analysis["details"],
            function_data=balance_sheet_analysis
        )
        
        progress.update_status("bill_ackman_agent", ticker, "Done", analysis=ackman_output.reasoning)
    
    # Wrap results in a single message for the chain
    message = HumanMessage(
        content=json.dumps(ackman_analysis),
        name="bill_ackman_agent"
    )
    
    # Show reasoning if requested
    if state["metadata"]["show_reasoning"]:
        show_agent_reasoning(ackman_analysis, "Bill Ackman Agent")
    
    # Add signals to the overall state
    state["data"]["analyst_signals"]["bill_ackman_agent"] = ackman_analysis

    progress.update_status("bill_ackman_agent", None, "Done")

    return {
        "messages": [message],
        "data": state["data"]
    }


@traceable(
    name="analyze_business_quality",
    tags=["bill_ackman", "quality_analysis", "competitive_moats"],
    metadata={"analysis_type": "business_quality"}
)
def analyze_business_quality(metrics: list, financial_line_items: list) -> dict:
    """
    Analyze whether the company has a high-quality business with stable or growing cash flows,
    durable competitive advantages (moats), and potential for long-term growth.
    Also tries to infer brand strength if intangible_assets data is present (optional).
    """
    score = 0
    details = []
    
    if not metrics or not financial_line_items:
        return {
            "score": 0,
            "details": "Insufficient data to analyze business quality"
        }
    
    # 1. Multi-period revenue growth analysis
    revenues = [item.revenue for item in financial_line_items if item.revenue is not None]
    if len(revenues) >= 2:
        initial, final = revenues[-1], revenues[0]
        if initial and final and final > initial:
            growth_rate = (final - initial) / abs(initial)
            if growth_rate > 0.5:  # e.g., 50% cumulative growth
                score += 2
                details.append(f"Revenue grew by {(growth_rate*100):.1f}% over the full period (strong growth).")
            else:
                score += 1
                details.append(f"Revenue growth is positive but under 50% cumulatively ({(growth_rate*100):.1f}%).")
        else:
            details.append("Revenue did not grow significantly or data insufficient.")
    else:
        details.append("Not enough revenue data for multi-period trend.")
    
    # 2. Operating margin and free cash flow consistency
    fcf_vals = [item.free_cash_flow for item in financial_line_items if item.free_cash_flow is not None]
    op_margin_vals = [item.operating_margin for item in financial_line_items if item.operating_margin is not None]
    
    if op_margin_vals:
        above_15 = sum(1 for m in op_margin_vals if m > 0.15)
        if above_15 >= (len(op_margin_vals) // 2 + 1):
            score += 2
            details.append("Operating margins have often exceeded 15% (indicates good profitability).")
        else:
            details.append("Operating margin not consistently above 15%.")
    else:
        details.append("No operating margin data across periods.")
    
    if fcf_vals:
        positive_fcf_count = sum(1 for f in fcf_vals if f > 0)
        if positive_fcf_count >= (len(fcf_vals) // 2 + 1):
            score += 1
            details.append("Majority of periods show positive free cash flow.")
        else:
            details.append("Free cash flow not consistently positive.")
    else:
        details.append("No free cash flow data across periods.")
    
    # 3. Return on Equity (ROE) check from the latest metrics
    latest_metrics = metrics[0]
    if latest_metrics.return_on_equity and latest_metrics.return_on_equity > 0.15:
        score += 2
        details.append(f"High ROE of {latest_metrics.return_on_equity:.1%}, indicating a competitive advantage.")
    elif latest_metrics.return_on_equity:
        details.append(f"ROE of {latest_metrics.return_on_equity:.1%} is moderate.")
    else:
        details.append("ROE data not available.")
    
    # 4. (Optional) Brand Intangible (if intangible_assets are fetched)
    # intangible_vals = [item.intangible_assets for item in financial_line_items if item.intangible_assets]
    # if intangible_vals and sum(intangible_vals) > 0:
    #     details.append("Significant intangible assets may indicate brand value or proprietary tech.")
    #     score += 1
    
    return {
        "score": score,
        "details": "; ".join(details)
    }


@traceable(
    name="analyze_financial_discipline",
    tags=["bill_ackman", "financial_discipline", "capital_allocation"],
    metadata={"analysis_type": "financial_discipline"}
)
def analyze_financial_discipline(metrics: list, financial_line_items: list) -> dict:
    """
    Evaluate the company's balance sheet over multiple periods:
    - Debt ratio trends
    - Capital returns to shareholders over time (dividends, buybacks)
    """
    score = 0
    details = []
    
    if not metrics or not financial_line_items:
        return {
            "score": 0,
            "details": "Insufficient data to analyze financial discipline"
        }
    
    # 1. Multi-period debt ratio or debt_to_equity
    debt_to_equity_vals = [item.debt_to_equity for item in financial_line_items if item.debt_to_equity is not None]
    if debt_to_equity_vals:
        below_one_count = sum(1 for d in debt_to_equity_vals if d < 1.0)
        if below_one_count >= (len(debt_to_equity_vals) // 2 + 1):
            score += 2
            details.append("Debt-to-equity < 1.0 for the majority of periods (reasonable leverage).")
        else:
            details.append("Debt-to-equity >= 1.0 in many periods (could be high leverage).")
    else:
        # Fallback to total_liabilities / total_assets
        liab_to_assets = []
        for item in financial_line_items:
            if item.total_liabilities and item.total_assets and item.total_assets > 0:
                liab_to_assets.append(item.total_liabilities / item.total_assets)
        
        if liab_to_assets:
            below_50pct_count = sum(1 for ratio in liab_to_assets if ratio < 0.5)
            if below_50pct_count >= (len(liab_to_assets) // 2 + 1):
                score += 2
                details.append("Liabilities-to-assets < 50% for majority of periods.")
            else:
                details.append("Liabilities-to-assets >= 50% in many periods.")
        else:
            details.append("No consistent leverage ratio data available.")
    
    # 2. Capital allocation approach (dividends + share counts)
    dividends_list = [
        item.dividends_and_other_cash_distributions
        for item in financial_line_items
        if item.dividends_and_other_cash_distributions is not None
    ]
    if dividends_list:
        paying_dividends_count = sum(1 for d in dividends_list if d < 0)
        if paying_dividends_count >= (len(dividends_list) // 2 + 1):
            score += 1
            details.append("Company has a history of returning capital to shareholders (dividends).")
        else:
            details.append("Dividends not consistently paid or no data on distributions.")
    else:
        details.append("No dividend data found across periods.")
    
    # Check for decreasing share count (simple approach)
    shares = [item.outstanding_shares for item in financial_line_items if item.outstanding_shares is not None]
    if len(shares) >= 2:
        # For buybacks, the newest count should be less than the oldest count
        if shares[0] < shares[-1]:
            score += 1
            details.append("Outstanding shares have decreased over time (possible buybacks).")
        else:
            details.append("Outstanding shares have not decreased over the available periods.")
    else:
        details.append("No multi-period share count data to assess buybacks.")
    
    return {
        "score": score,
        "details": "; ".join(details)
    }


@traceable(
    name="analyze_activism_potential",
    tags=["bill_ackman", "activism_analysis", "value_creation"],
    metadata={"analysis_type": "activism_potential"}
)
def analyze_activism_potential(financial_line_items: list) -> dict:
    """
    Bill Ackman often engages in activism if a company has a decent brand or moat
    but is underperforming operationally.
    
    We'll do a simplified approach:
    - Look for positive revenue trends but subpar margins
    - That may indicate 'activism upside' if operational improvements could unlock value.
    """
    if not financial_line_items:
        return {
            "score": 0,
            "details": "Insufficient data for activism potential"
        }
    
    # Check revenue growth vs. operating margin
    revenues = [item.revenue for item in financial_line_items if item.revenue is not None]
    op_margins = [item.operating_margin for item in financial_line_items if item.operating_margin is not None]
    
    if len(revenues) < 2 or not op_margins:
        return {
            "score": 0,
            "details": "Not enough data to assess activism potential (need multi-year revenue + margins)."
        }
    
    initial, final = revenues[-1], revenues[0]
    revenue_growth = (final - initial) / abs(initial) if initial else 0
    avg_margin = sum(op_margins) / len(op_margins)
    
    score = 0
    details = []
    
    # Suppose if there's decent revenue growth but margins are below 10%, Ackman might see activism potential.
    if revenue_growth > 0.15 and avg_margin < 0.10:
        score += 2
        details.append(
            f"Revenue growth is healthy (~{revenue_growth*100:.1f}%), but margins are low (avg {avg_margin*100:.1f}%). "
            "Activism could unlock margin improvements."
        )
    else:
        details.append("No clear sign of activism opportunity (either margins are already decent or growth is weak).")
    
    return {"score": score, "details": "; ".join(details)}


@traceable(
    name="analyze_valuation",
    tags=["bill_ackman", "valuation_analysis", "margin_of_safety"],
    metadata={"analysis_type": "valuation"}
)
def analyze_valuation(financial_line_items: list, market_cap: float) -> dict:
    """
    Ackman invests in companies trading at a discount to intrinsic value.
    Uses a simplified DCF with FCF as a proxy, plus margin of safety analysis.
    """
    if not financial_line_items or market_cap is None:
        return {
            "score": 0,
            "details": "Insufficient data to perform valuation"
        }
    
    # Since financial_line_items are in descending order (newest first),
    # the most recent period is the first element
    latest = financial_line_items[0]
    fcf = latest.free_cash_flow if latest.free_cash_flow else 0
    
    if fcf <= 0:
        return {
            "score": 0,
            "details": f"No positive FCF for valuation; FCF = {fcf}",
            "intrinsic_value": None
        }
    
    # Basic DCF assumptions
    growth_rate = 0.06
    discount_rate = 0.10
    terminal_multiple = 15
    projection_years = 5
    
    present_value = 0
    for year in range(1, projection_years + 1):
        future_fcf = fcf * (1 + growth_rate) ** year
        pv = future_fcf / ((1 + discount_rate) ** year)
        present_value += pv
    
    # Terminal Value
    terminal_value = (
        fcf * (1 + growth_rate) ** projection_years * terminal_multiple
    ) / ((1 + discount_rate) ** projection_years)
    
    intrinsic_value = present_value + terminal_value
    margin_of_safety = (intrinsic_value - market_cap) / market_cap
    
    score = 0
    # Simple scoring
    if margin_of_safety > 0.3:
        score += 3
    elif margin_of_safety > 0.1:
        score += 1
    
    details = [
        f"Calculated intrinsic value: ~{intrinsic_value:,.2f}",
        f"Market cap: ~{market_cap:,.2f}",
        f"Margin of safety: {margin_of_safety:.2%}"
    ]
    
    return {
        "score": score,
        "details": "; ".join(details),
        "intrinsic_value": intrinsic_value,
        "margin_of_safety": margin_of_safety
    }


@traceable(
    name="generate_ackman_output",
    tags=["bill_ackman", "llm_generation", "activist_investing"],
    metadata={"analysis_type": "signal_generation"}
)
def generate_ackman_output(
    ticker: str,
    analysis_data: dict[str, any],
    model_name: str,
    model_provider: str,
) -> BillAckmanSignal:
    """
    Generates investment decisions in the style of Bill Ackman.
    Includes more explicit references to brand strength, activism potential, 
    catalysts, and management changes in the system prompt.
    """
    template = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are a Bill Ackman AI agent, making investment decisions using his principles:

            1. Seek high-quality businesses with durable competitive advantages (moats), often in well-known consumer or service brands.
            2. Prioritize consistent free cash flow and growth potential over the long term.
            3. Advocate for strong financial discipline (reasonable leverage, efficient capital allocation).
            4. Valuation matters: target intrinsic value with a margin of safety.
            5. Consider activism where management or operational improvements can unlock substantial upside.
            6. Concentrate on a few high-conviction investments.

            In your reasoning:
            - Emphasize brand strength, moat, or unique market positioning.
            - Review free cash flow generation and margin trends as key signals.
            - Analyze leverage, share buybacks, and dividends as capital discipline metrics.
            - Provide a valuation assessment with numerical backup (DCF, multiples, etc.).
            - Identify any catalysts for activism or value creation (e.g., cost cuts, better capital allocation).
            - Use a confident, analytic, and sometimes confrontational tone when discussing weaknesses or opportunities.

            Return your final recommendation (signal: bullish, neutral, or bearish) with a 0-100 confidence and a thorough reasoning section.
            """
        ),
        (
            "human",
            """Based on the following analysis, create an Ackman-style investment signal.

            Analysis Data for {ticker}:
            {analysis_data}

            Return your output in strictly valid JSON:
            {{
              "signal": "bullish" | "bearish" | "neutral",
              "confidence": float (0-100),
              "reasoning": "string"
            }}
            """
        )
    ])

    prompt = template.invoke({
        "analysis_data": json.dumps(analysis_data, indent=2),
        "ticker": ticker
    })

    def create_default_bill_ackman_signal():
        return BillAckmanSignal(
            signal="neutral",
            confidence=0.0,
            reasoning="Error in analysis, defaulting to neutral"
        )

    return call_llm(
        prompt=prompt, 
        model_name=model_name, 
        model_provider=model_provider, 
        pydantic_model=BillAckmanSignal, 
        agent_name="bill_ackman_agent", 
        default_factory=create_default_bill_ackman_signal,
    )

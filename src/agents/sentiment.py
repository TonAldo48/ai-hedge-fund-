from langchain_core.messages import HumanMessage
from src.graph.state import AgentState, show_agent_reasoning
from src.utils.progress import progress
import pandas as pd
import numpy as np
import json
from src.utils.weight_manager import get_current_weights, track_agent_weights, weight_tracker
from datetime import datetime

from src.tools.api import get_insider_trades, get_company_news


##### Sentiment Agent #####
def sentiment_analyst_agent(state: AgentState):
    """Analyzes market sentiment and generates trading signals for multiple tickers."""
    data = state.get("data", {})
    end_date = data.get("end_date")
    tickers = data.get("tickers")
    
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
            selected_agents=["sentiment_analyst"]
        )

    # Initialize sentiment analysis for each ticker
    sentiment_analysis = {}
    
    # Get current weights for this agent
    current_weights = get_current_weights("sentiment_analyst")

    for ticker in tickers:
        progress.update_status("sentiment_analyst_agent", ticker, "Fetching insider trades")

        # Get the insider trades
        insider_trades = get_insider_trades(
            ticker=ticker,
            end_date=end_date,
            limit=1000,
        )

        progress.update_status("sentiment_analyst_agent", ticker, "Analyzing trading patterns")

        # Get the signals from the insider trades
        transaction_shares = pd.Series([t.transaction_shares for t in insider_trades]).dropna()
        insider_signals = np.where(transaction_shares < 0, "bearish", "bullish").tolist()

        progress.update_status("sentiment_analyst_agent", ticker, "Fetching company news")

        # Get the company news
        company_news = get_company_news(ticker, end_date, limit=100)

        # Get the sentiment from the company news
        sentiment = pd.Series([n.sentiment for n in company_news]).dropna()
        news_signals = np.where(sentiment == "negative", "bearish", 
                              np.where(sentiment == "positive", "bullish", "neutral")).tolist()
        
        progress.update_status("sentiment_analyst_agent", ticker, "Combining signals")
        # Combine signals from both sources with weights from registry
        insider_weight = current_weights["insider_weight"]
        news_weight = current_weights["news_weight"]
        
        # Calculate weighted signal counts
        bullish_signals = (
            insider_signals.count("bullish") * insider_weight +
            news_signals.count("bullish") * news_weight
        )
        bearish_signals = (
            insider_signals.count("bearish") * insider_weight +
            news_signals.count("bearish") * news_weight
        )

        if bullish_signals > bearish_signals:
            overall_signal = "bullish"
        elif bearish_signals > bullish_signals:
            overall_signal = "bearish"
        else:
            overall_signal = "neutral"

        # Calculate confidence level based on the weighted proportion
        total_weighted_signals = len(insider_signals) * insider_weight + len(news_signals) * news_weight
        confidence = 0  # Default confidence when there are no signals
        if total_weighted_signals > 0:
            confidence = round((max(bullish_signals, bearish_signals) / total_weighted_signals) * 100, 2)
        reasoning = f"Weighted Bullish signals: {bullish_signals:.1f}, Weighted Bearish signals: {bearish_signals:.1f}"
        
        # Calculate total score for tracking
        if overall_signal == "bullish":
            total_score = confidence / 10  # Convert 0-100 to 0-10
        elif overall_signal == "bearish":
            total_score = (100 - confidence) / 10  # Invert for bearish
        else:
            total_score = 5.0  # Neutral

        sentiment_analysis[ticker] = {
            "signal": overall_signal,
            "confidence": confidence,
            "reasoning": reasoning,
            "weights_used": current_weights  # Store weights used
        }
        
        # Track the weights used for this analysis
        track_agent_weights(
            session_id=session_id,
            agent_name="sentiment_analyst",
            ticker=ticker,
            weights_used=current_weights,
            total_score=total_score,
            signal=overall_signal,
            confidence=confidence
        )
        
        # Record function-level analyses
        weight_tracker.record_function_analysis(
            session_id=session_id,
            agent_name="sentiment_analyst",
            ticker=ticker,
            function_name="analyze_insider_trades",
            score=insider_signals.count("bullish") / max(len(insider_signals), 1) * 10,
            max_score=10,
            details=f"Bullish: {insider_signals.count('bullish')}, Bearish: {insider_signals.count('bearish')}",
            function_data={
                "bullish_count": insider_signals.count("bullish"),
                "bearish_count": insider_signals.count("bearish"),
                "total": len(insider_signals)
            }
        )
        
        weight_tracker.record_function_analysis(
            session_id=session_id,
            agent_name="sentiment_analyst",
            ticker=ticker,
            function_name="analyze_news_sentiment",
            score=news_signals.count("bullish") / max(len(news_signals), 1) * 10,
            max_score=10,
            details=f"Bullish: {news_signals.count('bullish')}, Bearish: {news_signals.count('bearish')}",
            function_data={
                "bullish_count": news_signals.count("bullish"),
                "bearish_count": news_signals.count("bearish"),
                "neutral_count": news_signals.count("neutral"),
                "total": len(news_signals)
            }
        )

        progress.update_status("sentiment_analyst_agent", ticker, "Done", analysis=json.dumps(reasoning, indent=4))

    # Create the sentiment message
    message = HumanMessage(
        content=json.dumps(sentiment_analysis),
        name="sentiment_analyst_agent",
    )

    # Print the reasoning if the flag is set
    if state["metadata"]["show_reasoning"]:
        show_agent_reasoning(sentiment_analysis, "Sentiment Analysis Agent")

    # Add the signal to the analyst_signals list
    state["data"]["analyst_signals"]["sentiment_agent"] = sentiment_analysis

    progress.update_status("sentiment_analyst_agent", None, "Done")

    return {
        "messages": [message],
        "data": data,
    }

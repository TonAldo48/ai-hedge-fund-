"""
Weight Management System for tracking and storing agent weights
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import sqlite3
from contextlib import contextmanager


@dataclass
class WeightSnapshot:
    """Represents a snapshot of weights used in an analysis"""
    session_id: str
    agent_name: str
    ticker: str
    weights: Dict[str, float]
    timestamp: datetime
    total_score: float
    signal: str
    confidence: float
    
    def to_dict(self):
        return {
            **asdict(self),
            'timestamp': self.timestamp.isoformat()
        }


class WeightRegistry:
    """Central registry of all agent weights"""
    
    # Define all current weights in one place
    AGENT_WEIGHTS = {
        "stanley_druckenmiller": {
            "growth_momentum": 0.35,
            "risk_reward": 0.20,
            "valuation": 0.20,
            "sentiment": 0.15,
            "insider_activity": 0.10
        },
        "peter_lynch": {
            "growth": 0.30,
            "valuation": 0.25,
            "fundamentals": 0.20,
            "sentiment": 0.15,
            "insider_activity": 0.10
        },
        "phil_fisher": {
            "growth_quality": 0.30,
            "margins_stability": 0.25,
            "management_efficiency": 0.20,
            "valuation": 0.15,
            "insider_activity": 0.05,
            "sentiment": 0.05
        },
        "charlie_munger": {
            "moat_strength": 0.35,
            "management_quality": 0.25,
            "predictability": 0.25,
            "valuation": 0.15
        },
        "warren_buffett": {
            "business_quality": 0.30,
            "management": 0.25,
            "financial_strength": 0.25,
            "valuation": 0.20
        },
        "bill_ackman": {
            "quality": 0.25,
            "balance_sheet": 0.25,
            "activism_potential": 0.25,
            "valuation": 0.25
        },
        "cathie_wood": {
            "disruptive_potential": 0.35,
            "revenue_growth": 0.25,
            "market_opportunity": 0.20,
            "innovation_score": 0.20
        },
        "ben_graham": {
            "margin_of_safety": 0.40,
            "financial_strength": 0.30,
            "earnings_stability": 0.30
        },
        "michael_burry": {
            "value": 0.40,
            "balance_sheet": 0.30,
            "insider_activity": 0.20,
            "contrarian_sentiment": 0.10
        },
        "technical_analyst": {
            "trend": 0.25,
            "mean_reversion": 0.20,
            "momentum": 0.25,
            "volatility": 0.15,
            "stat_arb": 0.15
        },
        "valuation_analyst": {
            "dcf": 0.35,
            "owner_earnings": 0.35,
            "ev_ebitda": 0.20,
            "residual_income": 0.10
        },
        "sentiment_analyst": {
            "insider_weight": 0.30,
            "news_weight": 0.70
        },
        "fundamentals_analyst": {
            "profitability": 0.25,
            "growth": 0.25,
            "financial_health": 0.25,
            "valuation": 0.25
        }
    }
    
    # Function-level weights (for sub-analyses)
    FUNCTION_WEIGHTS = {
        "analyze_growth_and_momentum": {
            "revenue_growth": 0.33,
            "eps_growth": 0.33,
            "price_momentum": 0.34
        },
        "weighted_signal_combination": {
            # Technical analyst strategy weights are defined at agent level
        }
    }
    
    @classmethod
    def get_agent_weights(cls, agent_name: str) -> Dict[str, float]:
        """Get current weights for an agent"""
        return cls.AGENT_WEIGHTS.get(agent_name, {}).copy()
    
    @classmethod
    def get_function_weights(cls, function_name: str) -> Dict[str, float]:
        """Get weights used within a specific function"""
        return cls.FUNCTION_WEIGHTS.get(function_name, {}).copy()
    
    @classmethod
    def get_all_weights_for_session(cls, selected_agents: List[str]) -> Dict[str, Any]:
        """Get all weights that will be used in a session"""
        session_weights = {}
        for agent in selected_agents:
            if agent in cls.AGENT_WEIGHTS:
                session_weights[agent] = cls.AGENT_WEIGHTS[agent].copy()
        return session_weights


class WeightTracker:
    """Tracks and stores weight usage during analysis sessions"""
    
    def __init__(self, storage_path: str = "weight_history"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.db_path = self.storage_path / "weights.db"
        self._init_db()
        
    def _init_db(self):
        """Initialize SQLite database for weight tracking"""
        with self._get_db() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS weight_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    agent_name TEXT NOT NULL,
                    ticker TEXT NOT NULL,
                    weights TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    total_score REAL,
                    signal TEXT,
                    confidence REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS analysis_sessions (
                    session_id TEXT PRIMARY KEY,
                    session_type TEXT,
                    tickers TEXT,
                    start_date TEXT,
                    end_date TEXT,
                    selected_agents TEXT,
                    session_weights TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS function_analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    agent_name TEXT NOT NULL,
                    ticker TEXT NOT NULL,
                    function_name TEXT NOT NULL,
                    score REAL,
                    max_score REAL,
                    details TEXT,
                    function_data TEXT,
                    sub_weights TEXT,
                    timestamp TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    @contextmanager
    def _get_db(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()
    
    def create_session(self, session_id: str, session_type: str, tickers: List[str], 
                      start_date: str, end_date: str, selected_agents: List[str]) -> Dict[str, Any]:
        """Create a new analysis session and capture all weights"""
        session_weights = WeightRegistry.get_all_weights_for_session(selected_agents)
        
        # Check if session already exists
        with self._get_db() as conn:
            existing = conn.execute(
                "SELECT session_id FROM analysis_sessions WHERE session_id = ?",
                (session_id,)
            ).fetchone()
            
            if existing:
                # Session already exists, just return the existing data
                return {
                    "session_id": session_id,
                    "session_type": session_type,
                    "tickers": tickers,
                    "start_date": start_date,
                    "end_date": end_date,
                    "selected_agents": selected_agents,
                    "session_weights": session_weights,
                    "already_exists": True
                }
            
            # Create new session
            conn.execute("""
                INSERT INTO analysis_sessions 
                (session_id, session_type, tickers, start_date, end_date, 
                 selected_agents, session_weights)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                session_type,
                json.dumps(tickers),
                start_date,
                end_date,
                json.dumps(selected_agents),
                json.dumps(session_weights)
            ))
        
        # Also save to JSON for easy access
        session_file = self.storage_path / f"session_{session_id}.json"
        session_data = {
            "session_id": session_id,
            "session_type": session_type,
            "tickers": tickers,
            "start_date": start_date,
            "end_date": end_date,
            "selected_agents": selected_agents,
            "session_weights": session_weights,
            "created_at": datetime.now().isoformat()
        }
        
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        return session_data
    
    def record_agent_analysis(self, session_id: str, agent_name: str, ticker: str,
                            weights_used: Dict[str, float], total_score: float,
                            signal: str, confidence: float) -> WeightSnapshot:
        """Record weights used in an agent analysis"""
        snapshot = WeightSnapshot(
            session_id=session_id,
            agent_name=agent_name,
            ticker=ticker,
            weights=weights_used,
            timestamp=datetime.now(),
            total_score=total_score,
            signal=signal,
            confidence=confidence
        )
        
        with self._get_db() as conn:
            conn.execute("""
                INSERT INTO weight_snapshots 
                (session_id, agent_name, ticker, weights, timestamp, 
                 total_score, signal, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                snapshot.session_id,
                snapshot.agent_name,
                snapshot.ticker,
                json.dumps(snapshot.weights),
                snapshot.timestamp.isoformat(),
                snapshot.total_score,
                snapshot.signal,
                snapshot.confidence
            ))
        
        return snapshot
    
    def record_function_analysis(self, session_id: str, agent_name: str, ticker: str,
                               function_name: str, score: float, max_score: Optional[float],
                               details: str, function_data: Dict[str, Any],
                               sub_weights: Optional[Dict[str, float]] = None):
        """Record function-level analysis details"""
        with self._get_db() as conn:
            conn.execute("""
                INSERT INTO function_analyses
                (session_id, agent_name, ticker, function_name, score, 
                 max_score, details, function_data, sub_weights, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                agent_name,
                ticker,
                function_name,
                score,
                max_score,
                details,
                json.dumps(function_data),
                json.dumps(sub_weights) if sub_weights else None,
                datetime.now().isoformat()
            ))
    
    def complete_session(self, session_id: str):
        """Mark a session as completed"""
        with self._get_db() as conn:
            conn.execute("""
                UPDATE analysis_sessions 
                SET completed_at = CURRENT_TIMESTAMP 
                WHERE session_id = ?
            """, (session_id,))
    
    def get_session_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent session history"""
        with self._get_db() as conn:
            rows = conn.execute("""
                SELECT * FROM analysis_sessions 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,)).fetchall()
            
            return [dict(row) for row in rows]
    
    def get_weight_evolution(self, agent_name: str, weight_name: str) -> List[Dict[str, Any]]:
        """Track how a specific weight has changed over time"""
        with self._get_db() as conn:
            rows = conn.execute("""
                SELECT 
                    session_id,
                    timestamp,
                    json_extract(weights, '$.' || ?) as weight_value,
                    total_score,
                    signal,
                    confidence
                FROM weight_snapshots 
                WHERE agent_name = ? 
                AND json_extract(weights, '$.' || ?) IS NOT NULL
                ORDER BY timestamp
            """, (weight_name, agent_name, weight_name)).fetchall()
            
            return [dict(row) for row in rows]
    
    def analyze_weight_performance(self, agent_name: Optional[str] = None) -> Dict[str, Any]:
        """Analyze which weight combinations perform best"""
        with self._get_db() as conn:
            query = """
                SELECT 
                    agent_name,
                    weights,
                    AVG(confidence) as avg_confidence,
                    COUNT(*) as analysis_count,
                    AVG(total_score) as avg_score,
                    SUM(CASE WHEN signal = 'bullish' THEN 1 ELSE 0 END) as bullish_count,
                    SUM(CASE WHEN signal = 'bearish' THEN 1 ELSE 0 END) as bearish_count,
                    SUM(CASE WHEN signal = 'neutral' THEN 1 ELSE 0 END) as neutral_count
                FROM weight_snapshots 
            """
            
            if agent_name:
                query += " WHERE agent_name = ?"
                rows = conn.execute(query + " GROUP BY agent_name, weights", (agent_name,)).fetchall()
            else:
                rows = conn.execute(query + " GROUP BY agent_name, weights").fetchall()
            
            results = []
            for row in rows:
                row_dict = dict(row)
                row_dict['weights'] = json.loads(row_dict['weights'])
                results.append(row_dict)
            
            return {
                "weight_performance": results,
                "analysis_timestamp": datetime.now().isoformat()
            }


# Global instance for easy access
weight_tracker = WeightTracker()


def get_current_weights(agent_name: str) -> Dict[str, float]:
    """Convenience function to get current weights for an agent"""
    return WeightRegistry.get_agent_weights(agent_name)


def track_agent_weights(session_id: str, agent_name: str, ticker: str,
                       weights_used: Dict[str, float], total_score: float,
                       signal: str, confidence: float) -> WeightSnapshot:
    """Convenience function to track weights used in an analysis"""
    return weight_tracker.record_agent_analysis(
        session_id, agent_name, ticker, weights_used, 
        total_score, signal, confidence
    ) 
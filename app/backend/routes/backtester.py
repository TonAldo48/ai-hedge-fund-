from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
import asyncio
from datetime import datetime
from typing import Optional
from langsmith import traceable

from app.backend.models.schemas import BacktestRequest, BacktestResult, ErrorResponse
from app.backend.services.backtester import backtest_manager, run_backtest_async
from app.backend.middleware.auth import verify_api_key
from src.utils.weight_manager import weight_tracker

router = APIRouter(prefix="/backtest")


@router.post("/start")
async def start_backtest(
    request: BacktestRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Start a new backtest session.
    
    **Authentication Required**: This endpoint requires a valid API key.
    
    Returns a backtest_id that can be used to:
    1. Stream real-time updates via `/backtest/stream/{backtest_id}`
    2. Get current status via `/backtest/status/{backtest_id}`
    """
    try:
        # Validate request
        if not request.tickers:
            raise HTTPException(status_code=400, detail="At least one ticker is required")
        
        if not request.selected_agents:
            raise HTTPException(status_code=400, detail="At least one agent must be selected")
        
        # Create session
        backtest_id = backtest_manager.create_session(request)
        session = backtest_manager.get_session(backtest_id)
        
        # Generate weight tracking session ID
        weight_session_id = f"backtest_{backtest_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create weight tracking session
        weight_tracker.create_session(
            session_id=weight_session_id,
            session_type="backtest",
            tickers=request.tickers,
            start_date=request.start_date,
            end_date=request.end_date,
            selected_agents=request.selected_agents
        )
        
        # Store weight session ID in the backtest session
        session.weight_session_id = weight_session_id
        
        # Start the backtest in background
        session.task = asyncio.create_task(run_backtest_async(session))
        
        return {
            "backtest_id": backtest_id,
            "weight_session_id": weight_session_id,
            "status": "started",
            "message": "Backtest started successfully. Use the backtest_id to stream updates.",
            "stream_url": f"/backtest/stream/{backtest_id}",
            "status_url": f"/backtest/status/{backtest_id}"
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start backtest: {str(e)}")


@router.get("/stream/{backtest_id}")
async def stream_backtest(
    backtest_id: str,
    api_key: str = Depends(verify_api_key)
):
    """
    Stream real-time updates for a running backtest.
    
    **Authentication Required**: This endpoint requires a valid API key.
    
    Returns Server-Sent Events with:
    - backtest_start: Initial event with backtest info
    - backtest_progress: Progress updates for each trading day
    - trading: Individual trading decisions
    - portfolio_update: Portfolio value changes
    - performance_update: Performance metrics updates (every 5 days)
    - backtest_complete: Final results
    """
    session = backtest_manager.get_session(backtest_id)
    if not session:
        raise HTTPException(status_code=404, detail="Backtest not found")
    
    async def event_generator():
        try:
            consecutive_timeouts = 0
            max_consecutive_timeouts = 30  # 30 seconds of consecutive timeouts
            
            while True:
                # Wait for events from the backtest
                try:
                    event = await asyncio.wait_for(session.event_queue.get(), timeout=1.0)
                    consecutive_timeouts = 0  # Reset timeout counter
                    yield event.to_sse()
                    
                    # If this is a completion event, break the loop
                    if hasattr(event, 'type') and event.type == "backtest_complete":
                        # Mark weight tracking session as complete
                        if hasattr(session, 'weight_session_id'):
                            weight_tracker.complete_session(session.weight_session_id)
                        break
                        
                except asyncio.TimeoutError:
                    consecutive_timeouts += 1
                    
                    # Check if the backtest is still running
                    if not session.is_running and session.result.status in ["completed", "failed"]:
                        # Mark weight tracking session as complete
                        if hasattr(session, 'weight_session_id'):
                            weight_tracker.complete_session(session.weight_session_id)
                        
                        # Send final completion message and break
                        yield f"event: backtest_complete\ndata: {{\"status\": \"{session.result.status}\", \"message\": \"Backtest completed\"}}\n\n"
                        break
                    
                    # If too many consecutive timeouts, assume the session is dead
                    if consecutive_timeouts >= max_consecutive_timeouts:
                        yield f"event: timeout\ndata: {{\"message\": \"Stream timeout - session may have ended\"}}\n\n"
                        break
                    
                    # Send keepalive
                    yield "event: keepalive\ndata: {}\n\n"
                    
        except Exception as e:
            yield f"event: error\ndata: {{\"message\": \"Stream error: {str(e)}\"}}\n\n"
        finally:
            # Clean up the session after streaming completes
            try:
                backtest_manager.cleanup_session(backtest_id)
            except Exception as cleanup_error:
                print(f"Error during session cleanup: {cleanup_error}")
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.get("/status/{backtest_id}")
async def get_backtest_status(
    backtest_id: str,
    api_key: str = Depends(verify_api_key)
):
    """
    Get the current status of a backtest.
    
    **Authentication Required**: This endpoint requires a valid API key.
    """
    session = backtest_manager.get_session(backtest_id)
    if not session:
        raise HTTPException(status_code=404, detail="Backtest not found")
    
    return {
        "backtest_id": backtest_id,
        "weight_session_id": getattr(session, 'weight_session_id', None),
        "status": session.result.status,
        "progress": session.result.progress,
        "current_date": session.result.current_date,
        "start_time": session.start_time.isoformat() if session.start_time else None,
        "is_running": session.is_running,
        "error_message": session.result.error_message,
        "request_summary": {
            "tickers": session.request.tickers,
            "agents": session.request.selected_agents,
            "start_date": session.request.start_date,
            "end_date": session.request.end_date,
            "initial_capital": session.request.initial_capital
        }
    }


@router.post("/run-sync")
@traceable(
    name="AI Hedge Fund Backtest Sync",
    metadata_key="backtest_sync_metadata"
)
async def run_backtest_sync(
    request: BacktestRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Run a backtest synchronously (blocking) and return complete results.
    
    **Authentication Required**: This endpoint requires a valid API key.
    
    ⚠️ **Warning**: This endpoint will block until the backtest completes,
    which can take several minutes for longer time periods.
    
    For real-time updates, use `/backtest/start` + `/backtest/stream/{id}` instead.
    """
    try:
        # Import here to avoid circular imports
        from src.backtester import Backtester
        from src.main import run_hedge_fund
        
        # Validate request
        if not request.tickers:
            raise HTTPException(status_code=400, detail="At least one ticker is required")
        
        if not request.selected_agents:
            raise HTTPException(status_code=400, detail="At least one agent must be selected")
        
        # Add metadata for tracing
        from langsmith import get_current_run_tree
        if get_current_run_tree():
            get_current_run_tree().extra = {
                "tickers": request.tickers,
                "selected_agents": request.selected_agents,
                "model_name": request.model_name,
                "model_provider": request.model_provider.value,
                "date_range": f"{request.start_date} to {request.end_date}",
                "initial_capital": request.initial_capital,
                "margin_requirement": request.margin_requirement,
                "backtest_type": "synchronous"
            }
        
        # Generate weight tracking session ID
        weight_session_id = f"backtest_sync_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Create weight tracking session
        weight_tracker.create_session(
            session_id=weight_session_id,
            session_type="backtest_sync",
            tickers=request.tickers,
            start_date=request.start_date,
            end_date=request.end_date,
            selected_agents=request.selected_agents
        )
        
        # Create backtester with session ID
        backtester = Backtester(
            agent=run_hedge_fund,
            tickers=request.tickers,
            start_date=request.start_date,
            end_date=request.end_date,
            initial_capital=request.initial_capital,
            model_name=request.model_name,
            model_provider=request.model_provider.value,
            selected_analysts=request.selected_agents,
            initial_margin_requirement=request.margin_requirement,
            session_id=weight_session_id  # Pass session ID
        )
        
        # Run the backtest
        performance_metrics = backtester.run_backtest()
        
        # Mark weight tracking session as complete
        weight_tracker.complete_session(weight_session_id)
        
        # Calculate final performance
        final_value = backtester.portfolio_values[-1]["Portfolio Value"] if backtester.portfolio_values else request.initial_capital
        total_return = (final_value / request.initial_capital - 1) * 100
        
        return {
            "status": "completed",
            "weight_session_id": weight_session_id,
            "performance_metrics": {
                "total_return": total_return,
                "final_value": final_value,
                "initial_capital": request.initial_capital,
                "sharpe_ratio": performance_metrics.get("sharpe_ratio"),
                "sortino_ratio": performance_metrics.get("sortino_ratio"),
                "max_drawdown": performance_metrics.get("max_drawdown")
            },
            "portfolio_history": [
                {
                    "date": item["Date"].strftime("%Y-%m-%d") if hasattr(item["Date"], "strftime") else str(item["Date"]),
                    "value": item["Portfolio Value"]
                }
                for item in backtester.portfolio_values
            ],
            "final_portfolio": {
                "cash": backtester.portfolio["cash"],
                "positions": backtester.portfolio["positions"],
                "realized_gains": backtester.portfolio["realized_gains"]
            }
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backtest failed: {str(e)}")


@router.delete("/{backtest_id}")
async def cancel_backtest(
    backtest_id: str,
    api_key: str = Depends(verify_api_key)
):
    """
    Cancel a running backtest.
    
    **Authentication Required**: This endpoint requires a valid API key.
    """
    session = backtest_manager.get_session(backtest_id)
    if not session:
        raise HTTPException(status_code=404, detail="Backtest not found")
    
    # Cancel the task if running
    if session.task and not session.task.done():
        session.task.cancel()
        session.result.status = "cancelled"
        session.is_running = False
    
    # Clean up the session
    backtest_manager.cleanup_session(backtest_id)
    
    return {"message": f"Backtest {backtest_id} cancelled successfully"}


@router.post("/cleanup")
async def cleanup_hung_sessions(
    api_key: str = Depends(verify_api_key)
):
    """
    Clean up all hung/completed backtest sessions to fix loading issues.
    
    **Authentication Required**: This endpoint requires a valid API key.
    """
    try:
        backtest_manager.cleanup_all_sessions()
        return {"message": "All backtest sessions cleaned up successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cleanup sessions: {str(e)}")


@router.get("/sessions")
async def list_active_sessions(
    api_key: str = Depends(verify_api_key)
):
    """
    List all active backtest sessions for debugging.
    
    **Authentication Required**: This endpoint requires a valid API key.
    """
    sessions_info = []
    for session_id, session in backtest_manager.sessions.items():
        sessions_info.append({
            "id": session_id,
            "status": session.result.status,
            "is_running": session.is_running,
            "progress": session.result.progress,
            "start_time": session.start_time.isoformat(),
            "tickers": session.request.tickers,
            "agents": session.request.selected_agents
        })
    
    return {
        "active_sessions": len(sessions_info),
        "sessions": sessions_info
    } 
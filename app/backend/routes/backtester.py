from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
import asyncio
from datetime import datetime
from typing import Optional

from app.backend.models.schemas import BacktestRequest, BacktestResult, ErrorResponse
from app.backend.services.backtester import backtest_manager, run_backtest_async
from app.backend.middleware.auth import verify_api_key

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
        
        # Start the backtest in background
        session.task = asyncio.create_task(run_backtest_async(session))
        
        return {
            "backtest_id": backtest_id,
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
            while True:
                # Wait for events from the backtest
                try:
                    event = await asyncio.wait_for(session.event_queue.get(), timeout=1.0)
                    yield event.to_sse()
                    
                    # If this is a completion event, break the loop
                    if hasattr(event, 'type') and event.type == "backtest_complete":
                        break
                        
                except asyncio.TimeoutError:
                    # Check if the backtest is still running
                    if not session.is_running and session.result.status in ["completed", "failed"]:
                        break
                    # Send keepalive
                    yield "event: keepalive\ndata: {}\n\n"
                    
        except Exception as e:
            yield f"event: error\ndata: {{\"message\": \"Stream error: {str(e)}\"}}\n\n"
        finally:
            # Clean up the session after streaming completes
            backtest_manager.cleanup_session(backtest_id)
    
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
        
        # Create backtester
        backtester = Backtester(
            agent=run_hedge_fund,
            tickers=request.tickers,
            start_date=request.start_date,
            end_date=request.end_date,
            initial_capital=request.initial_capital,
            model_name=request.model_name,
            model_provider=request.model_provider.value,
            selected_analysts=request.selected_agents,
            initial_margin_requirement=request.margin_requirement
        )
        
        # Run the backtest
        performance_metrics = backtester.run_backtest()
        
        # Calculate final performance
        final_value = backtester.portfolio_values[-1]["Portfolio Value"] if backtester.portfolio_values else request.initial_capital
        total_return = (final_value / request.initial_capital - 1) * 100
        
        return {
            "status": "completed",
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
    
    if session.task and not session.task.done():
        session.task.cancel()
        session.result.status = "cancelled"
        session.is_running = False
    
    backtest_manager.cleanup_session(backtest_id)
    
    return {
        "backtest_id": backtest_id,
        "status": "cancelled",
        "message": "Backtest cancelled successfully"
    } 
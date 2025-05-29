from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
import asyncio

from backend.models.schemas import ErrorResponse, HedgeFundRequest
from backend.models.events import StartEvent, ProgressUpdateEvent, ErrorEvent, CompleteEvent
from backend.services.graph import create_graph, parse_hedge_fund_response, run_graph_async
from backend.services.portfolio import create_portfolio
from backend.middleware.auth import verify_api_key, verify_api_key_optional
from src.utils.progress import progress
from src.utils.analysts import ANALYST_ORDER
from src.llm.models import LLM_ORDER, ModelProvider

router = APIRouter(prefix="/hedge-fund")


@router.get("/agents")
async def get_available_agents(
    _: str = Depends(verify_api_key_optional)  # Optional auth - allows public access
):
    """Get list of available AI agents/analysts."""
    return {
        "agents": [
            {"id": value, "name": display} 
            for display, value in ANALYST_ORDER
        ]
    }


@router.get("/models")
async def get_available_models(
    _: str = Depends(verify_api_key_optional)  # Optional auth - allows public access
):
    """Get list of available LLM models."""
    return {
        "models": [
            {
                "display_name": display,
                "model_name": name,
                "provider": provider
            }
            for display, name, provider in LLM_ORDER
        ]
    }


@router.post("/run-sync")
async def run_hedge_fund_sync(
    request: HedgeFundRequest,
    api_key: str = Depends(verify_api_key)  # Requires valid API key
):
    """
    Synchronous endpoint for running hedge fund analysis - easier for Postman testing.
    
    **Authentication Required**: This endpoint requires a valid API key.
    """
    try:
        # Create the portfolio
        portfolio = create_portfolio(request.initial_cash, request.margin_requirement, request.tickers)

        # Construct agent graph
        graph = create_graph(request.selected_agents)
        graph = graph.compile()

        # Convert model_provider to string if it's an enum
        model_provider = request.model_provider
        if hasattr(model_provider, "value"):
            model_provider = model_provider.value

        # Run the graph
        result = await run_graph_async(
            graph=graph,
            portfolio=portfolio,
            tickers=request.tickers,
            start_date=request.get_start_date(),
            end_date=request.end_date,
            model_name=request.model_name,
            model_provider=model_provider,
            show_reasoning=request.show_reasoning,
        )

        if not result or not result.get("messages"):
            raise HTTPException(status_code=500, detail="Failed to generate hedge fund decisions")

        # Return the final result
        return {
            "decisions": parse_hedge_fund_response(result.get("messages", [])[-1].content),
            "analyst_signals": result.get("data", {}).get("analyst_signals", {}),
            "metadata": {
                "tickers": request.tickers,
                "start_date": request.get_start_date(),
                "end_date": request.end_date,
                "model": f"{request.model_provider.value}:{request.model_name}",
                "selected_agents": request.selected_agents,
                "authenticated": True
            }
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.post(
    path="/run",
    responses={
        200: {"description": "Successful response with streaming updates"},
        400: {"model": ErrorResponse, "description": "Invalid request parameters"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def run_hedge_fund(
    request: HedgeFundRequest,
    api_key: str = Depends(verify_api_key)  # Requires valid API key
):
    """
    Streaming endpoint for running hedge fund analysis with real-time updates.
    
    **Authentication Required**: This endpoint requires a valid API key.
    """
    try:
        # Create the portfolio
        portfolio = create_portfolio(request.initial_cash, request.margin_requirement, request.tickers)

        # Construct agent graph
        graph = create_graph(request.selected_agents)
        graph = graph.compile()

        # Log a test progress update for debugging
        progress.update_status("system", None, "Preparing hedge fund run")

        # Convert model_provider to string if it's an enum
        model_provider = request.model_provider
        if hasattr(model_provider, "value"):
            model_provider = model_provider.value

        # Set up streaming response
        async def event_generator():
            # Queue for progress updates
            progress_queue = asyncio.Queue()

            # Simple handler to add updates to the queue
            def progress_handler(agent_name, ticker, status, analysis, timestamp):
                event = ProgressUpdateEvent(agent=agent_name, ticker=ticker, status=status, timestamp=timestamp, analysis=analysis)
                progress_queue.put_nowait(event)

            # Register our handler with the progress tracker
            progress.register_handler(progress_handler)

            try:
                # Start the graph execution in a background task
                run_task = asyncio.create_task(
                    run_graph_async(
                        graph=graph,
                        portfolio=portfolio,
                        tickers=request.tickers,
                        start_date=request.get_start_date(),
                        end_date=request.end_date,
                        model_name=request.model_name,
                        model_provider=model_provider,
                        show_reasoning=request.show_reasoning,
                    )
                )
                # Send initial message
                yield StartEvent().to_sse()

                # Stream progress updates until run_task completes
                while not run_task.done():
                    # Either get a progress update or wait a bit
                    try:
                        event = await asyncio.wait_for(progress_queue.get(), timeout=1.0)
                        yield event.to_sse()
                    except asyncio.TimeoutError:
                        # Just continue the loop
                        pass

                # Get the final result
                result = run_task.result()

                if not result or not result.get("messages"):
                    yield ErrorEvent(message="Failed to generate hedge fund decisions").to_sse()
                    return

                # Send the final result
                final_data = CompleteEvent(
                    data={
                        "decisions": parse_hedge_fund_response(result.get("messages", [])[-1].content),
                        "analyst_signals": result.get("data", {}).get("analyst_signals", {}),
                        "authenticated": True
                    }
                )
                yield final_data.to_sse()

            finally:
                # Clean up
                progress.unregister_handler(progress_handler)
                if "run_task" in locals() and not run_task.done():
                    run_task.cancel()

        # Return a streaming response
        return StreamingResponse(event_generator(), media_type="text/event-stream")

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while processing the request: {str(e)}")

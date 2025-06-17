from fastapi import APIRouter

from app.backend.routes.hedge_fund import router as hedge_fund_router
from app.backend.routes.health import router as health_router
from app.backend.routes.backtester import router as backtest_router
from app.backend.routes.chat import router as chat_router
from app.backend.routes.warren_buffett_chat import router as warren_buffett_router

# Main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(health_router, tags=["health"])
api_router.include_router(hedge_fund_router, tags=["hedge-fund"])
api_router.include_router(backtest_router, tags=["backtest"])
api_router.include_router(chat_router, tags=["chat"])
api_router.include_router(warren_buffett_router, tags=["warren-buffett-chat"])

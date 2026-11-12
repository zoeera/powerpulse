from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, bills, meter, appliances, forecasts, spikes,
    recommendations, reports, users, files
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(bills.router, prefix="/bills", tags=["Bills"])
api_router.include_router(meter.router, prefix="/meter", tags=["Smart Meter"])
api_router.include_router(appliances.router, prefix="/appliances", tags=["Appliances"])
api_router.include_router(forecasts.router, prefix="/forecasts", tags=["Forecasting"])
api_router.include_router(spikes.router, prefix="/spikes", tags=["Spike Alerts"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["Cost & Eco Recommendations"])
api_router.include_router(reports.router, prefix="/reports", tags=["PDF Reports"])
api_router.include_router(users.router, prefix="/users", tags=["Users & Privacy"])
api_router.include_router(files.router, prefix="/files", tags=["Secure Storage"])


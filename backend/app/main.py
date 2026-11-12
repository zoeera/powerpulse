from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router
from app.db.session import engine
from app.db.base import Base
from app.ml.model_loader import model_loader

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Full-stack AI-driven electricity consumption forecasting and cost optimization web application for Indian households.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware (allow any origin cleanly when "*" is configured, e.g. Render/Vercel deploys)
allow_all_origins = "*" in settings.BACKEND_CORS_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[] if allow_all_origins else settings.BACKEND_CORS_ORIGINS,
    allow_origin_regex=r"https?://.*" if allow_all_origins else None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    # Ensure database schema exists
    try:
        Base.metadata.create_all(bind=engine)
        print("[Startup] Database tables verified.")
    except Exception as e:
        print(f"[Startup] Note: Could not auto-create tables (database might be initializing): {e}")

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "app": settings.PROJECT_NAME,
        "version": "1.0.0",
        "models_loaded": len(model_loader._models)
    }

# Include API v1 router
app.include_router(api_router, prefix=settings.API_V1_STR)


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routes import health, payments, notifications

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend microservice for enterprise payment transaction processing and dispatch notifications.",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration
# Allow frontend client running on localhost:28080, Kubernetes NodePort 30099, or custom dev origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Sub-routers
app.include_router(health.router)
app.include_router(payments.router)
app.include_router(notifications.router)

@app.get("/", tags=["Root"], summary="API Root metadata")
def root_info():
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "status": "online",
        "documentation": "/docs",
        "endpoints": {
            "health": "/health",
            "payments": "/api/payments",
            "notifications": "/api/notifications",
        },
    }

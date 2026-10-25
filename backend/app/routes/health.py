from fastapi import APIRouter
from ..config import settings
from ..models import HealthStatus
from ..data import current_iso_time, get_uptime_seconds, get_counts

router = APIRouter(tags=["Health"])

@router.get("/health", response_model=HealthStatus, summary="Check engine service health")
def check_health() -> HealthStatus:
    payments_count, notifs_count = get_counts()
    return HealthStatus(
        status="healthy",
        service="Enterprise Payment & Notification Engine - Backend",
        version=settings.APP_VERSION,
        timestamp=current_iso_time(),
        uptime_seconds=get_uptime_seconds(),
        environment=settings.APP_ENV,
        active_records=payments_count,
        active_notifications=notifs_count,
    )

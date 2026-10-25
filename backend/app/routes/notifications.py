from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status
from ..models import (
    NotificationEvent,
    NotificationListResponse,
)
from ..data import (
    list_notifications,
    get_notification_by_id,
    current_iso_time,
)

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])

@router.get("", response_model=NotificationListResponse, summary="Retrieve notification events")
def get_notifications(
    status: Optional[str] = Query(None, description="Filter by status, e.g. DELIVERED, QUEUED, PROCESSING, FAILED"),
    limit: int = Query(50, ge=1, le=100, description="Max notifications to return"),
) -> NotificationListResponse:
    records = list_notifications(status=status, limit=limit)
    return NotificationListResponse(
        total=len(records),
        items=records,
        timestamp=current_iso_time(),
    )

@router.get("/{notification_id}", response_model=NotificationEvent, summary="Get notification by ID")
def get_notification(notification_id: str) -> NotificationEvent:
    event = get_notification_by_id(notification_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification event with ID '{notification_id}' was not found.",
        )
    return event

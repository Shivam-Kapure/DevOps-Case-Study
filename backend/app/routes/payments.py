from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, status
from ..models import (
    PaymentRecord,
    PaymentCreate,
    PaymentListResponse,
)
from ..data import (
    list_payments,
    get_payment_by_id,
    create_payment,
    current_iso_time,
)

router = APIRouter(prefix="/api/payments", tags=["Payments"])

@router.get("", response_model=PaymentListResponse, summary="Retrieve payment records")
def get_payments(
    status: Optional[str] = Query(None, description="Filter by status, e.g. COMPLETED, PENDING, PROCESSING, FAILED, REFUNDED"),
    search: Optional[str] = Query(None, description="Search term for ID, customer, or description"),
    limit: int = Query(50, ge=1, le=100, description="Max records to return"),
) -> PaymentListResponse:
    records = list_payments(status=status, search=search, limit=limit)
    return PaymentListResponse(
        total=len(records),
        items=records,
        timestamp=current_iso_time(),
    )

@router.get("/{transaction_id}", response_model=PaymentRecord, summary="Get payment by transaction ID")
def get_payment(transaction_id: str) -> PaymentRecord:
    payment = get_payment_by_id(transaction_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment transaction with ID '{transaction_id}' was not found.",
        )
    return payment

@router.post("", response_model=PaymentRecord, status_code=status.HTTP_201_CREATED, summary="Submit a new payment")
def post_payment(payload: PaymentCreate) -> PaymentRecord:
    new_record = create_payment(payload)
    return new_record

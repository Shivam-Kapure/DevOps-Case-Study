from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field

class PaymentStatus(str, Enum):
    COMPLETED = "COMPLETED"
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"

class PaymentMethod(str, Enum):
    CREDIT_CARD = "Credit Card"
    BANK_TRANSFER = "Bank Transfer"
    ACH = "ACH Direct Debit"
    WIRE = "Fedwire"
    SEPA = "SEPA Instant"

class NotificationChannel(str, Enum):
    EMAIL = "EMAIL"
    SMS = "SMS"
    WEBHOOK = "WEBHOOK"
    PUSH = "PUSH"

class NotificationStatus(str, Enum):
    DELIVERED = "DELIVERED"
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    FAILED = "FAILED"

class PaymentRecord(BaseModel):
    id: str = Field(..., description="Unique transaction identifier (e.g. TXN-100234)")
    amount: float = Field(..., gt=0, description="Transaction monetary amount")
    currency: str = Field(default="USD", min_length=3, max_length=3, description="ISO 4217 Currency Code")
    status: PaymentStatus = Field(..., description="Current settlement status")
    timestamp: str = Field(..., description="ISO 8601 formatted timestamp")
    customer: str = Field(..., description="Customer or entity identifier")
    method: PaymentMethod = Field(default=PaymentMethod.CREDIT_CARD, description="Settlement rail / method")
    description: Optional[str] = Field(default="", description="Transaction remarks")

class PaymentCreate(BaseModel):
    amount: float = Field(..., gt=0, description="Amount must be greater than zero")
    currency: str = Field(default="USD", min_length=3, max_length=3, description="ISO 4217 Currency Code")
    customer: str = Field(..., min_length=2, max_length=100, description="Customer or business name")
    method: PaymentMethod = Field(default=PaymentMethod.CREDIT_CARD, description="Payment method")
    description: Optional[str] = Field(default="", max_length=255, description="Brief description")
    status: Optional[PaymentStatus] = Field(default=PaymentStatus.COMPLETED, description="Initial status")

class NotificationEvent(BaseModel):
    id: str = Field(..., description="Unique notification event ID (e.g. NOTIF-5001)")
    event_type: str = Field(..., description="Event classification (e.g. PAYMENT_SETTLED)")
    related_payment_id: Optional[str] = Field(None, description="Associated transaction ID")
    channel: NotificationChannel = Field(..., description="Dispatch channel")
    recipient: str = Field(..., description="Destination address / webhook endpoint")
    status: NotificationStatus = Field(..., description="Dispatch lifecycle state")
    timestamp: str = Field(..., description="ISO 8601 formatted timestamp")
    payload_summary: str = Field(..., description="Short summary of notification payload")

class HealthStatus(BaseModel):
    status: str = Field(..., description="Engine health status: healthy, degraded, or unhealthy")
    service: str = Field(..., description="Service identifier")
    version: str = Field(..., description="Semantic application version")
    timestamp: str = Field(..., description="Current system ISO 8601 timestamp")
    uptime_seconds: float = Field(..., description="Elapsed runtime seconds since process start")
    environment: str = Field(..., description="Runtime environment (development, staging, production)")
    active_records: int = Field(..., description="Count of loaded payment records")
    active_notifications: int = Field(..., description="Count of loaded notification events")

class PaymentListResponse(BaseModel):
    total: int
    items: List[PaymentRecord]
    timestamp: str

class NotificationListResponse(BaseModel):
    total: int
    items: List[NotificationEvent]
    timestamp: str

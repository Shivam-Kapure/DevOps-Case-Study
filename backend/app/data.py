import time
import random
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from .models import (
    PaymentRecord,
    PaymentStatus,
    PaymentMethod,
    PaymentCreate,
    NotificationEvent,
    NotificationChannel,
    NotificationStatus,
)

# Application start time for uptime calculation
START_TIME = time.time()

def current_iso_time(offset_minutes: int = 0) -> str:
    now = datetime.now(timezone.utc) - timedelta(minutes=offset_minutes)
    return now.isoformat()

# Seed mock payments
_PAYMENTS_STORE: List[PaymentRecord] = [
    PaymentRecord(
        id="TXN-90214-ENT",
        amount=145000.00,
        currency="USD",
        status=PaymentStatus.COMPLETED,
        timestamp=current_iso_time(offset_minutes=12),
        customer="Apex Global Logistics",
        method=PaymentMethod.WIRE,
        description="Cross-border maritime clearing settlement",
    ),
    PaymentRecord(
        id="TXN-90213-ENT",
        amount=12450.50,
        currency="USD",
        status=PaymentStatus.COMPLETED,
        timestamp=current_iso_time(offset_minutes=28),
        customer="CyberSecure Technologies",
        method=PaymentMethod.ACH,
        description="Enterprise SaaS Q4 subscription renewal",
    ),
    PaymentRecord(
        id="TXN-90212-ENT",
        amount=3890.00,
        currency="EUR",
        status=PaymentStatus.PROCESSING,
        timestamp=current_iso_time(offset_minutes=45),
        customer="Starlight Media GmbH",
        method=PaymentMethod.SEPA,
        description="Content syndication royalties",
    ),
    PaymentRecord(
        id="TXN-90211-ENT",
        amount=84200.75,
        currency="USD",
        status=PaymentStatus.PENDING,
        timestamp=current_iso_time(offset_minutes=72),
        customer="Nordic Horizon Ventures",
        method=PaymentMethod.BANK_TRANSFER,
        description="Escrow deposit for Series A tranche",
    ),
    PaymentRecord(
        id="TXN-90210-ENT",
        amount=1750.25,
        currency="USD",
        status=PaymentStatus.COMPLETED,
        timestamp=current_iso_time(offset_minutes=110),
        customer="Quantum Dynamics Inc",
        method=PaymentMethod.CREDIT_CARD,
        description="Cloud compute infrastructure reservation",
    ),
    PaymentRecord(
        id="TXN-90209-ENT",
        amount=63000.00,
        currency="EUR",
        status=PaymentStatus.FAILED,
        timestamp=current_iso_time(offset_minutes=140),
        customer="Vanguard Biotech Ltd",
        method=PaymentMethod.WIRE,
        description="Hardware acquisition (insufficient liquidity limit)",
    ),
    PaymentRecord(
        id="TXN-90208-ENT",
        amount=5200.00,
        currency="USD",
        status=PaymentStatus.REFUNDED,
        timestamp=current_iso_time(offset_minutes=195),
        customer="Helios Renewable Power",
        method=PaymentMethod.ACH,
        description="Overpayment adjustment refund",
    ),
    PaymentRecord(
        id="TXN-90207-ENT",
        amount=29450.00,
        currency="USD",
        status=PaymentStatus.COMPLETED,
        timestamp=current_iso_time(offset_minutes=240),
        customer="Aura BioLabs",
        method=PaymentMethod.CREDIT_CARD,
        description="Precision laboratory reagents purchase",
    ),
]

# Seed mock notification events
_NOTIFICATIONS_STORE: List[NotificationEvent] = [
    NotificationEvent(
        id="NOTIF-8801",
        event_type="PAYMENT_SETTLED",
        related_payment_id="TXN-90214-ENT",
        channel=NotificationChannel.WEBHOOK,
        recipient="https://api.apexlogistics.com/hooks/settlement",
        status=NotificationStatus.DELIVERED,
        timestamp=current_iso_time(offset_minutes=11),
        payload_summary="HTTP 200 OK - Dispatched settlement payload for $145,000.00 USD",
    ),
    NotificationEvent(
        id="NOTIF-8802",
        event_type="PAYMENT_SETTLED",
        related_payment_id="TXN-90213-ENT",
        channel=NotificationChannel.EMAIL,
        recipient="finance@cybersecure.io",
        status=NotificationStatus.DELIVERED,
        timestamp=current_iso_time(offset_minutes=27),
        payload_summary="Receipt confirmation email dispatched for TXN-90213-ENT",
    ),
    NotificationEvent(
        id="NOTIF-8803",
        event_type="CLEARING_INITIATED",
        related_payment_id="TXN-90212-ENT",
        channel=NotificationChannel.PUSH,
        recipient="ops-dashboard-channel-eu",
        status=NotificationStatus.PROCESSING,
        timestamp=current_iso_time(offset_minutes=44),
        payload_summary="SEPA Instant clearing pipeline engaged",
    ),
    NotificationEvent(
        id="NOTIF-8804",
        event_type="APPROVAL_REQUIRED",
        related_payment_id="TXN-90211-ENT",
        channel=NotificationChannel.SMS,
        recipient="+1 (555) 019-2834",
        status=NotificationStatus.QUEUED,
        timestamp=current_iso_time(offset_minutes=70),
        payload_summary="2FA Approval SMS queued for treasury signatory",
    ),
    NotificationEvent(
        id="NOTIF-8805",
        event_type="TRANSACTION_ALERT",
        related_payment_id="TXN-90209-ENT",
        channel=NotificationChannel.WEBHOOK,
        recipient="https://compliance.vanguard.eu/alerts",
        status=NotificationStatus.FAILED,
        timestamp=current_iso_time(offset_minutes=139),
        payload_summary="Gateway rejection: Insufficient balance response code 51",
    ),
    NotificationEvent(
        id="NOTIF-8806",
        event_type="REFUND_ISSUED",
        related_payment_id="TXN-90208-ENT",
        channel=NotificationChannel.EMAIL,
        recipient="accounts@heliospower.com",
        status=NotificationStatus.DELIVERED,
        timestamp=current_iso_time(offset_minutes=194),
        payload_summary="Credit note adjustment notice dispatched",
    ),
]

def get_uptime_seconds() -> float:
    return round(time.time() - START_TIME, 2)

def list_payments(status: Optional[str] = None, search: Optional[str] = None, limit: int = 50) -> List[PaymentRecord]:
    results = _PAYMENTS_STORE
    if status:
        results = [p for p in results if p.status.value.lower() == status.lower()]
    if search:
        s = search.lower()
        results = [
            p for p in results
            if s in p.id.lower() or s in p.customer.lower() or s in p.description.lower()
        ]
    return results[:limit]

def get_payment_by_id(payment_id: str) -> Optional[PaymentRecord]:
    for p in _PAYMENTS_STORE:
        if p.id.lower() == payment_id.lower():
            return p
    return None

def create_payment(payment_in: PaymentCreate) -> PaymentRecord:
    # Generate unique ID
    random_suffix = random.randint(10000, 99999)
    new_id = f"TXN-{random_suffix}-ENT"
    now_str = current_iso_time(0)
    
    new_payment = PaymentRecord(
        id=new_id,
        amount=round(payment_in.amount, 2),
        currency=payment_in.currency.upper(),
        status=payment_in.status or PaymentStatus.COMPLETED,
        timestamp=now_str,
        customer=payment_in.customer,
        method=payment_in.method,
        description=payment_in.description or f"Payment from {payment_in.customer}",
    )
    _PAYMENTS_STORE.insert(0, new_payment)
    
    # Automatically emit associated notification event
    notif_id = f"NOTIF-{random.randint(1000, 9999)}"
    notif = NotificationEvent(
        id=notif_id,
        event_type="PAYMENT_CREATED",
        related_payment_id=new_id,
        channel=NotificationChannel.WEBHOOK,
        recipient=f"https://webhook.site/payments/{new_id.lower()}",
        status=NotificationStatus.DELIVERED if new_payment.status == PaymentStatus.COMPLETED else NotificationStatus.QUEUED,
        timestamp=now_str,
        payload_summary=f"Event triggered for {new_id}: {new_payment.currency} {new_payment.amount:,.2f} ({new_payment.status})",
    )
    _NOTIFICATIONS_STORE.insert(0, notif)
    return new_payment

def list_notifications(status: Optional[str] = None, limit: int = 50) -> List[NotificationEvent]:
    results = _NOTIFICATIONS_STORE
    if status:
        results = [n for n in results if n.status.value.lower() == status.lower()]
    return results[:limit]

def get_notification_by_id(notif_id: str) -> Optional[NotificationEvent]:
    for n in _NOTIFICATIONS_STORE:
        if n.id.lower() == notif_id.lower():
            return n
    return None

def get_counts() -> tuple[int, int]:
    return len(_PAYMENTS_STORE), len(_NOTIFICATIONS_STORE)

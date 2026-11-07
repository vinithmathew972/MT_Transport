from datetime import date, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.database import get_db
from backend.models import Owner, Trip, Notification
from backend.auth import get_current_owner
from backend.crud import (
    get_kpi_summary, get_monthly_charts_data,
    get_expense_breakdown_data, get_upcoming_expiries,
    get_quick_summary_stats
)

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/kpi")
def get_dashboard_kpis(
    period: str = Query("month", description="today, week, month, all, custom"),
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)
):
    today = date.today()
    if period == "today":
        d_from, d_to = today, today
    elif period == "week":
        d_from = today - timedelta(days=7)
        d_to = today
    elif period == "month":
        d_from = today.replace(day=1)
        d_to = today
    elif period == "custom" and date_from:
        d_from = date_from
        d_to = date_to or today
    else:
        d_from, d_to = None, None

    kpi = get_kpi_summary(db, date_from=d_from, date_to=d_to)
    return kpi

@router.get("/charts")
def get_charts(
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)
):
    monthly_data = get_monthly_charts_data(db)
    breakdown = get_expense_breakdown_data(db)
    return {
        "monthly_comparison": monthly_data,
        "expense_breakdown": breakdown
    }

@router.get("/upcoming-expiries")
def get_expiries(
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)
):
    return get_upcoming_expiries(db, limit=10)

@router.get("/recent-trips")
def get_recent_trips(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)
):
    trips = db.query(Trip).order_by(desc(Trip.trip_date), desc(Trip.id)).limit(limit).all()
    results = []
    for t in trips:
        results.append({
            "id": t.id,
            "date": t.trip_date.strftime("%d-%m-%Y") if t.trip_date else "",
            "vehicle_number": t.truck.vehicle_number if t.truck else "N/A",
            "from_location": t.from_location,
            "to_location": t.to_location,
            "route": f"{t.from_location} \u2192 {t.to_location}",
            "customer_name": t.customer_name,
            "rent": float(t.total_rent),
            "advance": float(t.advance_received),
            "balance": float(t.balance_receivable),
            "status": t.trip_status
        })
    return results

@router.get("/quick-summary")
def get_quick_summary(
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)
):
    return get_quick_summary_stats(db)

@router.get("/notifications")
def get_notifications(
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)
):
    notifs = db.query(Notification).order_by(desc(Notification.created_at)).limit(20).all()
    unread_count = db.query(Notification).filter(Notification.is_read == False).count()
    return {
        "unread_count": unread_count,
        "items": [
            {
                "id": n.id,
                "title": n.title,
                "message": n.message,
                "category": n.category,
                "severity": n.severity,
                "is_read": n.is_read,
                "created_at": n.created_at.strftime("%d %b %H:%M") if n.created_at else ""
            }
            for n in notifs
        ]
    }

@router.put("/notifications/{notif_id}/read")
def mark_notification_read(
    notif_id: int,
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)
):
    notif = db.query(Notification).filter(Notification.id == notif_id).first()
    if notif:
        notif.is_read = True
        db.commit()
    return {"success": True}

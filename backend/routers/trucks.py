from datetime import date, timedelta
from decimal import Decimal
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from backend.database import get_db
from backend.models import Owner, Truck, Driver, Trip, Expense, VehicleDocument
from backend.schemas import TruckCreate, TruckUpdate
from backend.auth import get_current_owner

router = APIRouter(prefix="/api/trucks", tags=["Trucks"])

@router.get("")
def list_trucks(
    search: Optional[str] = None,
    active_only: bool = False,
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)
):
    query = db.query(Truck)
    if active_only:
        query = query.filter(Truck.is_active == True)
    if search:
        query = query.filter(Truck.vehicle_number.ilike(f"%{search.strip()}%"))

    trucks = query.order_by(Truck.vehicle_number.asc()).all()
    today = date.today()
    threshold = today + timedelta(days=30)
    
    results = []
    for t in trucks:
        # Trip counts & earnings
        trips = db.query(Trip).filter(Trip.vehicle_id == t.id).all()
        active_trips_count = sum(1 for tr in trips if tr.trip_status in ["Ongoing", "Planned"])
        total_earnings = sum((tr.total_rent for tr in trips), Decimal("0.00"))
        
        # Expenses
        total_expenses = db.query(func.sum(Expense.amount)).filter(Expense.vehicle_id == t.id).scalar() or Decimal("0.00")
        
        # Document alerts
        alerts_count = 0
        for exp in [t.fc_expiry, t.insurance_expiry, t.permit_expiry, t.national_permit_expiry, t.puc_expiry, t.road_tax_expiry]:
            if exp and exp <= threshold:
                alerts_count += 1
        
        assigned_name = t.assigned_driver.full_name if t.assigned_driver else "Unassigned"

        results.append({
            "id": t.id,
            "vehicle_number": t.vehicle_number,
            "make_model": t.make_model,
            "vehicle_type": t.vehicle_type,
            "registration_date": t.registration_date.strftime("%d-%m-%Y") if t.registration_date else "",
            "assigned_driver_id": t.assigned_driver_id,
            "assigned_driver_name": assigned_name,
            "permit_number": t.permit_number,
            "permit_expiry": t.permit_expiry.strftime("%d-%m-%Y") if t.permit_expiry else "",
            "national_permit_expiry": t.national_permit_expiry.strftime("%d-%m-%Y") if t.national_permit_expiry else "",
            "insurance_policy_number": t.insurance_policy_number,
            "insurance_expiry": t.insurance_expiry.strftime("%d-%m-%Y") if t.insurance_expiry else "",
            "fc_expiry": t.fc_expiry.strftime("%d-%m-%Y") if t.fc_expiry else "",
            "puc_expiry": t.puc_expiry.strftime("%d-%m-%Y") if t.puc_expiry else "",
            "road_tax_expiry": t.road_tax_expiry.strftime("%d-%m-%Y") if t.road_tax_expiry else "",
            "is_active": t.is_active,
            "notes": t.notes,
            "active_trips_count": active_trips_count,
            "total_trips_count": len(trips),
            "total_earnings": float(total_earnings),
            "total_expenses": float(total_expenses),
            "net_profit": float(total_earnings - total_expenses),
            "document_alerts_count": alerts_count
        })
    return results

@router.get("/{truck_id}")
def get_truck_details(
    truck_id: int,
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)
):
    truck = db.query(Truck).filter(Truck.id == truck_id).first()
    if not truck:
        raise HTTPException(status_code=404, detail="Truck not found")

    trips = db.query(Trip).filter(Trip.vehicle_id == truck_id).order_by(desc(Trip.trip_date)).limit(15).all()
    expenses = db.query(Expense).filter(Expense.vehicle_id == truck_id).order_by(desc(Expense.date)).limit(15).all()
    docs = db.query(VehicleDocument).filter(VehicleDocument.vehicle_id == truck_id).all()

    total_rent = sum((tr.total_rent for tr in trips), Decimal("0.00"))
    total_exp = sum((e.amount for e in expenses), Decimal("0.00"))

    return {
        "truck": {
            "id": truck.id,
            "vehicle_number": truck.vehicle_number,
            "make_model": truck.make_model,
            "vehicle_type": truck.vehicle_type,
            "registration_date": truck.registration_date.strftime("%d-%m-%Y") if truck.registration_date else "",
            "assigned_driver_id": truck.assigned_driver_id,
            "assigned_driver_name": truck.assigned_driver.full_name if truck.assigned_driver else "Unassigned",
            "permit_number": truck.permit_number,
            "permit_expiry": truck.permit_expiry.strftime("%Y-%m-%d") if truck.permit_expiry else "",
            "national_permit_expiry": truck.national_permit_expiry.strftime("%Y-%m-%d") if truck.national_permit_expiry else "",
            "insurance_policy_number": truck.insurance_policy_number,
            "insurance_expiry": truck.insurance_expiry.strftime("%Y-%m-%d") if truck.insurance_expiry else "",
            "fc_expiry": truck.fc_expiry.strftime("%Y-%m-%d") if truck.fc_expiry else "",
            "puc_expiry": truck.puc_expiry.strftime("%Y-%m-%d") if truck.puc_expiry else "",
            "road_tax_expiry": truck.road_tax_expiry.strftime("%Y-%m-%d") if truck.road_tax_expiry else "",
            "is_active": truck.is_active,
            "notes": truck.notes,
            "total_earnings": float(total_rent),
            "total_expenses": float(total_exp),
            "net_profit": float(total_rent - total_exp)
        },
        "recent_trips": [
            {
                "id": tr.id,
                "date": tr.trip_date.strftime("%d-%m-%Y") if tr.trip_date else "",
                "route": f"{tr.from_location} \u2192 {tr.to_location}",
                "customer": tr.customer_name,
                "rent": float(tr.total_rent),
                "advance": float(tr.advance_received),
                "balance": float(tr.balance_receivable),
                "status": tr.trip_status
            }
            for tr in trips
        ],
        "recent_expenses": [
            {
                "id": e.id,
                "date": e.date.strftime("%d-%m-%Y") if e.date else "",
                "category": e.category,
                "amount": float(e.amount),
                "paid_to": e.paid_to,
                "desc": e.description
            }
            for e in expenses
        ]
    }

@router.post("", status_code=status.HTTP_201_CREATED)
def create_truck(
    payload: TruckCreate,
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)
):
    veh_num = payload.vehicle_number.strip().upper()
    existing = db.query(Truck).filter(Truck.vehicle_number == veh_num).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Truck with vehicle number {veh_num} already exists.")

    truck = Truck(
        vehicle_number=veh_num,
        make_model=payload.make_model or "TATA LPT 3118",
        vehicle_type=payload.vehicle_type or "12 Wheeler Container",
        registration_date=payload.registration_date,
        assigned_driver_id=payload.assigned_driver_id,
        permit_number=payload.permit_number,
        permit_expiry=payload.permit_expiry,
        national_permit_expiry=payload.national_permit_expiry,
        insurance_policy_number=payload.insurance_policy_number,
        insurance_expiry=payload.insurance_expiry,
        fc_expiry=payload.fc_expiry,
        puc_expiry=payload.puc_expiry,
        road_tax_expiry=payload.road_tax_expiry,
        is_active=payload.is_active,
        notes=payload.notes
    )
    db.add(truck)
    db.commit()
    db.refresh(truck)

    # Sync default statutory document records if dates provided
    docs_to_sync = [
        ("FC", payload.fc_expiry),
        ("Insurance", payload.insurance_expiry),
        ("Permit", payload.permit_expiry),
        ("National Permit", payload.national_permit_expiry),
        ("PUC", payload.puc_expiry),
        ("Road Tax", payload.road_tax_expiry)
    ]
    for doc_type, exp_date in docs_to_sync:
        if exp_date:
            db.add(VehicleDocument(
                vehicle_id=truck.id,
                document_type=doc_type,
                expiry_date=exp_date,
                notes=f"Statutory document for {truck.vehicle_number}"
            ))
    db.commit()

    return {"message": "Truck added successfully", "id": truck.id, "vehicle_number": truck.vehicle_number}

@router.put("/{truck_id}")
def update_truck(
    truck_id: int,
    payload: TruckUpdate,
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)
):
    truck = db.query(Truck).filter(Truck.id == truck_id).first()
    if not truck:
        raise HTTPException(status_code=404, detail="Truck not found")

    update_data = payload.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(truck, key, value)

    db.commit()
    db.refresh(truck)
    return {"message": "Truck updated successfully", "truck_id": truck.id}

@router.delete("/{truck_id}")
def delete_truck(
    truck_id: int,
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)
):
    truck = db.query(Truck).filter(Truck.id == truck_id).first()
    if not truck:
        raise HTTPException(status_code=404, detail="Truck not found")

    # Soft delete / deactivate to preserve historical integrity
    truck.is_active = False
    db.commit()
    return {"message": f"Truck {truck.vehicle_number} has been deactivated successfully."}

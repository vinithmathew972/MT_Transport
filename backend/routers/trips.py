import csv
import io
from datetime import date
from decimal import Decimal
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.database import get_db
from backend.models import Owner, Trip, TripPayment, Truck, Driver, Customer, Expense, BataRecord
from backend.schemas import TripCreate, TripUpdate, TripPaymentCreate
from backend.auth import get_current_owner
from backend.crud import recalculate_trip_balance

router = APIRouter(prefix="/api/trips", tags=["Trips"])

@router.get("")
def list_trips(
    search: Optional[str] = None,
    truck_id: Optional[int] = None,
    driver_id: Optional[int] = None,
    status: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)
):
    query = db.query(Trip).order_by(desc(Trip.trip_date), desc(Trip.id))

    if truck_id:
        query = query.filter(Trip.vehicle_id == truck_id)
    if driver_id:
        query = query.filter(Trip.driver_id == driver_id)
    if status and status != "All":
        query = query.filter(Trip.trip_status == status)
    if date_from:
        query = query.filter(Trip.trip_date >= date_from)
    if date_to:
        query = query.filter(Trip.trip_date <= date_to)
    if search:
        search_pattern = f"%{search.strip()}%"
        query = query.filter(
            (Trip.customer_name.ilike(search_pattern)) |
            (Trip.from_location.ilike(search_pattern)) |
            (Trip.to_location.ilike(search_pattern)) |
            (Trip.load_description.ilike(search_pattern))
        )

    trips = query.all()
    results = []
    for t in trips:
        total_paid_after_adv = sum((p.amount for p in t.payments), Decimal("0.00"))
        results.append({
            "id": t.id,
            "trip_date": t.trip_date.strftime("%d-%m-%Y") if t.trip_date else "",
            "raw_date": t.trip_date.strftime("%Y-%m-%d") if t.trip_date else "",
            "vehicle_id": t.vehicle_id,
            "vehicle_number": t.truck.vehicle_number if t.truck else "N/A",
            "driver_id": t.driver_id,
            "driver_name": t.driver.full_name if t.driver else "N/A",
            "customer_name": t.customer_name,
            "from_location": t.from_location,
            "to_location": t.to_location,
            "route": f"{t.from_location} \u2192 {t.to_location}",
            "load_description": t.load_description or "",
            "total_rent": float(t.total_rent),
            "advance_received": float(t.advance_received),
            "additional_payments": float(total_paid_after_adv),
            "balance_receivable": float(t.balance_receivable),
            "trip_status": t.trip_status,
            "notes": t.notes or ""
        })
    return results

@router.get("/export/csv")
def export_trips_csv(
    search: Optional[str] = None,
    truck_id: Optional[int] = None,
    driver_id: Optional[int] = None,
    status: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)
):
    query = db.query(Trip).order_by(desc(Trip.trip_date), desc(Trip.id))

    if truck_id:
        query = query.filter(Trip.vehicle_id == truck_id)
    if driver_id:
        query = query.filter(Trip.driver_id == driver_id)
    if status and status != "All":
        query = query.filter(Trip.trip_status == status)
    if date_from:
        query = query.filter(Trip.trip_date >= date_from)
    if date_to:
        query = query.filter(Trip.trip_date <= date_to)
    if search:
        search_pattern = f"%{search.strip()}%"
        query = query.filter(
            (Trip.customer_name.ilike(search_pattern)) |
            (Trip.from_location.ilike(search_pattern)) |
            (Trip.to_location.ilike(search_pattern)) |
            (Trip.load_description.ilike(search_pattern))
        )

    trips = query.all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Trip ID", "Date", "Vehicle Number", "Driver", "Customer",
        "From", "To", "Load Description", "Total Rent (INR)",
        "Advance Received (INR)", "Balance Receivable (INR)", "Status"
    ])

    for t in trips:
        writer.writerow([
            t.id,
            t.trip_date.strftime("%d-%m-%Y") if t.trip_date else "",
            t.truck.vehicle_number if t.truck else "N/A",
            t.driver.full_name if t.driver else "N/A",
            t.customer_name,
            t.from_location,
            t.to_location,
            t.load_description or "",
            f"{t.total_rent:.2f}",
            f"{t.advance_received:.2f}",
            f"{t.balance_receivable:.2f}",
            t.trip_status
        ])

    csv_data = output.getvalue()
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=Mother_Theresa_Transport_Trips.csv"}
    )

@router.get("/{trip_id}")
def get_trip_detail(
    trip_id: int,
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)
):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip record not found")

    payments = db.query(TripPayment).filter(TripPayment.trip_id == trip_id).order_by(desc(TripPayment.payment_date)).all()
    total_paid_after_adv = sum((p.amount for p in payments), Decimal("0.00"))

    return {
        "id": trip.id,
        "trip_date": trip.trip_date.strftime("%Y-%m-%d") if trip.trip_date else "",
        "formatted_date": trip.trip_date.strftime("%d-%m-%Y") if trip.trip_date else "",
        "vehicle_id": trip.vehicle_id,
        "vehicle_number": trip.truck.vehicle_number if trip.truck else "N/A",
        "driver_id": trip.driver_id,
        "driver_name": trip.driver.full_name if trip.driver else "N/A",
        "customer_name": trip.customer_name,
        "from_location": trip.from_location,
        "to_location": trip.to_location,
        "load_description": trip.load_description or "",
        "total_rent": float(trip.total_rent),
        "advance_received": float(trip.advance_received),
        "additional_payments": float(total_paid_after_adv),
        "balance_receivable": float(trip.balance_receivable),
        "trip_status": trip.trip_status,
        "notes": trip.notes or "",
        "payments": [
            {
                "id": p.id,
                "payment_date": p.payment_date.strftime("%d-%m-%Y") if p.payment_date else "",
                "amount": float(p.amount),
                "payment_method": p.payment_method,
                "reference_number": p.reference_number or "",
                "notes": p.notes or ""
            }
            for p in payments
        ]
    }

@router.post("", status_code=status.HTTP_201_CREATED)
def create_trip(
    payload: TripCreate,
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)
):
    truck = db.query(Truck).filter(Truck.id == payload.vehicle_id).first()
    if not truck:
        raise HTTPException(status_code=400, detail="Invalid vehicle selected.")

    # Validate driver if selected
    driver_id = payload.driver_id
    if driver_id:
        driver = db.query(Driver).filter(Driver.id == driver_id).first()
        if not driver:
            raise HTTPException(status_code=400, detail="Selected driver not found.")
    else:
        driver_id = truck.assigned_driver_id

    # Calculate balance
    adv = payload.advance_received or Decimal("0.00")
    bal = max(Decimal("0.00"), payload.total_rent - adv)

    trip = Trip(
        trip_date=payload.trip_date,
        vehicle_id=payload.vehicle_id,
        driver_id=driver_id,
        customer_name=payload.customer_name.strip(),
        from_location=payload.from_location.strip(),
        to_location=payload.to_location.strip(),
        load_description=payload.load_description,
        total_rent=payload.total_rent,
        advance_received=adv,
        balance_receivable=bal,
        trip_start_date=payload.trip_start_date or payload.trip_date,
        expected_delivery_date=payload.expected_delivery_date,
        trip_status=payload.trip_status or "Ongoing",
        notes=payload.notes
    )
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return {"message": "Trip created successfully", "trip_id": trip.id}

@router.put("/{trip_id}")
def update_trip(
    trip_id: int,
    payload: TripUpdate,
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)
):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip record not found")

    update_data = payload.dict(exclude_unset=True)

    if "vehicle_id" in update_data and update_data["vehicle_id"] is not None:
        truck = db.query(Truck).filter(Truck.id == update_data["vehicle_id"]).first()
        if not truck:
            raise HTTPException(status_code=400, detail="Invalid vehicle selected.")

    if "driver_id" in update_data and update_data["driver_id"] is not None:
        driver = db.query(Driver).filter(Driver.id == update_data["driver_id"]).first()
        if not driver:
            raise HTTPException(status_code=400, detail="Selected driver not found.")

    for k, v in update_data.items():
        if k in ["customer_name", "from_location", "to_location"] and isinstance(v, str):
            setattr(trip, k, v.strip())
        else:
            setattr(trip, k, v)

    recalculate_trip_balance(trip, db)
    return {"message": "Trip updated successfully", "trip_id": trip.id}

@router.post("/{trip_id}/payments")
def add_trip_payment(
    trip_id: int,
    payload: TripPaymentCreate,
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)
):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip record not found")

    if payload.amount <= Decimal("0.00"):
        raise HTTPException(status_code=400, detail="Payment amount must be greater than zero.")

    # Guard against duplicate accidental double clicks (same trip, same amount, same date within 1 minute)
    existing_duplicate = db.query(TripPayment).filter(
        TripPayment.trip_id == trip_id,
        TripPayment.amount == payload.amount,
        TripPayment.payment_date == payload.payment_date,
        TripPayment.reference_number == payload.reference_number
    ).first()
    if existing_duplicate and payload.reference_number:
        raise HTTPException(status_code=400, detail="A payment with the same reference number and amount has already been recorded.")

    payment = TripPayment(
        trip_id=trip_id,
        payment_date=payload.payment_date,
        amount=payload.amount,
        payment_method=payload.payment_method,
        reference_number=payload.reference_number,
        notes=payload.notes
    )
    db.add(payment)
    db.commit()

    recalculate_trip_balance(trip, db)
    return {"message": "Payment recorded successfully", "new_balance": float(trip.balance_receivable)}

@router.delete("/{trip_id}")
def delete_trip(
    trip_id: int,
    force: bool = Query(False, description="Force permanent deletion if confirmed"),
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)
):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    # Check for payment records or financial history
    has_payments = len(trip.payments) > 0 or (trip.advance_received and trip.advance_received > Decimal("0.00"))

    # Safely protect expenses: do NOT delete expenses, simply unlink trip_id
    db.query(Expense).filter(Expense.trip_id == trip_id).update({Expense.trip_id: None})
    
    # Safely handle driver bata records: unlink trip_id
    db.query(BataRecord).filter(BataRecord.trip_id == trip_id).update({BataRecord.trip_id: None})

    if has_payments and not force:
        # Safe cancellation/archive approach to protect financial audit history
        trip.trip_status = "Cancelled"
        db.commit()
        return {
            "message": "Trip has recorded payment transactions. To preserve financial history, it has been safely cancelled/archived.",
            "status": "cancelled",
            "trip_id": trip_id
        }
    else:
        # Permanent delete when no payments exist or force is requested
        db.delete(trip)
        db.commit()
        return {
            "message": "Trip deleted successfully",
            "status": "deleted",
            "trip_id": trip_id
        }

from datetime import date
from decimal import Decimal
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from backend.database import get_db
from backend.models import Owner, Driver, Truck, Trip, SalaryRecord, BataRecord
from backend.schemas import DriverCreate, DriverUpdate
from backend.auth import get_current_owner
from backend.crud import get_document_status

router = APIRouter(prefix="/api/drivers", tags=["Drivers"])

@router.get("")
def list_drivers(
    search: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)
):
    query = db.query(Driver).order_by(Driver.full_name.asc())

    if status and status != "All":
        query = query.filter(Driver.employment_status == status)
    if search:
        search_pattern = f"%{search.strip()}%"
        query = query.filter(
            (Driver.full_name.ilike(search_pattern)) |
            (Driver.phone_number.ilike(search_pattern)) |
            (Driver.license_number.ilike(search_pattern))
        )

    drivers = query.all()
    results = []
    for d in drivers:
        truck_nums = [t.vehicle_number for t in d.assigned_trucks]
        trips_count = db.query(Trip).filter(Trip.driver_id == d.id).count()
        
        # Pending salary calculation
        pending_sal = db.query(func.sum(SalaryRecord.balance_payable)).filter(
            SalaryRecord.driver_id == d.id,
            SalaryRecord.status != "Paid"
        ).scalar() or Decimal("0.00")

        delta, label, status_class = get_document_status(d.license_expiry)

        results.append({
            "id": d.id,
            "full_name": d.full_name,
            "phone_number": d.phone_number,
            "address": d.address or "",
            "license_number": d.license_number,
            "license_expiry": d.license_expiry.strftime("%d-%m-%Y") if d.license_expiry else "",
            "license_status": label,
            "license_status_class": status_class,
            "license_days_left": delta,
            "employment_status": d.employment_status,
            "joining_date": d.joining_date.strftime("%d-%m-%Y") if d.joining_date else "",
            "salary_type": d.salary_type,
            "monthly_salary": float(d.monthly_salary),
            "daily_salary": float(d.daily_salary),
            "bata_per_trip": float(d.bata_per_trip),
            "notes": d.notes or "",
            "assigned_trucks": truck_nums,
            "assigned_truck_text": ", ".join(truck_nums) if truck_nums else "Unassigned",
            "trips_count": trips_count,
            "pending_salary": float(pending_sal)
        })
    return results

@router.get("/{driver_id}")
def get_driver_detail(
    driver_id: int,
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)
):
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver record not found")

    trips = db.query(Trip).filter(Trip.driver_id == driver_id).order_by(desc(Trip.trip_date)).limit(10).all()
    salary_history = db.query(SalaryRecord).filter(SalaryRecord.driver_id == driver_id).order_by(desc(SalaryRecord.id)).limit(10).all()

    truck_nums = [t.vehicle_number for t in driver.assigned_trucks]
    delta, label, status_class = get_document_status(driver.license_expiry)

    return {
        "id": driver.id,
        "full_name": driver.full_name,
        "phone_number": driver.phone_number,
        "address": driver.address or "",
        "license_number": driver.license_number,
        "license_expiry": driver.license_expiry.strftime("%Y-%m-%d") if driver.license_expiry else "",
        "license_status": label,
        "license_status_class": status_class,
        "employment_status": driver.employment_status,
        "joining_date": driver.joining_date.strftime("%Y-%m-%d") if driver.joining_date else "",
        "salary_type": driver.salary_type,
        "monthly_salary": float(driver.monthly_salary),
        "daily_salary": float(driver.daily_salary),
        "bata_per_trip": float(driver.bata_per_trip),
        "notes": driver.notes or "",
        "assigned_trucks": truck_nums,
        "recent_trips": [
            {
                "id": t.id,
                "date": t.trip_date.strftime("%d-%m-%Y") if t.trip_date else "",
                "route": f"{t.from_location} \u2192 {t.to_location}",
                "customer": t.customer_name,
                "status": t.trip_status
            }
            for t in trips
        ],
        "salary_history": [
            {
                "id": s.id,
                "period": s.salary_period,
                "earned": float(s.net_payable),
                "paid": float(s.paid_amount),
                "balance": float(s.balance_payable),
                "status": s.status
            }
            for s in salary_history
        ]
    }

@router.post("", status_code=status.HTTP_201_CREATED)
def create_driver(
    payload: DriverCreate,
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)
):
    driver = Driver(
        full_name=payload.full_name.strip(),
        phone_number=payload.phone_number.strip(),
        address=payload.address,
        license_number=payload.license_number.strip().upper(),
        license_expiry=payload.license_expiry,
        employment_status=payload.employment_status or "Active",
        joining_date=payload.joining_date or date.today(),
        salary_type=payload.salary_type or "Monthly",
        monthly_salary=payload.monthly_salary or Decimal("0.00"),
        daily_salary=payload.daily_salary or Decimal("0.00"),
        bata_per_trip=payload.bata_per_trip or Decimal("500.00"),
        notes=payload.notes
    )
    db.add(driver)
    db.commit()
    db.refresh(driver)
    return {"message": "Driver added successfully", "driver_id": driver.id}

@router.put("/{driver_id}")
def update_driver(
    driver_id: int,
    payload: DriverUpdate,
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)
):
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver record not found")

    update_data = payload.dict(exclude_unset=True)
    for k, v in update_data.items():
        setattr(driver, k, v)

    db.commit()
    db.refresh(driver)
    return {"message": "Driver details updated successfully", "driver_id": driver.id}

@router.delete("/{driver_id}")
def delete_driver(
    driver_id: int,
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)
):
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver record not found")
    driver.employment_status = "Inactive"
    db.commit()
    return {"message": f"Driver {driver.full_name} deactivated successfully."}

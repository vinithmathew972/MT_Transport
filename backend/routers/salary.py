from datetime import date
from decimal import Decimal
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.database import get_db
from backend.models import Owner, Driver, SalaryRecord, SalaryPayment, BataRecord
from backend.schemas import SalaryRecordCreate, SalaryPayoutCreate, BataRecordCreate
from backend.auth import get_current_owner

router = APIRouter(prefix="/api/salary", tags=["Salary & Bata"])

@router.get("/records")
def list_salary_records(
    driver_id: Optional[int] = None,
    period: Optional[str] = None,
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)
):
    query = db.query(SalaryRecord).order_by(desc(SalaryRecord.id))
    if driver_id:
        query = query.filter(SalaryRecord.driver_id == driver_id)
    if period:
        query = query.filter(SalaryRecord.salary_period == period)

    records = query.all()
    results = []
    for r in records:
        results.append({
            "id": r.id,
            "driver_id": r.driver_id,
            "driver_name": r.driver.full_name if r.driver else "N/A",
            "salary_period": r.salary_period,
            "days_worked": r.days_worked,
            "base_salary_earned": float(r.base_salary_earned),
            "bata_earned": float(r.bata_earned),
            "allowance": float(r.allowance),
            "advance_deduction": float(r.advance_deduction),
            "other_deductions": float(r.other_deductions),
            "net_payable": float(r.net_payable),
            "paid_amount": float(r.paid_amount),
            "balance_payable": float(r.balance_payable),
            "status": r.status,
            "notes": r.notes or ""
        })
    return results

@router.post("/calculate")
def calculate_salary_statement(
    payload: SalaryRecordCreate,
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)
):
    driver = db.query(Driver).filter(Driver.id == payload.driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    # Compute base salary based on salary type
    if driver.salary_type == "Daily":
        rate = payload.base_salary_rate or driver.daily_salary
        base_earned = rate * Decimal(payload.days_worked)
    else:
        rate = payload.base_salary_rate or driver.monthly_salary
        # Pro-rated for 30-day month
        base_earned = (rate / Decimal("30.00")) * Decimal(payload.days_worked) if payload.days_worked < 30 else rate

    total_gross = base_earned + payload.bata_earned + payload.allowance
    total_deductions = payload.advance_deduction + payload.other_deductions
    net = max(Decimal("0.00"), total_gross - total_deductions)

    record = SalaryRecord(
        driver_id=payload.driver_id,
        salary_period=payload.salary_period,
        start_date=payload.start_date,
        end_date=payload.end_date,
        days_worked=payload.days_worked,
        base_salary_rate=rate,
        base_salary_earned=base_earned,
        bata_earned=payload.bata_earned,
        allowance=payload.allowance,
        advance_deduction=payload.advance_deduction,
        other_deductions=payload.other_deductions,
        net_payable=net,
        paid_amount=Decimal("0.00"),
        balance_payable=net,
        status="Pending",
        notes=payload.notes
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return {"message": "Salary calculated and statement generated", "record_id": record.id, "net_payable": float(net)}

@router.post("/payments")
def record_salary_payout(
    payload: SalaryPayoutCreate,
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)
):
    if payload.amount <= Decimal("0.00"):
        raise HTTPException(status_code=400, detail="Payout amount must be greater than zero.")

    payment = SalaryPayment(
        salary_record_id=payload.salary_record_id,
        driver_id=payload.driver_id,
        payment_date=payload.payment_date,
        amount=payload.amount,
        payment_method=payload.payment_method,
        payment_type=payload.payment_type,
        reference_number=payload.reference_number,
        notes=payload.notes
    )
    db.add(payment)

    # If linked to a salary record, adjust its balance
    if payload.salary_record_id:
        record = db.query(SalaryRecord).filter(SalaryRecord.id == payload.salary_record_id).first()
        if record:
            record.paid_amount += payload.amount
            record.balance_payable = max(Decimal("0.00"), record.net_payable - record.paid_amount)
            if record.balance_payable == Decimal("0.00"):
                record.status = "Paid"
            else:
                record.status = "Partially Paid"

    db.commit()
    return {"message": "Salary payment recorded successfully"}

@router.get("/bata")
def list_bata_records(
    driver_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)
):
    query = db.query(BataRecord).order_by(desc(BataRecord.date), desc(BataRecord.id))
    if driver_id:
        query = query.filter(BataRecord.driver_id == driver_id)

    records = query.all()
    results = []
    for b in records:
        results.append({
            "id": b.id,
            "driver_id": b.driver_id,
            "driver_name": b.driver.full_name if b.driver else "N/A",
            "trip_id": b.trip_id,
            "date": b.date.strftime("%d-%m-%Y") if b.date else "",
            "amount": float(b.amount),
            "status": b.status,
            "notes": b.notes or ""
        })
    return results

@router.post("/bata")
def add_bata_record(
    payload: BataRecordCreate,
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)
):
    bata = BataRecord(
        driver_id=payload.driver_id,
        trip_id=payload.trip_id,
        date=payload.date,
        amount=payload.amount,
        status=payload.status or "Pending",
        notes=payload.notes
    )
    db.add(bata)
    db.commit()
    db.refresh(bata)
    return {"message": "Bata recorded successfully", "id": bata.id}

@router.put("/bata/{bata_id}/pay")
def pay_bata(
    bata_id: int,
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)
):
    bata = db.query(BataRecord).filter(BataRecord.id == bata_id).first()
    if not bata:
        raise HTTPException(status_code=404, detail="Bata record not found")
    bata.status = "Paid"
    db.commit()
    return {"message": "Bata marked as paid"}

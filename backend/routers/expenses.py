import csv
import io
from datetime import date
from decimal import Decimal
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.database import get_db
from backend.models import Owner, Expense, Truck, Trip
from backend.schemas import ExpenseCreate, ExpenseUpdate
from backend.auth import get_current_owner

router = APIRouter(prefix="/api/expenses", tags=["Expenses"])

EXPENSE_CATEGORIES = [
    "Diesel",
    "Toll",
    "Driver Bata",
    "Loading/Unloading",
    "Repair & Maintenance",
    "Insurance",
    "Permit & FC",
    "Road Tax",
    "Other"
]

@router.get("/categories")
def get_categories():
    return EXPENSE_CATEGORIES

@router.get("")
def list_expenses(
    category: Optional[str] = None,
    truck_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)
):
    query = db.query(Expense).order_by(desc(Expense.date), desc(Expense.id))

    if category and category != "All":
        query = query.filter(Expense.category == category)
    if truck_id:
        query = query.filter(Expense.vehicle_id == truck_id)
    if date_from:
        query = query.filter(Expense.date >= date_from)
    if date_to:
        query = query.filter(Expense.date <= date_to)
    if search:
        search_pattern = f"%{search.strip()}%"
        query = query.filter(
            (Expense.paid_to.ilike(search_pattern)) |
            (Expense.description.ilike(search_pattern))
        )

    expenses = query.all()
    results = []
    for e in expenses:
        results.append({
            "id": e.id,
            "date": e.date.strftime("%d-%m-%Y") if e.date else "",
            "raw_date": e.date.strftime("%Y-%m-%d") if e.date else "",
            "vehicle_id": e.vehicle_id,
            "vehicle_number": e.truck.vehicle_number if e.truck else "General/Office",
            "trip_id": e.trip_id,
            "category": e.category,
            "amount": float(e.amount),
            "paid_to": e.paid_to or "",
            "payment_method": e.payment_method or "Cash",
            "description": e.description or ""
        })
    return results

@router.post("", status_code=status.HTTP_201_CREATED)
def create_expense(
    payload: ExpenseCreate,
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)
):
    if payload.amount <= Decimal("0.00"):
        raise HTTPException(status_code=400, detail="Expense amount must be greater than zero.")

    expense = Expense(
        date=payload.date,
        vehicle_id=payload.vehicle_id,
        trip_id=payload.trip_id,
        category=payload.category,
        amount=payload.amount,
        paid_to=payload.paid_to,
        payment_method=payload.payment_method,
        description=payload.description
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return {"message": "Expense recorded successfully", "expense_id": expense.id}

@router.put("/{expense_id}")
def update_expense(
    expense_id: int,
    payload: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)
):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense record not found")

    update_data = payload.dict(exclude_unset=True)
    for k, v in update_data.items():
        setattr(expense, k, v)

    db.commit()
    db.refresh(expense)
    return {"message": "Expense updated successfully", "expense_id": expense.id}

@router.delete("/{expense_id}")
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)
):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense record not found")
    db.delete(expense)
    db.commit()
    return {"message": "Expense deleted successfully"}

@router.get("/export/csv")
def export_expenses_csv(
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)
):
    expenses = db.query(Expense).order_by(desc(Expense.date)).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Expense ID", "Date", "Vehicle Number", "Category",
        "Amount (INR)", "Paid To", "Payment Method", "Description"
    ])

    for e in expenses:
        writer.writerow([
            e.id,
            e.date.strftime("%d-%m-%Y") if e.date else "",
            e.truck.vehicle_number if e.truck else "General",
            e.category,
            f"{e.amount:.2f}",
            e.paid_to or "",
            e.payment_method or "",
            e.description or ""
        ])

    csv_data = output.getvalue()
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=Mother_Theresa_Transport_Expenses.csv"}
    )

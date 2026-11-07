import csv
import io
from datetime import date
from decimal import Decimal
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from backend.database import get_db
from backend.models import Owner, Truck, Driver, Customer, Trip, Expense, SalaryRecord
from backend.auth import get_current_owner

router = APIRouter(prefix="/api/reports", tags=["Reports"])

@router.get("/vehicle-pl")
def get_vehicle_pl_report(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)
):
    trucks = db.query(Truck).all()
    results = []

    for t in trucks:
        trips_q = db.query(Trip).filter(Trip.vehicle_id == t.id)
        exp_q = db.query(Expense).filter(Expense.vehicle_id == t.id)

        if date_from:
            trips_q = trips_q.filter(Trip.trip_date >= date_from)
            exp_q = exp_q.filter(Expense.date >= date_from)
        if date_to:
            trips_q = trips_q.filter(Trip.trip_date <= date_to)
            exp_q = exp_q.filter(Expense.date <= date_to)

        trips_count = trips_q.count()
        total_income = trips_q.with_entities(func.sum(Trip.total_rent)).scalar() or Decimal("0.00")
        total_expenses = exp_q.with_entities(func.sum(Expense.amount)).scalar() or Decimal("0.00")
        net_profit = total_income - total_expenses
        margin = round(float((net_profit / total_income) * 100), 1) if total_income > 0 else 0.0

        results.append({
            "truck_id": t.id,
            "vehicle_number": t.vehicle_number,
            "make_model": t.make_model,
            "driver_name": t.assigned_driver.full_name if t.assigned_driver else "Unassigned",
            "trips_count": trips_count,
            "total_income": float(total_income),
            "total_expenses": float(total_expenses),
            "net_profit": float(net_profit),
            "margin_percentage": margin
        })
    return results

@router.get("/customer-outstanding")
def get_customer_outstanding_report(
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)
):
    customers = db.query(Customer).all()
    results = []

    for c in customers:
        trips = db.query(Trip).filter(Trip.customer_id == c.id).all()
        total_rent = sum((t.total_rent for t in trips), Decimal("0.00"))
        balance = sum((t.balance_receivable for t in trips), Decimal("0.00"))
        paid = total_rent - balance

        results.append({
            "customer_id": c.id,
            "name": c.name,
            "company_name": c.company_name or "",
            "phone": c.phone or "",
            "total_trips": len(trips),
            "total_billed": float(total_rent),
            "total_paid": float(paid),
            "outstanding_balance": float(balance)
        })
    return results

@router.get("/fuel")
def get_fuel_report(
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)
):
    trucks = db.query(Truck).all()
    results = []

    for t in trucks:
        fuel_expenses = db.query(Expense).filter(
            Expense.vehicle_id == t.id,
            Expense.category.ilike("%diesel%") | Expense.category.ilike("%fuel%")
        ).all()
        total_fuel = sum((e.amount for e in fuel_expenses), Decimal("0.00"))
        trips_count = db.query(Trip).filter(Trip.vehicle_id == t.id).count()

        results.append({
            "vehicle_id": t.id,
            "vehicle_number": t.vehicle_number,
            "total_fuel_cost": float(total_fuel),
            "refills_count": len(fuel_expenses),
            "trips_count": trips_count,
            "avg_fuel_per_trip": round(float(total_fuel / trips_count), 2) if trips_count > 0 else 0.0
        })
    return results

@router.get("/export/{report_type}")
def export_report_csv(
    report_type: str,
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)
):
    output = io.StringIO()
    writer = csv.writer(output)

    if report_type == "vehicle-pl":
        writer.writerow(["Vehicle Number", "Model", "Driver", "Trips", "Total Income (INR)", "Total Expenses (INR)", "Net Profit (INR)", "Margin %"])
        trucks = db.query(Truck).all()
        for t in trucks:
            trips_q = db.query(Trip).filter(Trip.vehicle_id == t.id)
            exp_q = db.query(Expense).filter(Expense.vehicle_id == t.id)
            inc = trips_q.with_entities(func.sum(Trip.total_rent)).scalar() or Decimal("0.00")
            exp = exp_q.with_entities(func.sum(Expense.amount)).scalar() or Decimal("0.00")
            net = inc - exp
            margin = round(float((net / inc) * 100), 1) if inc > 0 else 0.0
            writer.writerow([t.vehicle_number, t.make_model, t.assigned_driver.full_name if t.assigned_driver else "", trips_q.count(), f"{inc:.2f}", f"{exp:.2f}", f"{net:.2f}", f"{margin}%"])

    elif report_type == "customer-outstanding":
        writer.writerow(["Customer Name", "Company", "Phone", "Trips Count", "Total Billed (INR)", "Paid (INR)", "Outstanding (INR)"])
        customers = db.query(Customer).all()
        for c in customers:
            trips = db.query(Trip).filter(Trip.customer_id == c.id).all()
            total_rent = sum((t.total_rent for t in trips), Decimal("0.00"))
            balance = sum((t.balance_receivable for t in trips), Decimal("0.00"))
            writer.writerow([c.name, c.company_name or "", c.phone or "", len(trips), f"{total_rent:.2f}", f"{total_rent-balance:.2f}", f"{balance:.2f}"])

    elif report_type == "fuel":
        writer.writerow(["Vehicle Number", "Total Fuel Cost (INR)", "Refills Count", "Trips Count"])
        trucks = db.query(Truck).all()
        for t in trucks:
            fuel_expenses = db.query(Expense).filter(
                Expense.vehicle_id == t.id,
                Expense.category.ilike("%diesel%") | Expense.category.ilike("%fuel%")
            ).all()
            total_fuel = sum((e.amount for e in fuel_expenses), Decimal("0.00"))
            trips_count = db.query(Trip).filter(Trip.vehicle_id == t.id).count()
            writer.writerow([t.vehicle_number, f"{total_fuel:.2f}", len(fuel_expenses), trips_count])

    else:
        raise HTTPException(status_code=400, detail="Invalid report type.")

    csv_data = output.getvalue()
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=MT_Transport_Report_{report_type}.csv"}
    )

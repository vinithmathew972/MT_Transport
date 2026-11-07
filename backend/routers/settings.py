from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Owner, CompanySettings, Truck, Driver, Customer, Trip, Expense
from backend.schemas import CompanySettingsSchema, OwnerProfile, OwnerProfileUpdate
from backend.auth import get_current_owner

router = APIRouter(prefix="/api/settings", tags=["Settings"])

@router.get("/profile", response_model=OwnerProfile)
def get_owner_profile(
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)
):
    company = db.query(CompanySettings).first()
    return OwnerProfile(
        id=current_owner.id,
        username=current_owner.username,
        full_name=current_owner.full_name or "Owner",
        phone=current_owner.phone or (company.phone if company else ""),
        email=current_owner.email or (company.email if company else ""),
        company_name=company.company_name if company else "Mother Theresa Transport"
    )

@router.put("/profile", response_model=OwnerProfile)
def update_owner_profile(
    payload: OwnerProfileUpdate,
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)
):
    if payload.full_name is not None:
        current_owner.full_name = payload.full_name.strip()
    if payload.phone is not None:
        current_owner.phone = payload.phone.strip()
    if payload.email is not None:
        current_owner.email = payload.email.strip()

    company = db.query(CompanySettings).first()
    if payload.company_name is not None:
        if not company:
            company = CompanySettings(company_name=payload.company_name.strip())
            db.add(company)
        else:
            company.company_name = payload.company_name.strip()

    if company:
        if payload.phone is not None:
            company.phone = payload.phone.strip()
        if payload.email is not None:
            company.email = payload.email.strip()

    db.commit()
    db.refresh(current_owner)
    if company:
        db.refresh(company)

    return OwnerProfile(
        id=current_owner.id,
        username=current_owner.username,
        full_name=current_owner.full_name or "Owner",
        phone=current_owner.phone or "",
        email=current_owner.email or "",
        company_name=company.company_name if company else ""
    )

@router.get("", response_model=CompanySettingsSchema)
def get_settings(
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)
):
    settings = db.query(CompanySettings).first()
    if not settings:
        settings = CompanySettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings

@router.put("", response_model=CompanySettingsSchema)
def update_settings(
    payload: CompanySettingsSchema,
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)
):
    settings = db.query(CompanySettings).first()
    if not settings:
        settings = CompanySettings()
        db.add(settings)

    for k, v in payload.dict().items():
        setattr(settings, k, v)

    db.commit()
    db.refresh(settings)
    return settings

@router.get("/backup")
def export_database_backup(
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)
):
    trucks = [
        {"id": t.id, "vehicle_number": t.vehicle_number, "make_model": t.make_model, "fc_exp": str(t.fc_expiry)}
        for t in db.query(Truck).all()
    ]
    drivers = [
        {"id": d.id, "name": d.full_name, "phone": d.phone_number, "license": d.license_number}
        for d in db.query(Driver).all()
    ]
    trips = [
        {"id": tr.id, "date": str(tr.trip_date), "route": f"{tr.from_location} to {tr.to_location}", "rent": float(tr.total_rent)}
        for tr in db.query(Trip).all()
    ]
    expenses = [
        {"id": e.id, "date": str(e.date), "cat": e.category, "amt": float(e.amount)}
        for e in db.query(Expense).all()
    ]

    return {
        "company": "Mother Theresa Transport",
        "export_timestamp": str(db.query(CompanySettings).first().updated_at if db.query(CompanySettings).first() else ""),
        "trucks_count": len(trucks),
        "drivers_count": len(drivers),
        "trips_count": len(trips),
        "expenses_count": len(expenses),
        "data": {
            "trucks": trucks,
            "drivers": drivers,
            "trips": trips,
            "expenses": expenses
        }
    }

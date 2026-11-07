from datetime import date, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.database import get_db
from backend.models import Owner, VehicleDocument, Truck
from backend.schemas import VehicleDocumentCreate
from backend.auth import get_current_owner
from backend.crud import get_document_status

router = APIRouter(prefix="/api/documents", tags=["Documents & Reminders"])

@router.get("")
def list_documents(
    truck_id: Optional[int] = None,
    document_type: Optional[str] = None,
    status_filter: Optional[str] = None, # "expired", "expiring_soon", "valid"
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)
):
    query = db.query(VehicleDocument).join(Truck).order_by(VehicleDocument.expiry_date.asc())

    if truck_id:
        query = query.filter(VehicleDocument.vehicle_id == truck_id)
    if document_type and document_type != "All":
        query = query.filter(VehicleDocument.document_type == document_type)

    docs = query.all()
    results = []
    today = date.today()

    for d in docs:
        delta, label, status_class = get_document_status(d.expiry_date)
        
        # Apply status filter
        if status_filter == "expired" and delta >= 0:
            continue
        elif status_filter == "expiring_soon" and (delta < 0 or delta > 30):
            continue
        elif status_filter == "valid" and delta <= 30:
            continue

        results.append({
            "id": d.id,
            "vehicle_id": d.vehicle_id,
            "vehicle_number": d.truck.vehicle_number if d.truck else "N/A",
            "document_type": d.document_type,
            "document_number": d.document_number or "",
            "issue_date": d.issue_date.strftime("%d-%m-%Y") if d.issue_date else "",
            "expiry_date": d.expiry_date.strftime("%d-%m-%Y") if d.expiry_date else "",
            "raw_expiry": d.expiry_date.strftime("%Y-%m-%d") if d.expiry_date else "",
            "days_remaining": delta,
            "status_label": label,
            "status_class": status_class,
            "notes": d.notes or ""
        })
    return results

@router.post("", status_code=status.HTTP_201_CREATED)
def add_document(
    payload: VehicleDocumentCreate,
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)
):
    truck = db.query(Truck).filter(Truck.id == payload.vehicle_id).first()
    if not truck:
        raise HTTPException(status_code=400, detail="Invalid truck specified.")

    doc = VehicleDocument(
        vehicle_id=payload.vehicle_id,
        document_type=payload.document_type,
        document_number=payload.document_number,
        issue_date=payload.issue_date,
        expiry_date=payload.expiry_date,
        notes=payload.notes
    )
    db.add(doc)
    
    # Update truck specific field if applicable
    doc_lower = payload.document_type.lower()
    if "fc" in doc_lower:
        truck.fc_expiry = payload.expiry_date
    elif "insurance" in doc_lower:
        truck.insurance_expiry = payload.expiry_date
        if payload.document_number:
            truck.insurance_policy_number = payload.document_number
    elif "national" in doc_lower:
        truck.national_permit_expiry = payload.expiry_date
    elif "permit" in doc_lower:
        truck.permit_expiry = payload.expiry_date
        if payload.document_number:
            truck.permit_number = payload.document_number
    elif "puc" in doc_lower:
        truck.puc_expiry = payload.expiry_date
    elif "tax" in doc_lower:
        truck.road_tax_expiry = payload.expiry_date

    db.commit()
    db.refresh(doc)
    return {"message": "Document record added successfully", "id": doc.id}

@router.delete("/{doc_id}")
def delete_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_owner: Owner = Depends(get_current_owner)
):
    doc = db.query(VehicleDocument).filter(VehicleDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(doc)
    db.commit()
    return {"message": "Document removed successfully"}

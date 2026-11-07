from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Owner, CompanySettings
from backend.schemas import LoginRequest, TokenResponse, OwnerProfile, OwnerProfileUpdate
from backend.auth import verify_password, create_access_token, hash_password, get_current_owner

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    owner = db.query(Owner).filter(Owner.username == payload.username.strip(), Owner.is_active == True).first()
    if not owner or not verify_password(payload.password, owner.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password. Please verify credentials."
        )
    
    access_token = create_access_token(data={"sub": owner.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "owner_name": owner.full_name or "Owner",
        "username": owner.username
    }

@router.get("/me", response_model=OwnerProfile)
@router.get("/profile", response_model=OwnerProfile)
def get_profile(
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
def update_profile(
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

    if payload.new_password:
        if not payload.current_password or not verify_password(payload.current_password, current_owner.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is required and must be correct to set a new password."
            )
        current_owner.hashed_password = hash_password(payload.new_password)

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

@router.post("/logout")
def logout():
    return {"message": "Logged out successfully"}

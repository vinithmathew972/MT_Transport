from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Date, DateTime, 
    Numeric, ForeignKey, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from backend.database import Base

class Owner(Base):
    __tablename__ = "owners"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(150), default="Transport Owner")
    phone = Column(String(20), nullable=True)
    email = Column(String(120), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CompanySettings(Base):
    __tablename__ = "company_settings"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(200), default="Mother Theresa Transport")
    tagline = Column(String(255), default="Safe Journey... Stronger Tomorrow...")
    phone = Column(String(50), default="+91 98765 43210")
    email = Column(String(120), default="contact@mothertheresatransport.com")
    address = Column(Text, default="Transport Nagar, Salem, Tamil Nadu, India")
    currency = Column(String(10), default="₹")
    date_format = Column(String(20), default="DD/MM/YYYY")
    reminder_days_json = Column(String(100), default="[30, 15, 7]")
    salary_rules_json = Column(Text, default='{"default_bata": 500, "overtime_rate": 100}')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Truck(Base):
    __tablename__ = "trucks"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_number = Column(String(50), unique=True, index=True, nullable=False)
    make_model = Column(String(100), default="TATA LPT 3118")
    vehicle_type = Column(String(50), default="12 Wheeler Container")
    registration_date = Column(Date, nullable=True)
    assigned_driver_id = Column(Integer, ForeignKey("drivers.id", ondelete="SET NULL"), nullable=True)
    
    # Document Reference numbers and Expiry dates
    permit_number = Column(String(100), nullable=True)
    permit_expiry = Column(Date, nullable=True)
    national_permit_expiry = Column(Date, nullable=True)
    insurance_policy_number = Column(String(100), nullable=True)
    insurance_expiry = Column(Date, nullable=True)
    fc_expiry = Column(Date, nullable=True)
    puc_expiry = Column(Date, nullable=True)
    road_tax_expiry = Column(Date, nullable=True)
    
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assigned_driver = relationship("Driver", foreign_keys=[assigned_driver_id], back_populates="assigned_trucks")
    trips = relationship("Trip", back_populates="truck", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="truck")
    documents = relationship("VehicleDocument", back_populates="truck", cascade="all, delete-orphan")


class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False)
    phone_number = Column(String(30), nullable=False)
    address = Column(Text, nullable=True)
    license_number = Column(String(80), nullable=False)
    license_expiry = Column(Date, nullable=True)
    employment_status = Column(String(30), default="Active")  # Active, Inactive, On Leave
    joining_date = Column(Date, nullable=True)
    salary_type = Column(String(50), default="Monthly")       # Monthly, Daily, Trip Bata
    monthly_salary = Column(Numeric(12, 2), default=Decimal("0.00"))
    daily_salary = Column(Numeric(12, 2), default=Decimal("0.00"))
    bata_per_trip = Column(Numeric(12, 2), default=Decimal("500.00"))
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assigned_trucks = relationship("Truck", foreign_keys=[Truck.assigned_driver_id], back_populates="assigned_driver")
    trips = relationship("Trip", back_populates="driver")
    salary_records = relationship("SalaryRecord", back_populates="driver", cascade="all, delete-orphan")
    salary_payments = relationship("SalaryPayment", back_populates="driver", cascade="all, delete-orphan")
    bata_records = relationship("BataRecord", back_populates="driver", cascade="all, delete-orphan")


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    company_name = Column(String(150), nullable=True)
    phone = Column(String(30), nullable=True)
    email = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    gstin = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    trips = relationship("Trip", back_populates="customer")


class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    trip_date = Column(Date, nullable=False, default=date.today)
    vehicle_id = Column(Integer, ForeignKey("trucks.id", ondelete="RESTRICT"), nullable=False)
    driver_id = Column(Integer, ForeignKey("drivers.id", ondelete="SET NULL"), nullable=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="SET NULL"), nullable=True)
    customer_name = Column(String(150), nullable=False)
    from_location = Column(String(150), nullable=False)
    to_location = Column(String(150), nullable=False)
    load_description = Column(String(255), nullable=True)
    
    total_rent = Column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    advance_received = Column(Numeric(12, 2), default=Decimal("0.00"))
    balance_receivable = Column(Numeric(12, 2), default=Decimal("0.00"))
    
    trip_start_date = Column(Date, nullable=True)
    expected_delivery_date = Column(Date, nullable=True)
    actual_delivery_date = Column(Date, nullable=True)
    trip_status = Column(String(30), default="Ongoing") # Planned, Ongoing, Delivered, Completed, Cancelled
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    truck = relationship("Truck", back_populates="trips")
    driver = relationship("Driver", back_populates="trips")
    customer = relationship("Customer", back_populates="trips")
    payments = relationship("TripPayment", back_populates="trip", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="trip")


class TripPayment(Base):
    __tablename__ = "trip_payments"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id", ondelete="CASCADE"), nullable=False)
    payment_date = Column(Date, default=date.today, nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    payment_method = Column(String(50), default="Bank Transfer") # Cash, Bank Transfer, UPI, Cheque
    reference_number = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    trip = relationship("Trip", back_populates="payments")


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, default=date.today, nullable=False)
    vehicle_id = Column(Integer, ForeignKey("trucks.id", ondelete="SET NULL"), nullable=True)
    trip_id = Column(Integer, ForeignKey("trips.id", ondelete="SET NULL"), nullable=True)
    category = Column(String(60), nullable=False) # Diesel, Toll, Driver Bata, Loading/Unloading, Repair & Maintenance, Insurance, Permit & FC, Road Tax, Other
    amount = Column(Numeric(12, 2), nullable=False)
    paid_to = Column(String(150), nullable=True)
    payment_method = Column(String(50), default="Cash") # Cash, UPI, Card, Net Banking
    description = Column(Text, nullable=True)
    receipt_attachment = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    truck = relationship("Truck", back_populates="expenses")
    trip = relationship("Trip", back_populates="expenses")


class SalaryRecord(Base):
    __tablename__ = "salary_records"

    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey("drivers.id", ondelete="CASCADE"), nullable=False)
    salary_period = Column(String(30), nullable=False) # e.g. "October 2026" or "2026-10"
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    days_worked = Column(Integer, default=30)
    base_salary_rate = Column(Numeric(12, 2), default=Decimal("0.00"))
    base_salary_earned = Column(Numeric(12, 2), default=Decimal("0.00"))
    bata_earned = Column(Numeric(12, 2), default=Decimal("0.00"))
    allowance = Column(Numeric(12, 2), default=Decimal("0.00"))
    advance_deduction = Column(Numeric(12, 2), default=Decimal("0.00"))
    other_deductions = Column(Numeric(12, 2), default=Decimal("0.00"))
    net_payable = Column(Numeric(12, 2), default=Decimal("0.00"))
    paid_amount = Column(Numeric(12, 2), default=Decimal("0.00"))
    balance_payable = Column(Numeric(12, 2), default=Decimal("0.00"))
    status = Column(String(30), default="Pending") # Pending, Partially Paid, Paid
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    driver = relationship("Driver", back_populates="salary_records")
    payments = relationship("SalaryPayment", back_populates="salary_record", cascade="all, delete-orphan")


class SalaryPayment(Base):
    __tablename__ = "salary_payments"

    id = Column(Integer, primary_key=True, index=True)
    salary_record_id = Column(Integer, ForeignKey("salary_records.id", ondelete="CASCADE"), nullable=True)
    driver_id = Column(Integer, ForeignKey("drivers.id", ondelete="CASCADE"), nullable=False)
    payment_date = Column(Date, default=date.today, nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    payment_method = Column(String(50), default="Cash")
    payment_type = Column(String(50), default="Salary") # Salary, Bata, Advance
    reference_number = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    driver = relationship("Driver", back_populates="salary_payments")
    salary_record = relationship("SalaryRecord", back_populates="payments")


class BataRecord(Base):
    __tablename__ = "bata_records"

    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey("drivers.id", ondelete="CASCADE"), nullable=False)
    trip_id = Column(Integer, ForeignKey("trips.id", ondelete="SET NULL"), nullable=True)
    date = Column(Date, default=date.today, nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    status = Column(String(30), default="Pending") # Pending, Paid, Included in Salary
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    driver = relationship("Driver", back_populates="bata_records")


class VehicleDocument(Base):
    __tablename__ = "vehicle_documents"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("trucks.id", ondelete="CASCADE"), nullable=False)
    document_type = Column(String(80), nullable=False) # FC, Insurance, Permit, National Permit, PUC, Road Tax, Driver License
    document_number = Column(String(100), nullable=True)
    issue_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=False)
    document_file = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    truck = relationship("Truck", back_populates="documents")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    category = Column(String(50), default="General") # Document Alert, Trip, Payment, General
    severity = Column(String(20), default="info") # info, warning, danger, success
    is_read = Column(Boolean, default=False)
    link = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

from datetime import date as dt_date, datetime as dt_datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field

# --- Auth & Owner Schemas ---
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    owner_name: str
    username: str

class OwnerProfile(BaseModel):
    id: int
    username: str
    full_name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    company_name: Optional[str] = None

    class Config:
        from_attributes = True

class OwnerProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    company_name: Optional[str] = None
    new_password: Optional[str] = None
    current_password: Optional[str] = None

# --- Company Settings Schemas ---
class CompanySettingsSchema(BaseModel):
    company_name: str
    tagline: str
    phone: str
    email: str
    address: str
    currency: str
    date_format: str
    reminder_days_json: str
    salary_rules_json: str

    class Config:
        from_attributes = True

# --- Document Schemas ---
class VehicleDocumentBase(BaseModel):
    document_type: str
    document_number: Optional[str] = None
    issue_date: Optional[dt_date] = None
    expiry_date: dt_date
    notes: Optional[str] = None

class VehicleDocumentCreate(VehicleDocumentBase):
    vehicle_id: int

class VehicleDocumentResponse(VehicleDocumentBase):
    id: int
    vehicle_id: int
    vehicle_number: Optional[str] = None
    days_remaining: int
    status_label: str  # e.g. "Expired", "12 days left", "Valid"
    status_class: str  # "danger", "warning", "success"

    class Config:
        from_attributes = True

# --- Truck Schemas ---
class TruckBase(BaseModel):
    vehicle_number: str
    make_model: Optional[str] = "TATA LPT 3118"
    vehicle_type: Optional[str] = "12 Wheeler Container"
    registration_date: Optional[dt_date] = None
    assigned_driver_id: Optional[int] = None
    permit_number: Optional[str] = None
    permit_expiry: Optional[dt_date] = None
    national_permit_expiry: Optional[dt_date] = None
    insurance_policy_number: Optional[str] = None
    insurance_expiry: Optional[dt_date] = None
    fc_expiry: Optional[dt_date] = None
    puc_expiry: Optional[dt_date] = None
    road_tax_expiry: Optional[dt_date] = None
    is_active: bool = True
    notes: Optional[str] = None

class TruckCreate(TruckBase):
    pass

class TruckUpdate(BaseModel):
    make_model: Optional[str] = None
    vehicle_type: Optional[str] = None
    registration_date: Optional[dt_date] = None
    assigned_driver_id: Optional[int] = None
    permit_number: Optional[str] = None
    permit_expiry: Optional[dt_date] = None
    national_permit_expiry: Optional[dt_date] = None
    insurance_policy_number: Optional[str] = None
    insurance_expiry: Optional[dt_date] = None
    fc_expiry: Optional[dt_date] = None
    puc_expiry: Optional[dt_date] = None
    road_tax_expiry: Optional[dt_date] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None

class TruckResponse(TruckBase):
    id: int
    assigned_driver_name: Optional[str] = None
    active_trips_count: int = 0
    total_trips_count: int = 0
    total_earnings: Decimal = Decimal("0.00")
    total_expenses: Decimal = Decimal("0.00")
    net_profit: Decimal = Decimal("0.00")
    document_alerts_count: int = 0

    class Config:
        from_attributes = True

# --- Driver Schemas ---
class DriverBase(BaseModel):
    full_name: str
    phone_number: str
    address: Optional[str] = None
    license_number: str
    license_expiry: Optional[dt_date] = None
    employment_status: Optional[str] = "Active"
    joining_date: Optional[dt_date] = None
    salary_type: Optional[str] = "Monthly" # Monthly, Daily, Trip Bata
    monthly_salary: Optional[Decimal] = Decimal("0.00")
    daily_salary: Optional[Decimal] = Decimal("0.00")
    bata_per_trip: Optional[Decimal] = Decimal("500.00")
    notes: Optional[str] = None

class DriverCreate(DriverBase):
    pass

class DriverUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    license_number: Optional[str] = None
    license_expiry: Optional[dt_date] = None
    employment_status: Optional[str] = None
    joining_date: Optional[dt_date] = None
    salary_type: Optional[str] = None
    monthly_salary: Optional[Decimal] = None
    daily_salary: Optional[Decimal] = None
    bata_per_trip: Optional[Decimal] = None
    notes: Optional[str] = None

class DriverResponse(DriverBase):
    id: int
    assigned_truck_numbers: List[str] = []
    trips_count: int = 0
    pending_salary: Decimal = Decimal("0.00")
    license_status: str = "Valid"
    license_days_left: Optional[int] = None

    class Config:
        from_attributes = True

# --- Customer Schemas ---
class CustomerBase(BaseModel):
    name: str
    company_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    gstin: Optional[str] = None
    notes: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerResponse(CustomerBase):
    id: int
    total_trips: int = 0
    total_billed: Decimal = Decimal("0.00")
    total_paid: Decimal = Decimal("0.00")
    outstanding_balance: Decimal = Decimal("0.00")

    class Config:
        from_attributes = True

# --- Trip & Payment Schemas ---
class TripPaymentCreate(BaseModel):
    payment_date: dt_date = Field(default_factory=dt_date.today)
    amount: Decimal
    payment_method: str = "Bank Transfer"
    reference_number: Optional[str] = None
    notes: Optional[str] = None

class TripPaymentResponse(TripPaymentCreate):
    id: int
    trip_id: int
    created_at: dt_datetime

    class Config:
        from_attributes = True

class TripBase(BaseModel):
    trip_date: dt_date = Field(default_factory=dt_date.today)
    vehicle_id: int
    driver_id: Optional[int] = None
    customer_name: str
    from_location: str
    to_location: str
    load_description: Optional[str] = None
    total_rent: Decimal
    advance_received: Decimal = Decimal("0.00")
    trip_start_date: Optional[dt_date] = None
    expected_delivery_date: Optional[dt_date] = None
    actual_delivery_date: Optional[dt_date] = None
    trip_status: str = "Ongoing" # Planned, Ongoing, Delivered, Completed, Cancelled
    notes: Optional[str] = None

class TripCreate(TripBase):
    pass

class TripUpdate(BaseModel):
    trip_date: Optional[dt_date] = None
    vehicle_id: Optional[int] = None
    driver_id: Optional[int] = None
    customer_name: Optional[str] = None
    from_location: Optional[str] = None
    to_location: Optional[str] = None
    load_description: Optional[str] = None
    total_rent: Optional[Decimal] = None
    advance_received: Optional[Decimal] = None
    trip_start_date: Optional[dt_date] = None
    expected_delivery_date: Optional[dt_date] = None
    actual_delivery_date: Optional[dt_date] = None
    trip_status: Optional[str] = None
    notes: Optional[str] = None

class TripResponse(TripBase):
    id: int
    vehicle_number: str
    driver_name: Optional[str] = None
    payments_total: Decimal = Decimal("0.00")
    balance_receivable: Decimal = Decimal("0.00")
    payments: List[TripPaymentResponse] = []
    created_at: dt_datetime

    class Config:
        from_attributes = True

# --- Expense Schemas ---
class ExpenseBase(BaseModel):
    date: dt_date = Field(default_factory=dt_date.today)
    vehicle_id: Optional[int] = None
    trip_id: Optional[int] = None
    category: str # Diesel, Toll, Driver Bata, Loading/Unloading, Repair & Maintenance, Insurance, Permit & FC, Road Tax, Other
    amount: Decimal
    paid_to: Optional[str] = None
    payment_method: str = "Cash"
    description: Optional[str] = None
    receipt_attachment: Optional[str] = None

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseUpdate(BaseModel):
    date: Optional[dt_date] = None
    vehicle_id: Optional[int] = None
    trip_id: Optional[int] = None
    category: Optional[str] = None
    amount: Optional[Decimal] = None
    paid_to: Optional[str] = None
    payment_method: Optional[str] = None
    description: Optional[str] = None

class ExpenseResponse(ExpenseBase):
    id: int
    vehicle_number: Optional[str] = None
    created_at: dt_datetime

    class Config:
        from_attributes = True

# --- Salary & Bata Schemas ---
class SalaryRecordCreate(BaseModel):
    driver_id: int
    salary_period: str
    start_date: Optional[dt_date] = None
    end_date: Optional[dt_date] = None
    days_worked: int = 30
    base_salary_rate: Decimal = Decimal("0.00")
    base_salary_earned: Decimal = Decimal("0.00")
    bata_earned: Decimal = Decimal("0.00")
    allowance: Decimal = Decimal("0.00")
    advance_deduction: Decimal = Decimal("0.00")
    other_deductions: Decimal = Decimal("0.00")
    notes: Optional[str] = None

class SalaryPayoutCreate(BaseModel):
    salary_record_id: Optional[int] = None
    driver_id: int
    payment_date: dt_date = Field(default_factory=dt_date.today)
    amount: Decimal
    payment_method: str = "Cash"
    payment_type: str = "Salary" # Salary, Bata, Advance
    reference_number: Optional[str] = None
    notes: Optional[str] = None

class SalaryRecordResponse(BaseModel):
    id: int
    driver_id: int
    driver_name: str
    salary_period: str
    days_worked: int
    base_salary_earned: Decimal
    bata_earned: Decimal
    allowance: Decimal
    advance_deduction: Decimal
    other_deductions: Decimal
    net_payable: Decimal
    paid_amount: Decimal
    balance_payable: Decimal
    status: str
    notes: Optional[str] = None
    created_at: dt_datetime

    class Config:
        from_attributes = True

class BataRecordCreate(BaseModel):
    driver_id: int
    trip_id: Optional[int] = None
    date: dt_date = Field(default_factory=dt_date.today)
    amount: Decimal
    status: str = "Pending"
    notes: Optional[str] = None

class BataRecordResponse(BaseModel):
    id: int
    driver_id: int
    driver_name: str
    trip_id: Optional[int] = None
    date: dt_date
    amount: Decimal
    status: str
    notes: Optional[str] = None

    class Config:
        from_attributes = True

# --- Dashboard & Reports Schemas ---
class KPISummary(BaseModel):
    total_trucks: int
    active_trucks_count: int
    active_trips: int
    total_income: Decimal
    total_expenses: Decimal
    balance_receivable: Decimal
    driver_salary_pending: Decimal
    document_alerts: int
    fuel_expenses: Decimal
    profit_loss: Decimal
    
    # Context subtext
    trucks_subtext: str = "All Vehicles Active"
    active_trips_subtext: str = "Out of 4 Trucks"
    income_subtext: str = "↗ 12% from last month"
    expenses_subtext: str = "↗ 8% from last month"
    receivable_subtext: str = "From Customers"
    salary_subtext: str = "For 4 Drivers"
    alerts_subtext: str = "Expiring Soon"
    fuel_subtext: str = "This Month"

class ChartDataMonth(BaseModel):
    month: str
    income: Decimal
    expenses: Decimal

class ChartExpenseCategory(BaseModel):
    category: str
    amount: Decimal
    percentage: float

class QuickSummaryData(BaseModel):
    total_trips_month: int
    total_distance_approx: int
    total_fuel_cost: Decimal
    total_toll_cost: Decimal
    total_profit_approx: Decimal

class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    category: str
    severity: str
    is_read: bool
    created_at: dt_datetime
    link: Optional[str] = None

    class Config:
        from_attributes = True

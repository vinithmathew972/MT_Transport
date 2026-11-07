from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from backend.database import SessionLocal, engine, Base
from backend.models import (
    Owner, CompanySettings, Truck, Driver, Customer,
    Trip, TripPayment, Expense, SalaryRecord, SalaryPayment,
    BataRecord, VehicleDocument, Notification
)
from backend.auth import hash_password
from backend.config import settings

def seed_database(db: Session):
    # Create all tables first
    Base.metadata.create_all(bind=engine)

    # 1. Check or create Owner
    owner = db.query(Owner).first()
    if not owner:
        owner = Owner(
            username=settings.DEFAULT_OWNER_USERNAME,
            hashed_password=hash_password(settings.DEFAULT_OWNER_PASSWORD),
            full_name=settings.DEFAULT_OWNER_NAME,
            phone="+91 98420 12345",
            email="owner@mothertheresatransport.com",
            is_active=True
        )
        db.add(owner)
        db.commit()
        db.refresh(owner)
        print(f"[Seed] Created Owner: {owner.username}")

    # 2. Company Settings
    company_settings = db.query(CompanySettings).first()
    if not company_settings:
        company_settings = CompanySettings(
            company_name="Mother Theresa Transport",
            tagline="Safe Journey... Stronger Tomorrow...",
            phone="+91 98420 12345",
            email="info@mothertheresatransport.com",
            address="Plot No. 12, Transport Hub, Salem Bye-Pass Road, Tamil Nadu - 636004",
            currency="₹",
            date_format="DD/MM/YYYY",
            reminder_days_json="[30, 15, 7]",
            salary_rules_json='{"default_bata": 500, "overtime_rate": 150}'
        )
        db.add(company_settings)
        db.commit()

    # If trucks already exist, don't re-seed
    if db.query(Truck).count() > 0:
        print("[Seed] Database already seeded.")
        return

    # 3. Create Drivers (4 real drivers for the 4 trucks)
    drivers_data = [
        {"name": "M. Paulraj", "phone": "+91 98421 11001", "license": "TN-27-20150004321", "license_exp": date(2028, 5, 14), "salary": Decimal("22000.00"), "daily": Decimal("800.00"), "bata": Decimal("500.00")},
        {"name": "S. Selvam", "phone": "+91 98421 22002", "license": "TN-30-20170008892", "license_exp": date(2027, 9, 20), "salary": Decimal("20000.00"), "daily": Decimal("750.00"), "bata": Decimal("500.00")},
        {"name": "K. Kumar", "phone": "+91 98421 33003", "license": "TN-38-20180005514", "license_exp": date(2029, 1, 10), "salary": Decimal("21000.00"), "daily": Decimal("800.00"), "bata": Decimal("500.00")},
        {"name": "R. Rajendran", "phone": "+91 98421 44004", "license": "TN-60-20160002198", "license_exp": date(2027, 11, 28), "salary": Decimal("23000.00"), "daily": Decimal("850.00"), "bata": Decimal("500.00")},
    ]

    drivers = []
    for d in drivers_data:
        driver = Driver(
            full_name=d["name"],
            phone_number=d["phone"],
            address="Salem, Tamil Nadu",
            license_number=d["license"],
            license_expiry=d["license_exp"],
            employment_status="Active",
            joining_date=date(2024, 1, 15),
            salary_type="Monthly",
            monthly_salary=d["salary"],
            daily_salary=d["daily"],
            bata_per_trip=d["bata"],
            notes="Experienced heavy container vehicle driver"
        )
        db.add(driver)
        drivers.append(driver)
    db.commit()
    for d in drivers:
        db.refresh(d)

    # 4. Create 4 Trucks matching reference screenshot
    trucks_data = [
        {
            "num": "TN-60-9262", "make": "TATA LPT 3118 Signa", "type": "14 Wheeler Multi-Axle",
            "driver_id": drivers[0].id, "permit": "NP-TN-2024-8841",
            "fc_exp": date(2027, 4, 15), "ins_exp": date(2026, 11, 10),
            "permit_exp": date(2027, 8, 20), "np_exp": date(2027, 8, 20),
            "puc_exp": date(2027, 2, 28), "tax_exp": date(2027, 3, 31)
        },
        {
            "num": "TN-37-4631", "make": "TATA 2818.T BS6", "type": "10 Wheeler Long Haul",
            "driver_id": drivers[1].id, "permit": "NP-TN-2023-4122",
            "fc_exp": date(2026, 12, 18), "ins_exp": date(2027, 5, 22),
            "permit_exp": date(2027, 6, 15), "np_exp": date(2027, 6, 15),
            "puc_exp": date(2027, 3, 10), "tax_exp": date(2027, 3, 31)
        },
        {
            "num": "TN-38-9697", "make": "TATA Prima 3528.K", "type": "12 Wheeler Heavy Carrier",
            "driver_id": drivers[2].id, "permit": "NP-TN-2024-9102",
            "fc_exp": date(2027, 7, 12), "ins_exp": date(2027, 6, 30),
            "permit_exp": date(2026, 12, 22), "np_exp": date(2027, 1, 15),
            "puc_exp": date(2027, 1, 20), "tax_exp": date(2027, 3, 31)
        },
        {
            "num": "TN-38-9262", "make": "TATA LPT 2518", "type": "10 Wheeler Container",
            "driver_id": drivers[3].id, "permit": "NP-TN-2024-3310",
            "fc_exp": date(2027, 9, 14), "ins_exp": date(2027, 4, 18),
            "permit_exp": date(2027, 10, 10), "np_exp": date(2027, 10, 10),
            "puc_exp": date(2026, 11, 5), "tax_exp": date(2027, 1, 20)
        }
    ]

    trucks = []
    for t in trucks_data:
        truck = Truck(
            vehicle_number=t["num"],
            make_model=t["make"],
            vehicle_type=t["type"],
            registration_date=date(2022, 3, 10),
            assigned_driver_id=t["driver_id"],
            permit_number=t["permit"],
            permit_expiry=t["permit_exp"],
            national_permit_expiry=t["np_exp"],
            insurance_policy_number="UIIC-POL-992144",
            insurance_expiry=t["ins_exp"],
            fc_expiry=t["fc_exp"],
            puc_expiry=t["puc_exp"],
            road_tax_expiry=t["tax_exp"],
            is_active=True,
            notes="Regular highway commercial container service"
        )
        db.add(truck)
        trucks.append(truck)
    db.commit()
    for t in trucks:
        db.refresh(t)

    # 5. Vehicle Documents matching the Upcoming Document Expiry table
    doc_entries = [
        {"truck_id": trucks[0].id, "type": "Insurance", "num": "UIIC-992144", "exp": date(2026, 11, 10)}, # 12 days left
        {"truck_id": trucks[1].id, "type": "FC", "num": "FC-SLM-8891", "exp": date(2026, 12, 18)},        # 51 days left
        {"truck_id": trucks[2].id, "type": "Permit", "num": "NP-TN-2024-9102", "exp": date(2026, 12, 22)},# 55 days left
        {"truck_id": trucks[3].id, "type": "PUC", "num": "PUC-TN-9923", "exp": date(2026, 11, 5)},       # 9 days left
        {"truck_id": trucks[3].id, "type": "Road Tax", "num": "TAX-TN-4412", "exp": date(2027, 1, 20)},   # 85 days left
    ]
    for de in doc_entries:
        doc = VehicleDocument(
            vehicle_id=de["truck_id"],
            document_type=de["type"],
            document_number=de["num"],
            issue_date=date(2025, 11, 1),
            expiry_date=de["exp"],
            notes="Primary statutory transport document"
        )
        db.add(doc)
    db.commit()

    # 6. Customers
    customers_data = [
        {"name": "ABC Logistics", "company": "ABC Logistics Pvt Ltd", "phone": "+91 99401 23456", "address": "Chennai, Tamil Nadu"},
        {"name": "Sri Venkateshwara", "company": "Sri Venkateshwara Mills", "phone": "+91 99402 34567", "address": "Bangalore, Karnataka"},
        {"name": "R.K. Transport", "company": "R.K. Roadways Corporation", "phone": "+91 99403 45678", "address": "Hyderabad, Telangana"},
        {"name": "Sreeji Traders", "company": "Sreeji Agro Traders", "phone": "+91 99404 56789", "address": "Madurai, Tamil Nadu"},
        {"name": "Southern Logistics Hub", "company": "Southern Cargo Corp", "phone": "+91 99405 67890", "address": "Coimbatore, Tamil Nadu"},
    ]
    customers = []
    for c in customers_data:
        cust = Customer(name=c["name"], company_name=c["company"], phone=c["phone"], address=c["address"])
        db.add(cust)
        customers.append(cust)
    db.commit()
    for c in customers:
        db.refresh(c)

    # 7. Trips matching the reference screenshot & totals
    # Recent Trips table in screenshot:
    # 26-10-2026 | TN-60-9262 | Coimbatore -> Chennai | ABC Logistics | Rent 15,000 | Adv 5,000 | Bal 10,000 | Ongoing
    # 24-10-2026 | TN-37-4631 | Erode -> Bangalore | Sri Venkateshwara | Rent 12,000 | Adv 6,000 | Bal 6,000 | Completed
    # 22-10-2026 | TN-38-9697 | Tirupur -> Hyderabad | R.K. Transport | Rent 18,000 | Adv 8,000 | Bal 10,000 | Completed
    # 20-10-2026 | TN-38-9262 | Salem -> Madurai | Sreeji Traders | Rent 10,000 | Adv 4,000 | Bal 6,000 | Completed
    # Plus ongoing & earlier trips this month to meet Total Income = ₹ 1,50,000 and Balance Receivable = ₹ 1,10,000
    trips_seed = [
        {
            "date": date(2026, 10, 26), "truck": trucks[0], "driver": drivers[0], "customer": customers[0],
            "from_loc": "Coimbatore", "to_loc": "Chennai", "load": "Industrial Machinery",
            "rent": Decimal("15000.00"), "advance": Decimal("5000.00"), "status": "Ongoing"
        },
        {
            "date": date(2026, 10, 24), "truck": trucks[1], "driver": drivers[1], "customer": customers[1],
            "from_loc": "Erode", "to_loc": "Bangalore", "load": "Textile Cotton Bales",
            "rent": Decimal("12000.00"), "advance": Decimal("6000.00"), "status": "Completed"
        },
        {
            "date": date(2026, 10, 22), "truck": trucks[2], "driver": drivers[2], "customer": customers[2],
            "from_loc": "Tirupur", "to_loc": "Hyderabad", "load": "Garments & Yarn",
            "rent": Decimal("18000.00"), "advance": Decimal("8000.00"), "status": "Completed"
        },
        {
            "date": date(2026, 10, 20), "truck": trucks[3], "driver": drivers[3], "customer": customers[3],
            "from_loc": "Salem", "to_loc": "Madurai", "load": "Automobile Spare Parts",
            "rent": Decimal("10000.00"), "advance": Decimal("4000.00"), "status": "Completed"
        },
        {
            "date": date(2026, 10, 15), "truck": trucks[0], "driver": drivers[0], "customer": customers[4],
            "from_loc": "Chennai", "to_loc": "Mumbai", "load": "Heavy Engineering Steel",
            "rent": Decimal("50000.00"), "advance": Decimal("10000.00"), "status": "Ongoing"
        },
        {
            "date": date(2026, 10, 10), "truck": trucks[1], "driver": drivers[1], "customer": customers[0],
            "from_loc": "Bangalore", "to_loc": "Kolkata", "load": "FMCG Wholesale Goods",
            "rent": Decimal("45000.00"), "advance": Decimal("7000.00"), "status": "Completed"
        }
    ]

    total_rent_sum = sum(t["rent"] for t in trips_seed) # 15 + 12 + 18 + 10 + 50 + 45 = 150,000! Exact ₹ 1,50,000!
    total_adv_sum = sum(t["advance"] for t in trips_seed) # 5 + 6 + 8 + 4 + 10 + 7 = 40,000!
    # Balance = 150,000 - 40,000 = 110,000! Exact ₹ 1,10,000!

    trips = []
    for ts in trips_seed:
        bal = ts["rent"] - ts["advance"]
        trip = Trip(
            trip_date=ts["date"],
            vehicle_id=ts["truck"].id,
            driver_id=ts["driver"].id,
            customer_id=ts["customer"].id,
            customer_name=ts["customer"].name,
            from_location=ts["from_loc"],
            to_location=ts["to_loc"],
            load_description=ts["load"],
            total_rent=ts["rent"],
            advance_received=ts["advance"],
            balance_receivable=bal,
            trip_start_date=ts["date"],
            expected_delivery_date=ts["date"] + timedelta(days=2),
            actual_delivery_date=ts["date"] + timedelta(days=2) if ts["status"] == "Completed" else None,
            trip_status=ts["status"],
            notes=f"Dispatched via NH44, regular route"
        )
        db.add(trip)
        trips.append(trip)
    db.commit()

    # 8. Expenses matching the reference:
    # Total Expenses: ₹ 45,000
    # Diesel: 40% = ₹ 18,500 (approx 40% matching Fuel Expenses card ₹ 18,500)
    # Toll: 20% = ₹ 8,000 (matching Quick summary Total Toll Cost ₹ 8,000)
    # Driver Bata: 15% = ₹ 6,750
    # Repair & Maintenance: 10% = ₹ 4,500
    # Other: ₹ 7,250 (Total = 18,500 + 8,000 + 6,750 + 4,500 + 7,250 = ₹ 45,000 exact!)
    expenses_data = [
        {"date": date(2026, 10, 25), "cat": "Diesel", "amount": Decimal("10000.00"), "paid_to": "Indian Oil Corporation", "desc": "Diesel fuel refill 110L - TN-60-9262", "truck": trucks[0]},
        {"date": date(2026, 10, 21), "cat": "Diesel", "amount": Decimal("8500.00"), "paid_to": "Bharat Petroleum Salem", "desc": "Diesel fuel refill 95L - TN-38-9697", "truck": trucks[2]},
        {"date": date(2026, 10, 24), "cat": "Toll", "amount": Decimal("4200.00"), "paid_to": "FASTag NHAI", "desc": "FASTag toll recharge - TN-37-4631", "truck": trucks[1]},
        {"date": date(2026, 10, 22), "cat": "Toll", "amount": Decimal("3800.00"), "paid_to": "FASTag NHAI", "desc": "FASTag toll recharge - TN-38-9697", "truck": trucks[2]},
        {"date": date(2026, 10, 26), "cat": "Driver Bata", "amount": Decimal("3500.00"), "paid_to": "M. Murugan", "desc": "Trip daily meal and food allowance", "truck": trucks[0]},
        {"date": date(2026, 10, 20), "cat": "Driver Bata", "amount": Decimal("3250.00"), "paid_to": "R. Rajendran", "desc": "Trip daily meal allowance", "truck": trucks[3]},
        {"date": date(2026, 10, 18), "cat": "Repair & Maintenance", "amount": Decimal("4500.00"), "paid_to": "Sri Balaji Auto Garage", "desc": "Brake shoe lining and clutch adjustment", "truck": trucks[1]},
        {"date": date(2026, 10, 14), "cat": "Other", "amount": Decimal("7250.00"), "paid_to": "Transport Nagar Association & Loading", "desc": "Tarpaulin ropes, loading labour & administrative charges", "truck": trucks[3]},
    ]
    for ed in expenses_data:
        exp = Expense(
            date=ed["date"],
            vehicle_id=ed["truck"].id if ed["truck"] else None,
            category=ed["cat"],
            amount=ed["amount"],
            paid_to=ed["paid_to"],
            payment_method="UPI / Cash",
            description=ed["desc"]
        )
        db.add(exp)
    db.commit()

    # 9. Salary Records matching "Driver Salary Pending: ₹ 32,000 for 4 Drivers"
    # E.g. Drivers pending salary balances summing to ₹ 32,000:
    salary_records_data = [
        {"driver": drivers[0], "base": Decimal("22000.00"), "paid": Decimal("14000.00"), "bal": Decimal("8000.00")},
        {"driver": drivers[1], "base": Decimal("20000.00"), "paid": Decimal("12000.00"), "bal": Decimal("8000.00")},
        {"driver": drivers[2], "base": Decimal("21000.00"), "paid": Decimal("13000.00"), "bal": Decimal("8000.00")},
        {"driver": drivers[3], "base": Decimal("23000.00"), "paid": Decimal("15000.00"), "bal": Decimal("8000.00")},
    ]
    # Sum of balance_payable = 8000 * 4 = ₹ 32,000 exact!
    for sr in salary_records_data:
        record = SalaryRecord(
            driver_id=sr["driver"].id,
            salary_period="October 2026",
            start_date=date(2026, 10, 1),
            end_date=date(2026, 10, 31),
            days_worked=30,
            base_salary_rate=sr["base"],
            base_salary_earned=sr["base"],
            bata_earned=Decimal("0.00"),
            allowance=Decimal("0.00"),
            advance_deduction=Decimal("0.00"),
            other_deductions=Decimal("0.00"),
            net_payable=sr["base"],
            paid_amount=sr["paid"],
            balance_payable=sr["bal"],
            status="Partially Paid",
            notes="October regular monthly salary"
        )
        db.add(record)
    db.commit()

    # 10. Notifications
    notifs = [
        {"title": "Insurance Expiry Warning", "msg": "Truck TN-60-9262 Insurance expires in 12 days (10 Nov 2026)", "cat": "Document Alert", "sev": "warning"},
        {"title": "PUC Renewal Due", "msg": "Truck TN-38-9262 PUC certificate expires in 9 days (05 Nov 2026)", "cat": "Document Alert", "sev": "danger"},
        {"title": "Active Trip in Transit", "msg": "Trip #1 to Chennai with TN-60-9262 is currently ongoing", "cat": "Trip", "sev": "info"}
    ]
    for n in notifs:
        db.add(Notification(
            title=n["title"],
            message=n["msg"],
            category=n["cat"],
            severity=n["sev"],
            is_read=False
        ))
    db.commit()

    print("[Seed] Successfully seeded initial demo data matching Reference Image 1!")

if __name__ == "__main__":
    db = SessionLocal()
    seed_database(db)
    db.close()

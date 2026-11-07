"""Reset the Mother Teresa Transport Management System database to a fresh state.

This script performs the following steps:
1. Creates a timestamped backup of the existing SQLite database (`transport.db`).
2. Deletes all demo records while preserving:
   - The admin `Owner` account (first Owner record).
   - Company settings.
3. Leaves the database schema intact; no tables are dropped or recreated.
4. Prints a summary of deletions performed.

**Safety notes**
- The script runs inside the existing project environment and uses the same
  SQLAlchemy `SessionLocal` configuration defined in `backend/database.py`.
- All deletions are executed in the correct foreign‑key dependency order to
  avoid integrity errors.
- If you need to roll back, restore the backup file created in step 1.
"""

import os
import shutil
import datetime
from sqlalchemy.orm import Session

# Import the existing DB session and models
from backend.database import SessionLocal, engine
from backend.models import (
    Owner,
    CompanySettings,
    Truck,
    Driver,
    Customer,
    Trip,
    TripPayment,
    Expense,
    SalaryRecord,
    SalaryPayment,
    BataRecord,
    VehicleDocument,
    Notification,
)


def backup_database(db_path: str) -> str:
    """Create a timestamped backup of the SQLite database.

    Args:
        db_path: Path to the original SQLite file.
    Returns:
        Path to the backup file.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{os.path.splitext(db_path)[0]}_backup_{timestamp}.db"
    shutil.copy2(db_path, backup_path)
    print(f"[Backup] Created backup: {backup_path}")
    return backup_path


def reset_database():
    # Path to the SQLite file (as configured in backend/database.py)
    db_file = os.path.abspath("transport.db")
    if not os.path.exists(db_file):
        raise FileNotFoundError(f"Database file not found at {db_file}")

    # Step 1: backup
    backup_database(db_file)

    # Create a new session
    db: Session = SessionLocal()
    try:
        # Preserve admin Owner (first Owner record) and CompanySettings
        admin_owner = db.query(Owner).first()
        company_settings = db.query(CompanySettings).first()
        admin_owner_id = admin_owner.id if admin_owner else None
        settings_id = company_settings.id if company_settings else None

        # Deletion order respecting FK constraints
        # 1. SalaryPayment (depends on SalaryRecord & Driver)
        db.query(SalaryPayment).filter(SalaryPayment.id.is_not(None)).delete(synchronize_session=False)
        # 2. SalaryRecord (depends on Driver)
        db.query(SalaryRecord).filter(SalaryRecord.id.is_not(None)).delete(synchronize_session=False)
        # 3. BataRecord (depends on Driver & Trip)
        db.query(BataRecord).filter(BataRecord.id.is_not(None)).delete(synchronize_session=False)
        # 4. TripPayment (depends on Trip)
        db.query(TripPayment).filter(TripPayment.id.is_not(None)).delete(synchronize_session=False)
        # 5. Expense (depends on Truck & Trip)
        db.query(Expense).filter(Expense.id.is_not(None)).delete(synchronize_session=False)
        # 6. VehicleDocument (depends on Truck)
        db.query(VehicleDocument).filter(VehicleDocument.id.is_not(None)).delete(synchronize_session=False)
        # 7. Notification (demo‑only alerts)
        db.query(Notification).filter(Notification.id.is_not(None)).delete(synchronize_session=False)
        # 8. Trip (depends on Truck, Driver, Customer)
        db.query(Trip).filter(Trip.id.is_not(None)).delete(synchronize_session=False)
        # 9. Truck (depends on Driver via assigned_driver_id)
        db.query(Truck).filter(Truck.id.is_not(None)).delete(synchronize_session=False)
        # 10. Driver (keep admin Owner only; drivers are demo data)
        db.query(Driver).filter(Driver.id.is_not(None)).delete(synchronize_session=False)
        # 11. Customer (demo customers)
        db.query(Customer).filter(Customer.id.is_not(None)).delete(synchronize_session=False)
        # 12. CompanySettings – keep existing record (already stored in variable)
        # No action needed; we retain it.
        # 13. Owner – preserve admin account only
        if admin_owner_id:
            db.query(Owner).filter(Owner.id != admin_owner_id).delete(synchronize_session=False)
        else:
            print("[Warning] No admin Owner found; nothing will be preserved.")

        db.commit()
        print("[Reset] Demo data deleted while preserving admin account and settings.")
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    reset_database()

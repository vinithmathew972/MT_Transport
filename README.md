# Mother Theresa Transport Management Web Application

> **Tagline:** *"Safe Journey... Stronger Tomorrow..."*

A complete, professional, visually attractive, fully functional Transport Management Web Application custom-built for **Mother Theresa Transport**.

---

## 📸 Reference Visual Design Compliance

1. **Home Page — Full-Screen Rainy Highway Truck Image:**
   - Cinematic full-screen landing page using the exact rainy truck background image (`rainy_truck.jpg`).
   - High-contrast, elegant typography: `"Mother Theresa"` in premium serif white typography and `"Transport"` in warm golden gradient.
   - Tagline: *"Safe Journey... Stronger Tomorrow..."*.
   - Discreet access to the secure Owner Portal by clicking the company title, pressing keyboard shortcut <kbd>L</kbd> or <kbd>Enter</kbd>, or clicking the subtle corner key.
   - Strict adherence: No dashboard clutter, menus, or public registration forms on the landing screen.

2. **Dashboard — Exact Match to Reference Image 1:**
   - **Dark Navy Sidebar:** Collapsible navigation with brand truck badge, transport modules, active indicator pill, and bottom branding banner (*"Better Logistics, Better Tomorrow"*).
   - **Top Header:** Truck emblem, company name, tagline, live formatted calendar date (`26 Oct 2026 Monday`), active notification bell with unread badge count (`3`), and owner profile dropdown.
   - **Hero Welcome Banner:** Gradient banner featuring *"Good Morning, Owner!"*, highway view, and script quote *"Every Mile Counts..."*.
   - **8 Gradient Summary KPI Cards:**
     1. **Total Trucks:** 4 (`All Vehicles Active`) — *Sky Blue Gradient*
     2. **Active Trips:** 2 (`Out of 4 Trucks`) — *Emerald Green Gradient*
     3. **Total Income:** ₹ 1,50,000 (`↗ 12% from last month`) — *Teal Gradient*
     4. **Total Expenses:** ₹ 45,000 (`↗ 8% from last month`) — *Coral Red Gradient*
     5. **Balance Receivable:** ₹ 1,10,000 (`From Customers`) — *Warm Amber Gradient*
     6. **Driver Salary Pending:** ₹ 32,000 (`For 4 Drivers`) — *Purple Gradient*
     7. **Document Alerts:** 2 (`Expiring Soon`) — *Royal Blue Gradient*
     8. **Fuel Expenses:** ₹ 18,500 (`This Month`) — *Slate Navy Gradient*
   - **Income vs Expenses:** Interactive monthly comparison bar chart using Chart.js.
   - **Expense Breakdown:** Interactive doughnut chart showing Diesel (40%), Toll (20%), Driver Bata (15%), Repair & Maintenance (10%), and Other (15%).
   - **Upcoming Document Expiry Table:** Live statutory alerts with color-coded countdown badges (e.g. *12 days left*, *9 days left*).
   - **Recent Trips Ledger:** Live trip table with customer, rent, advance received, outstanding balance, and status badges.
   - **Quick Summary:** Monthly trips, approx distance, fuel cost, toll cost, and net profit.
   - **Quick Actions:** One-click modals to Add Trip, Add Expense, Add Driver, Add Truck, and Generate Reports, alongside the inspirational quote banner.

---

## 🛠️ Technology Stack

- **Frontend:**
  - Modern Semantic HTML5 & CSS3
  - Vanilla JavaScript (modular architecture, zero bulky framework dependencies)
  - Interactive charts powered by [Chart.js](https://www.chartjs.org/)
  - Custom Lucide / SVG icons
- **Backend:**
  - Python 3.10+
  - [FastAPI](https://fastapi.tiangolo.com/) (high performance REST API architecture)
  - [SQLAlchemy 2.0 ORM](https://www.sqlalchemy.org/) (decimal precision financial storage)
  - [Pydantic v2](https://docs.pydantic.dev/) (strict request and response validation)
  - [PyJWT](https://pyjwt.readthedocs.io/) & [bcrypt](https://pypi.org/project/bcrypt/) (secure authentication)
- **Database:**
  - **SQLite:** Pre-configured fallback for zero-setup local development.
  - **PostgreSQL:** Production-ready relational database configured through environment variables.

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10 or higher installed.

### 2. Installation
Open your terminal in the project directory:

```bash
cd d:\MT_Transport
```

Install backend dependencies (if not already installed in your Python environment):
```bash
pip install fastapi uvicorn sqlalchemy pydantic pydantic-settings bcrypt pyjwt python-dotenv python-multipart
```

### 3. Initialize & Seed Database
Run the automated database setup and seeding script:
```bash
python -m backend.seed
```
This automatically sets up all relational tables and populates the database with realistic transport data matching the reference dashboard figures.

### 4. Start the Application
Run the application server:
```bash
python run.py
```
Or with Uvicorn directly:
```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

### 5. Access the Web Application
Open your browser:
- **Home Landing Page:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Owner Login:** [http://127.0.0.1:8000/login](http://127.0.0.1:8000/login)
- **Dashboard:** [http://127.0.0.1:8000/dashboard](http://127.0.0.1:8000/dashboard)
- **Interactive API Documentation:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🔐 Default Owner Access & Credentials

To access the system securely:
- **Username:** `owner`
- **Password:** `mtt2026`

> **Security Note:** You can change your password immediately after logging in by clicking **Owner ▾** in the top-right header and selecting **Owner Profile**.

### Creating or Resetting the Owner Account Securely
You can customize the initial owner credentials in `.env` before first startup:
```env
DEFAULT_OWNER_USERNAME="your_custom_username"
DEFAULT_OWNER_PASSWORD="your_strong_secret_password"
DEFAULT_OWNER_NAME="Owner Full Name"
```

---

## 🗄️ PostgreSQL Production Database Setup

To switch from the default SQLite database to PostgreSQL:

1. Create a PostgreSQL database on your server:
   ```sql
   CREATE DATABASE mother_theresa_transport;
   ```
2. In your `.env` file, update the `DATABASE_URL`:
   ```env
   DATABASE_URL="postgresql://postgres:your_password@localhost:5432/mother_theresa_transport"
   ```
3. Install PostgreSQL driver if not present:
   ```bash
   pip install psycopg2-binary
   ```
4. Run the seed script to build all schemas:
   ```bash
   python -m backend.seed
   ```

---

## 📊 Core Business Modules

1. **Truck Fleet Management:**
   - Tracks registration number, make/model, vehicle type, and driver assignment.
   - Monitors expiry dates for FC, Insurance, State Permit, National Permit (NP), PUC, and Road Tax.
   - Calculates vehicle-wise earnings, expenses, and net profit.

2. **Trips & Loads Ledger:**
   - Registers trips with customer name, origin, destination, cargo, rent, and advance payments.
   - Prevents duplicate payment submissions and automatically maintains real-time balance receivable.
   - Single-click CSV export for accounting.

3. **Income & Expense Tracking:**
   - Categorizes costs: Diesel, Toll, Driver Bata, Repairs, Maintenance, Insurance, Tax, and Other.
   - Links expenses to specific trucks to enable accurate per-vehicle P&L calculations.

4. **Driver & Salary Management:**
   - Supports both Monthly Salary and Daily Wage schemes.
   - Tracks driver Bata per trip and separates advances/deductions from net earnings.
   - Generates monthly statements and records payouts.

5. **Documents & Reminders:**
   - Automated status tags: **Expired** (Red), **Expiring Soon** (Amber/Yellow: $\le$ 30 days), and **Valid** (Green).
   - In-app notification center for pending renewals.

6. **Reports & Exports:**
   - Vehicle-wise Profit & Loss report.
   - Customer Outstanding balances report.
   - Vehicle fuel consumption & efficiency report.
   - Full JSON database backup for disaster recovery.

---

## 🛡️ Security Features
- **Hashed Passwords:** Passwords hashed with `bcrypt` using cryptographic salt.
- **JWT Authentication:** Stateful Bearer token session management with expiration.
- **Numeric Precision:** All money values stored using `Numeric(12, 2)` to eliminate floating-point rounding errors.
- **Data Protection:** Soft-deactivation of trucks and drivers ensures historical trips and financial ledgers are preserved.

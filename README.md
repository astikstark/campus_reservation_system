# Smart Campus Resource & Study Space Reservation System

[![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/tests-passing-brightgreen.svg)]()

> A robust, modular campus resource scheduling and conflict-prevention system developed for the **VITyarthi Academic Project Framework**.

---

## 📌 Executive Overview
The **Smart Campus Resource & Study Space Reservation System** provides an automated, reliable platform for students and campus administrators to reserve study spaces, lab benches, and seminar equipment. Built with a focus on clean modular software engineering, the application guarantees ACID transaction safety and deterministic overlap checking to prevent double-booking conflicts.

---

## ✨ Key Features
- 🔐 **Secure Role-Based Authentication**: PBKDF2-HMAC-SHA256 password hashing with unique salts for Students and Administrators.
- 📅 **Real-Time Booking Engine**: Instant temporal conflict detection enforcing business constraints (e.g., max 4-hour slot limits, min 15-minute lead times).
- 📊 **Operational Analytics**: Comprehensive facility utilization reporting and top-booked resource metrics.
- 📁 **CSV Audit Exporter**: One-click generation of complete reservation history reports for administrative review.
- 🧪 **Automated Unit Test Suite**: Comprehensive testing coverage using Python's standard `unittest` framework.

---

## 🛠️ Technology Stack
- **Language**: Python 3.12
- **Database**: SQLite3 with Foreign Keys & Transactional WAL mode
- **Security**: Cryptographic standard library `hashlib` (PBKDF2 SHA-256)
- **Testing**: `unittest` framework with temporary database isolation
- **Data Format**: CSV, ISO-8601 Timestamps

---

## 📁 Repository Directory Layout
```text
campus_reservation_system/
├── data/                       # Database and export directory
│   └── campus_resource.db
├── logs/                       # Application runtime audit logs
│   └── app.log
├── src/                        # Core source code modules
│   ├── __init__.py
│   ├── analytics.py            # Facility metrics & CSV export engine
│   ├── auth.py                 # User authentication & password hashing
│   ├── booking_engine.py       # Core reservation logic & conflict checking
│   ├── config.py               # System constants & path configuration
│   ├── database.py             # SQLite schema manager & connection pool
│   ├── exceptions.py           # Custom exception domain hierarchy
│   └── models.py               # Data models (User, Resource, Reservation)
├── tests/                      # Automated test suite
│   ├── test_booking.py         # PyTest test cases
│   └── test_runner.py          # Standalone unittest runner
├── main.py                     # Interactive CLI driver application
├── README.md                   # Project overview & execution guide
└── statement.md                # Detailed problem statement & scope
```

---

## 🚀 Installation & Setup Guide

### 1. Prerequisites
Ensure Python **3.10+** is installed on your system:
```bash
python3 --version
```

### 2. Clone the Repository
```bash
git clone https://github.com/vityarthi-student/campus-reservation-system.git
cd campus-reservation-system
```

### 3. Run the CLI Application
No external pip dependencies required! Run using native Python:
```bash
PYTHONPATH=. python3 main.py
```

---

## 🧪 Running Automated Tests
To run the automated unit test suite and verify system logic:

```bash
PYTHONPATH=. python3 tests/test_runner.py
```

### Sample Test Output:
```text
....
----------------------------------------------------------------------
Ran 4 tests in 0.513s

OK
```

---

## 👨‍💻 Admin Credentials (Default Seed Data)
To test administrative functions (analytics & CSV exporting), register an admin user or run the application CLI to view automatically populated sample campus facilities.

---

## 📜 License
Developed under the **VITyarthi Academic Project Guidelines**. Licensed under the MIT License.

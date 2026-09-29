# Smart Campus Resource & Study Space Reservation System

[![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/tests-passing-brightgreen.svg)]()

> A robust, modular campus resource scheduling and conflict-prevention system developed for the **VITyarthi Academic Project Framework**.

---

##  Executive Overview
The **Smart Campus Resource & Study Space Reservation System** provides an automated, reliable platform for students and campus administrators to reserve study spaces, lab benches, and seminar equipment. Built with a focus on clean modular software engineering, the application guarantees ACID transaction safety and deterministic overlap checking to prevent double-booking conflicts.

---

##  Key Features
-  **Secure Role-Based Authentication**: PBKDF2-HMAC-SHA256 password hashing with unique salts for Students and Administrators.
-  **Real-Time Booking Engine**: Instant temporal conflict detection enforcing business constraints (e.g., max 4-hour slot limits, min 15-minute lead times).
-  **Operational Analytics**: Comprehensive facility utilization reporting and top-booked resource metrics.
-  **CSV Audit Exporter**: One-click generation of complete reservation history reports for administrative review.
-  **Automated Unit Test Suite**: Comprehensive testing coverage using Python's standard `unittest` framework.

---

##  Technology Stack
- **Language**: Python 3.12
- **Database**: SQLite3 with Foreign Keys & Transactional WAL mode
- **Security**: Cryptographic standard library `hashlib` (PBKDF2 SHA-256)
- **Testing**: `unittest` framework with temporary database isolation
- **Data Format**: CSV, ISO-8601 Timestamps

---

##  Repository Directory Layout
```text
campus_reservation_system/
├── data/                       
│   └── campus_resource.db
├── logs/                       
│   └── app.log
├── src/                        
│   ├── __init__.py
│   ├── analytics.py            
│   ├── auth.py                 
│   ├── booking_engine.py       
│   ├── config.py               
│   ├── database.py             
│   ├── exceptions.py           
│   └── models.py               
├── tests/                      
│   ├── test_booking.py         
│   └── test_runner.py          
├── main.py                     
├── README.md                   
└── statement.md                
```

### Sample Test Output:
```text
....
----------------------------------------------------------------------
Ran 4 tests in 0.513s

OK
```

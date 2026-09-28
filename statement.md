# Problem Statement & System Scope

## Project Title
**Smart Campus Resource & Study Space Reservation System**

## 1. Problem Statement
Educational institutions often struggle with managing high-demand academic resources such as library silent study pods, group discussion rooms, high-performance computing lab benches, and seminar hall AV equipment. Traditional manual sign-up sheets or unstructured booking systems lead to several critical inefficiencies:
- **Double-booking conflicts** caused by concurrent uncoordinated requests.
- **Underutilization and hoarding**, where spaces remain locked without actual active usage.
- **Lack of centralized audit trails** for campus administrators to track peak usage hours and optimize resource allocation.
- **Fairness issues**, where individual users monopolize scarce academic infrastructure for extended periods.

## 2. Project Scope
The **Smart Campus Resource & Study Space Reservation System** is a modular, multi-tier software solution designed to streamline the scheduling and allocation of campus facilities.

### In-Scope:
- **User Authentication & Role Management**: Secure registration and login for Students and System Administrators with role-based access control (RBAC).
- **Resource Inventory Cataloging**: Centralized metadata management for study pods, lab equipment, and seminar halls.
- **Real-Time Booking Engine**: Automated slot validation, duration policy enforcement, and real-time collision/overlap detection.
- **Self-Service Reservation Lifecycle**: Capability for students to view active bookings and cancel reservations when plans change.
- **Administrative Analytics & Reporting**: System health metrics, resource utilization stats, and CSV export functionality for administrative audits.

### Out-of-Scope (Future Work):
- Payment gateway integration for paid facility bookings.
- Hardware IoT door lock integration via NFC/RFID chips.

## 3. Target Users
1. **University Students**: Require quick, hassle-free booking of study pods and lab benches with immediate confirmation and double-booking protection.
2. **Faculty & Club Organizers**: Need access to reserve larger seminar halls and portable AV projectors for academic workshops.
3. **Campus Administrators**: Require usage analytics, peak hour insights, and audit logs to plan facility maintenance and expansion.

## 4. High-Level System Features
- **Deterministic Overlap Prevention**: SQL-level temporal checks enforcing `(start1 < end2) AND (end1 > start2)`.
- **PBKDF2 Password Security**: Cryptographic password hashing using PBKDF2 with SHA-256 and unique salts per user.
- **Custom Exception Hierarchy**: Granular error handling distinguishing authentication failures from booking time conflicts.
- **Automated CSV Exporter**: Streamed audit logging to standard CSV format for offline reporting.

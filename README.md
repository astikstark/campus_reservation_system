Smart Campus Resource & Study Space Reservation System
A Python-based command-line application built for the VITyarthi Academic Project Framework. It helps students and admins easily book study spaces and lab equipment without the headache of overlapping schedules or double-booking.

About the Project
Trying to find an open study room or lab bench on campus can be chaotic. I built this system to automate the reservation process. It handles user accounts, checks for time conflicts in real-time, and makes sure that once a space is booked, no one else can claim it for that specific time slot.

What It Does
Secure Logins: Separate roles for Students and Admins. Passwords are encrypted and not stored in plain text.

Smart Booking: The system automatically prevents double-booking. It also enforces realistic rules, like a maximum 4-hour limit per booking and a 15-minute minimum lead time.

Usage Stats: Admins can see which facilities are the most popular and track overall campus resource usage.

CSV Exports: Admins can download the full reservation history into a CSV file with one click for easy auditing.

Fully Tested: Includes an automated unit test suite to make sure the core booking logic works perfectly.

Tech Stack
Language: Python 3.12

Database: SQLite3 (built-in, so no extra setup required)

Security: Python native hashlib

Testing: Python unittest

Note: This project has zero external dependencies and runs completely on Python's standard library .

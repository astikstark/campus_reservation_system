from datetime import datetime, timedelta
import sqlite3
import logging
from typing import List, Optional
from src.database import DatabaseManager
from src.models import Resource, Reservation
from src.config import MAX_BOOKING_HOURS, MAX_ACTIVE_BOOKINGS_PER_USER, MIN_ADVANCE_BOOKING_MINS
from src.exceptions import (
    ResourceNotFoundError, SlotOverlapError, InvalidTimeSlotError, ReservationSystemError
)

logger = logging.getLogger("BookingEngine")


class BookingEngine:
    """
    Core domain service managing resource availability, slot conflict detection,
    reservation creation, and active reservation lifecycles.
    """

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def list_resources(self, category: Optional[str] = None) -> List[Resource]:
        """Fetches active resources filtered optionally by category."""
        query = "SELECT resource_id, name, category, capacity, location, is_active FROM resources WHERE is_active = 1"
        params = []
        if category:
            query += " AND category = ?"
            params.append(category)

        resources = []
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            for row in cursor.fetchall():
                resources.append(Resource(
                    resource_id=row['resource_id'],
                    name=row['name'],
                    category=row['category'],
                    capacity=row['capacity'],
                    location=row['location'],
                    is_active=bool(row['is_active'])
                ))
        return resources

    def validate_slot_times(self, start_dt: datetime, end_dt: datetime):
        """Validates requested start and end timestamps against business constraints."""
        now = datetime.now()
        
        if start_dt >= end_dt:
            raise InvalidTimeSlotError("End time must be strictly after start time.")

        if (start_dt - now).total_seconds() < (MIN_ADVANCE_BOOKING_MINS * 60) - 60: # allow 1 min drift
            raise InvalidTimeSlotError(f"Bookings must be placed at least {MIN_ADVANCE_BOOKING_MINS} minutes in advance.")

        duration = (end_dt - start_dt).total_seconds() / 3600.0
        if duration > MAX_BOOKING_HOURS:
            raise InvalidTimeSlotError(f"Reservation duration cannot exceed {MAX_BOOKING_HOURS} hours.")

    def check_conflict(self, resource_id: int, start_iso: str, end_iso: str, exclude_reservation_id: Optional[int] = None) -> bool:
        """
        Checks if the requested resource has an overlapping active reservation.
        SQL Overlap Rule: (start_time < requested_end) AND (end_time > requested_start)
        """
        query = """
        SELECT COUNT(*) FROM reservations
        WHERE resource_id = ?
          AND status = 'CONFIRMED'
          AND (start_time < ? AND end_time > ?)
        """
        params = [resource_id, end_iso, start_iso]
        if exclude_reservation_id:
            query += " AND reservation_id != ?"
            params.append(exclude_reservation_id)

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            count = cursor.fetchone()[0]
            return count > 0

    def create_reservation(self, user_id: int, resource_id: int, start_dt: datetime, end_dt: datetime) -> Reservation:
        """
        Executes reservation creation with full concurrency and rule checks.
        """
        self.validate_slot_times(start_dt, end_dt)
        start_iso = start_dt.isoformat()
        end_iso = end_dt.isoformat()

        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            # 1. Verify resource exists & active
            cursor.execute("SELECT name FROM resources WHERE resource_id = ? AND is_active = 1", (resource_id,))
            res_row = cursor.fetchone()
            if not res_row:
                raise ResourceNotFoundError(f"Active resource ID {resource_id} not found.")
            resource_name = res_row['name']

            # 2. Check active user booking limit
            cursor.execute(
                "SELECT COUNT(*) FROM reservations WHERE user_id = ? AND status = 'CONFIRMED' AND end_time > ?",
                (user_id, datetime.now().isoformat())
            )
            active_count = cursor.fetchone()[0]
            if active_count >= MAX_ACTIVE_BOOKINGS_PER_USER:
                raise ReservationSystemError(f"User limit reached: Maximum {MAX_ACTIVE_BOOKINGS_PER_USER} active bookings allowed.")

            # 3. Check time slot conflict
            if self.check_conflict(resource_id, start_iso, end_iso):
                raise SlotOverlapError("Selected time slot conflicts with an existing reservation for this resource.")

            # 4. Insert reservation atomically
            cursor.execute(
                "INSERT INTO reservations (user_id, resource_id, start_time, end_time) VALUES (?, ?, ?, ?)",
                (user_id, resource_id, start_iso, end_iso)
            )
            res_id = cursor.lastrowid
            conn.commit()
            logger.info(f"Reservation #{res_id} created for User #{user_id} on Resource #{resource_id}.")

            return Reservation(
                reservation_id=res_id,
                user_id=user_id,
                resource_id=resource_id,
                start_time=start_iso,
                end_time=end_iso,
                status="CONFIRMED",
                resource_name=resource_name
            )

    def cancel_reservation(self, reservation_id: int, user_id: int, is_admin: bool = False):
        """Cancels a reservation if owned by user or if admin."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, status FROM reservations WHERE reservation_id = ?", (reservation_id,))
            row = cursor.fetchone()

            if not row:
                raise ReservationSystemError(f"Reservation #{reservation_id} does not exist.")

            owner_id, status = row['user_id'], row['status']
            if not is_admin and owner_id != user_id:
                raise ReservationSystemError("Unauthorized: You do not own this reservation.")

            if status == 'CANCELLED':
                raise ReservationSystemError("Reservation is already cancelled.")

            cursor.execute("UPDATE reservations SET status = 'CANCELLED' WHERE reservation_id = ?", (reservation_id,))
            conn.commit()
            logger.info(f"Reservation #{reservation_id} cancelled by User #{user_id}.")

    def get_user_reservations(self, user_id: int) -> List[Reservation]:
        """Returns all reservations made by a specific user with resource details."""
        query = """
        SELECT r.reservation_id, r.user_id, r.resource_id, r.start_time, r.end_time, r.status,
               res.name as resource_name
        FROM reservations r
        JOIN resources res ON r.resource_id = res.resource_id
        WHERE r.user_id = ?
        ORDER BY r.start_time DESC
        """
        reservations = []
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (user_id,))
            for row in cursor.fetchall():
                reservations.append(Reservation(
                    reservation_id=row['reservation_id'],
                    user_id=row['user_id'],
                    resource_id=row['resource_id'],
                    start_time=row['start_time'],
                    end_time=row['end_time'],
                    status=row['status'],
                    resource_name=row['resource_name']
                ))
        return reservations

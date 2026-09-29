import unittest
import os
import tempfile
from datetime import datetime, timedelta
from src.database import DatabaseManager
from src.auth import AuthService
from src.booking_engine import BookingEngine
from src.exceptions import (
    SlotOverlapError, UserAuthenticationError, InvalidTimeSlotError, ReservationSystemError
)


class TestCampusReservationSystem(unittest.TestCase):

    def setUp(self):
        """Set up clean isolated temp database before each test."""
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.db = DatabaseManager(db_path=self.db_path)
        self.db.initialize_schema()
        self.db.seed_initial_data()
        self.auth_service = AuthService(self.db)
        self.booking_engine = BookingEngine(self.db)

    def tearDown(self):
        """Clean up temp database file."""
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_user_registration_and_auth(self):
        """Tests user registration and secure authentication."""
        user = self.auth_service.register_user("teststudent", "student@vit.ac.in", "securepass123")
        self.assertEqual(user.username, "teststudent")
        self.assertEqual(user.role, "student")

        auth_user = self.auth_service.authenticate_user("teststudent", "securepass123")
        self.assertEqual(auth_user.user_id, user.user_id)

        with self.assertRaises(UserAuthenticationError):
            self.auth_service.authenticate_user("teststudent", "wrongpassword")

    def test_time_slot_validation(self):
        """Tests business constraint validation for lead times and max duration."""
        now = datetime.now()

        # Past time booking attempt
        with self.assertRaises(InvalidTimeSlotError):
            self.booking_engine.validate_slot_times(now - timedelta(hours=2), now - timedelta(hours=1))

        # Exceeding 4 hour max duration
        start = now + timedelta(hours=1)
        end = start + timedelta(hours=5)
        with self.assertRaises(InvalidTimeSlotError):
            self.booking_engine.validate_slot_times(start, end)

    def test_reservation_creation_and_overlap_prevention(self):
        """Tests real-time slot conflict checking and overlap prevention."""
        u1 = self.auth_service.register_user("user1", "u1@vit.ac.in", "password123")
        u2 = self.auth_service.register_user("user2", "u2@vit.ac.in", "password123")

        resources = self.booking_engine.list_resources()
        res_id = resources[0].resource_id

        now = datetime.now()
        start_time = now + timedelta(hours=2)
        end_time = start_time + timedelta(hours=2)

        # First booking succeeds
        res1 = self.booking_engine.create_reservation(u1.user_id, res_id, start_time, end_time)
        self.assertGreater(res1.reservation_id, 0)
        self.assertEqual(res1.status, "CONFIRMED")

        # Overlapping booking attempt by user 2 must raise SlotOverlapError
        overlap_start = start_time + timedelta(minutes=30)
        overlap_end = end_time + timedelta(minutes=30)

        with self.assertRaises(SlotOverlapError):
            self.booking_engine.create_reservation(u2.user_id, res_id, overlap_start, overlap_end)

    def test_reservation_cancellation(self):
        """Tests cancellation workflows and access rights."""
        u1 = self.auth_service.register_user("user1", "u1@vit.ac.in", "password123")
        u2 = self.auth_service.register_user("user2", "u2@vit.ac.in", "password123")

        resources = self.booking_engine.list_resources()
        res_id = resources[0].resource_id

        start = datetime.now() + timedelta(hours=1)
        end = start + timedelta(hours=1)

        res = self.booking_engine.create_reservation(u1.user_id, res_id, start, end)

        # User 2 attempting to cancel User 1's reservation should fail
        with self.assertRaises(ReservationSystemError):
            self.booking_engine.cancel_reservation(res.reservation_id, u2.user_id, is_admin=False)

        # User 1 cancelling their own reservation should succeed
        self.booking_engine.cancel_reservation(res.reservation_id, u1.user_id, is_admin=False)
        user_reservations = self.booking_engine.get_user_reservations(u1.user_id)
        self.assertEqual(user_reservations[0].status, "CANCELLED")


if __name__ == "__main__":
    unittest.main()

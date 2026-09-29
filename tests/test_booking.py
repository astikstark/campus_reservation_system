import pytest
import os
import tempfile
from datetime import datetime, timedelta
from src.database import DatabaseManager
from src.auth import AuthService
from src.booking_engine import BookingEngine
from src.exceptions import (
    SlotOverlapError, UserAuthenticationError, InvalidTimeSlotError, ReservationSystemError
)


@pytest.fixture
def temp_db():
    """Provides a clean temporary SQLite database instance for isolated testing."""
    db_fd, db_path = tempfile.mkstemp()
    db = DatabaseManager(db_path=db_path)
    db.initialize_schema()
    db.seed_initial_data()
    yield db
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def auth_service(temp_db):
    return AuthService(temp_db)


@pytest.fixture
def booking_engine(temp_db):
    return BookingEngine(temp_db)


def test_user_registration_and_auth(auth_service):
    """Tests successful user registration and password authentication."""
    user = auth_service.register_user("teststudent", "student@vit.ac.in", "securepass123")
    assert user.username == "teststudent"
    assert user.role == "student"

    auth_user = auth_service.authenticate_user("teststudent", "securepass123")
    assert auth_user.user_id == user.user_id

    with pytest.raises(UserAuthenticationError):
        auth_service.authenticate_user("teststudent", "wrongpassword")


def test_time_slot_validation(booking_engine):
    """Tests business constraint validation for booking lead time and max duration."""
    now = datetime.now()

    # Past time booking attempt
    with pytest.raises(InvalidTimeSlotError):
        booking_engine.validate_slot_times(now - timedelta(hours=2), now - timedelta(hours=1))

    # Exceeding 4 hour max duration
    start = now + timedelta(hours=1)
    end = start + timedelta(hours=5)
    with pytest.raises(InvalidTimeSlotError):
        booking_engine.validate_slot_times(start, end)


def test_reservation_creation_and_overlap_prevention(auth_service, booking_engine):
    """Tests real-time conflict checking and overlap prevention engine."""
    u1 = auth_service.register_user("user1", "u1@vit.ac.in", "password123")
    u2 = auth_service.register_user("user2", "u2@vit.ac.in", "password123")

    resources = booking_engine.list_resources()
    res_id = resources[0].resource_id

    now = datetime.now()
    start_time = now + timedelta(hours=2)
    end_time = start_time + timedelta(hours=2)

    # First booking succeeds
    res1 = booking_engine.create_reservation(u1.user_id, res_id, start_time, end_time)
    assert res1.reservation_id > 0
    assert res1.status == "CONFIRMED"

    # Overlapping booking attempt by user 2 must raise SlotOverlapError
    overlap_start = start_time + timedelta(minutes=30)
    overlap_end = end_time + timedelta(minutes=30)

    with pytest.raises(SlotOverlapError):
        booking_engine.create_reservation(u2.user_id, res_id, overlap_start, overlap_end)


def test_reservation_cancellation(auth_service, booking_engine):
    """Tests reservation cancellation and owner permissions."""
    u1 = auth_service.register_user("user1", "u1@vit.ac.in", "password123")
    u2 = auth_service.register_user("user2", "u2@vit.ac.in", "password123")

    resources = booking_engine.list_resources()
    res_id = resources[0].resource_id

    start = datetime.now() + timedelta(hours=1)
    end = start + timedelta(hours=1)

    res = booking_engine.create_reservation(u1.user_id, res_id, start, end)

    # User 2 attempting to cancel User 1's reservation should fail
    with pytest.raises(ReservationSystemError):
        booking_engine.cancel_reservation(res.reservation_id, u2.user_id, is_admin=False)

    # User 1 cancelling their own reservation should succeed
    booking_engine.cancel_reservation(res.reservation_id, u1.user_id, is_admin=False)
    user_reservations = booking_engine.get_user_reservations(u1.user_id)
    assert user_reservations[0].status == "CANCELLED"

"""
Custom Exception Classes for Campus Resource Reservation System.
Handles specific domain-level error conditions cleanly across modules.
"""

class ReservationSystemError(Exception):
    """Base exception class for application errors."""
    pass


class ResourceNotFoundError(ReservationSystemError):
    """Raised when a requested facility or resource ID is not found."""
    pass


class UserAuthenticationError(ReservationSystemError):
    """Raised on invalid login credentials or unauthorized actions."""
    pass


class SlotOverlapError(ReservationSystemError):
    """Raised when a requested reservation time slot overlaps with an existing booking."""
    pass


class InvalidTimeSlotError(ReservationSystemError):
    """Raised when requested start/end times violate business rules."""
    pass

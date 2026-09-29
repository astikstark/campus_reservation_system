from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    user_id: int
    username: str
    email: str
    role: str = "student"
    created_at: Optional[str] = None


@dataclass
class Resource:
    resource_id: int
    name: str
    category: str
    capacity: int
    location: str
    is_active: bool = True


@dataclass
class Reservation:
    reservation_id: int
    user_id: int
    resource_id: int
    start_time: str
    end_time: str
    status: str = "CONFIRMED"
    resource_name: Optional[str] = None
    user_name: Optional[str] = None
    created_at: Optional[str] = None

    @property
    def start_datetime(self) -> datetime:
        return datetime.fromisoformat(self.start_time)

    @property
    def end_datetime(self) -> datetime:
        return datetime.fromisoformat(self.end_time)

    def duration_hours(self) -> float:
        delta = self.end_datetime - self.start_datetime
        return round(delta.total_seconds() / 3600.0, 2)

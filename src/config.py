import os
from pathlib import Path

# Base project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"

# Ensure runtime directories exist
DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

# Database Configuration
DB_PATH = DATA_DIR / "campus_resource.db"

# Business Rules / Constraints
MAX_BOOKING_HOURS = 4            # Max duration per reservation (hrs)
MAX_ACTIVE_BOOKINGS_PER_USER = 3  # Active booking limit per student
MIN_ADVANCE_BOOKING_MINS = 15     # Must book at least 15 mins in advance

# Logging Configuration
LOG_FILE = LOG_DIR / "app.log"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

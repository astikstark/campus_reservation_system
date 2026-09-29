import sqlite3
import logging
from src.config import DB_PATH, LOG_FILE, LOG_FORMAT

# Set up logger
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger("DatabaseManager")


class DatabaseManager:
    """
    Manages SQLite database connections, schema setup, and migration.
    Enforces foreign key constraints and transactional integrity.
    """

    def __init__(self, db_path=None):
        self.db_path = db_path or DB_PATH

    def get_connection(self):
        """Returns a database connection with foreign keys enabled."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def initialize_schema(self):
        """Creates tables if they do not already exist."""
        schema_sql = """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT CHECK(role IN ('student', 'admin')) NOT NULL DEFAULT 'student',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS resources (
            resource_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT CHECK(category IN ('study_room', 'lab_bench', 'seminar_hall', 'projector')) NOT NULL,
            capacity INTEGER NOT NULL,
            location TEXT NOT NULL,
            is_active INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS reservations (
            reservation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            resource_id INTEGER NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            status TEXT CHECK(status IN ('CONFIRMED', 'CANCELLED', 'COMPLETED')) DEFAULT 'CONFIRMED',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (resource_id) REFERENCES resources(resource_id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_res_times ON reservations(resource_id, start_time, end_time);
        """
        try:
            with self.get_connection() as conn:
                conn.executescript(schema_sql)
                conn.commit()
            logger.info("Database schema initialized successfully.")
        except sqlite3.Error as e:
            logger.error(f"Error initializing database schema: {e}")
            raise

    def seed_initial_data(self):
        """Seeds default campus resources if table is empty."""
        initial_resources = [
            ("VIT Central Library - Silent Study Pod 1", "study_room", 2, "Central Library L2"),
            ("VIT Central Library - Group Discussion Room B", "study_room", 8, "Central Library L3"),
            ("SJT High Performance Computing Bench 04", "lab_bench", 1, "SJT 302 Lab"),
            ("TT Seminar Hall Alpha", "seminar_hall", 40, "Technology Tower 1st Floor"),
            ("Portable HD Laser Projector Unit #2", "projector", 15, "Equipment Desk SJT Ground")
        ]
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM resources")
            if cursor.fetchone()[0] == 0:
                cursor.executemany(
                    "INSERT INTO resources (name, category, capacity, location) VALUES (?, ?, ?, ?)",
                    initial_resources
                )
                conn.commit()
                logger.info("Database seeded with sample campus resources.")

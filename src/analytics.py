import csv
import io
import logging
from typing import Dict, Any, List
from src.database import DatabaseManager

logger = logging.getLogger("AnalyticsModule")


class AnalyticsService:
    """Provides system operational metrics, facility usage analytics, and CSV export capabilities."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def get_summary_metrics(self) -> Dict[str, Any]:
        """Calculates high-level utilization and user stats."""
        metrics = {}
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM users")
            metrics['total_users'] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM resources WHERE is_active = 1")
            metrics['active_resources'] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM reservations WHERE status = 'CONFIRMED'")
            metrics['total_confirmed_reservations'] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM reservations WHERE status = 'CANCELLED'")
            metrics['total_cancelled_reservations'] = cursor.fetchone()[0]

            # Most popular resource
            cursor.execute("""
            SELECT res.name, COUNT(r.reservation_id) as booking_count
            FROM reservations r
            JOIN resources res ON r.resource_id = res.resource_id
            WHERE r.status = 'CONFIRMED'
            GROUP BY r.resource_id
            ORDER BY booking_count DESC
            LIMIT 1
            """)
            top_res = cursor.fetchone()
            metrics['most_popular_resource'] = top_res['name'] if top_res else "None"
            metrics['most_popular_count'] = top_res['booking_count'] if top_res else 0

        return metrics

    def get_resource_usage_breakdown(self) -> List[Dict[str, Any]]:
        """Calculates total hours booked per resource."""
        query = """
        SELECT res.name, res.category, COUNT(r.reservation_id) as total_bookings
        FROM resources res
        LEFT JOIN reservations r ON res.resource_id = r.resource_id AND r.status = 'CONFIRMED'
        GROUP BY res.resource_id
        ORDER BY total_bookings DESC
        """
        breakdown = []
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            for row in cursor.fetchall():
                breakdown.append({
                    "resource_name": row['name'],
                    "category": row['category'],
                    "total_bookings": row['total_bookings']
                })
        return breakdown

    def export_reservations_csv(self, filepath: str):
        """Exports all reservation audit logs to a CSV file."""
        query = """
        SELECT r.reservation_id, u.username, u.email, res.name as resource_name,
               res.category, r.start_time, r.end_time, r.status, r.created_at
        FROM reservations r
        JOIN users u ON r.user_id = u.user_id
        JOIN resources res ON r.resource_id = res.resource_id
        ORDER BY r.reservation_id ASC
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Reservation ID', 'Username', 'Email', 'Resource Name', 'Category', 'Start Time', 'End Time', 'Status', 'Created At'])
                for r in rows:
                    writer.writerow([r['reservation_id'], r['username'], r['email'], r['resource_name'], r['category'], r['start_time'], r['end_time'], r['status'], r['created_at']])
            logger.info(f"Exported reservation report to {filepath}")

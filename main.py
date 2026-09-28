import sys
from datetime import datetime, timedelta
from src.database import DatabaseManager
from src.auth import AuthService
from src.booking_engine import BookingEngine
from src.analytics import AnalyticsService
from src.exceptions import ReservationSystemError


class CampusReservationApp:
    """CLI Driver Application orchestrating user interactions and workflows."""

    def __init__(self):
        self.db = DatabaseManager()
        self.db.initialize_schema()
        self.db.seed_initial_data()

        self.auth = AuthService(self.db)
        self.engine = BookingEngine(self.db)
        self.analytics = AnalyticsService(self.db)
        self.current_user = None

    def display_banner(self):
        print("\n" + "=" * 65)
        print("  SMART CAMPUS RESOURCE & STUDY SPACE RESERVATION SYSTEM")
        print("  VITyarthi Academic Project Implementation")
        print("=" * 65)

    def main_menu(self):
        while True:
            self.display_banner()
            if not self.current_user:
                print(" 1. Register Student Account")
                print(" 2. User / Admin Login")
                print(" 3. View Available Resources")
                print(" 4. Exit Application")
                choice = input("\nSelect Option (1-4): ").strip()

                if choice == "1":
                    self.register_flow()
                elif choice == "2":
                    self.login_flow()
                elif choice == "3":
                    self.view_resources_flow()
                elif choice == "4":
                    print("\nThank you for using Campus Reservation System. Goodbye!")
                    sys.exit(0)
                else:
                    print("\n[!] Invalid selection. Please enter 1-4.")
            else:
                print(f"\nLogged in as: {self.current_user.username} ({self.current_user.role.upper()})")
                print(" 1. Browse & Book Campus Resource")
                print(" 2. View My Active Reservations")
                print(" 3. Cancel a Reservation")
                if self.current_user.role == 'admin':
                    print(" 4. View System Analytics & Metrics")
                    print(" 5. Export Reservations CSV Report")
                print(" 6. Logout")

                choice = input("\nSelect Option: ").strip()

                if choice == "1":
                    self.book_resource_flow()
                elif choice == "2":
                    self.view_my_reservations_flow()
                elif choice == "3":
                    self.cancel_reservation_flow()
                elif choice == "4" and self.current_user.role == 'admin':
                    self.view_analytics_flow()
                elif choice == "5" and self.current_user.role == 'admin':
                    self.export_csv_flow()
                elif choice == "6" or (choice == "4" and self.current_user.role != 'admin'):
                    self.current_user = None
                    print("\n[+] Successfully logged out.")
                else:
                    print("\n[!] Invalid selection.")

    def register_flow(self):
        print("\n--- Student Registration ---")
        username = input("Enter Username: ").strip()
        email = input("Enter Campus Email: ").strip()
        password = input("Enter Password (min 6 chars): ").strip()
        try:
            user = self.auth.register_user(username, email, password)
            print(f"\n[+] Registration successful! Welcome, {user.username}.")
            self.current_user = user
        except ReservationSystemError as e:
            print(f"\n[!] Registration Error: {e}")

    def login_flow(self):
        print("\n--- Account Login ---")
        identifier = input("Username or Email: ").strip()
        password = input("Password: ").strip()
        try:
            user = self.auth.authenticate_user(identifier, password)
            print(f"\n[+] Login successful! Welcome back, {user.username}.")
            self.current_user = user
        except ReservationSystemError as e:
            print(f"\n[!] Login Failed: {e}")

    def view_resources_flow(self):
        print("\n--- Available Campus Resources ---")
        resources = self.engine.list_resources()
        print(f"{'ID':<4} | {'Name':<42} | {'Category':<14} | {'Cap':<4} | {'Location'}")
        print("-" * 80)
        for r in resources:
            print(f"{r.resource_id:<4} | {r.name:<42} | {r.category:<14} | {r.capacity:<4} | {r.location}")

    def book_resource_flow(self):
        self.view_resources_flow()
        try:
            res_id_input = input("\nEnter Resource ID to book: ").strip()
            if not res_id_input.isdigit():
                print("[!] Resource ID must be numeric.")
                return
            res_id = int(res_id_input)

            hours_ahead = float(input("Enter hours from now to START booking (e.g., 1 for 1 hr from now): "))
            duration = float(input("Enter booking duration in hours (e.g., 2): "))

            now = datetime.now()
            start_dt = now + timedelta(hours=hours_ahead)
            end_dt = start_dt + timedelta(hours=duration)

            reservation = self.engine.create_reservation(self.current_user.user_id, res_id, start_dt, end_dt)
            print(f"\n[+] SUCCESS! Booking confirmed.")
            print(f"    Reservation ID: #{reservation.reservation_id}")
            print(f"    Resource: {reservation.resource_name}")
            print(f"    Start Time: {reservation.start_datetime.strftime('%Y-%m-%d %H:%M')}")
            print(f"    End Time:   {reservation.end_datetime.strftime('%Y-%m-%d %H:%M')}")

        except ReservationSystemError as e:
            print(f"\n[!] Booking Conflict / Violation: {e}")
        except ValueError:
            print("\n[!] Invalid numerical input.")

    def view_my_reservations_flow(self):
        print(f"\n--- Reservations for {self.current_user.username} ---")
        reservations = self.engine.get_user_reservations(self.current_user.user_id)
        if not reservations:
            print("No reservations found.")
            return

        print(f"{'ID':<6} | {'Resource Name':<35} | {'Start Time':<16} | {'End Time':<16} | {'Status'}")
        print("-" * 85)
        for r in reservations:
            st = r.start_datetime.strftime('%Y-%m-%d %H:%M')
            et = r.end_datetime.strftime('%Y-%m-%d %H:%M')
            print(f"{r.reservation_id:<6} | {r.resource_name:<35} | {st:<16} | {et:<16} | {r.status}")

    def cancel_reservation_flow(self):
        self.view_my_reservations_flow()
        try:
            res_id_input = input("\nEnter Reservation ID to cancel: ").strip()
            if not res_id_input.isdigit():
                print("[!] Invalid ID format.")
                return
            res_id = int(res_id_input)
            is_admin = (self.current_user.role == 'admin')
            self.engine.cancel_reservation(res_id, self.current_user.user_id, is_admin)
            print(f"\n[+] Reservation #{res_id} successfully cancelled.")
        except ReservationSystemError as e:
            print(f"\n[!] Cancellation Failed: {e}")

    def view_analytics_flow(self):
        print("\n--- System Operational Analytics ---")
        metrics = self.analytics.get_summary_metrics()
        print(f" Total Registered Users:          {metrics['total_users']}")
        print(f" Total Active Facilities:         {metrics['active_resources']}")
        print(f" Confirmed Reservations:          {metrics['total_confirmed_reservations']}")
        print(f" Cancelled Reservations:          {metrics['total_cancelled_reservations']}")
        print(f" Top Booked Resource:             {metrics['most_popular_resource']} ({metrics['most_popular_count']} bookings)")

        print("\n--- Facility Usage Breakdown ---")
        breakdown = self.analytics.get_resource_usage_breakdown()
        for b in breakdown:
            print(f" - {b['resource_name']} [{b['category']}]: {b['total_bookings']} bookings")

    def export_csv_flow(self):
        filepath = "data/reservation_audit_report.csv"
        self.analytics.export_reservations_csv(filepath)
        print(f"\n[+] Exported detailed audit log to {filepath}")


if __name__ == "__main__":
    app = CampusReservationApp()
    app.main_menu()

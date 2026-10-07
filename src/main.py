"""Student Information System - main menu and application entry point.

Run from the project root:   python src/main.py
"""

import json
import os
import sys

# Make imports like `from models.student import Student` work when run directly
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SRC_DIR)
sys.path.insert(0, SRC_DIR)

from services.student_service import (  # noqa: E402
    StudentService, StudentServiceError)
from utils import validator  # noqa: E402
from utils.logger import setup_logger  # noqa: E402

CONFIG_PATH = os.path.join(BASE_DIR, "config", "config.json")

# Fallback settings used if config.json is missing or broken
DEFAULT_CONFIG = {
    "app_name": "Student Information System",
    "version": "1.0.0",
    "data_file": "data/students.json",
    "log_file": "logs/app.log",
    "export_dir": "exports",
    "max_students": 500,
    "min_year_level": 1,
    "max_year_level": 4,
    "id_pattern": r"^\d{4}-\d{3,4}$",
}


def load_config() -> dict:
    """Read config.json, falling back to defaults on any problem."""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return {**DEFAULT_CONFIG, **json.load(f)}
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Warning: could not load config ({exc}). Using defaults.")
        return dict(DEFAULT_CONFIG)


# ----------------------------------------------------------------------
# Display helpers
# ----------------------------------------------------------------------
def print_table(students: list) -> None:
    """Print students as a clean aligned table."""
    if not students:
        print("\n  No records found.")
        return
    header = f"{'ID':<10} {'Name':<22} {'Course':<28} {'Year':<5} {'Email'}"
    print("\n" + header)
    print("-" * len(header) + "-" * 12)
    for s in students:
        print(f"{s.student_id:<10} {s.name[:21]:<22} {s.course[:27]:<28} "
              f"{s.year_level:<5} {s.email}")
    print(f"\n  Total: {len(students)} record(s)")


def prompt(label: str, validate_fn, allow_blank: bool = False):
    """Ask repeatedly until input is valid (or blank, if allowed).
    Typing 'cancel' returns None so the user can back out."""
    while True:
        value = input(f"  {label}: ").strip()
        if value.lower() == "cancel":
            return None
        if allow_blank and value == "":
            return ""
        try:
            return validate_fn(value)
        except validator.ValidationError as exc:
            print(f"  ! {exc} (or type 'cancel')")


def show_menu(title: str) -> None:
    print("\n" + "=" * 50)
    print(f"  {title}")
    print("=" * 50)
    print("  1. Add New Student")
    print("  2. View All Students")
    print("  3. Search Student (by ID or Name)")
    print("  4. Update Student")
    print("  5. Delete Student")
    print("  6. Filter by Course or Year Level")
    print("  7. Export Data (JSON / CSV)")
    print("  0. Exit")
    print("-" * 50)


# ----------------------------------------------------------------------
# Menu actions
# ----------------------------------------------------------------------
def add_student(service: StudentService, cfg: dict) -> None:
    print("\n--- Add New Student (type 'cancel' to abort) ---")
    pattern = cfg["id_pattern"]
    lo, hi = cfg["min_year_level"], cfg["max_year_level"]
    sid = prompt("Student ID (e.g. 2024-001)",
                 lambda v: validator.validate_student_id(v, pattern))
    if sid is None:
        return
    name = prompt("Full name", validator.validate_name)
    if name is None:
        return
    course = prompt("Course", validator.validate_course)
    if course is None:
        return
    year = prompt(f"Year level ({lo}-{hi})",
                  lambda v: validator.validate_year_level(v, lo, hi))
    if year is None:
        return
    email = prompt("Email", validator.validate_email)
    if email is None:
        return
    student = service.add_student(sid, name, course, year, email)
    print(f"\n  Student {student.student_id} added successfully!")


def view_all(service: StudentService, cfg: dict) -> None:
    print("\n--- All Students ---")
    print_table(service.get_all())


def search_student(service: StudentService, cfg: dict) -> None:
    print("\n--- Search Student ---")
    print("  1. By ID\n  2. By Name")
    choice = input("  Choose: ").strip()
    if choice == "1":
        student = service.search_by_id(input("  Enter Student ID: "))
        print_table([student] if student else [])
    elif choice == "2":
        print_table(service.search_by_name(input("  Enter name (or part): ")))
    else:
        print("  Invalid choice.")


def update_student(service: StudentService, cfg: dict) -> None:
    print("\n--- Update Student ---")
    sid = input("  Enter Student ID to update: ").strip()
    student = service.search_by_id(sid)
    if not student:
        print("  Student not found.")
        return
    print_table([student])
    print("  Press Enter to keep the current value. Type 'cancel' to abort.")
    lo, hi = cfg["min_year_level"], cfg["max_year_level"]
    name = prompt("New name", validator.validate_name, allow_blank=True)
    if name is None:
        return
    course = prompt("New course", validator.validate_course, allow_blank=True)
    if course is None:
        return
    year = prompt(f"New year level ({lo}-{hi})",
                  lambda v: validator.validate_year_level(v, lo, hi),
                  allow_blank=True)
    if year is None:
        return
    email = prompt("New email", validator.validate_email, allow_blank=True)
    if email is None:
        return
    updated = service.update_student(
        student.student_id, name=name, course=course,
        year_level=year, email=email)
    print("\n  Student updated successfully!")
    print_table([updated])


def delete_student(service: StudentService, cfg: dict) -> None:
    print("\n--- Delete Student ---")
    sid = input("  Enter Student ID to delete: ").strip()
    student = service.search_by_id(sid)
    if not student:
        print("  Student not found.")
        return
    print_table([student])
    confirm = input("  Are you sure you want to delete this record? (y/n): ")
    if confirm.strip().lower() == "y":
        service.delete_student(student.student_id)
        print("  Student deleted.")
    else:
        print("  Deletion cancelled.")


def filter_students(service: StudentService, cfg: dict) -> None:
    print("\n--- Filter Students ---")
    print("  1. By Course\n  2. By Year Level")
    choice = input("  Choose: ").strip()
    if choice == "1":
        print_table(service.filter_by_course(input("  Course (or part): ")))
    elif choice == "2":
        print_table(service.filter_by_year(input("  Year level: ")))
    else:
        print("  Invalid choice.")


def export_data(service: StudentService, cfg: dict) -> None:
    print("\n--- Export Data ---")
    fmt = input("  Format (json/csv) [json]: ").strip() or "json"
    path = service.export_data(fmt)
    print(f"  Exported to: {path}")


# ----------------------------------------------------------------------
# Main loop
# ----------------------------------------------------------------------
ACTIONS = {
    "1": add_student, "2": view_all, "3": search_student,
    "4": update_student, "5": delete_student,
    "6": filter_students, "7": export_data,
}


def main() -> None:
    cfg = load_config()
    log_path = cfg["log_file"]
    if not os.path.isabs(log_path):
        log_path = os.path.join(BASE_DIR, log_path)
    logger = setup_logger(log_path)
    logger.info("Application started")

    service = StudentService(cfg, BASE_DIR)
    title = f"{cfg['app_name']} v{cfg['version']}"

    while True:
        show_menu(title)
        try:
            choice = input("  Enter choice: ").strip()
            if choice == "0":
                break
            action = ACTIONS.get(choice)
            if action is None:
                print("  Invalid choice. Please enter a number from 0 to 7.")
                continue
            action(service, cfg)
        except StudentServiceError as exc:
            # Expected problems (duplicates, not found, save errors)
            logger.error("Service error: %s", exc)
            print(f"\n  Error: {exc}")
        except validator.ValidationError as exc:
            logger.error("Validation error: %s", exc)
            print(f"\n  Invalid input: {exc}")
        except (KeyboardInterrupt, EOFError):
            print("\n  Input interrupted.")
            break
        except Exception as exc:  # last-resort safety net: never crash
            logger.exception("Unexpected error: %s", exc)
            print(f"\n  Unexpected error: {exc}. See logs/app.log.")

    logger.info("Application closed")
    print("\n  Goodbye!\n")


if __name__ == "__main__":
    main()

"""Student service: all CRUD logic plus search, filter and export.

Records are kept in memory and saved to a JSON file after every change.
"""

import csv
import json
import os
import shutil
from datetime import datetime

from models.student import Student
from utils import validator
from utils.logger import get_logger


# ---- Custom exceptions give clear, specific error messages ----
class StudentServiceError(Exception):
    """Base class for service errors."""


class DuplicateStudentError(StudentServiceError):
    """Raised when adding a student whose ID already exists."""


class StudentNotFoundError(StudentServiceError):
    """Raised when a student ID does not exist."""


class StudentService:
    """Create, read, update, delete and export student records."""

    def __init__(self, config: dict, base_dir: str):
        self.config = config
        self.base_dir = base_dir
        self.data_file = self._resolve(config["data_file"])
        self.export_dir = self._resolve(config.get("export_dir", "exports"))
        self.log = get_logger()
        self.students = []          # list of Student objects
        self.load()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _resolve(self, path: str) -> str:
        """Turn a config path into an absolute path under the project root."""
        return path if os.path.isabs(path) else os.path.join(self.base_dir, path)

    def _find(self, student_id: str):
        """Return the Student with this ID, or None."""
        for student in self.students:
            if student.student_id.lower() == student_id.lower():
                return student
        return None

    # ------------------------------------------------------------------
    # Storage (JSON)
    # ------------------------------------------------------------------
    def load(self) -> None:
        """Load students from the JSON file; recover gracefully on errors."""
        if not os.path.exists(self.data_file):
            self.log.info("Data file not found. Starting with empty list.")
            self.students = []
            self.save()
            return
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                raw = json.load(f)
            self.students = [Student.from_dict(item) for item in raw]
            self.log.info("Loaded %d student(s) from %s",
                          len(self.students), self.data_file)
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            # Corrupted file: keep a backup and start fresh instead of crashing
            backup = self.data_file + ".corrupt.bak"
            shutil.copy(self.data_file, backup)
            self.log.error("Corrupted data file (%s). Backup saved to %s",
                           exc, backup)
            print(f"Warning: data file was corrupted. Backup saved to {backup}.")
            self.students = []
        except OSError as exc:
            self.log.error("Could not read data file: %s", exc)
            print(f"Error: could not read data file ({exc}).")
            self.students = []

    def save(self) -> None:
        """Write all students to the JSON file (temp file then replace,
        so a crash mid-write cannot damage existing data)."""
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            tmp_path = self.data_file + ".tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump([s.to_dict() for s in self.students], f, indent=2)
            os.replace(tmp_path, self.data_file)
        except OSError as exc:
            self.log.error("Failed to save data: %s", exc)
            raise StudentServiceError(f"Could not save data: {exc}")

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------
    def add_student(self, student_id, name, course, year_level, email) -> Student:
        """Validate input, block duplicate IDs, then save the new student."""
        cfg = self.config
        student = Student(
            student_id=validator.validate_student_id(
                student_id, cfg.get("id_pattern", r"^\d{4}-\d{3,4}$")),
            name=validator.validate_name(name),
            course=validator.validate_course(course),
            year_level=validator.validate_year_level(
                year_level, cfg.get("min_year_level", 1),
                cfg.get("max_year_level", 4)),
            email=validator.validate_email(email),
        )
        if len(self.students) >= cfg.get("max_students", 500):
            raise StudentServiceError("Maximum number of students reached.")
        if self._find(student.student_id):                  # duplicate prevention
            raise DuplicateStudentError(
                f"Student ID {student.student_id} already exists.")
        self.students.append(student)
        self.save()
        self.log.info("ADD student %s (%s)", student.student_id, student.name)
        return student

    def get_all(self) -> list:
        """Return all students sorted by ID."""
        return sorted(self.students, key=lambda s: s.student_id)

    def search_by_id(self, student_id: str):
        """Exact (case-insensitive) ID lookup. Returns Student or None."""
        student = self._find(validator.validate_not_empty(student_id, "Student ID"))
        self.log.info("SEARCH by id '%s' -> %s", student_id,
                      "found" if student else "not found")
        return student

    def search_by_name(self, keyword: str) -> list:
        """Case-insensitive partial name match."""
        keyword = validator.validate_not_empty(keyword, "Name").lower()
        results = [s for s in self.get_all() if keyword in s.name.lower()]
        self.log.info("SEARCH by name '%s' -> %d result(s)", keyword, len(results))
        return results

    def filter_by_course(self, course: str) -> list:
        """Partial, case-insensitive course filter."""
        course = validator.validate_not_empty(course, "Course").lower()
        results = [s for s in self.get_all() if course in s.course.lower()]
        self.log.info("FILTER by course '%s' -> %d result(s)", course, len(results))
        return results

    def filter_by_year(self, year_level) -> list:
        """Filter by exact year level."""
        year = validator.validate_year_level(
            year_level, self.config.get("min_year_level", 1),
            self.config.get("max_year_level", 4))
        results = [s for s in self.get_all() if s.year_level == year]
        self.log.info("FILTER by year %d -> %d result(s)", year, len(results))
        return results

    def update_student(self, student_id: str, **changes) -> Student:
        """Update only the provided fields (None/empty values are skipped)."""
        student = self._find(student_id)
        if not student:
            raise StudentNotFoundError(f"Student ID {student_id} not found.")

        cfg = self.config
        # Validate everything first so a bad value changes nothing
        validated = {}
        if changes.get("name"):
            validated["name"] = validator.validate_name(changes["name"])
        if changes.get("course"):
            validated["course"] = validator.validate_course(changes["course"])
        if changes.get("year_level") not in (None, ""):
            validated["year_level"] = validator.validate_year_level(
                changes["year_level"], cfg.get("min_year_level", 1),
                cfg.get("max_year_level", 4))
        if changes.get("email"):
            validated["email"] = validator.validate_email(changes["email"])

        for field, value in validated.items():
            setattr(student, field, value)
        self.save()
        self.log.info("UPDATE student %s fields=%s", student.student_id,
                      list(validated.keys()) or "none")
        return student

    def delete_student(self, student_id: str) -> Student:
        """Remove a student by ID."""
        student = self._find(student_id)
        if not student:
            raise StudentNotFoundError(f"Student ID {student_id} not found.")
        self.students.remove(student)
        self.save()
        self.log.info("DELETE student %s (%s)", student.student_id, student.name)
        return student

    # ------------------------------------------------------------------
    # Export (bonus)
    # ------------------------------------------------------------------
    def export_data(self, fmt: str = "json") -> str:
        """Save a copy of all records to exports/ and return the file path."""
        fmt = fmt.lower().strip()
        if fmt not in ("json", "csv"):
            raise StudentServiceError("Export format must be 'json' or 'csv'.")
        try:
            os.makedirs(self.export_dir, exist_ok=True)
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = os.path.join(self.export_dir, f"students_export_{stamp}.{fmt}")
            rows = [s.to_dict() for s in self.get_all()]
            if fmt == "json":
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(rows, f, indent=2)
            else:
                with open(path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(
                        f, fieldnames=["student_id", "name", "course",
                                       "year_level", "email"])
                    writer.writeheader()
                    writer.writerows(rows)
        except OSError as exc:
            self.log.error("Export failed: %s", exc)
            raise StudentServiceError(f"Export failed: {exc}")
        self.log.info("EXPORT %d record(s) to %s", len(rows), path)
        return path

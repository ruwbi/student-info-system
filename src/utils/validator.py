"""Input validation helpers. Each function returns a cleaned value or
raises ValidationError with a friendly message."""

import re


class ValidationError(ValueError):
    """Raised when user input fails validation."""


def validate_not_empty(value, field_name: str) -> str:
    """Reject empty / whitespace-only values."""
    if value is None or not str(value).strip():
        raise ValidationError(f"{field_name} cannot be empty.")
    return str(value).strip()


def validate_student_id(value, pattern: str = r"^\d{4}-\d{3,4}$") -> str:
    """Student ID must match the pattern, e.g. 2024-001."""
    value = validate_not_empty(value, "Student ID")
    if not re.match(pattern, value):
        raise ValidationError(
            "Invalid Student ID format. Use YYYY-NNN (example: 2024-001).")
    return value


def validate_name(value) -> str:
    """Names: letters, spaces, dots, hyphens and apostrophes only."""
    value = validate_not_empty(value, "Name")
    if not re.match(r"^[A-Za-z][A-Za-z .'\-]*$", value):
        raise ValidationError(
            "Name may only contain letters, spaces, '.', '-' and apostrophes.")
    return value


def validate_course(value) -> str:
    """Course must not be empty."""
    return validate_not_empty(value, "Course")


def validate_year_level(value, min_year: int = 1, max_year: int = 4) -> int:
    """Year level must be a whole number within the allowed range."""
    value = validate_not_empty(value, "Year level")
    try:
        year = int(value)
    except (TypeError, ValueError):
        raise ValidationError("Year level must be a number (e.g. 1, 2, 3, 4).")
    if not min_year <= year <= max_year:
        raise ValidationError(
            f"Year level must be between {min_year} and {max_year}.")
    return year


def validate_email(value) -> str:
    """Basic email format check (name@domain.tld)."""
    value = validate_not_empty(value, "Email")
    if not re.match(r"^[\w.+\-]+@[\w\-]+(\.[\w\-]+)+$", value):
        raise ValidationError(
            "Invalid email format (example: name@example.com).")
    return value

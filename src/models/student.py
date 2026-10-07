"""Student model: a simple data class representing one student record."""

from dataclasses import dataclass, asdict


@dataclass
class Student:
    """Holds the information stored for a single student."""

    student_id: str
    name: str
    course: str
    year_level: int
    email: str

    def to_dict(self) -> dict:
        """Convert the student to a plain dict (for JSON saving)."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Student":
        """Build a Student from a dict loaded from JSON."""
        return cls(
            student_id=str(data["student_id"]),
            name=str(data["name"]),
            course=str(data["course"]),
            year_level=int(data["year_level"]),
            email=str(data["email"]),
        )

    def __str__(self) -> str:
        return (f"[{self.student_id}] {self.name} | {self.course} | "
                f"Year {self.year_level} | {self.email}")

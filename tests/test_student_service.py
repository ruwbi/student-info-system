"""Unit tests for StudentService. Run with:  python -m unittest discover tests
Each test uses a temporary folder, so real data is never touched."""

import json
import os
import sys
import tempfile
import unittest

# Allow imports from src/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from services.student_service import (  # noqa: E402
    DuplicateStudentError, StudentNotFoundError, StudentService)
from utils import validator  # noqa: E402
from utils.logger import setup_logger  # noqa: E402

CONFIG = {
    "data_file": "data/students.json",
    "export_dir": "exports",
    "max_students": 500,
    "min_year_level": 1,
    "max_year_level": 4,
    "id_pattern": r"^\d{4}-\d{3,4}$",
}


class StudentServiceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        setup_logger(os.path.join(self.tmp.name, "logs", "test.log"))
        self.service = StudentService(dict(CONFIG), self.tmp.name)

    def tearDown(self):
        # Close log handlers so Windows can delete the temp folder
        import logging
        for h in list(logging.getLogger("student_info_system").handlers):
            h.close()
            logging.getLogger("student_info_system").removeHandler(h)
        self.tmp.cleanup()

    def _add(self, sid="2024-001", name="Test User", course="BSCS",
             year=1, email="t@example.com"):
        return self.service.add_student(sid, name, course, year, email)

    def test_add_and_get_all(self):
        self._add()
        self.assertEqual(len(self.service.get_all()), 1)

    def test_data_persisted_to_json(self):
        self._add()
        with open(self.service.data_file, encoding="utf-8") as f:
            self.assertEqual(json.load(f)[0]["student_id"], "2024-001")

    def test_duplicate_id_rejected(self):
        self._add()
        with self.assertRaises(DuplicateStudentError):
            self._add(name="Another Person")

    def test_invalid_year_rejected(self):
        with self.assertRaises(validator.ValidationError):
            self._add(year=5)
        with self.assertRaises(validator.ValidationError):
            self._add(year="abc")

    def test_invalid_id_and_empty_fields(self):
        with self.assertRaises(validator.ValidationError):
            self._add(sid="ABC")
        with self.assertRaises(validator.ValidationError):
            self._add(name="   ")

    def test_invalid_email_rejected(self):
        with self.assertRaises(validator.ValidationError):
            self._add(email="not-an-email")

    def test_search_by_id_and_name(self):
        self._add(name="Maria Santos")
        self.assertIsNotNone(self.service.search_by_id("2024-001"))
        self.assertIsNone(self.service.search_by_id("1999-999"))
        self.assertEqual(len(self.service.search_by_name("mari")), 1)

    def test_update_student(self):
        self._add()
        self.service.update_student("2024-001", name="New Name", year_level="3")
        student = self.service.search_by_id("2024-001")
        self.assertEqual((student.name, student.year_level), ("New Name", 3))

    def test_update_invalid_changes_nothing(self):
        self._add()
        with self.assertRaises(validator.ValidationError):
            self.service.update_student("2024-001", name="Good Name",
                                        year_level="9")
        self.assertEqual(self.service.search_by_id("2024-001").name, "Test User")

    def test_update_missing_student(self):
        with self.assertRaises(StudentNotFoundError):
            self.service.update_student("2024-999", name="X Y")

    def test_delete_student(self):
        self._add()
        self.service.delete_student("2024-001")
        self.assertEqual(self.service.get_all(), [])
        with self.assertRaises(StudentNotFoundError):
            self.service.delete_student("2024-001")

    def test_filters(self):
        self._add("2024-001", course="BS Computer Science", year=1)
        self._add("2024-002", course="BS Nursing", year=2)
        self.assertEqual(len(self.service.filter_by_course("nursing")), 1)
        self.assertEqual(len(self.service.filter_by_year(2)), 1)

    def test_export_json_and_csv(self):
        self._add()
        for fmt in ("json", "csv"):
            path = self.service.export_data(fmt)
            self.assertTrue(os.path.exists(path))

    def test_corrupted_file_recovers(self):
        self._add()
        with open(self.service.data_file, "w") as f:
            f.write("{ broken json")
        recovered = StudentService(dict(CONFIG), self.tmp.name)
        self.assertEqual(recovered.get_all(), [])


if __name__ == "__main__":
    unittest.main()

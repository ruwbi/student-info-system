# 🎓 Student Information System

A console-based **Student Information System** written in Python 3, with JSON
file storage, logging, input validation and a GitHub-ready project layout.
Built as a cloud computing lab activity.

**Author:** Ruby-Lynn M. Busto
**Course / Section:** BSIT-3A
**Date:** October 7, 2026

---

## 📌 Purpose

Manage student records (add, view, search, update, delete) from the terminal.
The project demonstrates modular design, configuration files, error handling,
logging and Git/GitHub workflow — using **only the Python standard library**
and **JSON files** (no databases, no web frameworks).

## ✨ Features

- **Add** a student (ID, name, course, year level, email)
- **View all** students in a clean table
- **Search** by student ID or by name (partial, case-insensitive)
- **Update** any field (press Enter to keep the current value)
- **Delete** with a confirmation prompt
- **Filter** by course or year level *(bonus)*
- **Export** all records to JSON or CSV in `exports/` *(bonus)*
- **Duplicate ID prevention** *(bonus)*
- **Input validation** with friendly messages: no empty fields, ID format
  `YYYY-NNN`, year level 1–4, valid email
- **Logging** of every add/update/delete/search and all errors → `logs/app.log`
- **Config file** (`config/config.json`) for paths and limits
- **Graceful error handling** (corrupted JSON is backed up, app never crashes)
- **Unit tests** (14 tests, run on a temporary folder) *(bonus)*

## 📁 Folder Structure

```
student-info-system/
├── src/
│   ├── models/
│   │   └── student.py          # Student class/model
│   ├── services/
│   │   └── student_service.py  # CRUD, search, filter, export logic
│   ├── utils/
│   │   ├── logger.py           # Logging system
│   │   └── validator.py        # Data validation
│   └── main.py                 # Main menu & app entry
├── data/
│   └── students.json           # All student records
├── config/
│   └── config.json             # App settings
├── logs/
│   └── app.log                 # Auto-generated log file
├── tests/
│   └── test_student_service.py # Unit tests
├── README.md
├── requirements.txt
└── .gitignore
```

## ⚙️ Installation & Running

**Requirements:** Python 3.8 or newer. No extra packages needed.

```bash
# 1. Clone the repository
git clone https://github.com/ruwbi/student-info-system.git
cd student-info-system

# 2. (Optional) install dependencies - there are none beyond the standard library
pip install -r requirements.txt

# 3. Run the app from the project root
python src/main.py          # use python3 on macOS/Linux if needed
```

### Run the tests

```bash
python -m unittest discover tests
```

## 🔧 Configuration (`config/config.json`)

| Setting | Meaning | Default |
|---|---|---|
| `data_file` | Where records are stored | `data/students.json` |
| `log_file` | Log file location | `logs/app.log` |
| `export_dir` | Folder for exported files | `exports` |
| `max_students` | Maximum records allowed | `500` |
| `min_year_level` / `max_year_level` | Allowed year range | `1` / `4` |
| `id_pattern` | Regex for valid student IDs | `^\d{4}-\d{3,4}$` |

## 💻 Example Usage

```
==================================================
  Student Information System v1.0.0
==================================================
  1. Add New Student
  2. View All Students
  3. Search Student (by ID or Name)
  4. Update Student
  5. Delete Student
  6. Filter by Course or Year Level
  7. Export Data (JSON / CSV)
  0. Exit
--------------------------------------------------
  Enter choice: 1

--- Add New Student (type 'cancel' to abort) ---
  Student ID (e.g. 2024-001): 2024-010
  Full name: Carlo Mendoza
  Course: BS Information Technology
  Year level (1-4): 2
  Email: carlo.mendoza@example.com

  Student 2024-010 added successfully!
```

Viewing all students:

```
ID         Name                   Course                       Year  Email
------------------------------------------------------------------------------
2023-015   Ana Reyes              BS Computer Science          4     ana.reyes@example.com
2024-001   Maria Santos           BS Computer Science          2     maria.santos@example.com
2024-002   Juan Dela Cruz         BS Information Technology    3     juan.delacruz@example.com

  Total: 3 record(s)
```

Sample log (`logs/app.log`):

```
2026-10-05 10:15:02 | INFO    | Application started
2026-10-05 10:15:20 | INFO    | ADD student 2024-010 (Carlo Mendoza)
2026-10-05 10:16:05 | ERROR   | Service error: Student ID 2024-010 already exists.
```

## 🚀 Pushing to GitHub

See the Git commands in the project guide (or run the commands below):

```bash
git init
git add .
git commit -m "Initial commit: Student Information System"
git branch -M main
git remote add origin https://github.com/ruwbi/student-info-system.git
git push -u origin main
```



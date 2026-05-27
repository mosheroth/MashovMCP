---
name: mashov
description: >
  Fetch student data from the Mashov school management system.
  Use for grades, homework, timetable, attendance (behave), groups,
  files, class directory (alfon), progress tracking (maakav), lessons history,
  and listing children (for parent accounts). Credentials must be set in
  .env in the project root before first use.
---

# Mashov School Data Skill

Retrieve student data from the Mashov API using the runner script.

## Credentials Setup (first time only)

Fill in `.env` in the project root:
```
MASHOV_USERNAME=your_username
MASHOV_PASSWORD=your_password
MASHOV_SEMEL=your_school_id
MASHOV_YEAR=2025
```

To find your school's SEMEL, run the `schools` operation (requires credentials).

## How to Run

Use Bash to invoke the runner from the project root:

```
cd <project-root> && .venv\Scripts\python.exe runner.py <operation> [flags]
```

The project root is the directory containing `runner.py`. Use the `pwd` or check
the current workspace to determine the correct path.

## Available Operations

| Operation  | Description                                        |
|------------|----------------------------------------------------|
| `grades`   | All grades (optionally filter by subject)          |
| `homework` | Homework assignments                               |
| `timetable`| Class schedule                                     |
| `behave`   | Attendance and behavior events                     |
| `groups`   | Groups/classes the student belongs to              |
| `files`    | Files shared with the student                      |
| `alfon`    | Class directory with classmates' contact info      |
| `maakav`   | Progress tracking info                             |
| `lessons`  | Lessons history (topics, dates, teachers)          |
| `schools`  | List all schools                                   |
| `children` | List all children (parent accounts only)           |

## Optional Flags

All operations support:
- `--child_name NAME` — child's first name (for parent accounts)
- `--child_guid GUID` — child's GUID (for parent accounts)
- `--subject SUBJECT` — filter grades by subject name (`grades` only)
- `--days N` — filter by last N days (homework only)

## Examples

```bash
# Basic operations
.venv\Scripts\python.exe runner.py homework
.venv\Scripts\python.exe runner.py children
.venv\Scripts\python.exe runner.py timetable

# With filters
.venv\Scripts\python.exe runner.py grades --subject מתמטיקה
.venv\Scripts\python.exe runner.py homework --child_name ישראל
.venv\Scripts\python.exe runner.py homework --child_name ישראל --days 7
.venv\Scripts\python.exe runner.py behave --days 30
```

## Workflow

1. Locate project root (directory containing `runner.py`) and `cd` to it
2. Determine user's intent (operation + filters)
   - If asking for recent homework: use `--days N`
   - If asking for specific child: use `--child_name NAME` or `--child_guid GUID`
   - If asking for specific subject: use `--subject SUBJECT`
3. Run `.venv\Scripts\python.exe runner.py <operation> [flags]`
4. Parse JSON output
5. Present data in clear, readable format
6. If Hebrew text appears, display as-is (do not transliterate)
7. If credentials missing, instruct user to fill in `.env`
8. If user asks what children available, run `children` operation first

the output of this skill is:

look for the children homework from the last 4 days. and print them out in the following format:

**Format:**
```
📝 סיכום שעורי בית - [תאריך]

🔴 למחר ([תאריך]):

**זיו (כיתה ד'):**
- [מקצוע]: [תיאור] (ניתן ב-[תאריך])

**עידו (כיתה א'):**  
- [מקצוע]: [תיאור] (ניתן ב-[תאריך])

🟡 למחרתיים ([תאריך]):
[...]
```

prioritise and bold what is due for tomorrow.
dont' write notes in the response or thoughts. 
be very percise and to the point.
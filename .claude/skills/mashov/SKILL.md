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
cd <project-root> && .venv\Scripts\python.exe runner.py <operation> [json_kwargs]
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

## Optional JSON kwargs (2nd argument)

Most operations accept optional filters as a JSON string:
- `child_name` — child's first name (for parent accounts)
- `child_guid` — child's GUID (for parent accounts)
- `subject` — filter grades by subject name (`grades` only)

## Examples

```bash
.venv\Scripts\python.exe runner.py homework
.venv\Scripts\python.exe runner.py grades "{\"subject\": \"מתמטיקה\"}"
.venv\Scripts\python.exe runner.py children
.venv\Scripts\python.exe runner.py homework "{\"child_name\": \"ישראל\"}"
```

## Workflow

1. Locate project root (directory containing `runner.py`) and `cd` to it
2. Run `.venv\Scripts\python.exe runner.py <operation> [json_kwargs]`
3. Parse the JSON output
4. Present the data in a clear, readable format to the user
5. If Hebrew text appears, display it as-is (do not transliterate)
6. If credentials are missing, instruct user to fill in `.env`
7. If the user asks what children are available, run `children` operation first

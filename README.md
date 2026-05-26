# Mashov Skill

Claude Code skill for the [Mashov](https://web.mashov.info) school management system.

## Setup

**1. Install dependencies**
```bash
uv venv && uv pip install -e .
```

**2. Fill in credentials** — edit `.env`:
```
MASHOV_USERNAME=your_username
MASHOV_PASSWORD=your_password
MASHOV_SEMEL=your_school_id
MASHOV_YEAR=2025
```

**3. Install the skill** — copy `~/.claude/skills/mashov/SKILL.md` (already done if you followed setup).

## Usage

### Claude Code (skill)

Invoke the skill, then ask naturally:

```
/mashov what homework do I have?
/mashov show me my grades in math
/mashov what's my timetable this week?
/mashov list my children
```

Claude reads `SKILL.md`, runs `runner.py` via Bash with the right operation and kwargs, parses the JSON response, and presents the data in plain language.

### Direct CLI

```bash
.venv/Scripts/python.exe runner.py <operation>
```

## Operations

| Operation  | Description                              |
|------------|------------------------------------------|
| `grades`   | All grades (optional: `subject` filter)  |
| `homework` | Homework assignments                     |
| `timetable`| Class schedule                           |
| `behave`   | Attendance and behavior events           |
| `groups`   | Groups/classes                           |
| `files`    | Files shared with student                |
| `alfon`    | Class directory                          |
| `maakav`   | Progress tracking                        |
| `lessons`  | Lessons history                          |
| `schools`  | List all schools                         |
| `children` | List children (parent accounts)          |

Optional JSON kwargs as 2nd arg:
```bash
.venv/Scripts/python.exe runner.py grades "{\"subject\": \"מתמטיקה\"}"
.venv/Scripts/python.exe runner.py homework "{\"child_name\": \"ישראל\"}"
```

## Files

| File                | Purpose                        |
|---------------------|--------------------------------|
| `mashov_client.py`  | Mashov API async client        |
| `config.py`         | Credential loading from `.env` |
| `runner.py`         | CLI entry point                |
| `test_runner.py`    | Quick test (VS Code F5)        |
| `AUTHENTICATION.md` | API auth flow reference        |

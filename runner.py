#!/usr/bin/env python3
"""
Mashov API CLI runner for Claude Code skill.
Usage: uv run python runner.py <operation> [json_kwargs]

Operations: grades, homework, timetable, behave, groups,
            files, alfon, maakav, lessons, schools, children
"""

import asyncio
import json
import os
import sys

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Force UTF-8 output on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from mashov_client import MashovClient
from config import load_config


OPERATIONS = {
    "grades":    lambda c, **kw: c.get_all_grades(**kw),
    "homework":  lambda c, **kw: c.get_homework(**kw),
    "timetable": lambda c, **kw: c.get_timetable(**kw),
    "behave":    lambda c, **kw: c.get_behave(**kw),
    "groups":    lambda c, **kw: c.get_groups(**kw),
    "files":     lambda c, **kw: c.get_files(**kw),
    "alfon":     lambda c, **kw: c.get_alfon(**kw),
    "maakav":    lambda c, **kw: c.get_maakav(**kw),
    "lessons":   lambda c, **kw: c.get_lessons_history(**kw),
    "schools":   lambda c, **kw: c.get_schools(),
}


async def main():
    if len(sys.argv) < 2 or sys.argv[1] == "help":
        print("Operations: " + ", ".join(list(OPERATIONS.keys()) + ["children"]))
        print("Optional 2nd arg: JSON kwargs, e.g. '{\"child_name\": \"ישראל\"}'")
        return

    op = sys.argv[1]
    kwargs = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}

    configured = load_config()
    if not configured:
        print("ERROR: Missing credentials. Create .env file at:", file=sys.stderr)
        print(f"  {os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')}", file=sys.stderr)
        print("With: MASHOV_USERNAME, MASHOV_PASSWORD, MASHOV_SEMEL, MASHOV_YEAR", file=sys.stderr)
        sys.exit(1)

    client = MashovClient.get_instance()

    try:
        if op == "children":
            await client._ensure_authenticated()
            result = client.get_children()
        elif op in OPERATIONS:
            result = await OPERATIONS[op](client, **kwargs)
        else:
            print(f"Unknown operation: {op}", file=sys.stderr)
            print("Operations: " + ", ".join(list(OPERATIONS.keys()) + ["children"]), file=sys.stderr)
            sys.exit(1)

        print(json.dumps(result, ensure_ascii=False, indent=2))
    finally:
        await client.close()


asyncio.run(main())

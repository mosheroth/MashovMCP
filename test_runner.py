#!/usr/bin/env python3
"""
Quick test: authenticate and run one operation per category.
Edit TESTS list to enable/disable operations.
"""

import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mashov_client import MashovClient
from config import load_config


TESTS = [
    "children",    # list children (parent accounts) — good first check
    "grades",
    "homework",
    "timetable",
    "behave",
    "groups",
    # "files",
    # "alfon",
    # "maakav",
    # "lessons",
    # "schools",
]

OPERATIONS = {
    "grades":    lambda c: c.get_all_grades(),
    "homework":  lambda c: c.get_homework(),
    "timetable": lambda c: c.get_timetable(),
    "behave":    lambda c: c.get_behave(),
    "groups":    lambda c: c.get_groups(),
    "files":     lambda c: c.get_files(),
    "alfon":     lambda c: c.get_alfon(),
    "maakav":    lambda c: c.get_maakav(),
    "lessons":   lambda c: c.get_lessons_history(),
    "schools":   lambda c: c.get_schools(),
}


async def main():
    configured = load_config()
    if not configured:
        print("ERROR: Fill in .env with MASHOV_USERNAME, MASHOV_PASSWORD, MASHOV_SEMEL, MASHOV_YEAR")
        sys.exit(1)

    client = MashovClient.get_instance()

    print("Logging in...")
    await client.login()
    print(f"OK — student_guid: {client.student_guid}")
    print()

    for op in TESTS:
        print(f"--- {op} ---")
        try:
            if op == "children":
                result = client.get_children()
            else:
                result = await OPERATIONS[op](client)

            if isinstance(result, list):
                print(f"{len(result)} items")
                if result:
                    print(json.dumps(result[0], ensure_ascii=False, indent=2))
            else:
                print(json.dumps(result, ensure_ascii=False, indent=2))
        except Exception as e:
            print(f"FAILED: {e}")
        print()

    await client.close()


asyncio.run(main())

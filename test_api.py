#!/usr/bin/env python3
"""
Test script for Mashov API Client
Tests the API endpoints without requiring MCP
"""

import asyncio
import json
import os
import sys
from dotenv import load_dotenv
from mashov_client import MashovClient


async def test_api():
    """Test Mashov API endpoints"""
    # Load environment variables
    load_dotenv()
    
    # Get credentials
    username = os.getenv("MASHOV_USERNAME")
    password = os.getenv("MASHOV_PASSWORD")
    semel = os.getenv("MASHOV_SEMEL")
    year = os.getenv("MASHOV_YEAR")
    
    if not all([username, password, semel, year]):
        print("❌ Error: Missing credentials in .env file")
        print("Please create a .env file with:")
        print("  MASHOV_USERNAME=your_username")
        print("  MASHOV_PASSWORD=your_password")
        print("  MASHOV_SEMEL=your_school_id")
        print("  MASHOV_YEAR=2024")
        sys.exit(1)
    
    print("🔐 Testing Mashov API Client\n")
    print(f"Username: {username}")
    print(f"School ID (Semel): {semel}")
    print(f"Year: {year}\n")
    
    client = MashovClient.get_instance()
    client.configure(username, password, semel, year)
    
    # Test authentication
    print("=" * 60)
    print("1. Testing Authentication...")
    print("=" * 60)
    try:
        result = await client.login()
        if result:
            print("✅ Authentication successful!")
            print(f"   Authenticated: {client.is_authenticated()}")
            if client.csrf_token:
                print(f"   CSRF Token: {client.csrf_token[:20]}...")
        else:
            print("❌ Authentication failed")
            return
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return
    
    print()
    
    # Test endpoints - only working ones
    tests = [
        ("get_all_grades", lambda: client.get_all_grades(), "Get All Grades"),
        ("get_schools", lambda: client.get_schools(), "Get Schools"),
        ("get_homework", lambda: client.get_homework(), "Get Homework"),
        ("get_alfon", lambda: client.get_alfon(), "Get Class Directory (Alfon)"),
        ("get_behave", lambda: client.get_behave(), "Get Behavior Events"),
        ("get_files", lambda: client.get_files(), "Get Files"),
        ("get_groups", lambda: client.get_groups(), "Get Groups"),
        ("get_timetable", lambda: client.get_timetable(), "Get Timetable"),
        ("get_maakav", lambda: client.get_maakav(), "Get Maakav"),
        ("get_lessons_history", lambda: client.get_lessons_history(), "Get Lessons History"),
    ]
    
    results = {}
    
    for test_name, test_func, description in tests:
        print("=" * 60)
        print(f"{len(results) + 2}. Testing {description}...")
        print("=" * 60)
        try:
            result = await test_func()
            results[test_name] = {"success": True, "data": result}
            print(f"✅ {description} - Success!")
            
            # Pretty print the result
            if isinstance(result, dict):
                print(f"   Response keys: {list(result.keys())[:10]}")
                if len(result) <= 5:
                    print(f"   Data: {json.dumps(result, indent=2, ensure_ascii=False)[:500]}")
            elif isinstance(result, list):
                print(f"   Response: List with {len(result)} items")
                if len(result) > 0 and len(result) <= 3:
                    print(f"   First item: {json.dumps(result[0], indent=2, ensure_ascii=False)[:500]}")
            else:
                print(f"   Response: {str(result)[:200]}")
        except Exception as e:
            results[test_name] = {"success": False, "error": str(e)}
            print(f"❌ {description} - Failed: {e}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")
        
        print()
    
    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    successful = sum(1 for r in results.values() if r.get("success"))
    total = len(results)
    print(f"✅ Successful: {successful}/{total}")
    print(f"❌ Failed: {total - successful}/{total}\n")
    
    for test_name, result in results.items():
        status = "✅" if result.get("success") else "❌"
        print(f"{status} {test_name}")
    
    # Cleanup
    await client.close()
    
    return results


if __name__ == "__main__":
    try:
        results = asyncio.run(test_api())
        # Exit with error code if any tests failed
        if any(not r.get("success") for r in results.values()):
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


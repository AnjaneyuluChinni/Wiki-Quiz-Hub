#!/usr/bin/env python3
"""
Quick test script to verify FastAPI backend is working correctly.
Run this after starting the backend to test all endpoints.
"""

import requests
import json
import sys
from typing import Dict, Any

BASE_URL = "http://localhost:8000"
TIMEOUT = 10


def print_header(title: str):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def print_success(message: str):
    """Print success message."""
    print(f"✅ {message}")


def print_error(message: str):
    """Print error message."""
    print(f"❌ {message}")


def print_info(message: str):
    """Print info message."""
    print(f"ℹ️  {message}")


def test_health_check() -> bool:
    """Test health check endpoint."""
    print_header("Testing Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            print_success("Health check passed")
            return True
        else:
            print_error(f"Expected 200, got {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Failed: {str(e)}")
        return False


def test_api_root() -> bool:
    """Test API root endpoint."""
    print_header("Testing API Root")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            print_success("API root endpoint working")
            return True
        else:
            print_error(f"Expected 200, got {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Failed: {str(e)}")
        return False


def test_list_quizzes() -> bool:
    """Test GET /api/quizzes endpoint."""
    print_header("Testing List Quizzes")
    try:
        response = requests.get(f"{BASE_URL}/api/quizzes", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            count = len(data)
            print(f"Found {count} quizzes")
            if count > 0:
                print(f"\nFirst quiz: {json.dumps(data[0], indent=2, default=str)}")
            print_success(f"List quizzes endpoint working ({count} quizzes)")
            return True, count
        else:
            print_error(f"Expected 200, got {response.status_code}")
            return False, 0
    except Exception as e:
        print_error(f"Failed: {str(e)}")
        return False, 0


def test_get_quiz(quiz_id: int) -> bool:
    """Test GET /api/quizzes/{id} endpoint."""
    print_header(f"Testing Get Quiz (ID: {quiz_id})")
    try:
        response = requests.get(f"{BASE_URL}/api/quizzes/{quiz_id}", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            questions_count = len(data.get("questions", []))
            print(f"Quiz: {data.get('title')}")
            print(f"URL: {data.get('url')}")
            print(f"Questions: {questions_count}")
            print_success(f"Get quiz endpoint working ({questions_count} questions)")
            return True
        elif response.status_code == 404:
            print_error(f"Quiz with ID {quiz_id} not found")
            return False
        else:
            print_error(f"Expected 200, got {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Failed: {str(e)}")
        return False


def test_generate_quiz(url: str) -> bool:
    """Test POST /api/quizzes/generate endpoint."""
    print_header(f"Testing Generate Quiz")
    print(f"URL: {url}\n")
    try:
        response = requests.post(
            f"{BASE_URL}/api/quizzes/generate",
            json={"url": url},
            timeout=30,  # Longer timeout for generation
        )
        if response.status_code == 201:
            data = response.json()
            questions_count = len(data.get("questions", []))
            print(f"Quiz ID: {data.get('id')}")
            print(f"Title: {data.get('title')}")
            print(f"Questions: {questions_count}")
            print(f"Related Topics: {', '.join(data.get('related_topics', []))}")
            print_success(f"Quiz generation working ({questions_count} questions)")
            return True
        elif response.status_code == 400:
            error = response.json()
            print_error(f"Bad request: {error.get('detail')}")
            return False
        else:
            print_error(f"Expected 201, got {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.Timeout:
        print_error("Request timeout (30 seconds) - LLM might be slow or API key invalid")
        print_info("This is normal if using dummy data without API keys")
        return False
    except Exception as e:
        print_error(f"Failed: {str(e)}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("  Wiki Quiz Hub - FastAPI Backend Test Suite")
    print("="*60)
    print(f"\nTesting API at: {BASE_URL}")
    print(f"Timeout: {TIMEOUT} seconds\n")

    results = {
        "health_check": False,
        "api_root": False,
        "list_quizzes": False,
        "get_quiz": False,
        "generate_quiz": False,
    }

    # Test 1: Health check
    results["health_check"] = test_health_check()

    # Test 2: API root
    results["api_root"] = test_api_root()

    # Test 3: List quizzes
    list_result, quiz_count = test_list_quizzes()
    results["list_quizzes"] = list_result

    # Test 4: Get quiz (if quizzes exist)
    if quiz_count > 0:
        results["get_quiz"] = test_get_quiz(1)
    else:
        print_header("Testing Get Quiz")
        print_info("Skipping - no quizzes in database. Run seed_database.py first.")

    # Test 5: Generate quiz
    print_header("Testing Generate Quiz")
    print_info("This will attempt to create a new quiz from Wikipedia")
    print_info("It may take 5-30 seconds depending on LLM API response")
    if test_generate_quiz("https://en.wikipedia.org/wiki/Albert_Einstein"):
        results["generate_quiz"] = True
    else:
        # Try with another URL
        print_info("\nRetrying with simpler Wikipedia article...")
        results["generate_quiz"] = test_generate_quiz("https://en.wikipedia.org/wiki/Computer_Science")

    # Summary
    print_header("Test Summary")
    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {test_name.replace('_', ' ').title()}")

    print(f"\n{passed}/{total} tests passed\n")

    if passed == total:
        print_success("All tests passed! Backend is working correctly.")
        return 0
    else:
        print_error(f"{total - passed} test(s) failed. Check logs above.")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⛔ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        sys.exit(1)

#!/usr/bin/env python3
# Copyright 2026 Espressif Systems (Shanghai) PTE LTD
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test runner for data model generation tools.

Usage:
    python3 tests/run_tests.py              # Run all tests
    python3 tests/run_tests.py conformance  # Run only conformance tests
    python3 tests/run_tests.py -v          # Run with verbose output
"""

import sys
import os
import unittest
import argparse

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_all_tests(verbosity=2):
    """Run all tests in the tests directory"""
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(start_dir, pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    return result.wasSuccessful()


def run_specific_test(test_name, verbosity=2):
    """Run a specific test module"""
    module_name = (
        f"test_{test_name}" if not test_name.startswith("test_") else test_name
    )

    try:
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName(module_name)

        runner = unittest.TextTestRunner(verbosity=verbosity)
        result = runner.run(suite)
        return result.wasSuccessful()
    except Exception as e:
        print(f"Error loading test module '{module_name}': {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Run tests for data model generation tools"
    )
    parser.add_argument(
        "test_name", nargs="?", help="Specific test module to run (e.g., conformance)"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Verbose output (show each test)"
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="Quiet output (minimal info)"
    )

    args = parser.parse_args()

    # Determine verbosity level
    if args.quiet:
        verbosity = 0
    elif args.verbose:
        verbosity = 2
    else:
        verbosity = 1

    # Run tests
    if args.test_name:
        success = run_specific_test(args.test_name, verbosity)
    else:
        success = run_all_tests(verbosity)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

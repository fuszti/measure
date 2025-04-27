#!/usr/bin/env python
"""
Test runner script for the Life Measurements Tracker
"""
import sys
import pytest
import argparse

def main():
    """Run tests with specified options"""
    parser = argparse.ArgumentParser(description="Run tests for the Life Measurements Tracker")
    parser.add_argument(
        "--skip-docker", 
        action="store_true", 
        help="Skip tests that require Docker"
    )
    parser.add_argument(
        "--coverage", 
        action="store_true", 
        help="Generate code coverage report"
    )
    parser.add_argument(
        "--unit-only", 
        action="store_true", 
        help="Run only unit tests"
    )
    
    args = parser.parse_args()
    
    pytest_args = ["-v"]
    
    # Handle test selection
    if args.skip_docker:
        pytest_args.append("-k 'not docker'")
    
    if args.unit_only:
        pytest_args.append("-m 'unit'")
    
    # Handle coverage
    if args.coverage:
        pytest_args.extend(["--cov=measure", "--cov=api", "--cov=db", "--cov=models"])
    
    # Run tests
    return pytest.main(pytest_args)

if __name__ == "__main__":
    sys.exit(main())
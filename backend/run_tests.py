#!/usr/bin/env python3
"""
Test Runner for ABA Session Notes Application

This script runs the test suite and provides options for different test configurations.

Usage:
    python run_tests.py [options]
    
Options:
    --verbose, -v      Verbose output
    --coverage, -c     Run with coverage report
    --fast, -f         Run only fast tests (skip integration tests)
    --help, -h         Show this help message
"""

import sys
import subprocess
import argparse

def run_pytest(args):
    """Run pytest with the specified arguments"""
    cmd = ["python", "-m", "pytest"]
    
    if args.verbose:
        cmd.append("-v")
    
    if args.coverage:
        cmd.extend(["--cov=.", "--cov-report=html", "--cov-report=term"])
    
    if args.fast:
        cmd.extend(["-m", "not integration"])
    
    # Add test directory
    cmd.append("tests/")
    
    print(f"Running: {' '.join(cmd)}")
    return subprocess.run(cmd)

def install_dependencies():
    """Install test dependencies if needed"""
    try:
        import pytest
        import faker
    except ImportError:
        print("Installing test dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def main():
    parser = argparse.ArgumentParser(description='Run tests for ABA Session Notes application')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('-c', '--coverage', action='store_true', help='Run with coverage report')
    parser.add_argument('-f', '--fast', action='store_true', help='Run only fast tests')
    
    args = parser.parse_args()
    
    print("🧪 ABA Session Notes - Test Runner")
    print("=" * 40)
    
    # Install dependencies if needed
    install_dependencies()
    
    # Run tests
    result = run_pytest(args)
    
    if result.returncode == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ Tests failed with exit code {result.returncode}")
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(main()) 
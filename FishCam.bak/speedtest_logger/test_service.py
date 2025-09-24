#!/usr/bin/env python3
"""
Test script for speedtest_service.py
Runs a quick test to verify the service wrapper works correctly
"""
import sys
import os
import time
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

def test_service_import():
    """Test that we can import the service module."""
    print("Testing service import...")
    try:
        from speedtest_service import SpeedtestService
        print("✓ Successfully imported SpeedtestService")
        return True
    except ImportError as e:
        print(f"✗ Failed to import SpeedtestService: {e}")
        return False

def test_logger_import():
    """Test that we can import the logger module."""
    print("Testing logger import...")
    try:
        from speedtest_logger import SpeedtestLogger
        print("✓ Successfully imported SpeedtestLogger")
        return True
    except ImportError as e:
        print(f"✗ Failed to import SpeedtestLogger: {e}")
        return False

def test_service_creation():
    """Test that we can create a service instance."""
    print("Testing service creation...")
    try:
        from speedtest_service import SpeedtestService
        service = SpeedtestService()
        print("✓ Successfully created SpeedtestService instance")
        return True
    except Exception as e:
        print(f"✗ Failed to create SpeedtestService: {e}")
        return False

def test_logger_creation():
    """Test that we can create a logger instance in service mode."""
    print("Testing logger creation in service mode...")
    try:
        from speedtest_logger import SpeedtestLogger
        logger = SpeedtestLogger(service_mode=True)
        print("✓ Successfully created SpeedtestLogger in service mode")
        return True
    except Exception as e:
        print(f"✗ Failed to create SpeedtestLogger: {e}")
        return False

def test_dependencies():
    """Test that all required dependencies are available."""
    print("Testing dependencies...")
    dependencies = ['speedtest', 'schedule', 'rich']
    all_good = True
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✓ {dep} is available")
        except ImportError:
            print(f"✗ {dep} is missing")
            all_good = False
    
    return all_good

def main():
    """Run all tests."""
    print("=" * 50)
    print("Speedtest Service Test Suite")
    print("=" * 50)
    
    tests = [
        test_dependencies,
        test_logger_import,
        test_service_import,
        test_logger_creation,
        test_service_creation,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            print()
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("✓ All tests passed! Service is ready to run.")
        return 0
    else:
        print("✗ Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

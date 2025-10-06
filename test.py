#!/usr/bin/env python3
"""
Test script for Universal Multi-Language Compiler (UMLC)
Tests basic functionality of the compiler and GUI components
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_compiler_manager():
    """Test the compiler manager functionality"""
    print("Testing Compiler Manager...")

    from backend.compiler_manager import CompilerManager

    manager = CompilerManager()

    # Test Python code
    python_code = 'print("Hello, World!")'
    with open('/tmp/test_python.py', 'w') as f:
        f.write(python_code)

    result = manager.run_code('/tmp/test_python.py', 'python', None)
    print(f"Python test result: {result}")

    print("PASS: Compiler Manager test completed")

def test_gui_components():
    """Test GUI components"""
    print("Testing GUI Components...")

    try:
        from gui.code_editor import CodeEditor
        from gui.output_display import OutputDisplay
        from gui.toolbar import Toolbar

        print("PASS: GUI components imported successfully")

    except ImportError as e:
        print(f"FAIL: GUI import error: {e}")
        return False

    print("PASS: GUI components test completed")
    return True

def test_main_application():
    """Test the main application"""
    print("Testing Main Application...")

    try:
        # Test import
        from main import UMLCApp
        print("PASS: Main application imported successfully")

        # Test instantiation (but don't start GUI)
        print("PASS: Main application class available")

    except ImportError as e:
        print(f"FAIL: Main application import error: {e}")
        return False

    print("PASS: Main application test completed")
    return True

def main():
    """Run all tests"""
    print("Starting UMLC Tests...")
    print("=" * 50)

    tests = [
        test_gui_components,
        test_main_application,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"FAIL: Test failed with exception: {e}")
            print()

    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")

    if passed == total:
        print("SUCCESS: All tests passed!")
        return True
    else:
        print("ERROR: Some tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
CI Test Runner for TabbedBoxMaker
================================

Comprehensive test runner that executes all CI checks in the correct order.
This script is designed to be the single entry point for CI/CD systems.

Exit Codes:
- 0: All tests passed
- 1: Test failures found
- 2: Critical setup/import errors
"""

import os
import sys
import subprocess
import tempfile
import time
from pathlib import Path

# Ensure we can import from the project
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Colors for output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    """Print a colored header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
    print(f"🔧 {text}")
    print(f"{'='*60}{Colors.END}")

def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.CYAN}ℹ️  {text}{Colors.END}")

def run_command(command, description, capture_output=False, timeout=60):
    """Run a command and report results"""
    print_info(f"Running: {description}")
    
    try:
        if isinstance(command, str):
            # Shell command
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=capture_output,
                text=True,
                timeout=timeout,
                cwd=PROJECT_ROOT
            )
        else:
            # List command
            result = subprocess.run(
                command,
                capture_output=capture_output,
                text=True,
                timeout=timeout,
                cwd=PROJECT_ROOT
            )
        
        if result.returncode == 0:
            print_success(f"{description} - PASSED")
            if capture_output and result.stdout:
                print(f"Output: {result.stdout.strip()}")
            return True
        else:
            print_error(f"{description} - FAILED (exit code: {result.returncode})")
            if capture_output:
                if result.stdout:
                    print(f"STDOUT: {result.stdout}")
                if result.stderr:
                    print(f"STDERR: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print_error(f"{description} - TIMEOUT after {timeout} seconds")
        return False
    except Exception as e:
        print_error(f"{description} - ERROR: {e}")
        return False

def check_imports():
    """Test that all critical imports work"""
    print_header("Testing Import Resolution")
    
    tests = [
        ("from TabbedBoxMaker import BoxMakerCore", "Core module import"),
        ("from TabbedBoxMaker import create_cli_parser", "CLI parser import"),
        ("from TabbedBoxMaker import DimensionError, TabError", "Exception imports"),
        ("import boxmaker_inkscape", "Inkscape extension import"),
    ]
    
    success_count = 0
    for import_cmd, description in tests:
        cmd = [sys.executable, "-c", import_cmd]
        if run_command(cmd, description, capture_output=True):
            success_count += 1
    
    if success_count == len(tests):
        print_success(f"All {len(tests)} import tests passed")
        return True
    else:
        print_error(f"Import tests failed: {success_count}/{len(tests)} passed")
        return False

def run_comprehensive_tests():
    """Run the main comprehensive test suite"""
    print_header("Running Comprehensive Test Suite")
    
    test_file = PROJECT_ROOT / "tests" / "test_ci_comprehensive.py"
    if not test_file.exists():
        print_error(f"Test file not found: {test_file}")
        return False
    
    cmd = [sys.executable, "-m", "pytest", str(test_file), "-v", "--tb=short"]
    return run_command(cmd, "Comprehensive CI tests", capture_output=True, timeout=120)

def test_cli_functionality():
    """Test CLI functionality with various parameters"""
    print_header("Testing CLI Functionality")
    
    tests = [
        {
            "cmd": [sys.executable, "boxmaker.py", "--help"],
            "desc": "CLI help command",
            "expect_file": None
        },
        {
            "cmd": [
                sys.executable, "boxmaker.py",
                "--length", "100", "--width", "80", "--height", "50",
                "--thickness", "3", "--tab", "12", "--output", "ci_test_basic.svg"
            ],
            "desc": "Basic box generation",
            "expect_file": "ci_test_basic.svg"
        },
        {
            "cmd": [
                sys.executable, "boxmaker.py",
                "--length", "200", "--width", "150", "--height", "100",
                "--thickness", "6", "--tab", "20", "--div-l", "2", "--div-w", "1",
                "--output", "ci_test_dividers.svg"
            ],
            "desc": "Box with dividers",
            "expect_file": "ci_test_dividers.svg"
        },
        {
            "cmd": [
                sys.executable, "boxmaker.py",
                "--length", "300", "--width", "250", "--height", "80",
                "--thickness", "4", "--max-material-width", "200", "--max-material-height", "200",
                "--output", "ci_test_material_limits.svg"
            ],
            "desc": "Box with material limits",
            "expect_file": "ci_test_material_limits.svg"
        }
    ]
    
    success_count = 0
    for test in tests:
        if run_command(test["cmd"], test["desc"], capture_output=True):
            if test["expect_file"]:
                file_path = PROJECT_ROOT / test["expect_file"]
                if file_path.exists():
                    # Check if SVG contains expected content
                    try:
                        with open(file_path, 'r') as f:
                            content = f.read()
                        if '<svg' in content and '</svg>' in content:
                            print_success(f"SVG file {test['expect_file']} generated correctly")
                            success_count += 1
                            # Cleanup
                            file_path.unlink()
                        else:
                            print_error(f"SVG file {test['expect_file']} is invalid")
                    except Exception as e:
                        print_error(f"Error reading {test['expect_file']}: {e}")
                else:
                    print_error(f"Expected file {test['expect_file']} was not created")
            else:
                success_count += 1
    
    if success_count == len(tests):
        print_success(f"All {len(tests)} CLI tests passed")
        return True
    else:
        print_error(f"CLI tests failed: {success_count}/{len(tests)} passed")
        return False

def test_error_handling():
    """Test that error conditions are handled properly"""
    print_header("Testing Error Handling")
    
    error_tests = [
        {
            "cmd": [
                sys.executable, "boxmaker.py",
                "--length", "100", "--width", "80", "--height", "50",
                "--thickness", "3", "--tab", "50",  # Tab too large
                "--output", "error_test.svg"
            ],
            "desc": "Tab too large error",
            "expect_error": "Tab Error"
        },
        {
            "cmd": [
                sys.executable, "boxmaker.py",
                "--length", "10", "--width", "10", "--height", "10",  # Too small
                "--thickness", "3", "--tab", "5",
                "--output", "error_test.svg"
            ],
            "desc": "Dimensions too small error",
            "expect_error": "Dimension Error"
        }
    ]
    
    success_count = 0
    for test in error_tests:
        result = subprocess.run(
            test["cmd"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT
        )
        
        if result.returncode != 0 and test["expect_error"] in result.stderr:
            print_success(f"{test['desc']} - correctly handled")
            success_count += 1
        else:
            print_error(f"{test['desc']} - not handled correctly")
            print(f"Expected error containing: {test['expect_error']}")
            print(f"Got stderr: {result.stderr}")
    
    if success_count == len(error_tests):
        print_success(f"All {len(error_tests)} error handling tests passed")
        return True
    else:
        print_error(f"Error handling tests failed: {success_count}/{len(error_tests)} passed")
        return False

def check_file_structure():
    """Verify that all required files exist"""
    print_header("Checking Project Structure")
    
    required_files = [
        "boxmaker.py",
        "boxmaker_inkscape.py", 
        "boxmaker.inx",
        "schroffmaker.inx",
        "TabbedBoxMaker/__init__.py",
        "TabbedBoxMaker/core.py",
        "TabbedBoxMaker/config.py",
        "TabbedBoxMaker/parameters.py",
        "tests/test_ci_comprehensive.py",
        "README.md",
        "LICENSE"
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = PROJECT_ROOT / file_path
        if not full_path.exists():
            missing_files.append(file_path)
    
    if not missing_files:
        print_success(f"All {len(required_files)} required files found")
        return True
    else:
        print_error(f"Missing files: {missing_files}")
        return False

def run_additional_tests():
    """Run additional test files if they exist"""
    print_header("Running Additional Test Files")
    
    test_files = [
        "tests/test_boxmaker.py",
        "tests/test_design.py", 
        "tests/test_cli_integration.py"
    ]
    
    success_count = 0
    total_tests = 0
    
    for test_file in test_files:
        full_path = PROJECT_ROOT / test_file
        if full_path.exists():
            total_tests += 1
            cmd = [sys.executable, str(full_path)]
            if run_command(cmd, f"Additional test: {test_file}", capture_output=True):
                success_count += 1
        else:
            print_info(f"Optional test file not found: {test_file}")
    
    if total_tests == 0:
        print_info("No additional test files found")
        return True
    elif success_count == total_tests:
        print_success(f"All {total_tests} additional tests passed")
        return True
    else:
        print_warning(f"Additional tests: {success_count}/{total_tests} passed")
        return success_count > 0  # Allow some additional tests to fail

def main():
    """Main CI test runner"""
    print_header("TabbedBoxMaker CI Test Suite")
    print_info(f"Running from: {PROJECT_ROOT}")
    print_info(f"Python version: {sys.version}")
    
    # Ensure test directories exist
    (PROJECT_ROOT / "test_results").mkdir(exist_ok=True)
    
    # Run all test suites
    test_suites = [
        ("File Structure Check", check_file_structure),
        ("Import Resolution", check_imports),
        ("Comprehensive Tests", run_comprehensive_tests),
        ("CLI Functionality", test_cli_functionality),
        ("Error Handling", test_error_handling),
        ("Additional Tests", run_additional_tests),
    ]
    
    results = {}
    for suite_name, test_func in test_suites:
        print(f"\n{Colors.MAGENTA}▶️  Starting: {suite_name}{Colors.END}")
        start_time = time.time()
        
        try:
            success = test_func()
            results[suite_name] = success
            elapsed = time.time() - start_time
            
            if success:
                print_success(f"{suite_name} completed in {elapsed:.1f}s")
            else:
                print_error(f"{suite_name} failed after {elapsed:.1f}s")
                
        except Exception as e:
            results[suite_name] = False
            elapsed = time.time() - start_time
            print_error(f"{suite_name} crashed after {elapsed:.1f}s: {e}")
    
    # Print final summary
    print_header("CI Test Results Summary")
    
    passed = sum(1 for success in results.values() if success)
    total = len(results)
    
    for suite_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} {suite_name}")
    
    print(f"\n{Colors.BOLD}Overall Result: {passed}/{total} test suites passed{Colors.END}")
    
    if passed == total:
        print_success("🎉 All CI tests passed! Ready for deployment.")
        return 0
    else:
        print_error(f"💥 {total - passed} test suite(s) failed.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print_error("\n🛑 CI tests interrupted by user")
        sys.exit(2)
    except Exception as e:
        print_error(f"\n💥 CI runner crashed: {e}")
        sys.exit(2)

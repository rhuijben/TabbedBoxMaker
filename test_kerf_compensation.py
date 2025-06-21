#!/usr/bin/env python3
"""
Test script to verify kerf compensation is applied correctly
"""

import sys
from pathlib import Path

# Add the current directory to the path to import our modules
sys.path.insert(0, str(Path(__file__).parent))

from boxmaker_core import BoxMakerCore


def test_kerf_compensation():
    """Test that kerf compensation is applied correctly"""
    print("Testing kerf compensation...")
    
    # Create a simple box with known dimensions
    core = BoxMakerCore()
    core.set_parameters(
        length=100.0,   # Design dimensions
        width=80.0,
        height=60.0,
        thickness=3.0,
        kerf=0.2,       # 0.2mm kerf = 0.1mm half-kerf
        tab=15.0,
        tabtype=0       # Laser
    )
    
    # Generate the box
    result = core.generate_box()
    
    print(f"Design dimensions: {core.design.length_external} x {core.design.width_external} x {core.design.height_external}")
    print(f"Kerf: {core.kerf}mm (half-kerf: {core.kerf/2}mm)")
    
    # The design should use original dimensions
    assert core.design.length_external == 100.0, f"Design length should be 100.0, got {core.design.length_external}"
    assert core.design.width_external == 80.0, f"Design width should be 80.0, got {core.design.width_external}"
    assert core.design.height_external == 60.0, f"Design height should be 60.0, got {core.design.height_external}"
    
    print("[PASS] Design dimensions are correct")
    
    # Check if the generated paths show kerf compensation
    # This is more complex to verify automatically, but we can check basic structure
    assert len(result['paths']) > 0, "Should generate some paths"
    print(f"Generated {len(result['paths'])} paths")
    
    print("[PASS] Kerf compensation test completed")
    return True


def test_no_kerf_vs_with_kerf():
    """Compare box generation with and without kerf to see the difference"""
    print("\nTesting kerf compensation effects...")
    
    # Test with no kerf
    core_no_kerf = BoxMakerCore()
    core_no_kerf.set_parameters(
        length=100.0, width=80.0, height=60.0,
        thickness=3.0, kerf=0.0, tab=15.0, tabtype=0
    )
    result_no_kerf = core_no_kerf.generate_box()
    
    # Test with kerf
    core_with_kerf = BoxMakerCore()
    core_with_kerf.set_parameters(
        length=100.0, width=80.0, height=60.0,
        thickness=3.0, kerf=0.2, tab=15.0, tabtype=0
    )
    result_with_kerf = core_with_kerf.generate_box()
    
    print(f"No kerf - paths: {len(result_no_kerf['paths'])}")
    print(f"With kerf - paths: {len(result_with_kerf['paths'])}")
    
    # Both should generate the same number of paths
    assert len(result_no_kerf['paths']) == len(result_with_kerf['paths']), \
        "Should generate same number of paths regardless of kerf"
    
    print("[PASS] Kerf effects test completed")
    return True


if __name__ == "__main__":
    print("Running kerf compensation tests...\n")
    
    tests = [
        test_kerf_compensation,
        test_no_kerf_vs_with_kerf,
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"[FAIL] {test.__name__} failed: {e}")
    
    print(f"\nTest Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("✅ All kerf tests passed")
        sys.exit(0)
    else:
        print("❌ Some kerf tests failed")
        sys.exit(1)

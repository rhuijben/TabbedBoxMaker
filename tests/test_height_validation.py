#!/usr/bin/env python3
"""
Test the updated height validation for open boxes
"""

import sys
from pathlib import Path

# Add the current directory to the path to import our modules
sys.path.insert(0, str(Path(__file__).parent))

from boxmaker_core import BoxMakerCore
from boxmaker_constants import BoxType


def test_shallow_open_box():
    """Test that a shallow box with no top works"""
    print("Testing shallow open box (no top)...")
    
    core = BoxMakerCore()
    core.set_parameters(
        length=220.0,
        width=206.0,
        height=18.0,  # This used to fail but should now work
        thickness=3.0,
        kerf=0.1,
        tab=6.0,
        boxtype=BoxType.NO_TOP,  # One side open (LxW) - no top
        tabtype=0  # Laser
    )
    
    try:
        result = core.generate_box()
        print(f"✓ Successfully generated box with {core.height}mm height (no top)")
        print(f"  Box type: {core.boxtype.name}")
        print(f"  Generated {len(result['paths'])} paths")
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False


def test_shallow_full_box():
    """Test that a shallow full box still fails (as it should)"""
    print("Testing shallow full box (should fail)...")
    
    core = BoxMakerCore()
    core.set_parameters(
        length=220.0,
        width=206.0,
        height=18.0,  # This should still fail for full box
        thickness=3.0,
        kerf=0.1,
        tab=6.0,
        boxtype=BoxType.FULL_BOX,  # Full box needs sufficient height
        tabtype=0  # Laser
    )
    
    try:
        result = core.generate_box()
        print(f"✗ Should have failed but didn't!")
        return False
    except Exception as e:
        print(f"✓ Correctly failed: {e}")
        return True


if __name__ == '__main__':
    print("Testing updated height validation...\n")
    
    test1 = test_shallow_open_box()
    print()
    test2 = test_shallow_full_box()
    
    if test1 and test2:
        print("\n✓ All height validation tests passed!")
    else:
        print("\n✗ Some tests failed!")

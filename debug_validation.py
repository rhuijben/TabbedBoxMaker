#!/usr/bin/env python3
"""
Debug the height validation issue
"""

import sys
from pathlib import Path

# Add the current directory to the path to import our modules
sys.path.insert(0, str(Path(__file__).parent))

from boxmaker_core import BoxMakerCore
from boxmaker_constants import BoxType
from box_design import get_wall_configuration


def debug_validation():
    """Debug the validation logic"""
    print("Debugging height validation...")
    
    # Test the wall configuration for NO_TOP box type
    wall_config = get_wall_configuration(BoxType.NO_TOP)
    print(f"Wall config for NO_TOP:")
    print(f"  has_top: {wall_config.has_top}")
    print(f"  has_bottom: {wall_config.has_bottom}")
    
    # Calculate what the minimum height should be
    thickness = 3.0
    expected_min_height = thickness * 2 + 5  # Should be 11mm
    print(f"  Expected min height: {expected_min_height}mm")
    
    # Test with the actual height
    test_height = 18.0
    print(f"  Test height: {test_height}mm")
    print(f"  Should pass: {test_height >= expected_min_height}")
    
    # Try to create the box
    core = BoxMakerCore()
    print(f"\nSetting parameters...")
    core.set_parameters(
        length=220.0,
        width=206.0,
        height=18.0,
        thickness=3.0,
        kerf=0.1,
        tab=6.0,
        boxtype=BoxType.NO_TOP,
        tabtype=0
    )
    
    print(f"Box type set to: {core.boxtype}")
    print(f"Box type name: {core.boxtype.name}")
    
    try:
        print("Calling _validate_dimensions...")
        core._validate_dimensions()
        print("✓ Validation passed!")
    except Exception as e:
        print(f"✗ Validation failed: {e}")


if __name__ == '__main__':
    debug_validation()

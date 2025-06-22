#!/usr/bin/env python3
"""
Test thickness-based overlap limits

This test verifies that overlap amounts are correctly calculated based on
material thickness with smart minimum and maximum limits.
"""

import sys
from pathlib import Path

# Add the current directory to the path to import our modules
sys.path.insert(0, str(Path(__file__).parent))

from boxmaker_core import BoxMakerCore
from boxmaker_constants import (
    BoxType, JoinType, DEFAULT_OVERLAP_MULTIPLIER, 
    MIN_OVERLAP_MULTIPLIER, MAX_OVERLAP_MULTIPLIER
)
from box_design import create_box_design


def test_thickness_based_overlap_limits():
    """Test that overlap amounts scale correctly with material thickness"""
    print("Testing thickness-based overlap limits...")
    
    # Test different material thicknesses
    test_cases = [
        # (thickness, overlap_multiplier, expected_min, expected_max, description)
        (1.0, 3.5, 1.0, 6.0, "Thin material (1mm)"),
        (3.0, 3.5, 3.0, 18.0, "Standard material (3mm)"),
        (6.0, 3.5, 6.0, 36.0, "Thick material (6mm)"),
        (12.0, 3.5, 12.0, 72.0, "Very thick material (12mm)"),
        (25.0, 3.5, 25.0, 150.0, "Extremely thick material (25mm)"),
    ]
    
    for thickness, multiplier, expected_min, expected_max, description in test_cases:
        print(f"\n{description}:")
        print(f"  Thickness: {thickness}mm")
        print(f"  Multiplier: {multiplier}x")
        
        # Test with default multiplier (should use base calculation)
        design = create_box_design(
            length=400.0,  # Large enough to trigger splitting
            width=200.0,
            height=100.0,
            thickness=thickness,
            max_material_width=300.0,
            max_material_height=300.0,
            overlap_multiplier=multiplier
        )
        
        if design.split_info:
            split_info = list(design.split_info.values())[0]  # Get first split piece
            actual_overlap = split_info.overlap
            expected_overlap = thickness * multiplier
            
            print(f"  Expected overlap: {expected_overlap:.1f}mm ({multiplier}x thickness)")
            print(f"  Actual overlap: {actual_overlap:.1f}mm")
            print(f"  Min allowed: {expected_min:.1f}mm ({MIN_OVERLAP_MULTIPLIER}x thickness)")  
            print(f"  Max allowed: {expected_max:.1f}mm ({MAX_OVERLAP_MULTIPLIER}x thickness)")
            
            # Verify overlap is within expected range
            if expected_min <= actual_overlap <= expected_max:
                print(f"  ✓ Overlap within valid range")
            else:
                print(f"  ❌ Overlap outside valid range!")
                return False
                
            # Verify overlap equals expected (since 3.5 is within 1.0-6.0 range)
            if abs(actual_overlap - expected_overlap) < 0.1:
                print(f"  ✓ Overlap matches expected calculation")
            else:
                print(f"  ❌ Overlap calculation error!")
                return False
        else:
            print(f"  ❌ No split info generated when expected")
            return False
    
    print(f"\n✓ All thickness-based overlap calculations correct")
    return True


def test_overlap_limit_clamping():
    """Test that extreme overlap multipliers are clamped to safe ranges"""
    print("\nTesting overlap limit clamping...")
    
    thickness = 3.0  # Standard 3mm material
    
    test_cases = [
        # (multiplier, expected_overlap, description)
        (0.5, 3.0, "Below minimum (0.5x) → clamped to 1.0x"),
        (1.0, 3.0, "At minimum (1.0x) → kept as 1.0x"),
        (3.5, 10.5, "Normal range (3.5x) → kept as 3.5x"),
        (6.0, 18.0, "At maximum (6.0x) → kept as 6.0x"),
        (10.0, 18.0, "Above maximum (10.0x) → clamped to 6.0x"),
        (0.1, 3.0, "Extremely low (0.1x) → clamped to 1.0x"),
        (50.0, 18.0, "Extremely high (50.0x) → clamped to 6.0x"),
    ]
    
    for multiplier, expected_overlap, description in test_cases:
        print(f"\n{description}:")
        
        design = create_box_design(
            length=400.0,
            width=200.0,
            height=100.0,
            thickness=thickness,
            max_material_width=300.0,
            max_material_height=300.0,
            overlap_multiplier=multiplier
        )
        
        if design.split_info:
            split_info = list(design.split_info.values())[0]
            actual_overlap = split_info.overlap
            
            print(f"  Input multiplier: {multiplier}x")
            print(f"  Expected overlap: {expected_overlap:.1f}mm")
            print(f"  Actual overlap: {actual_overlap:.1f}mm")
            
            if abs(actual_overlap - expected_overlap) < 0.1:
                print(f"  ✓ Correctly clamped to valid range")
            else:
                print(f"  ❌ Clamping failed!")
                return False
        else:
            print(f"  ❌ No split info generated")
            return False
    
    print(f"\n✓ All overlap limit clamping working correctly")
    return True


def test_real_world_scenarios():
    """Test overlap calculations for realistic material scenarios"""
    print("\nTesting real-world material scenarios...")
    
    scenarios = [
        # (material, thickness, description, expected_behavior)
        ("Paper/Cardboard", 0.5, "Very thin prototyping material", "Should get minimum 0.5mm overlap"),
        ("Thin Plywood", 3.0, "Standard 3mm plywood", "Should get 10.5mm overlap (3.5x)"),
        ("MDF", 6.0, "6mm MDF board", "Should get 21mm overlap (3.5x)"), 
        ("Thick Plywood", 12.0, "12mm plywood", "Should get 42mm overlap (3.5x)"),
        ("Thick Board", 18.0, "18mm construction board", "Should get 63mm overlap (3.5x)"),
        ("Very Thick", 30.0, "30mm thick material", "Should get 105mm overlap (3.5x)"),
    ]
    
    for material, thickness, description, expected_behavior in scenarios:
        print(f"\n{material} ({thickness}mm):")
        print(f"  {description}")
        print(f"  {expected_behavior}")
        
        design = create_box_design(
            length=400.0,
            width=200.0, 
            height=100.0,
            thickness=thickness,
            max_material_width=300.0,
            max_material_height=300.0,
            overlap_multiplier=DEFAULT_OVERLAP_MULTIPLIER
        )
        
        if design.split_info:
            split_info = list(design.split_info.values())[0]
            actual_overlap = split_info.overlap
            overlap_ratio = actual_overlap / thickness
            
            print(f"  Actual overlap: {actual_overlap:.1f}mm ({overlap_ratio:.1f}x thickness)")
            
            # Verify overlap is reasonable for the material
            if thickness <= 1.0:
                # Very thin materials should get minimum overlap
                if overlap_ratio >= MIN_OVERLAP_MULTIPLIER:
                    print(f"  ✓ Adequate overlap for thin material")
                else:
                    print(f"  ❌ Insufficient overlap for thin material")
                    return False
            else:
                # Normal materials should get default overlap  
                expected_ratio = DEFAULT_OVERLAP_MULTIPLIER
                if abs(overlap_ratio - expected_ratio) < 0.1:
                    print(f"  ✓ Expected overlap ratio achieved")
                else:
                    print(f"  ❌ Unexpected overlap ratio")
                    return False
        else:
            print(f"  ❌ No split info generated")
            return False
    
    print(f"\n✓ All real-world scenarios handled appropriately")
    return True


if __name__ == "__main__":
    print("Testing Thickness-Based Overlap Limits")
    print("=" * 50)
    
    # Run tests
    test1 = test_thickness_based_overlap_limits()
    test2 = test_overlap_limit_clamping()
    test3 = test_real_world_scenarios()
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"  Thickness-based limits:  {'✓ PASS' if test1 else '❌ FAIL'}")
    print(f"  Overlap limit clamping:  {'✓ PASS' if test2 else '❌ FAIL'}")
    print(f"  Real-world scenarios:    {'✓ PASS' if test3 else '❌ FAIL'}")
    
    if all([test1, test2, test3]):
        print("\n🎉 All thickness-based overlap tests passed!")
        print("\nThe system correctly:")
        print("- Scales overlap with material thickness")
        print("- Enforces minimum 1x thickness overlap")
        print("- Limits maximum to 6x thickness overlap") 
        print("- Handles extreme multiplier values gracefully")
        print("- Provides appropriate overlaps for real materials")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)

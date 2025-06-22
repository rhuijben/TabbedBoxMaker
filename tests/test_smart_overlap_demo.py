#!/usr/bin/env python3
"""
Demonstration of smart thickness-based overlap limits
Shows how overlap scales automatically with material thickness
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from box_design import create_box_design, check_material_limits

def test_thickness_scaling():
    """Test how overlap automatically scales with thickness"""
    
    print("Smart Thickness-Based Overlap Demonstration")
    print("=" * 55)
    
    # Test different material thicknesses with same multiplier
    test_cases = [
        (0.5, "Paper/Cardboard"),
        (1.0, "Thin cardboard"),
        (3.0, "3mm plywood"), 
        (6.0, "6mm MDF"),
        (9.0, "9mm plywood"),
        (12.0, "12mm plywood"),
        (18.0, "18mm construction board"),
        (25.0, "25mm thick lumber")
    ]
    
    # Fixed material limits for testing
    material_limit = 200.0  # 200mm limit
    box_size = 350.0  # 350mm box (needs splitting)
    overlap_multiplier = 3.5  # Default multiplier
    
    print(f"Test scenario: {box_size}mm box with {material_limit}mm material limit")
    print(f"Overlap multiplier: {overlap_multiplier}x")
    print()
    
    for thickness, material_name in test_cases:
        print(f"{material_name} ({thickness}mm thick):")
        
        # Create design with this thickness
        design = create_box_design(
            length=box_size,
            width=100,  # Keep simple
            height=100,
            thickness=thickness,
            max_material_width=material_limit,
            max_material_height=material_limit,
            overlap_multiplier=overlap_multiplier
        )
        
        # Check material limits
        split_info = check_material_limits(design)
        
        if split_info:
            # Get the first split piece info
            piece_name = list(split_info.keys())[0]
            info = split_info[piece_name]
            
            expected_overlap = thickness * overlap_multiplier
            min_overlap = thickness * 1.0  # MIN_OVERLAP_MULTIPLIER
            max_overlap = thickness * 6.0  # MAX_OVERLAP_MULTIPLIER
            
            print(f"  Expected overlap: {expected_overlap:.1f}mm ({overlap_multiplier}x thickness)")
            print(f"  Actual overlap: {info.overlap:.1f}mm")
            print(f"  Valid range: {min_overlap:.1f}mm - {max_overlap:.1f}mm")
            print(f"  Pieces needed: {info.num_pieces}")
            
            # Check if it's within valid range
            if min_overlap <= info.overlap <= max_overlap:
                print(f"  ✓ Overlap within smart thickness-based range")
            else:
                print(f"  ✗ Overlap outside valid range!")
                
            # Check if it matches expected calculation
            if abs(info.overlap - expected_overlap) < 0.1:
                print(f"  ✓ Overlap matches expected calculation")
            else:
                print(f"  ✗ Overlap calculation error!")
                
        else:
            print(f"  No splitting needed (shouldn't happen with {box_size}mm > {material_limit}mm)")
            
        print()

def test_extreme_multipliers():
    """Test extreme multiplier values to show clamping"""
    
    print("Extreme Multiplier Clamping Test")
    print("=" * 35)
    
    thickness = 3.0  # Standard 3mm material
    test_multipliers = [
        (0.1, "Way too small"),
        (0.5, "Below minimum"), 
        (1.0, "At minimum"),
        (3.5, "Default value"),
        (6.0, "At maximum"),
        (10.0, "Above maximum"),
        (100.0, "Extremely large")
    ]
    
    for multiplier, description in test_multipliers:
        print(f"{description} ({multiplier}x):")
        
        # Create design with this multiplier
        design = create_box_design(
            length=350,
            width=100,
            height=100,
            thickness=thickness,
            max_material_width=200,
            max_material_height=200,
            overlap_multiplier=multiplier
        )
        
        # Check material limits
        split_info = check_material_limits(design)
        
        if split_info:
            piece_name = list(split_info.keys())[0]
            info = split_info[piece_name]
            
            expected_raw = thickness * multiplier
            min_allowed = thickness * 1.0
            max_allowed = thickness * 6.0
            expected_clamped = max(min_allowed, min(expected_raw, max_allowed))
            
            print(f"  Raw calculation: {expected_raw:.1f}mm")
            print(f"  Expected after clamp: {expected_clamped:.1f}mm")
            print(f"  Actual overlap: {info.overlap:.1f}mm")
            
            if abs(info.overlap - expected_clamped) < 0.1:
                print(f"  ✓ Correctly clamped to valid range")
            else:
                print(f"  ✗ Clamping failed!")
                
        print()

if __name__ == "__main__":
    test_thickness_scaling()
    test_extreme_multipliers()
    
    print("🎉 Smart thickness-based overlap demonstration complete!")
    print()
    print("KEY BENEFITS:")
    print("- Overlap automatically scales with material thickness")
    print("- Never less than 1x thickness (adequate for joining)")
    print("- Never more than 6x thickness (prevents waste)")
    print("- Default 3.5x provides good balance for most applications")
    print("- Works consistently across all material types")

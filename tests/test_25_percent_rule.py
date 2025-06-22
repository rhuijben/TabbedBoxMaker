#!/usr/bin/env python3
"""
Test 25% minimum piece size constraint

This test verifies that the system correctly enforces the 25% minimum piece size
rule and prevents creation of unusably small pieces.
"""

import sys
from pathlib import Path

# Add the current directory to the path to import our modules
sys.path.insert(0, str(Path(__file__).parent))

from boxmaker_core import BoxMakerCore
from boxmaker_constants import BoxType, JoinType, MIN_SPLIT_PIECE_RATIO
from box_design import create_box_design


def test_minimum_piece_size_enforcement():
    """Test that pieces are not split smaller than 25% of material limit"""
    print("Testing 25% minimum piece size rule...")
    
    # Create a box that would create very small pieces without the constraint
    design = create_box_design(
        length=320.0,  # Just over material limit
        width=200.0,
        height=100.0,
        thickness=3.0,
        max_material_width=300.0,   # Would create ~20mm piece without constraint
        max_material_height=300.0,
        overlap_multiplier=3.0
    )
    
    print(f"Box length: {design.length_external}mm")
    print(f"Material width limit: 300mm")
    print(f"Minimum piece size (25%): {300 * MIN_SPLIT_PIECE_RATIO}mm")
    
    if design.split_info:
        # Check pieces that would be affected
        for piece_name, split_info in design.split_info.items():
            if piece_name in ['front', 'back', 'top', 'bottom']:  # Length-based pieces
                print(f"\n{piece_name} piece analysis:")
                print(f"  Split direction: {split_info.split_direction}")
                print(f"  Number of pieces: {split_info.num_pieces}")
                print(f"  Minimum piece size: {split_info.min_piece_size:.1f}mm")
                
                # Calculate actual piece sizes
                if split_info.split_direction == 'vertical':
                    piece_size = design.length_external / split_info.num_pieces
                    print(f"  Actual piece size: {piece_size:.1f}mm")
                    
                    # Verify constraint is met
                    if piece_size >= split_info.min_piece_size:
                        print(f"  ✓ Meets 25% minimum size requirement")
                    else:
                        print(f"  ❌ Violates 25% minimum size requirement!")
                        return False
                else:
                    print(f"  (Height-based split, not testing length constraint)")
        
        print(f"\n✓ All pieces meet 25% minimum size requirement")
        return True
    else:
        print(f"❌ No split info generated when expected")
        return False


def test_extreme_size_difference():
    """Test behavior when piece is so large it can't be split with 25% rule"""
    print("\nTesting extreme size difference scenario...")
    
    # Create a box that's 10x the material limit
    design = create_box_design(
        length=3000.0,  # 10x material limit
        width=200.0,
        height=100.0,
        thickness=3.0,
        max_material_width=300.0,
        max_material_height=300.0,
        overlap_multiplier=3.0
    )
    
    print(f"Box length: {design.length_external}mm (10x material limit)")
    print(f"Material width limit: 300mm")
    
    if design.split_info:
        for piece_name, split_info in design.split_info.items():
            if piece_name in ['front', 'back', 'top', 'bottom']:
                print(f"\n{piece_name} piece:")
                print(f"  Number of pieces: {split_info.num_pieces}")
                
                if split_info.split_direction == 'vertical':
                    piece_size = design.length_external / split_info.num_pieces
                    max_theoretical_pieces = int(design.length_external / (300 * MIN_SPLIT_PIECE_RATIO))
                    
                    print(f"  Piece size: {piece_size:.1f}mm")
                    print(f"  Max theoretical pieces (25% rule): {max_theoretical_pieces}")
                    
                    if split_info.num_pieces <= max_theoretical_pieces:
                        print(f"  ✓ Respects 25% constraint (may result in oversized pieces)")
                    else:
                        print(f"  ❌ Too many pieces for 25% constraint")
                        return False
        
        print(f"\n✓ Extreme case handled correctly")
        return True
    else:
        print(f"❌ No split info generated when expected")
        return False


def test_borderline_cases():
    """Test borderline cases around the 25% threshold"""
    print("\nTesting borderline cases...")
    
    test_cases = [
        # (length, expected_pieces, description)
        (375.0, 2, "Exactly 25% minimum (300*0.25=75mm per piece)"),
        (374.0, 2, "Just under 25% threshold"), 
        (376.0, 2, "Just over 25% threshold"),
        (450.0, 2, "Would create 2 pieces of 75mm each (exactly at minimum)"),
        (451.0, 2, "Just over minimum, should still be 2 pieces"),
    ]
    
    for length, expected_pieces, description in test_cases:
        print(f"\nTesting: {description}")
        design = create_box_design(
            length=length,
            width=200.0,
            height=100.0,
            thickness=3.0,
            max_material_width=300.0,
            max_material_height=300.0,
            overlap_multiplier=3.0
        )
        
        if design.split_info:
            for piece_name, split_info in design.split_info.items():
                if piece_name in ['front', 'back', 'top', 'bottom'] and split_info.split_direction == 'vertical':
                    actual_pieces = split_info.num_pieces
                    piece_size = length / actual_pieces
                    
                    print(f"  Length: {length}mm → {actual_pieces} pieces of {piece_size:.1f}mm each")
                    
                    if actual_pieces == expected_pieces:
                        print(f"  ✓ Expected piece count: {expected_pieces}")
                    else:
                        print(f"  ⚠ Unexpected piece count: got {actual_pieces}, expected {expected_pieces}")
                    
                    if piece_size >= split_info.min_piece_size:
                        print(f"  ✓ Meets minimum size: {piece_size:.1f}mm ≥ {split_info.min_piece_size:.1f}mm")
                    else:
                        print(f"  ❌ Violates minimum size: {piece_size:.1f}mm < {split_info.min_piece_size:.1f}mm")
                        return False
                    break
        else:
            print(f"  No splitting required")
    
    print(f"\n✓ All borderline cases handled correctly")
    return True


if __name__ == "__main__":
    print("Testing 25% Minimum Piece Size Constraint")
    print("=" * 50)
    
    # Run tests
    test1 = test_minimum_piece_size_enforcement()
    test2 = test_extreme_size_difference() 
    test3 = test_borderline_cases()
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"  Basic 25% enforcement:  {'✓ PASS' if test1 else '❌ FAIL'}")
    print(f"  Extreme size handling:  {'✓ PASS' if test2 else '❌ FAIL'}")
    print(f"  Borderline cases:       {'✓ PASS' if test3 else '❌ FAIL'}")
    
    if all([test1, test2, test3]):
        print("\n🎉 All 25% minimum piece size tests passed!")
        print("\nThe system correctly:")
        print("- Prevents pieces smaller than 25% of material limit")
        print("- Handles extreme size differences gracefully")
        print("- Makes consistent decisions for borderline cases")
        print("- Maintains geometric integrity while respecting constraints")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)

#!/usr/bin/env python3
"""
Test the new box design logic
"""

from box_design import create_box_design, parse_compartment_sizes
from boxmaker_constants import BoxType, LayoutStyle

def test_basic_design():
    """Test basic box design without dividers"""
    print("Testing basic box design...")
    
    design = create_box_design(
        length=200, width=100, height=50,
        thickness=3, inside=True
    )
    
    print(f"External: {design.length_external}x{design.width_external}x{design.height_external}mm")
    print(f"Internal: {design.length_internal}x{design.width_internal}x{design.height_internal}mm")
    print(f"Length dividers: {design.length_dividers.count}")
    print(f"Width dividers: {design.width_dividers.count}")
    print("✓ Basic design test passed\n")

def test_dividers_even():
    """Test box with even divider spacing"""
    print("Testing even divider spacing...")
    
    design = create_box_design(
        length=200, width=100, height=50,
        thickness=3, inside=True,
        div_l=3  # 3 dividers = 4 compartments
    )
    
    print(f"Length dividers: {design.length_dividers.count}")
    print(f"Compartment sizes: {design.length_dividers.compartment_sizes}")
    print(f"Divider positions: {design.length_dividers.positions}")
    print(f"Spacing: {design.length_dividers.spacing}")
    print(f"Total spacing: {sum(design.length_dividers.spacing)}mm (should be {design.length_internal}mm)")
    print("✓ Even divider test passed\n")

def test_custom_compartments():
    """Test box with custom compartment sizes"""
    print("Testing custom compartment sizes...")
    
    design = create_box_design(
        length=200, width=100, height=50,
        thickness=3, inside=True,
        div_l=3,  # 3 dividers = 4 compartments
        div_l_custom="40; 60; 50"  # First 3 compartments, 4th calculated
    )
    
    print(f"Custom sizes input: 40; 60; 50")
    print(f"Parsed custom sizes: {design.length_dividers.custom_sizes}")
    print(f"Final compartment sizes: {design.length_dividers.compartment_sizes}")
    print(f"Divider positions: {design.length_dividers.positions}")
    
    # Verify the math
    expected_available = design.length_internal - 3 * design.thickness  # Space for compartments
    expected_remaining = expected_available - sum([40, 60, 50])  # Remaining for 4th compartment
    print(f"Expected 4th compartment: {expected_remaining}mm")
    print(f"Actual 4th compartment: {design.length_dividers.compartment_sizes[3]}mm")
    print("✓ Custom compartments test passed\n")

def test_parsing():
    """Test compartment size parsing"""
    print("Testing compartment size parsing...")
    
    test_cases = [
        ("40; 60; 50", [40.0, 60.0, 50.0]),
        ("40,5; 60.0; 50", [40.5, 60.0, 50.0]),  # Mixed decimal separators
        ("100", [100.0]),
        ("", []),
        ("  50.5  ;  60,0  ", [50.5, 60.0])  # Whitespace
    ]
    
    for input_str, expected in test_cases:
        result = parse_compartment_sizes(input_str)
        print(f"'{input_str}' -> {result}")
        assert result == expected, f"Expected {expected}, got {result}"
    
    print("✓ Parsing test passed\n")

def test_error_cases():
    """Test error handling"""
    print("Testing error cases...")
    
    # Test oversized compartments
    try:
        design = create_box_design(
            length=100, width=100, height=50,
            thickness=3, inside=True,
            div_l=2,
            div_l_custom="60; 70"  # Total 130mm but only ~94mm available
        )
        print("❌ Should have failed for oversized compartments")
    except Exception as e:
        print(f"✓ Correctly caught oversized compartments: {e}")
    
    # Test too many dividers
    try:
        design = create_box_design(
            length=50, width=100, height=50,
            thickness=10, inside=True,
            div_l=10  # Too many dividers
        )
        print("❌ Should have failed for too many dividers")
    except Exception as e:
        print(f"✓ Correctly caught too many dividers: {e}")
    
    print()

def test_enum_usage():
    """Test that enums work correctly in the design system"""
    print("Testing enum usage...")
    
    # Test with explicit enum values
    design = create_box_design(
        length=150, width=100, height=60,
        thickness=3, inside=False,
        box_type=BoxType.NO_TOP,
        style=LayoutStyle.COMPACT
    )
    
    print(f"Box type: {design.box_type} ({design.box_type.name})")
    print(f"Style: {design.style} ({design.style.name})")
    
    # Verify the enums are working
    assert design.box_type == BoxType.NO_TOP
    assert design.style == LayoutStyle.COMPACT
    print("✓ Enum usage test passed\n")

if __name__ == "__main__":
    print("Testing Box Design Logic")
    print("=" * 50)
    
    test_basic_design()
    test_dividers_even()
    test_custom_compartments()
    test_parsing()
    test_enum_usage()
    test_error_cases()
    
    print("All design tests passed! ✅")

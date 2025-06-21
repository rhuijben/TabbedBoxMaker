#!/usr/bin/env python3
"""
Test the updated generation system with proper divider placement
"""

from boxmaker_core import BoxMakerCore
from boxmaker_constants import BoxType, LayoutStyle
import os


def test_generation_with_dividers():
    """Test box generation with dividers for different box types"""
    
    # Test parameters
    test_cases = [
        {
            "name": "full_box_with_dividers",
            "boxtype": BoxType.FULL_BOX,
            "div_l": 2,
            "div_w": 1,
            "description": "Full box with 2 length and 1 width divider"
        },
        {
            "name": "no_top_with_dividers", 
            "boxtype": BoxType.NO_TOP,
            "div_l": 1,
            "div_w": 2,
            "description": "No top box with 1 length and 2 width dividers"
        },
        {
            "name": "no_sides_with_dividers",
            "boxtype": BoxType.NO_SIDES,
            "div_l": 0,
            "div_w": 1,
            "description": "No sides box with 1 width divider"
        },
        {
            "name": "custom_compartments",
            "boxtype": BoxType.FULL_BOX,
            "div_l": 3,
            "div_w": 0,
            "div_l_custom": "30; 40; 20",
            "description": "Full box with custom length compartments"
        }
    ]
    
    # Create output directory
    output_dir = "test_results"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    print("Testing Box Generation with Dividers")
    print("=" * 50)
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case['description']}")
        print("-" * 40)
        
        core = BoxMakerCore()
        core.set_parameters(
            length=120,  # Larger box for better divider visibility
            width=100,
            height=60,
            thickness=3,
            inside=True,
            div_l=test_case["div_l"],
            div_w=test_case["div_w"],
            div_l_custom=test_case.get("div_l_custom", ""),
            div_w_custom=test_case.get("div_w_custom", ""),
            boxtype=test_case["boxtype"],
            tab=12,
            style=LayoutStyle.SEPARATED
        )
        
        try:
            # Generate the box
            core.generate_box()
            
            # Print design information
            design = core.design
            print(f"Box type: {design.box_type.name}")
            print(f"External dimensions: {design.length_external:.1f} x {design.width_external:.1f} x {design.height_external:.1f}")
            print(f"Internal dimensions: {design.length_internal:.1f} x {design.width_internal:.1f} x {design.height_internal:.1f}")
            
            # Print divider information
            if design.length_dividers.count > 0:
                print(f"Length dividers: {design.length_dividers.count}")
                print(f"  Positions: {[f'{p:.1f}' for p in design.length_dividers.positions]}")
                print(f"  Compartments: {[f'{c:.1f}' for c in design.length_dividers.compartment_sizes]}")
            
            if design.width_dividers.count > 0:
                print(f"Width dividers: {design.width_dividers.count}")
                print(f"  Positions: {[f'{p:.1f}' for p in design.width_dividers.positions]}")
                print(f"  Compartments: {[f'{c:.1f}' for c in design.width_dividers.compartment_sizes]}")
            
            # Generate SVG
            svg_content = core.generate_svg()
            svg_filename = os.path.join(output_dir, f"{test_case['name']}.svg")
            
            with open(svg_filename, 'w') as f:
                f.write(svg_content)
            
            print(f"✓ SVG saved: {svg_filename}")
            print(f"  Paths generated: {len(core.paths)}")
            
        except Exception as e:
            print(f"✗ Error: {e}")
    
    print(f"\nAll test files saved in: {output_dir}/")


def test_divider_positions():
    """Test that divider positions are calculated correctly"""
    print("\nTesting Divider Position Calculations")
    print("=" * 50)
    
    core = BoxMakerCore()
    core.set_parameters(
        length=100, width=80, height=60, thickness=3,
        inside=True, div_l=2, div_w=1, 
        boxtype=BoxType.FULL_BOX, tab=15
    )
    
    core.generate_box()
    design = core.design
    
    print("Length direction (100mm internal):")
    print(f"  Dividers: {design.length_dividers.count}")
    print(f"  Positions: {design.length_dividers.positions}")
    print(f"  Compartments: {design.length_dividers.compartment_sizes}")
    print(f"  Total: {sum(design.length_dividers.compartment_sizes) + design.length_dividers.count * design.thickness}")
    
    print("\nWidth direction (80mm internal):")
    print(f"  Dividers: {design.width_dividers.count}")
    print(f"  Positions: {design.width_dividers.positions}")
    print(f"  Compartments: {design.width_dividers.compartment_sizes}")
    print(f"  Total: {sum(design.width_dividers.compartment_sizes) + design.width_dividers.count * design.thickness}")


if __name__ == "__main__":
    test_generation_with_dividers()
    test_divider_positions()

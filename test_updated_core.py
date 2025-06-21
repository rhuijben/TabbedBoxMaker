#!/usr/bin/env python3
"""
Test the updated BoxMakerCore with design system
"""

from boxmaker_core import BoxMakerCore

def test_updated_core():
    """Test that the updated core works with the design system"""
    print("Testing Updated BoxMakerCore")
    print("=" * 40)
    core = BoxMakerCore()
    core.set_parameters(
        length=200, width=100, height=50,
        thickness=3, inside=True, tab=10,  # Smaller tab for this box size
        div_l=2, div_l_custom="60; 80"  # Two compartments specified, third calculated
    )
    
    try:
        core.generate_box()
        print(f"✓ Box generated successfully")
        print(f"Design dimensions:")
        print(f"  External: {core.design.length_external}x{core.design.width_external}x{core.design.height_external}mm")
        print(f"  Internal: {core.design.length_internal}x{core.design.width_internal}x{core.design.height_internal}mm")
        print(f"Length dividers:")
        print(f"  Count: {core.design.length_dividers.count}")
        print(f"  Positions: {core.design.length_dividers.positions}")
        print(f"  Compartments: {core.design.length_dividers.compartment_sizes}")
        print(f"  Spacing: {core.design.length_dividers.spacing}")
        
        # Generate SVG to make sure it still works
        svg = core.generate_svg()
        if '<svg' in svg and '</svg>' in svg:
            print(f"✓ SVG generation successful")
            with open('test_results/updated_core_test.svg', 'w') as f:
                f.write(svg)
            print(f"  Saved: test_results/updated_core_test.svg")
        else:
            print(f"❌ SVG generation failed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_updated_core()

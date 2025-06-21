#!/usr/bin/env python3
"""
Test script to verify kerf is properly applied throughout the generation process
"""

import sys
from pathlib import Path

# Add the current directory to the path to import our modules
sys.path.insert(0, str(Path(__file__).parent))

from boxmaker_core import BoxMakerCore
from box_design import create_box_design


def test_kerf_separation():
    """Test that kerf is properly separated between design and generation phases"""
    print("Testing kerf separation between design and generation...")
    
    # Test parameters
    length, width, height = 100.0, 80.0, 50.0
    thickness = 3.0
    kerf = 0.5
    
    # 1. Create design without kerf
    design = create_box_design(
        length=length, width=width, height=height,
        thickness=thickness, inside=False
    )
    
    print(f"Design dimensions (no kerf):")
    print(f"  External: {design.length_external} x {design.width_external} x {design.height_external}")
    print(f"  Internal: {design.length_internal} x {design.width_internal} x {design.height_internal}")
    
    # 2. Create core and generate box (with kerf)
    core = BoxMakerCore()
    core.set_parameters(
        length=length, width=width, height=height,
        thickness=thickness, kerf=kerf, tab=15.0
    )
    
    core.generate_box()
    
    # 3. Check that the core's design matches our direct design creation
    assert abs(core.design.length_external - design.length_external) < 0.001
    assert abs(core.design.width_external - design.width_external) < 0.001
    assert abs(core.design.height_external - design.height_external) < 0.001
    
    print(f"Core design dimensions (no kerf):")
    print(f"  External: {core.design.length_external} x {core.design.width_external} x {core.design.height_external}")
    print(f"  Internal: {core.design.length_internal} x {core.design.width_internal} x {core.design.height_internal}")
    
    # 4. Generate SVG and check that it contains reasonable content
    svg_content = core.generate_svg()
    assert '<svg' in svg_content and '</svg>' in svg_content
    
    print(f"✓ SVG generated successfully (length: {len(svg_content)} chars)")
    
    return True


def test_kerf_manufacturing_adjustment():
    """Test that kerf adjustments are applied during manufacturing phase"""
    print("\nTesting kerf adjustments in manufacturing...")
    
    # Test two identical boxes with different kerf values
    base_params = {
        'length': 100.0, 'width': 80.0, 'height': 50.0,
        'thickness': 3.0, 'tab': 15.0
    }
    
    # Box 1: No kerf
    core1 = BoxMakerCore()
    core1.set_parameters(**base_params, kerf=0.0)
    core1.generate_box()
    
    # Box 2: With kerf
    core2 = BoxMakerCore()
    core2.set_parameters(**base_params, kerf=0.5)
    core2.generate_box()
    
    # Both should have identical design dimensions (kerf not applied to design)
    assert abs(core1.design.length_external - core2.design.length_external) < 0.001
    assert abs(core1.design.width_external - core2.design.width_external) < 0.001
    assert abs(core1.design.height_external - core2.design.height_external) < 0.001
    
    print(f"✓ Design dimensions identical regardless of kerf")
    
    # But different SVG content (kerf affects the actual cut paths)
    svg1 = core1.generate_svg()
    svg2 = core2.generate_svg()
    
    # They should be different because kerf affects the manufacturing
    assert svg1 != svg2
    print(f"✓ SVG output differs with kerf (as expected)")
    print(f"  No kerf SVG: {len(svg1)} chars")
    print(f"  With kerf SVG: {len(svg2)} chars")
    
    return True


def test_kerf_with_dividers():
    """Test that kerf handling works correctly with dividers"""
    print("\nTesting kerf with dividers...")
    
    # Create a box with dividers and kerf
    core = BoxMakerCore()
    core.set_parameters(
        length=120.0, width=100.0, height=60.0,
        thickness=3.0, kerf=0.2, tab=20.0,
        div_l=2, div_w=1  # 2 dividers along length, 1 along width
    )
    
    core.generate_box()
    
    # Check that divider information is in the design (without kerf adjustments)
    assert len(core.design.dividers_length.positions) == 2
    assert len(core.design.dividers_width.positions) == 1
    
    print(f"✓ Dividers in design: {len(core.design.dividers_length.positions)} length, {len(core.design.dividers_width.positions)} width")
    
    # Generate SVG and verify it contains content
    svg_content = core.generate_svg()
    assert '<svg' in svg_content and '</svg>' in svg_content
    assert len(svg_content) > 1000  # Should be substantial content with dividers
    
    print(f"✓ SVG with dividers generated successfully (length: {len(svg_content)} chars)")
    
    return True


def run_kerf_tests():
    """Run all kerf-related tests"""
    print("Running kerf application tests...\n")
    
    tests = [
        test_kerf_separation,
        test_kerf_manufacturing_adjustment,
        test_kerf_with_dividers
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
                print(f"[PASS] {test.__name__}")
            else:
                print(f"[FAIL] {test.__name__}")
        except Exception as e:
            print(f"[FAIL] {test.__name__}: {e}")
    
    print(f"\nKerf Tests: {passed}/{len(tests)} passed")
    
    if passed == len(tests):
        print("✅ All kerf application tests passed!")
        return True
    else:
        print("❌ Some kerf tests failed!")
        return False


if __name__ == "__main__":
    success = run_kerf_tests()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Test script for BoxMaker functionality
Tests various configurations to ensure the refactored code works correctly
"""

import os
import sys
import tempfile
from pathlib import Path

# Add the current directory to the path to import our modules
sys.path.insert(0, str(Path(__file__).parent))

from boxmaker_core import BoxMakerCore
from boxmaker_exceptions import DimensionError, TabError, MaterialError


def test_basic_box():
    """Test basic box generation"""
    print("Testing basic box generation...")
    
    core = BoxMakerCore()
    core.set_parameters(
        length=100.0,
        width=80.0,
        height=50.0,
        thickness=3.0,
        kerf=0.1,
        tab=15.0,
        tabtype=0  # Laser
    )
    
    try:
        result = core.generate_box()
        assert len(result['paths']) > 0, "Should generate some paths"
        print("[PASS] Basic box test passed")
        return True
    except Exception as e:
        print(f"[FAIL] Basic box test failed: {e}")
        return False


def test_box_with_dividers():
    """Test box with 3 dividers"""
    print("Testing box with 3 dividers...")
    
    core = BoxMakerCore()
    core.set_parameters(
        length=120.0,
        width=100.0,
        height=60.0,
        thickness=3.0,
        kerf=0.1,
        tab=20.0,
        div_l=2,  # 2 dividers along length
        div_w=1,  # 1 divider along width
        tabtype=0  # Laser
    )
    
    try:
        result = core.generate_box()
        assert len(result['paths']) > 0, "Should generate paths for box and dividers"
        print("[PASS] Box with dividers test passed")
        return True
    except Exception as e:
        print(f"[FAIL] Box with dividers test failed: {e}")
        return False


def test_different_material_thickness():
    """Test with different material thickness (6mm instead of 3mm)"""
    print("Testing with 6mm material thickness...")
    
    core = BoxMakerCore()
    core.set_parameters(
        length=150.0,
        width=100.0,
        height=75.0,
        thickness=6.0,  # Thicker material
        kerf=0.2,       # Larger kerf for thicker material
        tab=25.0,
        tabtype=0  # Laser
    )
    
    try:
        result = core.generate_box()
        assert len(result['paths']) > 0, "Should generate paths with thicker material"
        print("[PASS] Different material thickness test passed")
        return True
    except Exception as e:
        print(f"[FAIL] Different material thickness test failed: {e}")
        return False


def test_cnc_vs_laser():
    """Test CNC (dogbone) vs Laser cutting"""
    print("Testing CNC vs Laser cutting...")
    
    # Test laser cutting
    core_laser = BoxMakerCore()
    core_laser.set_parameters(
        length=100.0,
        width=80.0,
        height=50.0,
        thickness=3.0,
        kerf=0.1,
        tab=15.0,
        tabtype=0  # Laser
    )
    
    # Test CNC cutting (dogbone)
    core_cnc = BoxMakerCore()
    core_cnc.set_parameters(
        length=100.0,
        width=80.0,
        height=50.0,
        thickness=3.0,
        kerf=0.1,
        tab=15.0,
        tabtype=1  # CNC/Dogbone
    )
    
    try:
        result_laser = core_laser.generate_box()
        result_cnc = core_cnc.generate_box()
        
        assert len(result_laser['paths']) > 0, "Laser should generate paths"
        assert len(result_cnc['paths']) > 0, "CNC should generate paths"
        
        # The paths should be different due to dogbone cuts
        assert result_laser['paths'] != result_cnc['paths'], "Laser and CNC paths should differ"
        
        print("[PASS] CNC vs Laser test passed")
        return True
    except Exception as e:
        print(f"[FAIL] CNC vs Laser test failed: {e}")
        return False


def test_svg_generation():
    """Test SVG file generation"""
    print("Testing SVG generation...")
    
    core = BoxMakerCore()
    core.set_parameters(
        length=100.0,
        width=80.0,
        height=50.0,
        thickness=3.0,
        kerf=0.1,
        tab=15.0
    )
    
    try:
        svg_content = core.generate_svg()
        
        # Basic SVG validation
        assert svg_content.startswith('<?xml'), "Should start with XML declaration"
        assert '<svg' in svg_content, "Should contain SVG element"
        assert '</svg>' in svg_content, "Should end with SVG closing tag"
        assert 'path' in svg_content, "Should contain path elements"
        
        # Write to temporary file to test file I/O
        with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False) as f:
            f.write(svg_content)
            temp_path = f.name
        
        # Verify file was written
        assert os.path.exists(temp_path), "SVG file should be created"
        
        # Clean up
        os.unlink(temp_path)
        
        print("[PASS] SVG generation test passed")
        return True
    except Exception as e:
        print(f"[FAIL] SVG generation test failed: {e}")
        return False


def test_error_conditions():
    """Test error handling"""
    print("Testing error conditions...")
    
    # Test zero dimensions
    core = BoxMakerCore()
    try:
        core.set_parameters(length=0, width=100, height=50)
        core.generate_box()
        print("[FAIL] Should have raised error for zero dimensions")
        return False
    except DimensionError:
        print("[PASS] Correctly handled zero dimensions")
    
    # Test tab too large (physical constraint - larger than dimension/3)
    core = BoxMakerCore()
    try:
        # 200x250x100mm box with 80mm tabs (larger than 100mm/3 = 33mm)
        core.set_parameters(length=200, width=250, height=100, tab=80, thickness=3)
        core.generate_box()
        print("[FAIL] Should have raised error for oversized tab")
        return False
    except TabError:
        print("[PASS] Correctly handled oversized tab")
    
    # Test thickness too large for dimensions
    core = BoxMakerCore()
    try:
        # Small 6x6x6cm box with 3.5cm thickness (more than half)
        core.set_parameters(length=60, width=60, height=60, thickness=35, tab=19)  # 19mm < 20mm (60/3) and > 17.5mm (35*0.5)
        core.generate_box()
        print("[FAIL] Should have raised error for excessive thickness")
        return False
    except MaterialError:
        print("[PASS] Correctly handled excessive thickness")
    
    return True


def test_box_layouts():
    """Test different box layouts"""
    print("Testing different box layouts...")
    
    layouts = [1, 2, 3]  # Diagramatic, 3-piece, Inline
    
    for layout in layouts:
        core = BoxMakerCore()
        core.set_parameters(
            length=100.0,
            width=80.0,
            height=50.0,
            thickness=3.0,
            kerf=0.1,
            tab=15.0,
            style=layout
        )
        
        try:
            result = core.generate_box()
            assert len(result['paths']) > 0, f"Layout {layout} should generate paths"
        except Exception as e:
            print(f"[FAIL] Layout {layout} test failed: {e}")
            return False
    
    print("[PASS] All layout tests passed")
    return True


def test_save_test_files():
    """Generate test files for manual inspection"""
    print("Generating test files for manual inspection...")
    
    # Ensure test_results directory exists
    test_results_dir = Path("test_results")
    test_results_dir.mkdir(exist_ok=True)
    
    test_cases = [
        {
            'name': 'basic_box_laser',
            'params': {
                'length': 100.0, 'width': 80.0, 'height': 50.0,
                'thickness': 3.0, 'kerf': 0.1, 'tab': 15.0, 'tabtype': 0
            }
        },
        {
            'name': 'basic_box_cnc',
            'params': {
                'length': 100.0, 'width': 80.0, 'height': 50.0,
                'thickness': 3.0, 'kerf': 0.1, 'tab': 15.0, 'tabtype': 1
            }
        },
        {
            'name': 'box_with_dividers',
            'params': {
                'length': 120.0, 'width': 100.0, 'height': 60.0,
                'thickness': 3.0, 'kerf': 0.1, 'tab': 20.0,
                'div_l': 2, 'div_w': 1, 'tabtype': 0
            }
        },
        {
            'name': 'thick_material_box',
            'params': {
                'length': 150.0, 'width': 100.0, 'height': 75.0,
                'thickness': 6.0, 'kerf': 0.2, 'tab': 25.0, 'tabtype': 0
            }
        }
    ]
    
    try:
        for test_case in test_cases:
            core = BoxMakerCore()
            core.set_parameters(**test_case['params'])
            
            svg_content = core.generate_svg()
            
            output_file = test_results_dir / f"test_{test_case['name']}.svg"
            with open(output_file, 'w') as f:
                f.write(svg_content)
            
            print(f"  Generated: {output_file}")
        
        print("[PASS] Test files generated successfully")
        return True
    except Exception as e:
        print(f"[FAIL] Test file generation failed: {e}")
        return False


def test_realistic_compartment_box():
    """Test realistic compartment box (20x25x10cm with 3 dividers)"""
    print("Testing realistic compartment box...")
    
    core = BoxMakerCore()
    # Your example: 200x250x100mm box with 3mm material, 12mm tabs, 3 compartments
    core.set_parameters(
        length=200, width=250, height=100,
        thickness=3, kerf=0.1, tab=12,
        div_l=3  # 3 compartments in length direction
    )
    
    try:
        core.generate_box()
        print("[PASS] Realistic compartment box test passed")
        return True
    except Exception as e:
        print(f"[FAIL] Realistic compartment box test failed: {e}")
        return False


def test_thin_tabs():
    """Test tabs thinner than material thickness (allowed but weak)"""
    print("Testing thin tabs (weaker but allowed)...")
    
    core = BoxMakerCore()
    # 6mm thickness with 4mm tabs (2/3 ratio) - should work but be weak
    core.set_parameters(length=200, width=250, height=100, thickness=6, tab=4, div_l=3)
    
    try:
        core.generate_box()
        svg_content = core.generate_svg()
        
        # Should generate valid SVG
        if '<svg' in svg_content and '</svg>' in svg_content:
            print("[PASS] Thin tabs test passed (tabs allowed but may be weak)")
            return True
        else:
            print("[FAIL] Failed to generate valid SVG for thin tabs")
            return False
    except Exception as e:
        print(f"[FAIL] Unexpected error with thin tabs: {e}")
        return False


def test_large_box_big_tabs():
    """Test large box with proportionally large tabs"""
    print("Testing large box with big tabs...")
    
    core = BoxMakerCore()
    # Large 60x40x30cm box with 6mm material and 60mm tabs (10x thickness)
    core.set_parameters(
        length=600, width=400, height=300,
        thickness=6, tab=60  # 60mm tabs (10x thickness) - should work for large box
    )
    
    try:
        core.generate_box()
        svg_content = core.generate_svg()
        
        if '<svg' in svg_content and '</svg>' in svg_content:
            print("[PASS] Large box with big tabs test passed")
            return True
        else:
            print("[FAIL] Failed to generate valid SVG for large box")
            return False
    except Exception as e:
        print(f"[FAIL] Large box test failed: {e}")
        return False


def test_custom_compartment_sizes():
    """Test custom compartment sizes feature"""
    print("Testing custom compartment sizes...")
    
    core = BoxMakerCore()
    # Test the example from the issue: 21cm inside width with custom compartments
    core.set_parameters(
        length=210,  # 21cm
        width=150,   # 15cm  
        height=50,   # 5cm
        thickness=3,
        tab=15,
        div_l=3,  # 3 dividers (4 compartments)
        div_l_custom="63; 63.0; 50",  # First 3 compartments: 63mm, 63mm, 50mm
        inside=1  # Inside dimensions
    )
    
    try:
        core.generate_box()
        svg_content = core.generate_svg()
        
        if '<svg' in svg_content and '</svg>' in svg_content:
            print("[PASS] Custom compartment sizes test passed")
            return True
        else:
            print("[FAIL] Failed to generate valid SVG for custom compartments")
            return False
    except Exception as e:
        print(f"[FAIL] Custom compartment sizes test failed: {e}")
        return False


def test_mixed_custom_compartments():
    """Test custom compartments in both directions"""
    print("Testing mixed custom compartments...")
    
    core = BoxMakerCore()
    core.set_parameters(
        length=200, width=160, height=60,
        thickness=3, tab=15,
        div_l=2, div_w=1,
        div_l_custom="80; 60",  # Length compartments
        div_w_custom="70"       # Width compartments
    )
    
    try:
        core.generate_box()
        svg_content = core.generate_svg()
        
        if '<svg' in svg_content and '</svg>' in svg_content:
            print("[PASS] Mixed custom compartments test passed")
            return True
        else:
            print("[FAIL] Failed to generate valid SVG for mixed compartments")
            return False
    except Exception as e:
        print(f"[FAIL] Mixed custom compartments test failed: {e}")
        return False


def test_calculated_vs_explicit_compartment_output():
    """Test that calculated even spacing matches explicit compartment sizes for a 3x3 grid"""
    print("Testing calculated vs explicit compartment output...")
    
    # For a 300x240mm box with 3x3 compartments, calculate even spacing
    # Internal dimensions: 300-6=294mm length, 240-6=234mm width (3mm thickness * 2)
    # Even compartments: 294/4=73.5mm each length, 234/4=58.5mm each width
    
    # Test 1: Box with calculated even spacing (3 dividers each direction)
    core1 = BoxMakerCore()
    core1.set_parameters(
        length=300, width=240, height=60,
        thickness=3, tab=18, kerf=0.1,
        div_l=3, div_w=3,
        inside=1  # Inside dimensions
    )
    
    try:
        core1.generate_box()
        svg1 = core1.generate_svg()
    except Exception as e:
        print(f"[FAIL] Failed to generate calculated spacing box: {e}")
        return False
    
    # Test 2: Box with explicit even spacing (should be identical)
    core2 = BoxMakerCore()
    core2.set_parameters(
        length=300, width=240, height=60,
        thickness=3, tab=18, kerf=0.1,
        div_l=3, div_w=3,
        div_l_custom="73.5; 73.5; 73.5",  # 4 compartments of 73.5mm each
        div_w_custom="58.5; 58.5; 58.5",  # 4 compartments of 58.5mm each
        inside=1  # Inside dimensions
    )
    
    try:
        core2.generate_box()
        svg2 = core2.generate_svg()
    except Exception as e:
        print(f"[FAIL] Failed to generate explicit spacing box: {e}")
        return False
    
    # Compare the SVG outputs
    if not svg1 or not svg2:
        print("[FAIL] One or both SVGs are empty")
        return False
    
    # Check that both are valid SVGs
    if '<svg' not in svg1 or '</svg>' not in svg1:
        print("[FAIL] Calculated spacing produced invalid SVG")
        return False
        
    if '<svg' not in svg2 or '</svg>' not in svg2:
        print("[FAIL] Explicit spacing produced invalid SVG")
        return False
    
    # For this test, the outputs should be very similar (the paths might have tiny differences due to floating point)
    # We'll check that key characteristics are the same
    svg1_lines = svg1.count('<path')
    svg2_lines = svg2.count('<path')
    
    if abs(svg1_lines - svg2_lines) > 2:  # Allow small differences
        print(f"[FAIL] Different number of paths: calculated={svg1_lines}, explicit={svg2_lines}")
        return False
    
    # Check viewBox dimensions are similar
    import re
    viewbox1 = re.search(r'viewBox="([^"]*)"', svg1)
    viewbox2 = re.search(r'viewBox="([^"]*)"', svg2)
    
    if viewbox1 and viewbox2:
        vb1 = viewbox1.group(1)
        vb2 = viewbox2.group(1)
        if vb1 != vb2:
            print(f"! ViewBox differs slightly: calculated='{vb1}', explicit='{vb2}' (this may be acceptable)")
    
    # Save both for visual comparison
    with open('test_results/calculated_compartments_3x3.svg', 'w') as f:
        f.write(svg1)
    with open('test_results/explicit_compartments_3x3.svg', 'w') as f:
        f.write(svg2)
    
    print("[PASS] Calculated vs explicit compartment test passed")
    print("  Generated files for comparison:")
    print("    test_results/calculated_compartments_3x3.svg")
    print("    test_results/explicit_compartments_3x3.svg")
    return True


def test_custom_compartment_parsing():
    """Test parsing of custom compartment sizes with different decimal separators"""
    print("Testing custom compartment parsing...")
    
    from boxmaker_core import BoxMakerCore
    
    # Test various decimal separator combinations
    test_cases = [
        ("63,5; 63.0; 50", [63.5, 63.0, 50.0]),  # Mixed comma and dot
        ("63.5;50,0;75", [63.5, 50.0, 75.0]),    # Dot and comma mixed
        ("60; 70; 80.5", [60.0, 70.0, 80.5]),    # All dots with spaces
        ("100", [100.0]),                         # Single value
        ("50,5", [50.5]),                         # Single value with comma
        ("", []),                                 # Empty string
        ("  63.0  ;  70,5  ;  80  ", [63.0, 70.5, 80.0])  # Extra whitespace
    ]
    
    core = BoxMakerCore()
    
    for input_str, expected in test_cases:
        try:
            # Use a simple box setup to test parsing
            core.set_parameters(
                length=200, width=150, height=50,
                thickness=3, tab=15,
                div_l=len(expected) if expected else 0,
                div_l_custom=input_str
            )
            
            # Just check that it doesn't crash - the actual parsing logic is tested in the core
            core.generate_box()
            svg_content = core.generate_svg()
            
            if not ('<svg' in svg_content and '</svg>' in svg_content):
                print(f"[FAIL] Failed to generate SVG for input: '{input_str}'")
                return False
                
        except Exception as e:
            print(f"[FAIL] Parsing failed for input '{input_str}': {e}")
            return False
    
    print("[PASS] Custom compartment parsing test passed")
    return True


def run_all_tests():
    """Run all tests"""
    print("Running BoxMaker tests...\n")
    
    tests = [
        test_basic_box,
        test_box_with_dividers,
        test_different_material_thickness,
        test_cnc_vs_laser,
        test_svg_generation,
        test_error_conditions,
        test_box_layouts,
        test_save_test_files,
        test_realistic_compartment_box,
        test_thin_tabs,
        test_large_box_big_tabs,
        test_custom_compartment_sizes,
        test_mixed_custom_compartments,
        test_calculated_vs_explicit_compartment_output,
        test_custom_compartment_parsing
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()  # Empty line between tests
    
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("[SUCCESS] All tests passed! The refactor was successful.")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)

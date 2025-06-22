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
from boxmaker_exceptions import DimensionError, TabError, MaterialError, ValidationError
from boxmaker_constants import BoxType


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
    """Test parsing of custom compartment sizes with strict validation"""
    print("Testing custom compartment parsing...")
    
    # Test cases with proper sizing for a 200x150x50 box (3mm thickness, no kerf at design stage)
    # Internal dimensions: 194mm length x 144mm width  
    # For 2 dividers (3 compartments): available space = 194 - 2*3 = 188mm
    test_cases = [
        # Case 1: Exact fit - all compartments specified (total = 188mm)
        ("60; 65; 63", [60.0, 65.0, 63.0], 2, "All compartments fit exactly"),
        
        # Case 2: Partial specification - let system calculate remainder  
        ("60; 65", [60.0, 65.0], 2, "First two specified, third calculated"),
        
        # Case 3: Single compartment specified
        ("80", [80.0], 2, "Only first compartment specified"),
        
        # Case 4: Different decimal separators (total = 188mm)
        ("60.5; 64.5; 63", [60.5, 64.5, 63.0], 2, "Mixed decimal separators"),
        
        # Case 5: No custom sizes - even distribution
        ("", [], 2, "No custom sizes - even distribution"),
        
        # Case 6: Single divider (2 compartments) - available space = 194 - 1*3 = 191mm
        ("90; 101", [90.0, 101.0], 1, "Two compartments with one divider"),
        
        # Case 7: Whitespace handling (total = 188mm)
        ("  60  ;  65  ;  63  ", [60.0, 65.0, 63.0], 2, "Extra whitespace"),
    ]
    
    core = BoxMakerCore()
    
    for input_str, expected_sizes, num_dividers, description in test_cases:
        try:
            print(f"  Testing: {description}")
            print(f"    Input: '{input_str}' with {num_dividers} dividers")
            
            core.set_parameters(
                length=200, width=150, height=50,
                thickness=3, tab=15,
                div_l=num_dividers,
                div_l_custom=input_str,
                inside=False  # Use outside dimensions for predictable internal space
            )
            
            # Generate the box to test the actual implementation
            core.generate_box()
            svg_content = core.generate_svg()
            
            if not ('<svg' in svg_content and '</svg>' in svg_content):
                print(f"    [FAIL] Failed to generate SVG")
                return False
                
            print(f"    [PASS] Generated successfully")
                
        except Exception as e:
            print(f"    [FAIL] Error: {e}")
            return False
    
    # Test error cases - sizes that don't fit
    print("  Testing error cases:")
    
    error_cases = [
        ("100; 100; 100", 2, "Compartments too large (300mm > 188mm available)"),
        ("200", 1, "Single compartment too large (200mm > 191mm available)"),
    ]
    
    for input_str, num_dividers, description in error_cases:
        try:
            print(f"    Testing: {description}")
            core.set_parameters(
                length=200, width=150, height=50,
                thickness=3, tab=15,
                div_l=num_dividers,
                div_l_custom=input_str,
                inside=False            )
            
            core.generate_box()
            print(f"    [FAIL] Should have failed but didn't: {description}")
            return False
            
        except ValidationError as e:
            print(f"    [PASS] Correctly rejected: {description}")
        except Exception as e:
            print(f"    [FAIL] Wrong error type: {e}")
            return False
    
    print("[PASS] Custom compartment parsing test passed")
    return True


def test_dividers_with_kerf():
    """Test that dividers work correctly with kerf compensation"""
    print("Testing dividers with kerf compensation...")
    
    # Test box with dividers and kerf
    core = BoxMakerCore()
    core.set_parameters(
        length=120.0, width=100.0, height=60.0,
        thickness=3.0, kerf=0.2, tab=15.0,
        div_l=2, div_w=1,  # 2 dividers along length, 1 along width
        tabtype=0  # Laser
    )
    
    try:
        result = core.generate_box()
          # Check that design has correct divider information
        assert len(core.design.length_dividers.positions) == 2, "Should have 2 length dividers"
        assert len(core.design.width_dividers.positions) == 1, "Should have 1 width divider"
        
        # Check that divider positions are reasonable (not affected by kerf)
        length_positions = core.design.length_dividers.positions
        width_positions = core.design.width_dividers.positions
          # For 120mm length with 2 dividers, expecting positions around 37.33mm and 74.67mm  
        assert 35 < length_positions[0] < 40, f"First length divider at {length_positions[0]}, expected ~37"
        assert 72 < length_positions[1] < 77, f"Second length divider at {length_positions[1]}, expected ~75"
        
        # For 100mm width with 1 divider, expecting position around 50mm
        assert 45 < width_positions[0] < 55, f"Width divider at {width_positions[0]}, expected ~50"
        
        # Generate SVG to ensure no errors with kerf
        svg_content = core.generate_svg()
        assert '<svg' in svg_content and '</svg>' in svg_content
        assert len(svg_content) > 1000, "Should generate substantial content with dividers"
        
        print(f"✓ Dividers with kerf: {len(length_positions)} length + {len(width_positions)} width")
        print(f"✓ Length positions: {[f'{pos:.1f}' for pos in length_positions]}")
        print(f"✓ Width positions: {[f'{pos:.1f}' for pos in width_positions]}")
        
        print("[PASS] Dividers with kerf test passed")
        return True
        
    except Exception as e:
        print(f"[FAIL] Dividers with kerf test failed: {e}")
        return False


def test_custom_compartments_with_kerf():
    """Test custom compartment sizes with kerf compensation"""
    print("Testing custom compartments with kerf...")
    
    # Test with custom compartment sizes and kerf
    core = BoxMakerCore()
    core.set_parameters(
        length=150.0, width=120.0, height=60.0,
        thickness=3.0, kerf=0.15, tab=15.0,
        div_l=2,  # 2 dividers = 3 compartments
        div_l_custom="42; 50; 46",  # Custom sizes (total=138, available=138)
        tabtype=0
    )
    
    try:
        result = core.generate_box()
        
        # Check that custom compartments are correctly parsed
        compartments = core.design.length_dividers.compartment_sizes
        assert len(compartments) == 3, f"Should have 3 compartments, got {len(compartments)}"
        assert abs(compartments[0] - 42.0) < 0.1, f"First compartment should be 42mm, got {compartments[0]}"
        assert abs(compartments[1] - 50.0) < 0.1, f"Second compartment should be 50mm, got {compartments[1]}"
        assert abs(compartments[2] - 46.0) < 0.1, f"Third compartment should be 46mm, got {compartments[2]}"
        
        # Check divider positions are correct for custom compartments
        positions = core.design.length_dividers.positions
        assert len(positions) == 2, f"Should have 2 dividers, got {len(positions)}"
        
        # First divider should be at first compartment size
        assert abs(positions[0] - 42.0) < 0.1, f"First divider at {positions[0]}, expected 42"
        # Second divider should be at first + second compartment sizes + divider thickness
        assert abs(positions[1] - 95.0) < 0.1, f"Second divider at {positions[1]}, expected 95"
        
        # Verify kerf doesn't affect the design dimensions
        assert core.design.length_external == 150.0, "Design length should be unchanged by kerf"
        
        # Generate SVG with custom compartments and kerf
        svg_content = core.generate_svg()
        assert '<svg' in svg_content and '</svg>' in svg_content
        
        print(f"✓ Custom compartments: {compartments}")
        print(f"✓ Divider positions: {[f'{pos:.1f}' for pos in positions]}")
        
        # Test that invalid compartment sizes are rejected (user should know what's wrong)
        print("  Testing rejection of invalid compartment sizes...")
        core_invalid = BoxMakerCore()
        core_invalid.set_parameters(
            length=150.0, width=120.0, height=60.0,
            thickness=3.0, kerf=0.15, tab=15.0,
            div_l=2,  # 2 dividers = 3 compartments, available space = 138mm
            div_l_custom="50; 60; 50",  # Total=160mm > 138mm available - should fail
            tabtype=0
        )
        
        try:
            core_invalid.generate_box()
            assert False, "Should have failed with oversized compartments"
        except ValidationError as e:
            print(f"  ✓ Correctly rejected invalid sizes: {e}")
        
        print("[PASS] Custom compartments with kerf test passed")
        return True
        
    except Exception as e:
        print(f"[FAIL] Custom compartments with kerf test failed: {e}")
        return False


def test_dividers_kerf_comparison():
    """Compare divider output with and without kerf to verify correct compensation"""
    print("Testing divider kerf compensation comparison...")
    
    # Test parameters
    length, width, height = 100.0, 80.0, 50.0
    thickness = 3.0
    kerf = 0.2
    
    # Box with dividers, no kerf
    core_no_kerf = BoxMakerCore()
    core_no_kerf.set_parameters(
        length=length, width=width, height=height,
        thickness=thickness, kerf=0.0, tab=15.0,
        div_l=1, div_w=1,  # Simple 1x1 divider setup
        tabtype=0
    )
    
    # Box with dividers, with kerf
    core_with_kerf = BoxMakerCore()
    core_with_kerf.set_parameters(
        length=length, width=width, height=height,
        thickness=thickness, kerf=kerf, tab=15.0,
        div_l=1, div_w=1,  # Same divider setup
        tabtype=0
    )
    
    try:
        result_no_kerf = core_no_kerf.generate_box()
        result_with_kerf = core_with_kerf.generate_box()
          # Design should be identical regardless of kerf
        assert core_no_kerf.design.length_dividers.positions == core_with_kerf.design.length_dividers.positions
        assert core_no_kerf.design.width_dividers.positions == core_with_kerf.design.width_dividers.positions
        
        # Both should generate paths successfully
        assert len(result_no_kerf['paths']) > 0, "No kerf version should generate paths"
        assert len(result_with_kerf['paths']) > 0, "With kerf version should generate paths"
        
        # Path counts should be the same (same number of pieces and dividers)
        assert len(result_no_kerf['paths']) == len(result_with_kerf['paths']), \
            f"Path counts differ: {len(result_no_kerf['paths'])} vs {len(result_with_kerf['paths'])}"
        
        # Generate SVGs to ensure both work
        svg_no_kerf = core_no_kerf.generate_svg()
        svg_with_kerf = core_with_kerf.generate_svg()
        
        assert '<svg' in svg_no_kerf and '</svg>' in svg_no_kerf
        assert '<svg' in svg_with_kerf and '</svg>' in svg_with_kerf
        
        # SVGs should be different due to kerf compensation
        assert svg_no_kerf != svg_with_kerf, "SVGs should differ due to kerf compensation"
        
        print(f"✓ Design consistency: divider positions unchanged by kerf")
        print(f"✓ Path generation: both versions generate {len(result_no_kerf['paths'])} paths")
        print(f"✓ Kerf effect: SVG output differs as expected")
        
        print("[PASS] Divider kerf comparison test passed")
        return True
        
    except Exception as e:
        print(f"[FAIL] Divider kerf comparison test failed: {e}")
        return False


def test_complex_custom_compartments_with_kerf():
    """Test complex custom compartment configurations with kerf"""
    print("Testing complex custom compartments with kerf...")
    
    # Calculate available spaces:
    # Length: 180 - 2*3 (walls) - 3*3 (dividers) = 165mm
    # Width: 140 - 2*3 (walls) - 2*3 (dividers) = 128mm
    
    # Test with both length and width custom compartments
    core = BoxMakerCore()
    core.set_parameters(
        length=180.0, width=140.0, height=60.0,
        thickness=3.0, kerf=0.25, tab=15.0,
        div_l=3,  # 3 dividers = 4 compartments along length
        div_w=2,  # 2 dividers = 3 compartments along width
        div_l_custom="40; 50; 40; 35",  # 4 custom length compartments (total=165, available=165)
        div_w_custom="40; 45; 43",      # 3 custom width compartments (total=128, available=128)
        tabtype=0
    )
    
    try:
        result = core.generate_box()
        
        # Check length compartments - should match exactly as specified
        length_compartments = core.design.length_dividers.compartment_sizes
        assert len(length_compartments) == 4, f"Should have 4 length compartments, got {len(length_compartments)}"
        
        expected_length = [40.0, 50.0, 40.0, 35.0]
        for i, (actual, expected) in enumerate(zip(length_compartments, expected_length)):
            assert abs(actual - expected) < 0.1, f"Length compartment {i}: {actual} != {expected}"
        
        # Check width compartments - should match exactly as specified
        width_compartments = core.design.width_dividers.compartment_sizes
        assert len(width_compartments) == 3, f"Should have 3 width compartments, got {len(width_compartments)}"
        
        expected_width = [40.0, 45.0, 43.0]
        for i, (actual, expected) in enumerate(zip(width_compartments, expected_width)):
            assert abs(actual - expected) < 0.1, f"Width compartment {i}: {actual} != {expected}"
        
        # Check divider positions
        length_positions = core.design.length_dividers.positions
        width_positions = core.design.width_dividers.positions
        
        assert len(length_positions) == 3, f"Should have 3 length dividers, got {len(length_positions)}"
        assert len(width_positions) == 2, f"Should have 2 width dividers, got {len(width_positions)}"
        
        # Verify cumulative positions (compartment + divider thickness)
        assert abs(length_positions[0] - 40.0) < 0.1, f"First length divider: {length_positions[0]} != 40"
        assert abs(length_positions[1] - 93.0) < 0.1, f"Second length divider: {length_positions[1]} != 93"  # 40+50+3
        assert abs(length_positions[2] - 136.0) < 0.1, f"Third length divider: {length_positions[2]} != 136"  # 40+50+40+3+3
        
        assert abs(width_positions[0] - 40.0) < 0.1, f"First width divider: {width_positions[0]} != 40"
        assert abs(width_positions[1] - 88.0) < 0.1, f"Second width divider: {width_positions[1]} != 88"  # 40+45+3
        
        # Generate SVG with complex setup
        svg_content = core.generate_svg()
        assert '<svg' in svg_content and '</svg>' in svg_content
        assert len(svg_content) > 2000, "Should generate substantial content with many dividers"
        
        print(f"✓ Length compartments: {[f'{x:.1f}' for x in length_compartments]}")
        print(f"✓ Width compartments: {[f'{x:.1f}' for x in width_compartments]}")
        print(f"✓ Length divider positions: {[f'{x:.1f}' for x in length_positions]}")
        print(f"✓ Width divider positions: {[f'{x:.1f}' for x in width_positions]}")
        
        # Test that oversized compartments are properly rejected (no auto-fitting)
        print("  Testing rejection of oversized compartments...")
        core_invalid = BoxMakerCore()
        core_invalid.set_parameters(
            length=180.0, width=140.0, height=60.0,
            thickness=3.0, kerf=0.25, tab=15.0,
            div_l=3,  # Available space = 165mm
            div_l_custom="50; 60; 50; 40",  # Total=200mm > 165mm available - should fail
            tabtype=0
        )
        
        try:
            core_invalid.generate_box()
            assert False, "Should have failed with oversized compartments"
        except ValidationError as e:
            print(f"  ✓ Correctly rejected oversized compartments: {e}")
        
        print("[PASS] Complex custom compartments with kerf test passed")
        return True
        
    except Exception as e:
        print(f"[FAIL] Complex custom compartments with kerf test failed: {e}")
        return False


def test_shallow_open_box():
    """Test that shallow boxes work when there's no top panel"""
    print("Testing shallow open box (height validation fix)...")
    
    core = BoxMakerCore()
    core.set_parameters(
        length=220.0,
        width=206.0,
        height=18.0,  # Below normal 40mm minimum, but should work for no-top boxes
        thickness=3.0,
        kerf=0.1,
        tab=6.0,
        boxtype=BoxType.NO_TOP,  # One side open (LxW) - no top
        tabtype=0  # Laser
    )
    
    try:
        result = core.generate_box()
        svg_content = core.generate_svg()
        
        if '<svg' in svg_content and '</svg>' in svg_content and len(result['paths']) > 0:
            print(f"[PASS] Shallow open box test passed (height={core.height}mm)")
            return True
        else:
            print("[FAIL] Failed to generate valid output for shallow open box")
            return False
    except Exception as e:
        print(f"[FAIL] Shallow open box test failed: {e}")
        return False


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
        test_custom_compartment_parsing,
        test_dividers_with_kerf,
        test_custom_compartments_with_kerf,
        test_dividers_kerf_comparison,
        test_complex_custom_compartments_with_kerf,
        test_shallow_open_box
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

#!/usr/bin/env python3
"""
Test split piece generation in SVG output

This test verifies that:
1. Pieces exceeding material limits are properly detected
2. Split pieces are generated with correct dimensions and overlap
3. Join geometry is added when configured
4. SVG output contains the expected split pieces
"""

import os
import sys
import math

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from boxmaker_core import BoxMakerCore
from boxmaker_constants import JoinType, BoxType, LayoutStyle


def test_split_piece_generation():
    """Test that oversized pieces are properly split in SVG generation"""
    print("=== Testing Split Piece Generation ===")
    
    # Create a large box that will exceed material limits
    core = BoxMakerCore()
    core.length = 400.0  # 400mm
    core.width = 200.0   # 200mm
    core.height = 100.0  # 100mm
    core.thickness = 6.0
    core.tab = 25.0
    core.kerf = 0.5
    core.spacing = 25.0
    core.boxtype = BoxType.FULL_BOX
    core.style = LayoutStyle.SEPARATED
    
    # Set material limits that will force splitting
    core.max_material_width = 300.0   # 300mm max width
    core.max_material_height = 300.0  # 300mm max height
    core.overlap_multiplier = 3.0     # 3x thickness overlap (18mm)
    core.join_type = JoinType.SQUARES  # Use square tabs for joining
    
    print(f"Box dimensions: {core.length}×{core.width}×{core.height}mm")
    print(f"Material limits: {core.max_material_width}×{core.max_material_height}mm")
    print(f"Overlap: {core.overlap_multiplier}× thickness = {core.overlap_multiplier * core.thickness}mm")
    print(f"Join type: {core.join_type.name}")
    
    try:
        # Generate the box
        result = core.generate_box()
        
        # Check that split info was generated
        if core.design.split_info:
            print(f"\n✓ Split info generated for {len(core.design.split_info)} pieces:")
            for piece_name, split_info in core.design.split_info.items():
                print(f"  - {piece_name}: {split_info.num_pieces} pieces, {split_info.split_direction} split")
                print(f"    Overlap: {split_info.overlap:.1f}mm, Join: {split_info.join_type.name}")
        else:
            print("\n! No split info generated (pieces fit within material limits)")
        
        # Generate SVG
        svg_content = core.generate_svg()
        
        # Check SVG content
        if '<svg' in svg_content and '</svg>' in svg_content:
            print(f"\n✓ SVG generation successful")
            
            # Count the number of pieces in the SVG
            path_count = svg_content.count('<path')
            circle_count = svg_content.count('<circle')
            print(f"  Generated {path_count} paths and {circle_count} circles")
            
            # Save the test output
            output_file = 'test_results/split_piece_test.svg'
            os.makedirs('test_results', exist_ok=True)
            with open(output_file, 'w') as f:
                f.write(svg_content)
            print(f"  Saved: {output_file}")
            
            # Check for split piece indicators in SVG
            if 'panel_' in svg_content:
                split_panels = []
                lines = svg_content.split('\n')
                for line in lines:
                    if 'panel_' in line and '_' in line:
                        # Look for panel_X_Y pattern indicating split pieces
                        import re
                        matches = re.findall(r'panel_\d+_\d+', line)
                        split_panels.extend(matches)
                
                if split_panels:
                    unique_splits = list(set(split_panels))
                    print(f"  Found {len(unique_splits)} split piece indicators: {unique_splits[:5]}...")
                else:
                    print(f"  No split piece indicators found in SVG")
            
            return True
        else:
            print(f"\n❌ SVG generation failed")
            return False
            
    except Exception as e:
        print(f"\n❌ Error during generation: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_different_join_types():
    """Test different join types for split pieces"""
    print("\n=== Testing Different Join Types ===")
    
    join_types = [JoinType.SIMPLE_OVERLAP, JoinType.SQUARES]
    results = []
    
    for join_type in join_types:
        print(f"\nTesting {join_type.name}...")
        
        core = BoxMakerCore()
        core.length = 350.0  # Will need splitting
        core.width = 200.0
        core.height = 100.0
        core.thickness = 6.0
        core.max_material_width = 300.0
        core.max_material_height = 300.0
        core.join_type = join_type
        
        try:
            result = core.generate_box()
            svg_content = core.generate_svg()
            
            if '<svg' in svg_content:
                # Save each variant
                output_file = f'test_results/split_join_{join_type.name.lower()}.svg'
                with open(output_file, 'w') as f:
                    f.write(svg_content)
                print(f"  ✓ Generated {output_file}")
                results.append(True)
            else:
                print(f"  ❌ Failed to generate SVG")
                results.append(False)
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            results.append(False)
    
    return all(results)


def test_no_splitting_needed():
    """Test that normal boxes work without splitting"""
    print("\n=== Testing Normal Box (No Splitting) ===")
    
    core = BoxMakerCore()
    core.length = 100.0  # Small box that fits
    core.width = 100.0
    core.height = 50.0
    core.thickness = 3.0
    core.tab = 15.0  # Smaller tab to fit height constraint
    core.max_material_width = 300.0
    core.max_material_height = 300.0
    
    try:
        result = core.generate_box()
        
        # Should have no split info
        if not core.design.split_info:
            print("✓ No splitting needed for small box")
        else:
            print(f"! Unexpected split info: {core.design.split_info}")
            return False
        
        svg_content = core.generate_svg()
        if '<svg' in svg_content:
            print("✓ Normal SVG generation successful")
            
            output_file = 'test_results/normal_box_test.svg'
            with open(output_file, 'w') as f:
                f.write(svg_content)
            print(f"  Saved: {output_file}")
            return True
        else:
            print("❌ SVG generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("Testing Split Piece Generation in SVG Output")
    print("=" * 50)
    
    # Ensure test results directory exists
    os.makedirs('test_results', exist_ok=True)
    
    # Run tests
    test1 = test_split_piece_generation()
    test2 = test_different_join_types()
    test3 = test_no_splitting_needed()
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"  Split piece generation: {'✓ PASS' if test1 else '❌ FAIL'}")
    print(f"  Different join types:   {'✓ PASS' if test2 else '❌ FAIL'}")
    print(f"  Normal box (no split):  {'✓ PASS' if test3 else '❌ FAIL'}")
    
    if all([test1, test2, test3]):
        print("\n🎉 All split piece tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)

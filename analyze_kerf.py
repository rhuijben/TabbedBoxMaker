#!/usr/bin/env python3
"""
Detailed kerf compensation analysis
"""

import sys
from pathlib import Path

# Add the current directory to the path to import our modules
sys.path.insert(0, str(Path(__file__).parent))

from boxmaker_core import BoxMakerCore


def analyze_piece_dimensions():
    """Analyze the actual piece dimensions with and without kerf"""
    print("Analyzing piece dimensions with kerf compensation...")
    
    # Test dimensions
    length, width, height = 100.0, 80.0, 60.0
    thickness = 3.0
    kerf = 0.2
    
    print(f"Design: {length} x {width} x {height} (thickness: {thickness})")
    print(f"Kerf: {kerf} (half-kerf: {kerf/2})")
    
    # Generate box with kerf
    core = BoxMakerCore()
    core.set_parameters(
        length=length, width=width, height=height,
        thickness=thickness, kerf=kerf, tab=15.0, tabtype=0
    )
    
    result = core.generate_box()
    
    print(f"\nGenerated {len(result['paths'])} paths")
    
    # Analyze each path to extract piece dimensions
    for i, path in enumerate(result['paths']):
        path_data = path['data']
        print(f"\nPath {i}: {path_data[:50]}...")
        
        # Extract coordinates from path
        coords = core.extract_coords_from_path(path_data)
        if coords:
            # Find bounding box
            min_x = min(coord[0] for coord in coords)
            max_x = max(coord[0] for coord in coords)
            min_y = min(coord[1] for coord in coords)
            max_y = max(coord[1] for coord in coords)
            
            piece_width = max_x - min_x
            piece_height = max_y - min_y
            
            print(f"  Piece dimensions: {piece_width:.2f} x {piece_height:.2f}")
            
            # Check if this matches expected dimensions for different faces
            if abs(piece_width - length) < 1 and abs(piece_height - width) < 1:
                print(f"  -> Likely top/bottom face (expected: {length} x {width})")
                expected_with_kerf = f"{length + kerf} x {width + kerf}"
                print(f"  -> With full kerf should be: {expected_with_kerf}")
                print(f"  -> With half-kerf compensation should be: {length + kerf} x {width + kerf}")
            elif abs(piece_width - length) < 1 and abs(piece_height - height) < 1:
                print(f"  -> Likely front/back face (expected: {length} x {height})")
            elif abs(piece_width - width) < 1 and abs(piece_height - height) < 1:
                print(f"  -> Likely left/right face (expected: {width} x {height})")
            else:
                print(f"  -> Unknown face type")


def compare_with_without_kerf():
    """Compare actual path coordinates with and without kerf"""
    print("\n" + "="*60)
    print("Comparing paths with and without kerf...")
    
    # Test parameters
    length, width, height = 100.0, 80.0, 60.0
    thickness = 3.0
    kerf = 0.2
    
    # Generate without kerf
    core_no_kerf = BoxMakerCore()
    core_no_kerf.set_parameters(
        length=length, width=width, height=height,
        thickness=thickness, kerf=0.0, tab=15.0, tabtype=0
    )
    result_no_kerf = core_no_kerf.generate_box()
    
    # Generate with kerf
    core_with_kerf = BoxMakerCore()
    core_with_kerf.set_parameters(
        length=length, width=width, height=height,
        thickness=thickness, kerf=kerf, tab=15.0, tabtype=0
    )
    result_with_kerf = core_with_kerf.generate_box()
    
    print(f"Paths without kerf: {len(result_no_kerf['paths'])}")
    print(f"Paths with kerf: {len(result_with_kerf['paths'])}")
    
    # Compare first few paths
    for i in range(min(3, len(result_no_kerf['paths']))):
        print(f"\nPath {i} comparison:")
        
        no_kerf_data = result_no_kerf['paths'][i]['data']
        with_kerf_data = result_with_kerf['paths'][i]['data']
        
        print(f"  No kerf:   {no_kerf_data[:60]}...")
        print(f"  With kerf: {with_kerf_data[:60]}...")
        
        # Extract first coordinate to see difference
        no_kerf_coords = core_no_kerf.extract_coords_from_path(no_kerf_data)
        with_kerf_coords = core_with_kerf.extract_coords_from_path(with_kerf_data)
        
        if no_kerf_coords and with_kerf_coords:
            print(f"  First coord - No kerf: {no_kerf_coords[0]}")
            print(f"  First coord - With kerf: {with_kerf_coords[0]}")
            
            diff_x = with_kerf_coords[0][0] - no_kerf_coords[0][0]
            diff_y = with_kerf_coords[0][1] - no_kerf_coords[0][1]
            print(f"  Difference: ({diff_x:.3f}, {diff_y:.3f})")


if __name__ == "__main__":
    analyze_piece_dimensions()
    compare_with_without_kerf()

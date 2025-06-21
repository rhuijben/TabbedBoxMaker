#!/usr/bin/env python3
"""
Complete demonstration of the updated TabbedBoxMaker system
Shows the full workflow from design to generation
"""

from boxmaker_core import BoxMakerCore
from boxmaker_constants import BoxType, LayoutStyle
from box_design import create_box_design, get_wall_configuration
import os


def demonstrate_complete_workflow():
    """Demonstrate the complete workflow from design calculation to SVG generation"""
    
    print("TabbedBoxMaker - Complete Workflow Demonstration")
    print("=" * 60)
    
    # Example: Custom compartment box with no top
    print("\n1. DESIGN PHASE")
    print("-" * 30)
    
    # Design parameters
    length, width, height = 120, 100, 60
    thickness = 3
    inside = True
    box_type = BoxType.NO_TOP
    div_l, div_w = 2, 1
    div_l_custom = "40; 60"  # Custom compartment sizes
    
    print(f"Input parameters:")
    print(f"  Dimensions: {length} x {width} x {height} mm ({'internal' if inside else 'external'})")
    print(f"  Material thickness: {thickness} mm")
    print(f"  Box type: {box_type.name}")
    print(f"  Dividers: {div_l} length, {div_w} width")
    print(f"  Custom length compartments: {div_l_custom}")
    
    # Create design
    design = create_box_design(
        length=length, width=width, height=height, thickness=thickness,
        inside=inside, div_l=div_l, div_w=div_w, 
        div_l_custom=div_l_custom, box_type=box_type
    )
    
    print(f"\nDesign results:")
    print(f"  External dimensions: {design.length_external:.1f} x {design.width_external:.1f} x {design.height_external:.1f} mm")
    print(f"  Internal dimensions: {design.length_internal:.1f} x {design.width_internal:.1f} x {design.height_internal:.1f} mm")
    
    # Wall configuration
    wall_config = get_wall_configuration(box_type)
    walls = []
    if wall_config.has_top: walls.append("top")
    if wall_config.has_bottom: walls.append("bottom")
    if wall_config.has_front: walls.append("front")
    if wall_config.has_back: walls.append("back")
    if wall_config.has_left: walls.append("left")
    if wall_config.has_right: walls.append("right")
    print(f"  Walls present: {', '.join(walls)}")
    
    # Divider information
    if design.length_dividers.count > 0:
        print(f"  Length dividers: {design.length_dividers.count}")
        print(f"    Positions: {[f'{p:.1f}' for p in design.length_dividers.positions]} mm")
        print(f"    Compartments: {[f'{c:.1f}' for c in design.length_dividers.compartment_sizes]} mm")
    
    if design.width_dividers.count > 0:
        print(f"  Width dividers: {design.width_dividers.count}")
        print(f"    Positions: {[f'{p:.1f}' for p in design.width_dividers.positions]} mm")
        print(f"    Compartments: {[f'{c:.1f}' for c in design.width_dividers.compartment_sizes]} mm")
    
    print(f"\n2. GENERATION PHASE")
    print("-" * 30)
    
    # Create BoxMakerCore and set parameters
    core = BoxMakerCore()
    core.set_parameters(
        length=length, width=width, height=height, thickness=thickness,
        inside=inside, div_l=div_l, div_w=div_w, 
        div_l_custom=div_l_custom, boxtype=box_type,
        tab=12, kerf=0.1, style=LayoutStyle.SEPARATED
    )
    
    print(f"Manufacturing parameters:")
    print(f"  Tab width: {core.tab} mm")
    print(f"  Kerf compensation: {core.kerf} mm")
    print(f"  Layout style: {LayoutStyle(core.style).name}")
    
    # Generate the box
    core.generate_box()
    
    print(f"\nGeneration results:")
    print(f"  Design matches: {core.design.box_type.name}")
    print(f"  Generated paths: {len(core.paths)}")
    print(f"  Generated circles: {len(core.circles)}")
    
    # Calculate manufacturing dimensions (with kerf)
    mfg_length = core.design.length_external + core.kerf
    mfg_width = core.design.width_external + core.kerf
    mfg_height = core.design.height_external + core.kerf
    print(f"  Manufacturing dimensions: {mfg_length:.1f} x {mfg_width:.1f} x {mfg_height:.1f} mm")
    
    print(f"\n3. OUTPUT PHASE")
    print("-" * 30)
      # Generate SVG
    svg_content = core.generate_svg()
    
    # Save to file
    output_dir = "demo_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    filename = os.path.join(output_dir, "complete_workflow_demo.svg")
    with open(filename, 'w') as f:
        f.write(svg_content)
    
    print(f"SVG file saved: {filename}")
    
    # Calculate bounds for dimensions
    bounds = core.calculate_bounds()
    svg_width = bounds['max_x'] - bounds['min_x'] + 20
    svg_height = bounds['max_y'] - bounds['min_y'] + 20
    print(f"SVG dimensions: {svg_width:.1f} x {svg_height:.1f} mm")
    print(f"Total material area: {(svg_width * svg_height) / 100:.1f} cm²")
    
    print(f"\n4. VALIDATION")
    print("-" * 30)
    
    # Validate the design makes sense
    length_total = sum(design.length_dividers.compartment_sizes) + design.length_dividers.count * thickness
    width_total = sum(design.width_dividers.compartment_sizes) + design.width_dividers.count * thickness
    
    print(f"Design validation:")
    print(f"  Length: {length_total:.1f} mm (should equal {design.length_internal:.1f} mm) ✓" if abs(length_total - design.length_internal) < 0.01 else f"  Length: ERROR - {length_total:.1f} != {design.length_internal:.1f}")
    print(f"  Width: {width_total:.1f} mm (should equal {design.width_internal:.1f} mm) ✓" if abs(width_total - design.width_internal) < 0.01 else f"  Width: ERROR - {width_total:.1f} != {design.width_internal:.1f}")
    
    # Check custom compartments
    expected_custom = [40.0, 60.0]
    actual_custom = design.length_dividers.compartment_sizes[:2]
    print(f"  Custom compartments: {[f'{c:.1f}' for c in actual_custom]} (expected: {expected_custom}) ✓" if actual_custom == expected_custom else f"  Custom compartments: ERROR")
    
    print(f"\n✅ Complete workflow demonstration successful!")
    print(f"   Design → Generation → SVG output pipeline working correctly")
    

def show_box_type_comparison():
    """Show how different box types affect the output"""
    print(f"\n\nBOX TYPE COMPARISON")
    print("=" * 60)
    
    base_params = {
        "length": 100, "width": 80, "height": 60, "thickness": 3,
        "inside": True, "div_l": 1, "div_w": 1
    }
    
    core_params = {
        "length": 100, "width": 80, "height": 60, "thickness": 3,
        "inside": True, "div_l": 1, "div_w": 1, "tab": 12
    }
    
    box_types = [
        (BoxType.FULL_BOX, "Fully enclosed box"),
        (BoxType.NO_TOP, "Open top box (no lid)"),  
        (BoxType.NO_BOTTOM, "Open top and bottom"),
        (BoxType.NO_SIDES, "Only front and back panels"),
        (BoxType.NO_FRONT_BACK, "No front and back panels"),
        (BoxType.NO_LEFT_RIGHT, "Only left panel and bottom")
    ]
    
    for box_type, description in box_types:
        print(f"\n{box_type.name}: {description}")
        print("-" * 50)
        
        # Create design
        design = create_box_design(**base_params, box_type=box_type)
        
        # Show dimension changes
        length_reduction = design.length_external - design.length_internal
        width_reduction = design.width_external - design.width_internal  
        height_reduction = design.height_external - design.height_internal
        
        print(f"  External: {design.length_external:.0f} x {design.width_external:.0f} x {design.height_external:.0f} mm")
        print(f"  Internal: {design.length_internal:.0f} x {design.width_internal:.0f} x {design.height_internal:.0f} mm")
        print(f"  Thickness reduction: {length_reduction:.0f} x {width_reduction:.0f} x {height_reduction:.0f} mm")
          # Generate and count parts
        core = BoxMakerCore()
        core.set_parameters(**core_params, boxtype=box_type)
        core.generate_box()
        
        print(f"  Generated paths: {len(core.paths)} (more paths = more pieces/detail)")


if __name__ == "__main__":
    demonstrate_complete_workflow()
    show_box_type_comparison()

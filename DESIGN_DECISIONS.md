"""
DESIGN DECISIONS: Piece Splitting for Material Size Constraints
===============================================================

FUNDAMENTAL PRINCIPLES:
======================

1. GEOMETRIC INTEGRITY PRESERVATION:
   ✓ Combined split pieces must be geometrically identical to original piece
   ✓ All external cuts, tabs, slots must align perfectly when assembled
   ✓ Internal divider holes and features must maintain proper spacing
   ✓ Kerf compensation applied consistently across all split pieces

2. PIECE SIZE OPTIMIZATION:
   ✓ No split piece smaller than 25% of maximum material dimension
   ✓ Prevents unusably small pieces that are difficult to handle/cut
   ✓ May require adjusting split positions or increasing piece count
   ✓ Balances between minimizing pieces and maintaining usable sizes

3. SMART THICKNESS-BASED OVERLAP:
   ✓ Overlap automatically scales with material thickness for consistency
   ✓ Minimum overlap = 1.0x thickness (ensures adequate joining material)
   ✓ Default overlap = 3.5x thickness (balanced strength and efficiency)
   ✓ Maximum overlap = 6.0x thickness (prevents excessive material waste)
   ✓ Works proportionally across all material types and thicknesses

4. INTELLIGENT OVERLAP PLACEMENT:
   ⚠ Overlap regions positioned to avoid critical tab/slot areas (PLANNED)
   ⚠ External geometry preserved (tabs that connect to other pieces) (PLANNED)
   ⚠ Split boundaries adjusted to maintain joint integrity (PLANNED)
   ⚠ Different strategies needed for different join types (PLANNED)

5. SVG LAYOUT INTEGRATION:
   ⚠ Split pieces placed adjacent to each other in SVG output (PLANNED)
   ⚠ Other box pieces shifted right to accommodate split piece groups (PLANNED)
   ⚠ Clear labeling for assembly identification (PLANNED)
   ⚠ Maintains existing layout algorithms where possible (PLANNED)

DETAILED IMPLEMENTATION STRATEGY:
=================================

SMART THICKNESS-BASED OVERLAP (Priority 1):
-------------------------------------------

CURRENT STATUS: ✓ FULLY IMPLEMENTED
- Overlap calculation automatically scales with material thickness
- Smart clamping prevents inadequate or excessive overlap amounts
- Consistent behavior across all material types and thicknesses

THICKNESS-BASED IMPLEMENTATION:
```
def calculate_overlap(material_thickness, join_type):
    """Calculate overlap size based on material thickness and joint type"""
    if join_type == "simple":
        return material_thickness * 3.5
    elif join_type == "dovetail":
        return material_thickness * 6.0
    elif join_type == "finger_joint":
        return material_thickness * 4.0THICKNESS-BASED IMPLEMENTATION:
- Base overlap = material_thickness × overlap_multiplier (user-configurable)
- Minimum overlap = material_thickness × 1.0 (adequate for any joining method)
- Maximum overlap = material_thickness × 6.0 (prevents excessive waste)
- Clamping formula: overlap = max(min_overlap, min(base_overlap, max_overlap))

MATERIAL-SPECIFIC BENEFITS:
- Thin materials (0.5-2mm): Automatically get adequate overlap despite small thickness
- Standard materials (3-12mm): Proportional overlap provides optimal strength/efficiency
- Thick materials (15-25mm): Limited maximum prevents excessive waste
- All materials: Consistent proportional behavior regardless of thickness

EXAMPLE CALCULATIONS:
```
3mm plywood:
  User multiplier: 3.5x
  Base overlap: 3.0 × 3.5 = 10.5mm
  Min allowed: 3.0 × 1.0 = 3.0mm  
  Max allowed: 3.0 × 6.0 = 18.0mm
  Final overlap: 10.5mm (within range)

25mm lumber:
  User multiplier: 3.5x
  Base overlap: 25.0 × 3.5 = 87.5mm
  Min allowed: 25.0 × 1.0 = 25.0mm
  Max allowed: 25.0 × 6.0 = 150.0mm
  Final overlap: 87.5mm (within range)

Extreme case - 0.1x multiplier on 3mm:
  Base overlap: 3.0 × 0.1 = 0.3mm
  Clamped to minimum: 3.0mm (adequate for joining)
```

REQUIRED ENHANCEMENTS:
- Smart split line positioning to avoid critical geometry
- Tab preservation analysis (ensure tabs don't fall on split lines)  
- Slot alignment verification across piece boundaries
- Kerf compensation consistency checking

GEOMETRIC INTEGRITY (Priority 2):
---------------------------------

CURRENT STATUS: ✓ FOUNDATION IMPLEMENTED
- Split pieces maintain exact external geometry
- Overlap regions extend inward from split lines
- Tab and slot positions preserved across splits

IMPLEMENTATION APPROACH:
```python
def validate_split_geometry(original_piece, split_pieces):
    """Ensure split pieces maintain geometric integrity"""
    # 1. Verify total dimensions match original
    # 2. Check tab positions don't fall on split lines
    # 3. Validate slot alignment across boundaries
    # 4. Confirm kerf compensation consistency
```

PIECE SIZE CONSTRAINTS (Priority 1):
------------------------------------

CURRENT STATUS: ✓ FULLY IMPLEMENTED
- 25% minimum piece size rule actively enforced
- Size constraint checking integrated with split calculation
- Prevents unusably small pieces across all scenarios

DESIGN RULE: min_piece_size = max_material_dimension * 0.25

IMPLEMENTATION STRATEGY:
```python
def calculate_optimal_splits(piece_dimension, max_material_size, overlap):
    """Calculate split positions ensuring minimum piece sizes"""
    min_piece_size = max_material_size * 0.25
    
    # Calculate initial even distribution
    available_per_piece = max_material_size - overlap
    initial_pieces = ceil(piece_dimension / available_per_piece)
    
    # Check if any piece would be too small
    actual_piece_size = piece_dimension / initial_pieces
    if actual_piece_size < min_piece_size:
        # Reduce piece count to ensure minimum size
        max_allowed_pieces = floor(piece_dimension / min_piece_size)
        num_pieces = max(2, max_allowed_pieces)  # At least 2 for splitting
        return distribute_pieces_evenly(piece_dimension, num_pieces)
    
    return initial_pieces
    
    return generate_split_positions(piece_dimension, base_pieces, overlap)
```

REQUIRED VALIDATIONS:
- Pre-split size checking to prevent tiny pieces
- Post-split validation of all piece dimensions
- Fallback strategies for extreme size mismatches
- Warning generation when constraints cannot be met

INTELLIGENT OVERLAP PLACEMENT (Priority 2):
-------------------------------------------

CURRENT STATUS: ❌ NOT IMPLEMENTED
- Current implementation uses simple edge-based overlap
- No consideration of tab/slot positions
- No boundary adjustment for joint preservation

DESIGN PRINCIPLES:
1. Never split through tabs that connect to other pieces
2. Avoid splitting through slots that receive tabs from other pieces
3. Position overlaps in "safe zones" without critical geometry
4. Adjust split boundaries rather than lose critical features

IMPLEMENTATION STRATEGY:
```python
def find_safe_split_zones(piece_geometry, split_direction):
    """Identify areas safe for splitting without losing critical geometry"""
    safe_zones = []
    
    # Analyze tab positions along split direction
    tabs = extract_tabs_along_axis(piece_geometry, split_direction)
    slots = extract_slots_along_axis(piece_geometry, split_direction)
    
    # Find gaps between critical features
    for position in range(piece_length):
        if not overlaps_critical_geometry(position, tabs, slots):
            safe_zones.append(position)
    
    return safe_zones

def adjust_split_boundaries(split_positions, safe_zones, overlap_size):
    """Move split lines to safe zones while maintaining overlap requirements"""
    adjusted_positions = []
    
    for split_pos in split_positions:
        # Find nearest safe zone
        nearest_safe = find_nearest_safe_zone(split_pos, safe_zones)
        
        # Verify overlap requirements still met
        if validate_overlap_constraints(nearest_safe, overlap_size):
            adjusted_positions.append(nearest_safe)
        else:
            # Find alternative or flag as problematic
            alternative = find_alternative_split(split_pos, safe_zones, overlap_size)
            adjusted_positions.append(alternative)
    
    return adjusted_positions
```

JOINT TYPE CONSIDERATIONS:
- SIMPLE_OVERLAP: Can adjust boundaries freely within overlap tolerance
- SQUARES: Must align tab centers, may need custom overlap positioning  
- DOVETAIL: Requires precise angle alignment, limited boundary flexibility
- FINGER_JOINT: Must maintain finger spacing, complex boundary constraints

SVG LAYOUT INTEGRATION (Priority 3):
------------------------------------

CURRENT STATUS: ⚠ PARTIAL IMPLEMENTATION
- Basic framework exists for split piece generation
- No layout positioning implemented yet

DESIGN APPROACH:
```
Original Layout:        Split Piece Layout:
[Front][Back]          [Front_1][Front_2][Back_1][Back_2]
[Left][Right]    =>    [Left_1][Left_2][Right_1][Right_2]
[Top][Bottom]          [Top][Bottom]
```

IMPLEMENTATION STRATEGY:
```python
def layout_split_pieces(pieces, layout_style):
    """Arrange split pieces in SVG while maintaining readability"""
    
    # Group split pieces together
    piece_groups = group_by_original_piece(pieces)
    
    # Calculate spacing requirements
    total_width = calculate_total_width_needed(piece_groups)
    
    # Position pieces with appropriate spacing
    positions = []
    x_offset = 0
    
    for group_name, split_pieces in piece_groups.items():
        # Place split pieces adjacent to each other
        group_positions = position_split_group(split_pieces, x_offset)
        positions.extend(group_positions)
        
        # Update offset for next group
        x_offset += calculate_group_width(split_pieces) + INTER_GROUP_SPACING
    
    return positions
```

LABELING STRATEGY:
- Original piece names: "front", "back", "left", "right", "top", "bottom"
- Split piece names: "front_1", "front_2", "back_1", "back_2", etc.
- Assembly order indicated by numeric suffix
- SVG groups for easy selection and manipulation

IMPLEMENTATION ROADMAP:
======================

PHASE 1 (IMMEDIATE - THIS ITERATION):
- ✓ Document design decisions (this file)
- ✓ Update SplitInfo dataclass with size constraint fields
- ✓ Implement minimum piece size validation
- ✓ Add boundary adjustment framework

PHASE 2 (NEXT ITERATION):
- Implement safe zone detection for tab/slot positions
- Add split boundary adjustment algorithms
- Create SVG layout positioning for split pieces
- Add comprehensive testing for edge cases

PHASE 3 (FUTURE ITERATIONS):
- Advanced joint type support with specific overlap strategies
- Split optimization algorithms for minimal waste
- Assembly instruction generation
- Material grain direction consideration

TESTING REQUIREMENTS:
=====================

CRITICAL TEST CASES:
1. Pieces exactly at size limits (no splitting needed)
2. Pieces slightly over size limits (2-piece splits)
3. Very large pieces requiring multiple splits in one direction
4. Pieces requiring splits in both directions (future)
5. Pieces with many tabs that constrain split positions
6. Edge cases where 25% rule conflicts with other constraints

VALIDATION SCENARIOS:
- Split pieces maintain identical total geometry
- All piece sizes ≥ 25% of maximum material dimension  
- No tabs or slots cut by split lines
- Proper overlap positioning for each join type
- SVG layout maintains readability and organization

This design document ensures the splitting implementation will be robust,
maintainable, and will produce high-quality results suitable for actual
manufacturing while preserving the precision and reliability users expect
from BoxMaker.
"""

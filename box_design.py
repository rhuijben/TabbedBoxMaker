#!/usr/bin/env python3
"""
BoxMaker Design System

This module implements the core design logic for the TabbedBoxMaker Inkscape extension.
It separates design concerns (geometry, compartments) from manufacturing concerns (kerf, tabs).

DESIGN DECISIONS:
================

1. SEPARATION OF CONCERNS:
   - Design system handles pure geometry and compartment layout
   - Generation system handles manufacturing details (kerf compensation, tab placement)
   - This separation enables testing, validation, and future enhancements

2. CUSTOM COMPARTMENT VALIDATION:
   - When ALL compartment sizes are provided: strict validation, no auto-fitting
   - When PARTIAL sizes provided: auto-fit remaining compartments
   - When NO sizes provided: divide space evenly
   - This prevents user errors and ensures predictable behavior

3. ENUM-BASED CONSTANTS:
   - Replaced magic integers with BoxType and LayoutStyle enums
   - Improves code readability and prevents invalid values

4. WALL CONFIGURATION:
   - Each box type has explicit wall configuration
   - Enables correct dimension calculations for partial boxes
   - Supports future box type extensions

5. KERF HANDLING:
   - Design dimensions are kerf-free (pure geometry)
   - Kerf compensation applied during generation
   - Half-kerf expansion on all external piece edges
   - Maintains design intent while ensuring proper fit

Classes:
  DividerInfo: Information about dividers in one direction
  WallConfiguration: Which walls exist for a box type  
  BoxDesign: Complete box design with all geometric information

Functions:
  create_box_design: Main factory function for creating box designs
  calculate_divider_info: Calculate divider positions and compartment sizes
  get_wall_configuration: Get wall configuration for box type
  parse_compartment_sizes: Parse custom compartment size strings
"""

from typing import List, Optional, Tuple, Dict
from dataclasses import dataclass
import math
from boxmaker_exceptions import DimensionError, ValidationError
from boxmaker_constants import (
    BoxType, LayoutStyle, JoinType, MIN_SPLIT_PIECE_RATIO,
    DEFAULT_OVERLAP_MULTIPLIER, MIN_OVERLAP_MULTIPLIER, MAX_OVERLAP_MULTIPLIER
)


@dataclass
class DividerInfo:
    """Information about dividers in one direction"""
    count: int                    # Number of dividers
    positions: List[float]        # Positions of dividers from start
    compartment_sizes: List[float] # Sizes of compartments
    spacing: List[float]          # Spacing between elements (compartments + dividers)
    custom_sizes: List[float]     # Original custom compartment sizes provided


@dataclass 
class BoxDesign:
    """Complete box design with all calculated dimensions and divider info"""
    
    # Input parameters
    length: float
    width: float
    height: float
    thickness: float
    inside: bool
    
    # Calculated dimensions (design phase - no kerf)
    length_external: float
    width_external: float
    height_external: float
    length_internal: float
    width_internal: float
    height_internal: float
    
    # Divider information
    length_dividers: DividerInfo  # Dividers running parallel to width (in length direction)
    width_dividers: DividerInfo   # Dividers running parallel to length (in width direction)    # Box configuration
    box_type: BoxType
    style: LayoutStyle
    
    # Material size limits and piece splitting (TODO: implement full splitting logic)
    max_material_width: float = 0.0   # 0 = unlimited
    max_material_height: float = 0.0  # 0 = unlimited
    overlap_multiplier: float = 3.0   # Overlap = thickness * multiplier  
    join_type: JoinType = JoinType.SIMPLE_OVERLAP
      # Split information (calculated during design)
    split_info: Optional[Dict[str, 'SplitInfo']] = None  # piece_name -> SplitInfo
    split_pieces: Optional[List['SplitPiece']] = None    # All split pieces
    
    def __post_init__(self):
        """Validate the design after creation"""
        self._validate_design()

    def _validate_design(self):
        """Validate that the design is feasible"""
        # Check that internal dimensions are positive
        if self.length_internal <= 0:
            raise DimensionError("length_internal", self.length_internal, min_val=0.1)
        if self.width_internal <= 0:
            raise DimensionError("width_internal", self.width_internal, min_val=0.1)
        if self.height_internal <= 0:
            raise DimensionError("height_internal", self.height_internal, min_val=0.1)
            
        # Check that dividers fit
        self._validate_dividers(self.length_dividers, self.length_internal, "length")
        self._validate_dividers(self.width_dividers, self.width_internal, "width")
    
    def _validate_dividers(self, dividers: DividerInfo, internal_dim: float, direction: str):
        """Validate divider configuration for one direction"""
        if dividers.count == 0:
            return
            
        # Check that all compartments are positive
        for i, size in enumerate(dividers.compartment_sizes):
            if size <= 0:
                raise ValidationError(f"Compartment {i+1} in {direction} direction has invalid size {size}mm")
        
        # Check that total spacing equals internal dimension
        total_spacing = sum(dividers.spacing)
        if abs(total_spacing - internal_dim) > 0.001:
            raise ValidationError(f"Total spacing ({total_spacing}mm) does not match internal {direction} ({internal_dim}mm)")


@dataclass
class WallConfiguration:
    """Configuration of which walls exist for a box type"""
    has_top: bool
    has_bottom: bool
    has_front: bool
    has_back: bool
    has_left: bool
    has_right: bool
    
    @property
    def has_length_walls(self) -> bool:
        """Whether the box has walls in the length direction (front/back)"""
        return self.has_front and self.has_back
    
    @property
    def has_width_walls(self) -> bool:
        """Whether the box has walls in the width direction (left/right)"""
        return self.has_left and self.has_right
    
    @property
    def has_height_walls(self) -> bool:
        """Whether the box has walls in the height direction (top/bottom)"""
        return self.has_top and self.has_bottom


def parse_compartment_sizes(sizes_string: str) -> List[float]:
    """Parse compartment sizes string with support for both '.' and ',' decimal separators
    
    Args:
        sizes_string: String like "40; 60,5; 50" or "40.0;60.5;50.0"
        
    Returns:
        List of parsed sizes
        
    Raises:
        ValueError: If parsing fails
    """
    if not sizes_string or not sizes_string.strip():
        return []
        
    sizes = []
    parts = sizes_string.split(';')
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
            
        try:
            # Replace comma with dot for consistent decimal parsing
            normalized = part.replace(',', '.')
            size = float(normalized)
            if size <= 0:
                raise ValueError(f"Size must be positive, got {size}")
            sizes.append(size)
        except ValueError as e:
            raise ValueError(f"Invalid compartment size '{part}': {e}")
            
    return sizes


def calculate_divider_configuration(internal_dimension: float, 
                                  custom_sizes: List[float],
                                  num_dividers: int,
                                  thickness: float) -> DividerInfo:
    """Calculate divider positions and compartment sizes for one direction
    
    Args:
        internal_dimension: Internal space available (design dimension, no kerf)
        custom_sizes: List of custom compartment sizes (if any)
        num_dividers: Number of dividers requested
        thickness: Material thickness
        
    Returns:
        DividerInfo with all calculated values
        
    Raises:
        ValidationError: If configuration is invalid
    """
    if num_dividers < 0:
        raise ValidationError(f"Number of dividers cannot be negative: {num_dividers}")
    
    if num_dividers == 0:
        # No dividers - single compartment
        return DividerInfo(
            count=0,
            positions=[],
            compartment_sizes=[internal_dimension],
            spacing=[internal_dimension],
            custom_sizes=custom_sizes
        )
    
    num_compartments = num_dividers + 1
    available_for_compartments = internal_dimension - (num_dividers * thickness)
    
    if available_for_compartments <= 0:
        raise ValidationError(f"No space available for compartments. {num_dividers} dividers of {thickness}mm "
                            f"thickness require {num_dividers * thickness}mm, but only {internal_dimension}mm available.")
      # Determine compartment sizes
    if not custom_sizes:
        # No custom sizes - divide evenly
        compartment_size = available_for_compartments / num_compartments
        compartment_sizes = [compartment_size] * num_compartments
    elif len(custom_sizes) >= num_compartments:
        # DESIGN DECISION: All compartment sizes provided - must match exactly
        # NO AUTO-FITTING: Better to inform user of incorrect sizes than create wrong box
        compartment_sizes = custom_sizes[:num_compartments]
        total_custom = sum(compartment_sizes)
        if abs(total_custom - available_for_compartments) > 0.001:
            raise ValidationError(f"Custom compartment sizes total {total_custom:.1f}mm but available space is "
                                f"{available_for_compartments:.1f}mm. Adjust sizes to match exactly.")
    else:
        # Partial custom sizes - auto-fit remaining compartments
        # DESIGN DECISION: Only auto-fit when user hasn't specified all sizes
        compartment_sizes = custom_sizes[:]
        used_space = sum(custom_sizes)
        remaining_compartments = num_compartments - len(custom_sizes)
        remaining_space = available_for_compartments - used_space
        
        if remaining_space < 0:
            raise ValidationError(f"Custom compartment sizes ({used_space:.1f}mm) exceed available compartment space "
                                f"({available_for_compartments:.1f}mm). Reduce sizes by {-remaining_space:.1f}mm.")
        
        if remaining_compartments > 0:
            remaining_size = remaining_space / remaining_compartments
            compartment_sizes.extend([remaining_size] * remaining_compartments)
    
    # Calculate divider positions
    positions = []
    current_pos = 0
    
    for i in range(num_dividers):
        current_pos += compartment_sizes[i]  # Move past compartment
        positions.append(current_pos)       # Position divider at end of compartment
        current_pos += thickness            # Move past divider thickness
    
    # Calculate spacing (alternating compartments and dividers)
    spacing = []
    for i in range(num_dividers):
        spacing.append(compartment_sizes[i])  # Compartment
        spacing.append(thickness)             # Divider
    spacing.append(compartment_sizes[-1])     # Final compartment
    
    return DividerInfo(
        count=num_dividers,
        positions=positions,
        compartment_sizes=compartment_sizes,
        spacing=spacing,
        custom_sizes=custom_sizes
    )


def get_wall_configuration(box_type: BoxType) -> WallConfiguration:
    """Get the wall configuration for a given box type
    
    Args:
        box_type: Type of box (from INX definitions)
            1: Fully enclosed
            2: One side open (LxW) - no top
            3: Two sides open (LxW and LxH) - no top, no bottom  
            4: Three sides open (LxW, LxH, HxW) - no top, no bottom, no sides
            5: Opposite ends open (LxW) - no front, no back
            6: Two panels only (LxW and LxH) - only left and bottom panels
        
    Returns:
        WallConfiguration indicating which walls exist
    """
    # Start with all walls present
    has_top = has_bottom = has_front = has_back = has_left = has_right = True
    
    if box_type == BoxType.FULL_BOX:  # 1: Fully enclosed
        # All walls present (default)
        pass
    elif box_type == BoxType.NO_TOP:  # 2: One side open (LxW) - no top
        has_top = False
    elif box_type == BoxType.NO_BOTTOM:  # 3: Two sides open (LxW and LxH) - no top, no bottom
        has_top = has_bottom = False
    elif box_type == BoxType.NO_SIDES:  # 4: Three sides open (LxW, LxH, HxW) - no top, no bottom, no sides
        has_top = has_bottom = has_left = has_right = False
    elif box_type == BoxType.NO_FRONT_BACK:  # 5: Opposite ends open (LxW) - no front, no back
        has_front = has_back = False
    elif box_type == BoxType.NO_LEFT_RIGHT:  # 6: Two panels only (LxW and LxH) - only left and bottom
        has_top = has_front = has_back = has_right = False
    
    return WallConfiguration(
        has_top=has_top,
        has_bottom=has_bottom,
        has_front=has_front,
        has_back=has_back,
        has_left=has_left,
        has_right=has_right
    )


def create_box_design(length: float, width: float, height: float, thickness: float,
                     inside: bool = False,
                     div_l: int = 0, div_w: int = 0,
                     div_l_custom: str = "", div_w_custom: str = "",
                     box_type: BoxType = BoxType.FULL_BOX, 
                     style: LayoutStyle = LayoutStyle.SEPARATED,
                     max_material_width: float = 0.0,
                     max_material_height: float = 0.0,
                     overlap_multiplier: float = 3.0,
                     join_type: JoinType = JoinType.SIMPLE_OVERLAP) -> BoxDesign:
    """Create a complete box design from input parameters
    
    Args:
        length, width, height: Box dimensions
        thickness: Material thickness
        inside: Whether dimensions are internal (True) or external (False)
        div_l: Number of dividers in length direction
        div_w: Number of dividers in width direction
        div_l_custom: Custom compartment sizes for length direction        div_w_custom: Custom compartment sizes for width direction
        box_type: Type of box (BoxType enum: FULL_BOX, NO_TOP, etc.)
        style: Layout style (LayoutStyle enum: SEPARATED, NESTED, COMPACT)
        max_material_width: Maximum material width (0 = unlimited)
        max_material_height: Maximum material height (0 = unlimited)
        overlap_multiplier: Overlap = thickness * multiplier for split pieces
        join_type: Type of joint for connecting split pieces
        
    Returns:
        BoxDesign object with all calculated dimensions and divider info
    """
    # Validate input parameters
    if length <= 0:
        raise DimensionError("length", length, min_val=0.1)
    if width <= 0:
        raise DimensionError("width", width, min_val=0.1)
    if height <= 0:
        raise DimensionError("height", height, min_val=0.1)
    if thickness <= 0:
        raise DimensionError("thickness", thickness, min_val=0.1)
    if thickness >= min(length, width, height) / 2:
        raise DimensionError("thickness", thickness, max_val=min(length, width, height) / 2)
      # Get wall configuration for this box type
    wall_config = get_wall_configuration(box_type)
    
    # Calculate external and internal dimensions based on which walls are present
    if inside:
        # Input dimensions are internal
        length_internal = length
        width_internal = width
        height_internal = height
        
        # External = internal + thickness for each wall that exists
        length_external = length_internal + thickness * (
            (1 if wall_config.has_left else 0) + (1 if wall_config.has_right else 0)
        )
        width_external = width_internal + thickness * (
            (1 if wall_config.has_front else 0) + (1 if wall_config.has_back else 0)
        )
        height_external = height_internal + thickness * (
            (1 if wall_config.has_bottom else 0) + (1 if wall_config.has_top else 0)
        )
    else:
        # Input dimensions are external
        length_external = length
        width_external = width
        height_external = height
        
        # Internal = external - thickness for each wall that exists
        length_internal = length_external - thickness * (
            (1 if wall_config.has_left else 0) + (1 if wall_config.has_right else 0)
        )
        width_internal = width_external - thickness * (
            (1 if wall_config.has_front else 0) + (1 if wall_config.has_back else 0) 
        )
        height_internal = height_external - thickness * (
            (1 if wall_config.has_bottom else 0) + (1 if wall_config.has_top else 0)
        )
    
    # Validate that internal dimensions are positive (only matters if walls exist)
    # For missing walls, internal dimension equals external dimension
    if length_internal <= 0 and (wall_config.has_left or wall_config.has_right):
        raise DimensionError("length_internal", length_internal, min_val=0.1,
                           message=f"Internal length too small after accounting for wall thickness. "
                                 f"Need at least {thickness * 2 + 0.1}mm external length.")
    if width_internal <= 0 and (wall_config.has_front or wall_config.has_back):
        raise DimensionError("width_internal", width_internal, min_val=0.1,
                           message=f"Internal width too small after accounting for wall thickness. "
                                 f"Need at least {thickness * 2 + 0.1}mm external width.")
    if height_internal <= 0 and (wall_config.has_bottom or wall_config.has_top):
        raise DimensionError("height_internal", height_internal, min_val=0.1,
                           message=f"Internal height too small after accounting for wall thickness. "
                                 f"Need at least {thickness * 2 + 0.1}mm external height.")
    
    # Parse custom compartment sizes
    custom_l_sizes = parse_compartment_sizes(div_l_custom)
    custom_w_sizes = parse_compartment_sizes(div_w_custom)
      # Calculate divider configurations
    length_dividers = calculate_divider_configuration(
        length_internal, custom_l_sizes, div_l, thickness)
    width_dividers = calculate_divider_configuration(
        width_internal, custom_w_sizes, div_w, thickness)
    
    # Create initial design
    design = BoxDesign(
        length=length,
        width=width,
        height=height,
        thickness=thickness,
        inside=inside,
        length_external=length_external,
        width_external=width_external,
        height_external=height_external,
        length_internal=length_internal,
        width_internal=width_internal,
        height_internal=height_internal,
        length_dividers=length_dividers,
        width_dividers=width_dividers,
        box_type=box_type,
        style=style,
        max_material_width=max_material_width,
        max_material_height=max_material_height,
        overlap_multiplier=overlap_multiplier,
        join_type=join_type
    )
    
    # Check for material limits and calculate split information
    if max_material_width > 0 or max_material_height > 0:
        split_info = check_material_limits(design)
        design.split_info = split_info if split_info else None
        
        # TODO: Calculate actual split pieces
        # design.split_pieces = calculate_split_pieces(design, split_info)
    
    return design


@dataclass
class SplitInfo:
    """
    Information about how a piece needs to be split to fit material size constraints.
    
    DESIGN PURPOSE:
    ===============
    This dataclass encapsulates all the information needed to split a box piece
    that exceeds the maximum material dimensions. It serves as the planning
    stage output that feeds into the actual piece generation process.
    
    FIELD DESCRIPTIONS:
    ===================
    needs_splitting: bool
        - True if piece exceeds material limits and requires splitting
        - False for pieces that fit within material constraints
        - Used as a quick check before processing split logic
    
    split_direction: str  
        - 'horizontal': Split with horizontal cuts (pieces stacked vertically)
        - 'vertical': Split with vertical cuts (pieces arranged horizontally)
        - Direction chosen based on which dimension exceeds limits
        - Affects overlap placement and join geometry
    
    num_pieces: int
        - Total number of pieces after splitting
        - Calculated as ceil(dimension / available_per_piece)
        - Minimum value is 2 (original piece requires at least one split)
        - Higher values for severely oversized pieces
    
    overlap: float
        - Amount of material overlap between adjacent pieces (in mm)
        - Provides joining surface for assembly
        - Calculated as thickness × overlap_multiplier with minimum 5mm
        - Must be subtracted from available material area per piece
    
    split_positions: List[float]
        - Positions where cuts are made in the original piece
        - Values are distances from origin (top-left corner)
        - Used to determine piece boundaries and overlap regions
        - Length = num_pieces - 1 (one less cut than pieces)
    
    join_type: JoinType
        - Type of mechanical joint to create in overlap regions
        - SIMPLE_OVERLAP: Just overlapping material (current implementation)
        - Future: DOVETAIL, FINGER_JOINT, SQUARES for stronger connections
        - Affects the complexity of generated geometry
    
    USAGE FLOW:
    ===========
    1. check_material_limits() creates SplitInfo for oversized pieces
    2. _generate_split_pieces() uses SplitInfo to create individual SplitPiece objects
    3. SVG generation processes each SplitPiece separately
    4. Join geometry is added based on join_type specification    """
    needs_splitting: bool         # Whether the piece exceeds material limits
    split_direction: str          # 'horizontal' or 'vertical' 
    num_pieces: int              # Number of pieces after splitting
    overlap: float               # Overlap distance between pieces
    split_positions: List[float] # Positions where splits occur
    join_type: JoinType          # Type of joint to use
    
    # NEW FIELDS FOR ENHANCED DESIGN REQUIREMENTS:
    min_piece_size: float        # Minimum allowed piece size (25% of max material dim)
    adjusted_positions: List[float] # Split positions adjusted to avoid tabs/slots
    safe_zones: List[Tuple[float, float]] # Areas safe for splitting (no critical geometry)
    has_boundary_adjustments: bool # True if split lines were moved from optimal positions
    geometry_conflicts: List[str]  # List of any unresolvable conflicts with tabs/slots
    

@dataclass
class SplitPiece:
    """
    A single piece resulting from splitting an oversized box component.
    
    DESIGN PURPOSE:
    ===============
    Represents one individual piece after an oversized box component has been
    split to fit within material size constraints. Contains all the information
    needed to generate the SVG geometry for this specific piece.
    
    COORDINATE SYSTEM:
    ==================
    All measurements are in mm, relative to the original piece's coordinate system.
    - offset_x, offset_y: Position of this piece within the original piece boundaries
    - width, height: Final dimensions of this piece including any overlap regions
    - Overlap flags indicate which edges extend beyond the original piece boundaries
    
    FIELD DESCRIPTIONS:
    ===================
    width, height: float
        - Final dimensions of this piece in mm
        - Includes overlap regions where applicable
        - Used directly for SVG path generation
        - May differ from calculated dimensions due to remainder handling
    
    x_offset, y_offset: float  
        - Position of this piece's origin within the original piece
        - Used to calculate which portion of the original geometry to include
        - Critical for maintaining proper tab/slot alignment across pieces
        - Zero for first piece in each direction
    
    piece_index: int
        - Index of this piece within the split sequence (0-based)
        - Used for identification and assembly instruction generation
        - Affects overlap placement (first/middle/last pieces differ)
        - Important for maintaining proper piece ordering
    
    total_pieces: int
        - Total number of pieces in this split sequence
        - Used to determine if this is first, middle, or last piece
        - Affects overlap geometry and join requirements
        - Constant across all pieces from same original component
    
    is_first, is_last: bool
        - Convenience flags for overlap and join geometry decisions
        - First piece: no overlap at leading edge, overlap at trailing edge
        - Last piece: overlap at leading edge, no overlap at trailing edge
        - Middle pieces: overlap on both edges for double connections
    
    USAGE IN GENERATION:
    ====================
    1. Each SplitPiece is processed as an independent box component
    2. Original box geometry is clipped to piece boundaries using offsets
    3. Overlap regions receive special join geometry based on join_type
    4. Tab/slot positions are adjusted to maintain alignment across splits
    5. Each piece gets unique identification for assembly purposes
    
    ASSEMBLY CONSIDERATIONS:
    ========================
    - Pieces must be assembled in sequence (piece_index order)
    - Overlap regions require mechanical fasteners or adhesive
    - Join geometry must align precisely between adjacent pieces
    - Assembly instructions should reference piece_index for clarity
    """
    width: float                 # Final width of this piece
    height: float                # Final height of this piece
    x_offset: float              # X offset from original piece origin
    y_offset: float              # Y offset from original piece origin
    piece_index: int             # Index within the split pieces (0, 1, 2...)
    total_pieces: int            # Total number of pieces in split
    is_first: bool               # True for first piece in sequence
    is_last: bool                # True for last piece in sequence


def get_piece_dimensions(design: BoxDesign) -> Dict[str, Tuple[float, float]]:
    """Get the dimensions (width, height) of each box piece
    
    Returns:
        Dictionary mapping piece names to (width, height) tuples
        
    TODO: Add support for different box types beyond full box
    TODO: Consider divider dimensions for boxes with dividers
    """
    wall_config = get_wall_configuration(design.box_type)
    pieces = {}
    
    # Main panels (assuming full box for now)
    if wall_config.has_front:
        pieces['front'] = (design.length_external, design.height_external)
    if wall_config.has_back:
        pieces['back'] = (design.length_external, design.height_external)
    if wall_config.has_left:
        pieces['left'] = (design.width_external, design.height_external)
    if wall_config.has_right:
        pieces['right'] = (design.width_external, design.height_external)
    if wall_config.has_top:
        pieces['top'] = (design.length_external, design.width_external)
    if wall_config.has_bottom:
        pieces['bottom'] = (design.length_external, design.width_external)
    
    # TODO: Add divider pieces
    # if design.length_dividers.count > 0:
    #     for i in range(design.length_dividers.count):
    #         pieces[f'divider_l_{i}'] = (design.width_internal, design.height_internal)
    # if design.width_dividers.count > 0:
    #     for i in range(design.width_dividers.count):
    #         pieces[f'divider_w_{i}'] = (design.length_internal, design.height_internal)
    
    return pieces


def check_material_limits(design: BoxDesign) -> Dict[str, SplitInfo]:
    """
    Check which pieces exceed material size limits and calculate split requirements.
    
    DETECTION STRATEGY:
    ===================
    This function implements the first phase of piece splitting: detection and planning.
    It analyzes each box piece against the configured material size limits and determines
    if splitting is required and how it should be performed.
    
    MATERIAL LIMIT HANDLING:
    - Width limit: Maximum width of material sheet (e.g., 300mm for small laser cutters)
    - Height limit: Maximum height of material sheet (e.g., 300mm for small laser cutters)
    - Setting limits to 0 disables size checking (unlimited material)
    - Both limits can be active simultaneously for square material constraints
    
    SPLIT DIRECTION LOGIC:
    - Height exceeds limit → Horizontal split (multiple pieces stacked vertically)
    - Width exceeds limit → Vertical split (multiple pieces arranged horizontally)
    - Both exceed → Height takes priority (horizontal split chosen)
    - This prioritization minimizes the number of splits needed
    
    OVERLAP CALCULATION:
    - Base overlap = material thickness × overlap_multiplier (default 3x)
    - Minimum overlap = 5mm (ensures sufficient material for joining)
    - Overlap provides material for mechanical fasteners or adhesive bonding
    - Must be subtracted from available cutting area per piece
      PIECE COUNT CALCULATION WITH SIZE CONSTRAINTS:
    - Available area per piece = material_limit - overlap_amount  
    - Initial pieces = ceil(piece_dimension / available_per_piece)
    - Minimum piece size = material_limit × MIN_SPLIT_PIECE_RATIO (25%)
    - If any piece would be < minimum, reduce piece count and recalculate
    - Split positions calculated to distribute pieces optimally
    - Each split position represents where the original piece will be cut
    
    SIZE CONSTRAINT ENFORCEMENT:
    - No piece smaller than 25% of maximum material dimension
    - Prevents unusably small pieces difficult to handle/cut
    - May result in fewer, larger pieces instead of many small ones
    - Ensures practical manufacturability across all piece sizes
    
    CURRENT LIMITATIONS:
    ====================
    - Only implements simple even splitting (future: optimize for minimal waste)
    - No consideration of grain direction (future: respect wood grain orientation)
    - Fixed overlap amount (future: variable overlap based on join type)
    - No joint complexity consideration (future: account for tab/slot requirements)
    
    FUTURE ENHANCEMENTS:
    ====================
    - Split optimization algorithms (minimize waste, balance piece sizes)
    - Material grain direction awareness for wood/plywood
    - Variable overlap based on join type and stress analysis
    - Integration with tab/slot positioning to avoid splits through joints
    - User-selectable split strategies (even, optimized, custom)
    - Assembly instruction generation for split pieces
    
    Args:
        design: BoxDesign with material limits and overlap configuration
        
    Returns:
        Dictionary mapping piece names to SplitInfo objects for pieces requiring splits.
        Empty dictionary if no pieces exceed material limits.
    """
    split_info = {}
    
    # Early exit if no material limits configured (unlimited material size)
    if design.max_material_width <= 0 and design.max_material_height <= 0:
        return split_info
    
    # Get dimensions of all box pieces that will be generated
    piece_dimensions = get_piece_dimensions(design)
      # Calculate overlap amount with smart thickness-based limits
    # Base overlap from user configuration (default 3.5x thickness)
    base_overlap = design.thickness * design.overlap_multiplier
    
    # Apply thickness-based minimum and maximum limits
    min_overlap = design.thickness * MIN_OVERLAP_MULTIPLIER  # Never less than 1x thickness
    max_overlap = design.thickness * MAX_OVERLAP_MULTIPLIER  # Never more than 6x thickness
    
    # Clamp overlap to smart range
    overlap = max(min_overlap, min(base_overlap, max_overlap))
    
    # Check each piece against material limits
    for piece_name, (width, height) in piece_dimensions.items():
        # Determine which dimensions exceed limits
        needs_width_split = design.max_material_width > 0 and width > design.max_material_width
        needs_height_split = design.max_material_height > 0 and height > design.max_material_height
        
        if needs_width_split or needs_height_split:
            # SPLIT DIRECTION PRIORITY:
            # Height constraint takes priority over width constraint
            # This typically results in fewer total pieces
            split_direction = 'horizontal' if needs_height_split else 'vertical'
              # Calculate number of pieces and split positions with size constraints
            if split_direction == 'horizontal':
                # HORIZONTAL SPLITTING (pieces stacked vertically)
                # Each piece height must fit within material height limit
                available_per_piece = design.max_material_height - overlap
                initial_num_pieces = int(math.ceil(height / available_per_piece))
                
                # Apply 25% minimum piece size constraint
                min_piece_size = design.max_material_height * MIN_SPLIT_PIECE_RATIO
                actual_piece_size = height / initial_num_pieces
                
                if actual_piece_size < min_piece_size:
                    # Reduce piece count to ensure minimum size
                    max_allowed_pieces = int(math.floor(height / min_piece_size))
                    num_pieces = max(2, max_allowed_pieces)  # At least 2 pieces for splitting
                else:
                    num_pieces = initial_num_pieces
                
                # Calculate optimized split positions
                piece_height = height / num_pieces
                split_positions = []
                for i in range(1, num_pieces):
                    # Position of cut line from top of original piece
                    split_positions.append(i * piece_height)
                    
            else:
                # VERTICAL SPLITTING (pieces arranged horizontally)
                # Each piece width must fit within material width limit
                available_per_piece = design.max_material_width - overlap
                initial_num_pieces = int(math.ceil(width / available_per_piece))
                
                # Apply 25% minimum piece size constraint  
                min_piece_size = design.max_material_width * MIN_SPLIT_PIECE_RATIO
                actual_piece_size = width / initial_num_pieces
                
                if actual_piece_size < min_piece_size:
                    # Reduce piece count to ensure minimum size
                    max_allowed_pieces = int(math.floor(width / min_piece_size))
                    num_pieces = max(2, max_allowed_pieces)  # At least 2 pieces for splitting
                else:
                    num_pieces = initial_num_pieces
                
                # Calculate optimized split positions
                piece_width = width / num_pieces
                split_positions = []
                for i in range(1, num_pieces):
                    # Position of cut line from left of original piece
                    split_positions.append(i * piece_width)
                
                # Calculate where to make cuts in the original piece
                split_positions = []
                for i in range(1, num_pieces):
                    # Position of cut line from left of original piece
                    split_positions.append(i * available_per_piece)
              # Determine minimum piece size based on split direction
            if split_direction == 'horizontal':
                min_piece_size = design.max_material_height * MIN_SPLIT_PIECE_RATIO
                material_limit = design.max_material_height
            else:
                min_piece_size = design.max_material_width * MIN_SPLIT_PIECE_RATIO  
                material_limit = design.max_material_width
            
            # Create split info for this piece
            split_info[piece_name] = SplitInfo(
                needs_splitting=True,
                split_direction=split_direction,
                num_pieces=num_pieces,
                overlap=overlap,
                split_positions=split_positions,
                join_type=design.join_type,
                # NEW FIELDS for enhanced design requirements:
                min_piece_size=min_piece_size,
                adjusted_positions=split_positions.copy(),  # Initially same as split_positions
                safe_zones=[],  # Will be populated when tab/slot analysis is implemented
                has_boundary_adjustments=False,  # No adjustments in current implementation
                geometry_conflicts=[]  # No conflicts detected yet (future feature)
            )
    
    return split_info

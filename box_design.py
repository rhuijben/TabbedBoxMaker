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

from typing import List, Optional, Tuple
from dataclasses import dataclass
from boxmaker_exceptions import DimensionError, ValidationError
from boxmaker_constants import BoxType, LayoutStyle


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
    width_dividers: DividerInfo   # Dividers running parallel to length (in width direction)
      # Box configuration
    box_type: BoxType
    style: LayoutStyle
    
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
                     style: LayoutStyle = LayoutStyle.SEPARATED) -> BoxDesign:
    """Create a complete box design from input parameters
    
    Args:
        length, width, height: Box dimensions
        thickness: Material thickness
        inside: Whether dimensions are internal (True) or external (False)
        div_l: Number of dividers in length direction
        div_w: Number of dividers in width direction
        div_l_custom: Custom compartment sizes for length direction
        div_w_custom: Custom compartment sizes for width direction
        box_type: Type of box (BoxType enum: FULL_BOX, NO_TOP, etc.)
        style: Layout style (LayoutStyle enum: SEPARATED, NESTED, COMPACT)
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
    
    return BoxDesign(
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
        style=style
    )

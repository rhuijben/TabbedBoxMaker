"""
Unified parameter configuration for BoxMaker CLI and Inkscape extension
======================================================================

This module provides a single source of truth for all BoxMaker parameters,
ensuring consistency between CLI arguments and Inkscape extension options.

Key Features:
- Uses enums instead of magic integers
- Provides parameter validation and type checking
- Supports both CLI argparse and Inkscape extension generation
- Centralizes all parameter definitions and metadata
"""

from dataclasses import dataclass
from typing import Optional, List, Union, Any, Dict
from enum import IntEnum

from boxmaker_constants import (
    BoxType, TabType, LayoutStyle, KeyDividerType, JoinType,
    DEFAULT_OVERLAP_MULTIPLIER, MIN_OVERLAP_MULTIPLIER, MAX_OVERLAP_MULTIPLIER
)


class UnitType(IntEnum):
    """Measurement units"""
    MM = 0
    CM = 1
    INCH = 2


class InsideOutside(IntEnum):
    """Dimension interpretation"""
    OUTSIDE = 0  # Dimensions are outside measurements
    INSIDE = 1   # Dimensions are inside measurements


class TabWidth(IntEnum):
    """Tab width calculation method"""
    FIXED = 0        # Fixed width tabs
    PROPORTIONAL = 1 # Proportional to edge length


class TabSymmetry(IntEnum):
    """Tab symmetry options"""
    XY_SYMMETRIC = 0      # Symmetric in both X and Y
    ROTATE_SYMMETRIC = 1  # Rotationally symmetric


class LineThickness(IntEnum):
    """Line thickness options"""
    DEFAULT = 0   # Default line thickness
    HAIRLINE = 1  # Hairline thickness (0.002" for Epilog)


@dataclass
class ParameterDefinition:
    """
    Definition of a single parameter for BoxMaker
    
    This class contains all metadata needed to generate both CLI arguments
    and Inkscape extension XML parameters from a single source.
    """
    name: str                    # Internal parameter name
    param_type: type            # Python type (int, float, str, bool)
    default: Any                # Default value
    description: str            # Help text/description
    
    # CLI-specific options
    cli_name: Optional[str] = None      # CLI argument name (defaults to --name)
    cli_short: Optional[str] = None     # Short CLI argument (-x)
    
    # Inkscape-specific options  
    inkscape_name: Optional[str] = None # Inkscape parameter name (defaults to name)
    inkscape_gui_text: Optional[str] = None  # GUI label (defaults to description)
    
    # Validation options
    min_val: Optional[Union[int, float]] = None
    max_val: Optional[Union[int, float]] = None
    choices: Optional[List[Any]] = None
    enum_type: Optional[type] = None    # Enum class for validation
    
    # Display options
    precision: Optional[int] = None     # Decimal places for float display
    hidden: bool = False               # Hide from CLI/GUI (internal use only)
    advanced: bool = False             # Advanced option (maybe separate tab/section)


# CORE PARAMETER DEFINITIONS
# ==========================
# Single source of truth for all BoxMaker parameters

PARAMETER_DEFINITIONS = [
    # Basic Dimensions
    ParameterDefinition(
        name="length",
        param_type=float,
        default=100.0,
        description="Length of box (mm)",
        min_val=40.0,
        max_val=10000.0,
        precision=3
    ),
    
    ParameterDefinition(
        name="width", 
        param_type=float,
        default=100.0,
        description="Width of box (mm)",
        min_val=40.0,
        max_val=10000.0,
        precision=3
    ),
    
    ParameterDefinition(
        name="height",
        param_type=float,
        default=100.0,
        description="Height of box (mm)",
        inkscape_name="depth",  # Inkscape uses 'depth' for height
        min_val=40.0,
        max_val=10000.0,
        precision=3
    ),
    
    # Material Properties
    ParameterDefinition(
        name="thickness",
        param_type=float,
        default=3.0,
        description="Material thickness (mm)",
        min_val=0.1,
        max_val=50.0,
        precision=2
    ),
    
    ParameterDefinition(
        name="kerf",
        param_type=float,
        default=0.5,
        description="Kerf width (cut width) (mm)",
        min_val=0.0,
        max_val=10.0,
        precision=3
    ),
    
    # Tab Configuration
    ParameterDefinition(
        name="tab",
        param_type=float,
        default=25.0,
        description="Tab width (mm)",
        inkscape_gui_text="Min/Preferred Width",
        min_val=2.0,
        max_val=1000.0,
        precision=2
    ),
    
    ParameterDefinition(
        name="equal",
        param_type=int,
        default=TabWidth.FIXED,
        description="Tab width calculation method",
        enum_type=TabWidth,
        choices=[TabWidth.FIXED, TabWidth.PROPORTIONAL],
        inkscape_gui_text="Width"
    ),
    
    ParameterDefinition(
        name="tabtype",
        param_type=int,
        default=TabType.LASER,
        description="Tab cutting type",
        enum_type=TabType,
        choices=[TabType.LASER, TabType.CNC],
        inkscape_gui_text="Type"
    ),
    
    ParameterDefinition(
        name="tabsymmetry",
        param_type=int,
        default=TabSymmetry.XY_SYMMETRIC,
        description="Tab symmetry style",
        enum_type=TabSymmetry,
        choices=[TabSymmetry.XY_SYMMETRIC, TabSymmetry.ROTATE_SYMMETRIC],
        inkscape_gui_text="Symmetry"
    ),
    
    # Tab Dimples (CNC specific)
    ParameterDefinition(
        name="dimpleheight",
        param_type=float,
        default=0.0,
        description="Tab dimple height (mm)",
        inkscape_gui_text="Dimple Height", 
        min_val=0.0,
        max_val=100.0,
        precision=2,
        advanced=True
    ),
    
    ParameterDefinition(
        name="dimplelength",
        param_type=float,
        default=0.0,
        description="Tab dimple tip length (mm)",
        inkscape_gui_text="Dimple Length",
        min_val=0.0,
        max_val=100.0,
        precision=2,
        advanced=True
    ),
    
    # Box Configuration
    ParameterDefinition(
        name="boxtype",
        param_type=int,
        default=BoxType.FULL_BOX,
        description="Box type (which sides to include)",
        enum_type=BoxType,
        choices=list(BoxType),
        inkscape_gui_text="Box Type"
    ),
    
    ParameterDefinition(
        name="inside",
        param_type=int,
        default=InsideOutside.OUTSIDE,
        description="Dimension interpretation",
        enum_type=InsideOutside,
        choices=[InsideOutside.OUTSIDE, InsideOutside.INSIDE],
        inkscape_gui_text="Box Dimensions"
    ),
    
    # Layout and Style
    ParameterDefinition(
        name="style",
        param_type=int,
        default=LayoutStyle.SEPARATED,
        description="Layout style for arranging pieces",
        enum_type=LayoutStyle,
        choices=list(LayoutStyle),
        inkscape_gui_text="Layout"
    ),
    
    ParameterDefinition(
        name="spacing",
        param_type=float,
        default=25.0,
        description="Space between parts in layout (mm)",
        inkscape_gui_text="Space Between Parts",
        min_val=0.0,
        max_val=1000.0,
        precision=2
    ),
    
    # Line Rendering
    ParameterDefinition(
        name="hairline",
        param_type=int,
        default=LineThickness.DEFAULT,
        description="Line thickness style",
        enum_type=LineThickness,
        choices=[LineThickness.DEFAULT, LineThickness.HAIRLINE],
        inkscape_gui_text="Line Thickness"
    ),
      # Units
    ParameterDefinition(
        name="unit",
        param_type=str,
        default="mm",
        description="Measurement units",
        choices=["mm", "cm", "in"],
        inkscape_gui_text="Units"
    ),
    
    # Dividers
    ParameterDefinition(
        name="div_l",
        param_type=int,
        default=0,
        description="Number of dividers along length axis",
        cli_name="--div-l",
        inkscape_gui_text="Dividers (Length axis)",
        min_val=0,
        max_val=20
    ),
    
    ParameterDefinition(
        name="div_w",
        param_type=int,
        default=0,
        description="Number of dividers along width axis", 
        cli_name="--div-w",
        inkscape_gui_text="Dividers (Width axis)",
        min_val=0,
        max_val=20
    ),
    
    ParameterDefinition(
        name="div_l_custom",
        param_type=str,
        default="",
        description="Custom compartment sizes along length (semicolon-separated)",
        cli_name="--div-l-custom",
        inkscape_gui_text="Custom Length Compartment Widths (semicolon-separated, optional)"
    ),
    
    ParameterDefinition(
        name="div_w_custom",
        param_type=str,
        default="",
        description="Custom compartment sizes along width (semicolon-separated)",
        cli_name="--div-w-custom", 
        inkscape_gui_text="Custom Width Compartment Widths (semicolon-separated, optional)"
    ),
    
    ParameterDefinition(
        name="keydiv",
        param_type=int,
        default=KeyDividerType.NONE,
        description="Key dividers into walls/floor",
        enum_type=KeyDividerType,
        choices=list(KeyDividerType),
        inkscape_gui_text="Key the dividers into"
    ),
    
    # Material Size Limits
    ParameterDefinition(
        name="max_material_width",
        param_type=float,
        default=0.0,
        description="Maximum material width in mm (0 = unlimited)",
        cli_name="--max-material-width",
        min_val=0.0,
        max_val=10000.0,
        precision=1
    ),
    
    ParameterDefinition(
        name="max_material_height", 
        param_type=float,
        default=0.0,
        description="Maximum material height in mm (0 = unlimited)",
        cli_name="--max-material-height",
        min_val=0.0,
        max_val=10000.0,
        precision=1
    ),
    
    ParameterDefinition(
        name="overlap_multiplier",
        param_type=float,
        default=DEFAULT_OVERLAP_MULTIPLIER,
        description=f"Overlap multiplier for split pieces (range: {MIN_OVERLAP_MULTIPLIER}-{MAX_OVERLAP_MULTIPLIER})",
        cli_name="--overlap-multiplier",
        min_val=MIN_OVERLAP_MULTIPLIER,
        max_val=MAX_OVERLAP_MULTIPLIER,
        precision=1
    ),    # Output Options
    ParameterDefinition(
        name="output",
        param_type=str,
        default="box.svg",
        description="Output SVG filename",
        cli_short="-o"
    ),
    
    # Advanced/Internal Options
    ParameterDefinition(
        name="optimize",
        param_type=bool,
        default=True,
        description="Combine and clean paths",
        inkscape_gui_text="Combine and clean paths",
        hidden=True  # CLI doesn't expose this
    ),
    
    # Schroff-specific (legacy support)
    ParameterDefinition(
        name="schroff",
        param_type=int,
        default=0,
        description="Enable Schroff mode",
        hidden=True,
        advanced=True
    ),
    
    ParameterDefinition(
        name="rail_height",
        param_type=float,
        default=10.0,
        description="Height of rail (Schroff mode)",
        hidden=True,
        advanced=True
    ),
    
    ParameterDefinition(
        name="rail_mount_depth",
        param_type=float,
        default=17.4,
        description="Depth for rail mount bolt (Schroff mode)",
        hidden=True,
        advanced=True
    ),
    
    ParameterDefinition(
        name="rail_mount_centre_offset",
        param_type=float,
        default=0.0,
        description="Rail mount bolt offset (Schroff mode)",
        hidden=True,
        advanced=True
    ),
    
    ParameterDefinition(
        name="rows",
        param_type=int,
        default=0,
        description="Number of Schroff rows",
        hidden=True,
        advanced=True
    ),
    
    ParameterDefinition(
        name="hp",
        param_type=int,
        default=0,
        description="Width in TE/HP units (Schroff mode)",
        hidden=True,
        advanced=True
    ),
    
    ParameterDefinition(
        name="row_spacing",
        param_type=float,
        default=10.0,
        description="Row spacing (Schroff mode)",
        hidden=True,
        advanced=True
    )
]


def get_parameter_by_name(name: str) -> Optional[ParameterDefinition]:
    """Get parameter definition by name"""
    for param in PARAMETER_DEFINITIONS:
        if param.name == name:
            return param
    return None


def get_parameters_for_cli() -> List[ParameterDefinition]:
    """Get parameters that should be exposed in CLI"""
    return [p for p in PARAMETER_DEFINITIONS if not p.hidden]


def get_parameters_for_inkscape() -> List[ParameterDefinition]:
    """Get parameters that should be exposed in Inkscape extension"""
    return [p for p in PARAMETER_DEFINITIONS if not p.hidden]


def validate_parameter_value(param: ParameterDefinition, value: Any) -> Any:
    """
    Validate and convert a parameter value according to its definition
    
    Args:
        param: Parameter definition
        value: Value to validate
        
    Returns:
        Validated and converted value
        
    Raises:
        ValueError: If value is invalid
    """
    # Type conversion
    if param.param_type == bool:
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        return bool(value)
    
    try:
        converted_value = param.param_type(value)
    except (ValueError, TypeError):
        raise ValueError(f"Parameter '{param.name}' must be of type {param.param_type.__name__}")
    
    # Range validation
    if param.min_val is not None and converted_value < param.min_val:
        raise ValueError(f"Parameter '{param.name}' must be >= {param.min_val}")
    
    if param.max_val is not None and converted_value > param.max_val:
        raise ValueError(f"Parameter '{param.name}' must be <= {param.max_val}")
    
    # Choice validation
    if param.choices is not None and converted_value not in param.choices:
        raise ValueError(f"Parameter '{param.name}' must be one of: {param.choices}")
    
    return converted_value


def get_enum_display_name(enum_value, enum_type) -> str:
    """Get human-readable name for enum value"""
    if enum_type == BoxType:
        names = {
            BoxType.FULL_BOX: "Fully enclosed",
            BoxType.NO_TOP: "One side open (LxW)", 
            BoxType.NO_BOTTOM: "Two sides open (LxW and LxH)",
            BoxType.NO_SIDES: "Three sides open (LxW, LxH, HxW)",
            BoxType.NO_FRONT_BACK: "Opposite ends open (LxW)",
            BoxType.NO_LEFT_RIGHT: "Two panels only (LxW and LxH)"
        }
        return names.get(enum_value, str(enum_value))
    
    elif enum_type == TabType:
        names = {
            TabType.LASER: "Regular (Laser)",
            TabType.CNC: "Dogbone (Mill)"
        }
        return names.get(enum_value, str(enum_value))
    
    elif enum_type == LayoutStyle:
        names = {
            LayoutStyle.SEPARATED: "Diagramatic",
            LayoutStyle.NESTED: "3 piece", 
            LayoutStyle.COMPACT: "Inline(compact)"
        }
        return names.get(enum_value, str(enum_value))
    
    elif enum_type == KeyDividerType:
        names = {
            KeyDividerType.WALLS_AND_FLOOR: "All sides",
            KeyDividerType.WALLS_ONLY: "Walls",
            KeyDividerType.FLOOR_ONLY: "Floor / Ceiling",
            KeyDividerType.NONE: "None"
        }
        return names.get(enum_value, str(enum_value))
    
    elif enum_type == TabWidth:
        names = {
            TabWidth.FIXED: "Fixed",
            TabWidth.PROPORTIONAL: "Proportional"
        }
        return names.get(enum_value, str(enum_value))
    
    elif enum_type == TabSymmetry:
        names = {
            TabSymmetry.XY_SYMMETRIC: "XY Symmetric",
            TabSymmetry.ROTATE_SYMMETRIC: "Rotate Symmetric"
        }
        return names.get(enum_value, str(enum_value))
    
    elif enum_type == LineThickness:
        names = {
            LineThickness.DEFAULT: "Default",
            LineThickness.HAIRLINE: "Hairline (0.002\" for Epilog)"
        }
        return names.get(enum_value, str(enum_value))
    
    elif enum_type == InsideOutside:
        names = {
            InsideOutside.OUTSIDE: "Outside",
            InsideOutside.INSIDE: "Inside"
        }
        return names.get(enum_value, str(enum_value))
    
    return str(enum_value)

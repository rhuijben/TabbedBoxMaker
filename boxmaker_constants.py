"""
Constants and enums for BoxMaker
"""
from enum import IntEnum


class BoxType(IntEnum):
    """Box types available"""
    FULL_BOX = 1
    NO_TOP = 2
    NO_BOTTOM = 3
    NO_SIDES = 4
    NO_FRONT_BACK = 5
    NO_LEFT_RIGHT = 6


class TabType(IntEnum):
    """Tab cutting types"""
    LASER = 0  # Standard tabs for laser cutting
    CNC = 1    # Dogbone tabs for CNC milling


class LayoutStyle(IntEnum):
    """Layout styles for arranging box pieces"""
    SEPARATED = 1
    NESTED = 2
    COMPACT = 3


class KeyDividerType(IntEnum):
    """Key divider types"""
    WALLS_AND_FLOOR = 0
    WALLS_ONLY = 1
    FLOOR_ONLY = 2
    NONE = 3


class JoinType(IntEnum):
    """
    Types of joints for connecting split pieces together.
    
    DESIGN CONSIDERATIONS:
    ======================
    When a box piece exceeds material size limits, it must be split into smaller pieces.
    These pieces need to be joined back together during assembly. Different join types
    offer different trade-offs between strength, cutting complexity, and assembly ease.
    
    JOIN TYPE DETAILS:
    ==================
    
    SIMPLE_OVERLAP (0):
    - Description: Plain overlapping material with no special geometry
    - Strength: Moderate (depends on adhesive or fasteners)
    - Cutting: Very simple, no special cuts required
    - Assembly: Easy, just align and attach with glue/screws/etc.
    - Use case: Quick prototypes, non-structural applications
    - Material waste: Minimal (just the overlap amount)
    
    SQUARES (1):
    - Description: Simple rectangular tabs of uniform dimensions
    - Strength: Good mechanical connection, resists separation
    - Cutting: Simple rectangular cuts, easy to program
    - Assembly: Self-aligning, positive mechanical connection
    - Use case: General purpose strong connection
    - Material waste: Low (small tab cuts)
    
    DOVETAIL (2):
    - Description: Angled interlocking tabs that resist tension
    - Strength: Excellent, prevents pulling apart under load
    - Cutting: More complex angled cuts, requires precise angles
    - Assembly: Very strong mechanical lock, minimal fasteners needed
    - Use case: High-stress applications, traditional woodworking
    - Material waste: Moderate (angled cuts waste small triangles)
    
    FINGER_JOINT (3):
    - Description: Alternating rectangular tabs and slots (box joint)
    - Strength: Excellent, large glue surface area
    - Cutting: Complex pattern of multiple precise cuts
    - Assembly: Requires precise fit, strong when assembled
    - Use case: Traditional cabinetry, visible joints
    - Material waste: Low to moderate depending on finger spacing
    
    IMPLEMENTATION STATUS:
    ======================
    - SIMPLE_OVERLAP: ✓ Implemented (default)
    - SQUARES: ⚠ Planned for next iteration
    - DOVETAIL: ⚠ Planned for future release
    - FINGER_JOINT: ⚠ Planned for future release
    
    SELECTION GUIDELINES:
    =====================
    - For beginners or quick prototypes: SIMPLE_OVERLAP
    - For general woodworking projects: SQUARES
    - For furniture or load-bearing: DOVETAIL
    - For visible decorative joints: FINGER_JOINT
    """
    SIMPLE_OVERLAP = 0   # Simple overlap with no special joint
    SQUARES = 1          # Simple square tabs for connection (same height and width)
    DOVETAIL = 2         # Dovetail joint for strong connection
    FINGER_JOINT = 3     # Finger/box joint for connection


# Default values
DEFAULT_LENGTH = 100.0
DEFAULT_WIDTH = 100.0
DEFAULT_HEIGHT = 100.0
DEFAULT_TAB_WIDTH = 25.0
DEFAULT_THICKNESS = 3.0
DEFAULT_KERF = 0.5
DEFAULT_SPACING = 25.0

# Minimum values for validation (realistic for woodworking)
MIN_DIMENSION = 40.0  # 4cm minimum for practical boxes
MIN_THICKNESS = 0.1
MIN_TAB_WIDTH = 2.0   # Minimum practical tab width (2mm is reasonable for thin materials)

# Tab sizing guidelines (based on material thickness)
MIN_TAB_TO_THICKNESS_RATIO = 0.5  # Tabs can be thinner but become weak
RECOMMENDED_MIN_TAB_TO_THICKNESS_RATIO = 1.0  # Recommended minimum for strength
MAX_TAB_TO_THICKNESS_RATIO = 20.0  # Very large tabs for big boxes (was 8.0)
RECOMMENDED_MAX_TAB_TO_THICKNESS_RATIO = 8.0  # Typical maximum for most boxes
RECOMMENDED_TAB_TO_THICKNESS_RATIO = 3.0  # 3x thickness is typical

# Maximum values
MAX_DIMENSION = 10000.0  # 10 meters (practical limit)
MAX_THICKNESS = 50.0
MAX_MATERIAL_DIMENSION = 10000.0  # Maximum material sheet size

# Material size limits (for cutting equipment)
# ==============================================
# These settings enable BoxMaker to work with laser cutters, CNC machines, and other
# cutting equipment that have limited bed/material sizes. When a box piece exceeds
# these dimensions, it will be automatically split into smaller pieces with overlap
# regions for joining during assembly.
#
# COMMON EQUIPMENT SIZES:
# - Small desktop laser cutters: 300mm x 300mm (12" x 12")
# - Medium laser cutters: 600mm x 400mm (24" x 16") 
# - Large laser cutters: 1200mm x 900mm (48" x 36")
# - CNC routers: varies widely, often 600mm x 600mm to 1500mm x 3000mm
#
# USAGE:
# - Set to 0 to disable size checking (unlimited material size)
# - Set to actual cutting area dimensions to enable automatic splitting
# - Both width and height limits can be active simultaneously
# - Pieces are split with overlap regions for assembly
DEFAULT_MAX_MATERIAL_WIDTH = 0.0   # 0 = unlimited/disabled
DEFAULT_MAX_MATERIAL_HEIGHT = 0.0  # 0 = unlimited/disabled

# Piece splitting constants
# =========================
# Configuration for how oversized pieces are split to fit material constraints.
# The splitting system creates multiple smaller pieces with overlap regions that
# can be joined together during assembly.
#
# OVERLAP CALCULATION:
# The overlap between adjacent split pieces provides material for joining:
# - Base overlap = material_thickness × DEFAULT_OVERLAP_MULTIPLIER  
# - Minimum overlap = MIN_OVERLAP (safety margin for thin materials)
# - Maximum overlap = MAX_OVERLAP (prevents excessive waste)
#
# OVERLAP PURPOSES:
# - Provides surface area for adhesive bonding
# - Allows space for mechanical fasteners (screws, bolts, etc.)
# - Enables alignment features like dowel holes
# - Accommodates manufacturing tolerances
#
# RECOMMENDED VALUES:
# - 3x thickness works well for most woodworking applications
# - Thicker materials may need proportionally less overlap
# - Complex join types (dovetail, finger) may need more overlap
DEFAULT_OVERLAP_MULTIPLIER = 3.0  # Overlap = thickness * multiplier
MIN_OVERLAP = 5.0                 # Minimum overlap in mm (safety for thin materials)
MAX_OVERLAP = 50.0                # Maximum overlap in mm (prevents excessive waste)

# Join configuration defaults
# ===========================
# Determines how split pieces are designed to connect together.
# Currently only SIMPLE_OVERLAP is implemented, with other join types
# planned for future versions.
#
# JOIN TYPE CHARACTERISTICS:
# - SIMPLE_OVERLAP: Just overlapping material, suitable for adhesive/fasteners
# - SQUARES: Simple square tabs, moderate strength, easy to cut
# - DOVETAIL: Angled interlocking, strong mechanical connection  
# - FINGER_JOINT: Alternating tabs/slots, strong with large glue area
DEFAULT_JOIN_TYPE = JoinType.SIMPLE_OVERLAP

# Conversion factors
INCHES_TO_MM = 25.4
HAIRLINE_THICKNESS_INCHES = 0.002

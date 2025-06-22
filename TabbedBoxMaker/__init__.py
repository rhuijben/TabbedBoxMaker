"""
TabbedBoxMaker - Tabbed Box Generator Library

A Python library for generating SVG files of laser-cut tabbed boxes.
"""

__version__ = "1.3"

from .core import BoxMakerCore
from .constants import BoxType, TabType, LayoutStyle
from .exceptions import BoxMakerError, DimensionError, TabError, MaterialError, ValidationError
from .parameters import *
from .config import (
    create_cli_parser, 
    create_inkscape_extension_args,
    extract_parameters_from_namespace, 
    validate_all_parameters
)

__all__ = [
    'BoxMakerCore',
    'BoxType', 'TabType', 'LayoutStyle',
    'BoxMakerError', 'DimensionError', 'TabError', 'MaterialError', 'ValidationError',
    'create_cli_parser', 'create_inkscape_extension_args',
    'extract_parameters_from_namespace', 'validate_all_parameters'
]

#!/usr/bin/env python3
"""
BoxMaker CLI - Command Line Interface for Tabbed Box Generator

This is the CLI-only entry point for BoxMaker. For Inkscape extension usage,
see boxmaker_inkscape.py instead.

Generates Inkscape SVG files containing box components needed to 
CNC (laser/mill) cut a box with tabbed joints taking kerf and clearance into account.

ARCHITECTURE NOTES:
- This file contains only CLI logic, no Inkscape dependencies
- Uses the unified parameter system defined in boxmaker_parameters.py
- Core box generation logic is in boxmaker_core.py
- Inkscape extension is in boxmaker_inkscape.py
- Parameter definitions and parsing utilities are in boxmaker_config.py

USAGE:
    python boxmaker.py --length 100 --width 80 --height 50 --thickness 3 --output box.svg

Original Tabbed Box Maker Copyright (C) 2011 elliot white
Refactoring for testability and separation of concerns by GitHub Copilot 2025
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from boxmaker_config import create_cli_parser, extract_parameters_from_namespace, validate_all_parameters
from boxmaker_core import BoxMakerCore
from boxmaker_exceptions import DimensionError, TabError, MaterialError

def main():
    """Main CLI function with unified parameter system"""
    parser = create_cli_parser()
    args = parser.parse_args()
    
    try:
        # Extract and validate parameters using unified system
        param_dict = extract_parameters_from_namespace(args)
        validated_params = validate_all_parameters(param_dict)
        
        # Create core instance and set parameters
        core = BoxMakerCore()
        core.set_parameters(**validated_params)
        
        # Generate SVG
        svg_content = core.generate_svg()
        
        # Write to file
        output_file = validated_params['output']
        with open(output_file, 'w') as f:
            f.write(svg_content)
        
        print(f"Box SVG generated: {output_file}")
        
        # Show material limits info if applicable
        if validated_params['max_material_width'] > 0 or validated_params['max_material_height'] > 0:
            print(f"Material limits: {validated_params['max_material_width']}mm x {validated_params['max_material_height']}mm")
            print(f"Overlap multiplier: {validated_params['overlap_multiplier']}x thickness")
        
    except DimensionError as e:
        print(f"ERROR: Dimension Error: {e}")
        print("TIP: All dimensions should be at least 40mm for practical boxes")
        sys.exit(1)
    except TabError as e:
        print(f"ERROR: Tab Error: {e}")
        print("TIP: Use tabs between material thickness and dimension/3")
        sys.exit(1)
    except MaterialError as e:
        print(f"ERROR: Material Error: {e}")
        print("TIP: Material thickness should be much smaller than box dimensions")
        sys.exit(1)
    except ValueError as e:
        print(f"ERROR: Parameter Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Unexpected Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

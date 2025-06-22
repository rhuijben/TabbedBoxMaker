#!/usr/bin/env python3
"""
BoxMaker Inkscape Extension - SVG Extension for Tabbed Box Generation
=====================================================================

This is the dedicated Inkscape extension for BoxMaker, completely separate
from the CLI interface. This separation provides several benefits:

BENEFITS OF SEPARATION:
- Focused Inkscape-specific functionality
- Proper SVG integration and unit handling
- Clean separation of concerns
- Easier maintenance and testing
- No dual-mode complexity

This file is referenced by the .inx extension files and provides the
inkex.Effect subclass that Inkscape requires.

INKSCAPE INTEGRATION:
- Inherits from inkex.Effect for proper Inkscape integration
- Handles unit conversion using Inkscape's unit system
- Generates SVG elements directly in the current document
- Uses Inkscape's error reporting system

For command-line usage, use boxmaker.py instead.
"""

import os
import sys

# Import Inkscape modules
try:
    import inkex
    import gettext
    _ = gettext.gettext
except ImportError:
    print("Error: This file requires Inkscape's Python environment")
    print("Use boxmaker.py for command-line usage")
    sys.exit(1)

from boxmaker_core import BoxMakerCore
from boxmaker_exceptions import DimensionError, TabError, MaterialError
from boxmaker_config import (
    create_inkscape_extension_args, extract_parameters_from_namespace, validate_all_parameters
)

__version__ = "1.3"

# Global line thickness variable (used by SVG generation functions)
linethickness = 1

def log(text):
    """Debug logging if environment variable is set"""
    if 'SCHROFF_LOG' in os.environ:
        f = open(os.environ.get('SCHROFF_LOG'), 'a')
        f.write(text + "\n")

def newGroup(canvas):
    """Create a new SVG group for organizing elements"""
    panelId = canvas.svg.get_unique_id('panel')
    group = canvas.svg.get_current_layer().add(inkex.Group(id=panelId))
    return group
  
def getLine(XYstring):
    """Create an SVG line element from path data"""
    line = inkex.PathElement()
    line.style = { 
        'stroke': '#000000', 
        'stroke-width': str(linethickness), 
        'fill': 'none' 
    }
    line.path = XYstring
    return line

def getCircle(r, c):
    """Create an SVG circle element"""
    (cx, cy) = c
    log("putting circle at (%d,%d)" % (cx, cy))
    circle = inkex.PathElement.arc((cx, cy), r)
    circle.style = { 
        'stroke': '#000000', 
        'stroke-width': str(linethickness), 
        'fill': 'none' 
    }
    return circle


class BoxMaker(inkex.Effect):
    """
    Inkscape Extension for BoxMaker
    
    This class provides the Inkscape extension interface for generating
    tabbed boxes directly in SVG documents. It uses the unified parameter
    system to ensure consistency with the CLI version.
    """
    
    def __init__(self):
        """Initialize the Inkscape extension"""
        # Call the base class constructor
        inkex.Effect.__init__(self)
        
        # Add arguments using unified parameter system
        # This ensures consistency with the CLI interface
        create_inkscape_extension_args(self)

    def effect(self):
        """
        Main effect method called by Inkscape
        
        This method:
        1. Extracts parameters from Inkscape's option system
        2. Validates and converts parameters using the unified system
        3. Handles Inkscape-specific unit conversion
        4. Generates the box using BoxMakerCore
        5. Converts the output to SVG elements in the document
        """
        global linethickness
        
        try:
            # Extract and validate parameters from Inkscape options
            param_dict = extract_parameters_from_namespace(self.options)
            validated_params = validate_all_parameters(param_dict)
            
            # Handle unit conversion for Inkscape
            unit = validated_params.get('unit', 'mm')
            
            # Convert dimensional parameters using Inkscape's unit conversion
            # This ensures proper scaling regardless of document units
            dimensional_params = [
                'kerf', 'length', 'width', 'height', 'thickness', 'tab', 'spacing', 
                'dimpleheight', 'dimplelength', 'max_material_width', 'max_material_height'
            ]
            
            for param_name in dimensional_params:
                if param_name in validated_params and validated_params[param_name] != 0:
                    value = validated_params[param_name]
                    
                    # For outer dimensions, add kerf compensation
                    if param_name in ['length', 'width', 'height']:
                        value += validated_params.get('kerf', 0)
                    
                    # Convert to document units
                    validated_params[param_name] = self.svg.unittouu(str(value) + unit)
            
            # Set line thickness based on hairline option
            if validated_params.get('hairline', 0):
                linethickness = self.svg.unittouu('0.002in')  # Epilog hairline
            else:
                linethickness = 1  # Default thickness
            
            # Add line thickness to parameters
            validated_params['linethickness'] = linethickness
            
            # Create core instance and set parameters
            core = BoxMakerCore()
            core.set_parameters(**validated_params)
            
            # Generate the box using core functionality
            result = core.generate_box()
            
            # Convert core output to Inkscape SVG elements
            # Paths (box edges, tabs, etc.)
            for path_data in result['paths']:
                line = getLine(path_data['data'])
                group = newGroup(self)
                group.add(line)
            
            # Circles (divider holes, etc.)  
            for circle_data in result['circles']:
                circle = getCircle(circle_data['r'], (circle_data['cx'], circle_data['cy']))
                group = newGroup(self)
                group.add(circle)
                
        except DimensionError as e:
            inkex.errormsg(_(f"Dimension Error: {e}"))
            inkex.errormsg(_("Tip: All dimensions should be at least 40mm for practical boxes"))
            return
            
        except TabError as e:
            inkex.errormsg(_(f"Tab Error: {e}"))
            inkex.errormsg(_("Tip: Use tabs between material thickness and dimension/3"))
            return
            
        except MaterialError as e:
            inkex.errormsg(_(f"Material Error: {e}"))
            inkex.errormsg(_("Tip: Material thickness should be much smaller than box dimensions"))
            return
            
        except ValueError as e:
            inkex.errormsg(_(f"Parameter Error: {e}"))
            return
            
        except Exception as e:
            inkex.errormsg(_(f"Unexpected Error: {e}"))
            inkex.errormsg(_("Please report this issue"))
            return


# Entry point for Inkscape extension system
if __name__ == '__main__':
    BoxMaker().run()

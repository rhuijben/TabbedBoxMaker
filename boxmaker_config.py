"""
Parameter configuration generators for BoxMaker
===============================================

This module generates CLI argument parsers and Inkscape extension XML
from the unified parameter definitions, ensuring consistency between
both interfaces.
"""

import argparse
from typing import Dict, Any
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

from boxmaker_parameters import (
    PARAMETER_DEFINITIONS, get_parameters_for_cli, get_parameters_for_inkscape,
    get_enum_display_name, ParameterDefinition
)


def create_cli_parser() -> argparse.ArgumentParser:
    """
    Create CLI argument parser from unified parameter definitions
    
    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        description='Generate tabbed box SVG files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic box
  %(prog)s --length 100 --width 80 --height 50 --thickness 3 --output mybox.svg
  
  # Box with material size limits (for laser cutters)
  %(prog)s --length 400 --width 300 --max-material-width 300 --max-material-height 300
  
  # Box with dividers
  %(prog)s --length 200 --width 150 --div-l 2 --div-w 1
        """
    )
    
    # Add parameters from unified definitions
    for param in get_parameters_for_cli():
        add_cli_argument(parser, param)
    
    return parser


def add_cli_argument(parser: argparse.ArgumentParser, param: ParameterDefinition):
    """Add a single CLI argument based on parameter definition"""
    
    # Determine argument name(s)
    arg_names = []
    if param.cli_name:
        arg_names.append(param.cli_name)
    else:
        arg_names.append(f"--{param.name.replace('_', '-')}")
    
    if param.cli_short:
        arg_names.append(param.cli_short)
    
    # Build argument kwargs
    kwargs = {
        'help': param.description,
        'default': param.default
    }
    
    # Handle type and choices
    if param.enum_type:
        # For enums, use the integer values but show meaningful choices in help
        kwargs['type'] = int
        kwargs['choices'] = [int(choice) for choice in param.choices] if param.choices else None
        
        # Enhance help text with enum meanings
        if param.choices:
            choice_help = []
            for choice in param.choices:
                display_name = get_enum_display_name(choice, param.enum_type)
                choice_help.append(f"{int(choice)}={display_name}")
            kwargs['help'] += f" ({', '.join(choice_help)})"
            
    elif param.param_type == bool:
        kwargs['action'] = 'store_true'
        kwargs.pop('type', None)  # Remove type for boolean flags
        if param.default:
            # If default is True, make it store_false
            kwargs['action'] = 'store_false'
            
    else:
        kwargs['type'] = param.param_type
        if param.choices:
            kwargs['choices'] = param.choices
    
    # Add the argument
    parser.add_argument(*arg_names, **kwargs)


def create_inkscape_extension_args(extension_class):
    """
    Add Inkscape extension arguments from unified parameter definitions
    
    Args:
        extension_class: Inkscape extension class to add arguments to
    """
    for param in get_parameters_for_inkscape():
        add_inkscape_argument(extension_class, param)


def add_inkscape_argument(extension_class, param: ParameterDefinition):
    """Add a single Inkscape argument based on parameter definition"""
    
    # Determine parameter name
    param_name = param.inkscape_name or param.name
    
    # Build argument kwargs
    kwargs = {
        'action': 'store',
        'dest': param.name,  # Always use canonical name for dest
        'default': param.default,
        'help': param.description
    }
    
    # Handle type
    if param.enum_type or param.param_type == int:
        kwargs['type'] = int
    elif param.param_type == float:
        kwargs['type'] = float
    elif param.param_type == str:
        kwargs['type'] = str
    elif param.param_type == bool:
        kwargs['type'] = bool  # Inkscape handles this specially
    
    # Add the argument
    extension_class.arg_parser.add_argument(f'--{param_name}', **kwargs)


def generate_inkscape_xml() -> str:
    """
    Generate Inkscape extension XML from unified parameter definitions
    
    Returns:
        Formatted XML string for .inx file
    """
    # Create root element
    root = Element('inkscape-extension')
    root.set('xmlns', 'http://www.inkscape.org/namespace/inkscape/extension')
    
    # Basic extension info
    name_elem = SubElement(root, '_name')
    name_elem.text = 'CNC Tabbed Box Maker'
    
    id_elem = SubElement(root, 'id') 
    id_elem.text = 'nz.paulh-rnd.tabbedboxmaker'
    
    # Create main layout container
    hbox = SubElement(root, 'hbox')
    
    # Left column - dimensions and tabs
    left_vbox = SubElement(hbox, 'vbox')
      # Dimensions section
    add_xml_section(left_vbox, "Dimensions", [
        'unit', 'inside', 'length', 'width', 'height'
    ])
    
    # Tabs section  
    add_xml_section(left_vbox, "Tabs", [
        'equal', 'tab', 'tabtype', 'tabsymmetry', 'dimpleheight', 'dimplelength'
    ])
    
    # Separator
    SubElement(hbox, 'spacer')
    SubElement(hbox, 'separator')
    SubElement(hbox, 'spacer')
    
    # Right column - material, layout, dividers
    right_vbox = SubElement(hbox, 'vbox')
    
    # Line and kerf section
    add_xml_section(right_vbox, "Line and kerf", [
        'hairline', 'thickness', 'kerf'
    ])
    
    # Layout section
    add_xml_section(right_vbox, "Layout", [
        'style', 'boxtype', 'spacing'
    ])
    
    # Dividers section
    add_xml_section(right_vbox, "Dividers", [
        'div_l', 'div_l_custom', 'div_w', 'div_w_custom', 'keydiv'
    ])
    
    # Material limits section
    add_xml_section(right_vbox, "Material Size Limits", [
        'max_material_width', 'max_material_height', 'overlap_multiplier'
    ])
    
    # Effect configuration
    effect = SubElement(root, 'effect')
    object_type = SubElement(effect, 'object-type')
    object_type.text = 'all'
    
    effects_menu = SubElement(effect, 'effects-menu')
    submenu = SubElement(effects_menu, 'submenu')
    submenu.set('_name', 'CNC Tools')
    
    # Script configuration
    script = SubElement(root, 'script')
    command = SubElement(script, 'command')
    command.set('location', 'inx')
    command.set('interpreter', 'python')
    command.text = 'boxmaker.py'
    
    # Format and return XML
    rough_string = tostring(root, 'unicode')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def add_xml_section(parent_element, section_name: str, param_names: list):
    """Add a section with parameters to XML"""
    
    # Section label
    label = SubElement(parent_element, 'label')
    label.text = section_name
    
    # Separator
    SubElement(parent_element, 'separator')
    
    # Add parameters
    for param_name in param_names:
        param = next((p for p in PARAMETER_DEFINITIONS if p.name == param_name), None)
        if param and not param.hidden:
            add_xml_parameter(parent_element, param)
    
    # Spacer after section
    SubElement(parent_element, 'spacer')


def add_xml_parameter(parent_element, param: ParameterDefinition):
    """Add a single parameter to XML"""
    
    param_elem = SubElement(parent_element, 'param')
    param_elem.set('name', param.inkscape_name or param.name)
    param_elem.set('_gui-text', param.inkscape_gui_text or param.description)
    
    # Handle different parameter types
    if param.enum_type:
        param_elem.set('type', 'optiongroup')
        param_elem.set('appearance', 'combo')
        
        # Add options
        if param.choices:
            for choice in param.choices:
                option = SubElement(param_elem, '_option')
                option.set('value', str(int(choice)))
                option.text = get_enum_display_name(choice, param.enum_type)
                
    elif param.param_type == bool:
        param_elem.set('type', 'boolean')
        param_elem.text = str(param.default).lower()
        
    elif param.param_type == str:
        if param.choices:
            # String parameter with choices becomes optiongroup
            param_elem.set('type', 'optiongroup')
            param_elem.set('appearance', 'combo')
            
            # Add options
            for choice in param.choices:
                option = SubElement(param_elem, 'option')
                option.set('value', str(choice))
                option.text = str(choice)
        else:
            param_elem.set('type', 'string')
            if param.default:
                param_elem.text = str(param.default)
            
    elif param.param_type in (int, float):
        param_elem.set('type', 'int' if param.param_type == int else 'float')
        
        if param.precision is not None:
            param_elem.set('precision', str(param.precision))
        if param.min_val is not None:
            param_elem.set('min', str(param.min_val))
        if param.max_val is not None:
            param_elem.set('max', str(param.max_val))
            
        param_elem.text = str(param.default)


def extract_parameters_from_namespace(namespace) -> Dict[str, Any]:
    """
    Extract parameter values from argparse namespace or Inkscape options
    
    Args:
        namespace: argparse.Namespace or similar object with parameter attributes
        
    Returns:
        Dictionary mapping parameter names to values
    """
    result = {}
    
    for param in PARAMETER_DEFINITIONS:
        if hasattr(namespace, param.name):
            value = getattr(namespace, param.name)
            result[param.name] = value
            
    return result


def validate_all_parameters(param_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate all parameters in a dictionary
    
    Args:
        param_dict: Dictionary of parameter names to values
        
    Returns:
        Dictionary of validated parameters
        
    Raises:
        ValueError: If any parameter is invalid
    """
    from boxmaker_parameters import validate_parameter_value, get_parameter_by_name
    
    validated = {}
    
    for name, value in param_dict.items():
        param = get_parameter_by_name(name)
        if param:
            validated[name] = validate_parameter_value(param, value)
        else:
            # Unknown parameter, pass through
            validated[name] = value
            
    return validated

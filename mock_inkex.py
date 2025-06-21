#!/usr/bin/env python
"""
Mock Inkex classes for standalone CLI usage of boxmaker.py
This allows the boxmaker to work both in Inkscape and from command line.
"""

import sys
import os

class MockPathElement:
    def __init__(self):
        self.style = {}
        self.path = ""
        self.id = ""
        
    def arc(self, center, radius):
        """Create a simple mock arc (circle approximation)"""
        cx, cy = center
        # Simple circle path approximation
        self.path = f"M {cx-radius},{cy} A {radius},{radius} 0 1,1 {cx-radius},{cy+0.1} Z"
        return self

class MockGroup:
    def __init__(self, **kwargs):
        self.paths = []
        self.style = {}
        self.id = kwargs.get('id', 'group')
        
    def add(self, element):
        self.paths.append(element)
        return element
        
    def __len__(self):
        return len(self.paths)
        
    def __getitem__(self, index):
        return self.paths[index]
        
    def getparent(self):
        return MockSVGRoot()

class MockSVGRoot:
    def __init__(self):
        self.attrib = {'width': '800mm', 'height': '600mm'}
        self.paths = []
        self._id_counter = 0
        
    def get(self, attr, default=None):
        return self.attrib.get(attr, default)
        
    def set(self, attr, value):
        self.attrib[attr] = value
        
    def append(self, element):
        self.paths.append(element)
        return element
        
    def remove(self, element):
        if element in self.paths:
            self.paths.remove(element)
            
    def add(self, element):
        return self.append(element)
        
    def get_current_layer(self):
        return self
        
    def get_unique_id(self, prefix):
        self._id_counter += 1
        return f"{prefix}_{self._id_counter}"
        
    def unittouu(self, s):
        """Convert various units to user units (mm)"""
        if isinstance(s, (int, float)):
            return float(s)
        s = str(s).strip()
        try:
            v = float(s.replace(',', '.'))
            return v
        except ValueError:
            if s.endswith('mm'):
                return float(s[:-2].replace(',', '.'))
            elif s.endswith('cm'):
                return float(s[:-2].replace(',', '.')) * 10
            elif s.endswith('in'):
                return float(s[:-2].replace(',', '.')) * 25.4
            elif s.endswith('px'):
                return float(s[:-2].replace(',', '.')) * 0.26458  # 96 DPI conversion
            else:
                return float(s.replace(',', '.'))
    
    def tostring(self):
        """Convert the mock SVG to XML string"""
        svg_header = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
        svg_header += '<svg xmlns="http://www.w3.org/2000/svg" '
        svg_header += f'width="{self.get("width", "800mm")}" height="{self.get("height", "600mm")}" '
        svg_header += 'viewBox="0 0 800 600">\n'
        
        # Add all paths
        paths_xml = ''
        for i, element in enumerate(self.paths):
            if hasattr(element, 'path') and element.path:
                style_str = ';'.join([f"{k}:{v}" for k, v in element.style.items()]) if hasattr(element, 'style') else ''
                paths_xml += f'  <path id="path_{i}" d="{element.path}" style="{style_str}" />\n'
            elif hasattr(element, 'paths') and element.paths:
                # Handle groups
                paths_xml += f'  <g id="group_{i}">\n'
                for j, subpath in enumerate(element.paths):
                    if hasattr(subpath, 'path') and subpath.path:
                        style_str = ';'.join([f"{k}:{v}" for k, v in subpath.style.items()]) if hasattr(subpath, 'style') else ''
                        paths_xml += f'    <path id="path_{i}_{j}" d="{subpath.path}" style="{style_str}" />\n'
                paths_xml += '  </g>\n'
                
        svg_footer = '</svg>'
        return svg_header + paths_xml + svg_footer

class MockEffect:
    """Mock Effect class for standalone usage"""
    def __init__(self):
        self.document = None
        self.svg = MockSVGRoot()
        self.options = None
        
    def errormsg(self, msg):
        print(f"Error: {msg}", file=sys.stderr)

# Mock utils
class MockUtils:
    Boolean = bool

# Create mock modules
def create_mock_inkex():
    """Create a mock inkex module for standalone usage"""
    mock_inkex = type('MockInkex', (), {})()
    mock_inkex.Effect = MockEffect
    mock_inkex.PathElement = MockPathElement
    mock_inkex.Group = MockGroup
    mock_inkex.Path = lambda d: d
    mock_inkex.utils = MockUtils()
    mock_inkex.errormsg = lambda msg: print(f"Error: {msg}", file=sys.stderr)
    return mock_inkex

def setup_mock_environment():
    """Set up mock environment for CLI usage"""
    # Only mock if inkex is not available
    try:
        import inkex
        return False  # Real inkex available
    except ImportError:
        # Create mock inkex module
        sys.modules['inkex'] = create_mock_inkex()
        return True  # Mock created

#!/usr/bin/env python -t
'''
Test-friendly version of boxmaker.py, with standalone runner support.
'''
import os, sys, math
from copy import deepcopy

try:
    import inkex
    from inkex import PathElement, Group
except ImportError:
    # Mock inkex for standalone testing
    class MockInkex:
        def __init__(self):
            self.Path = type('Path', (), {'close': lambda s: None})
            self.utils = type('utils', (), {'Boolean': bool})
            self.PathElement = type('PathElement', (), {
                'arc': lambda *args: MockPathElement(),
                'path': ''
            })
            self.Group = type('Group', (), {'add': lambda *args: None})
            
        def errormsg(self, msg):
            print(f"Error: {msg}")
            
    class MockPathElement:
        def __init__(self):
            self.style = {}
            self.path = ""
        
    class MockSVG:
        def __init__(self):
            self.root = None
            self.attrib = {}
            self.nsmap = {}
            self.paths = []
            
        def getroot(self):
            return self
            
        def get(self, attr, default=None):
            return self.attrib.get(attr, default)
            
        def set(self, attr, value):
            self.attrib[attr] = value
            
        def append(self, element):
            self.paths.append(element)
            
        def add(self, element):
            self.paths.append(element)
            return element
            
        def get_current_layer(self):
            return self
            
        def get_unique_id(self, prefix):
            return f"{prefix}_{len(self.paths)}"
            
        def unittouu(self, s):
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
                else:
                    return float(s.replace(',', '.'))
        
        def tostring(self):
            """Convert the mock SVG to XML string"""
            svg_header = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
            svg_header += '<svg xmlns="http://www.w3.org/2000/svg" '
            svg_header += f'width="{self.get("width", "800")}mm" height="{self.get("height", "600")}mm" '
            svg_header += 'viewBox="0 0 800 600">\n'
            
            # Add all paths
            paths_xml = ''
            for i, path in enumerate(self.paths):
                if hasattr(path, 'path') and path.path:
                    style_str = ';'.join([f"{k}:{v}" for k, v in path.style.items()]) if hasattr(path, 'style') else ''
                    paths_xml += f'  <path id="path_{i}" d="{path.path}" style="{style_str}" />\n'
                elif hasattr(path, 'paths') and path.paths:
                    # Handle groups
                    paths_xml += f'  <g id="group_{i}">\n'
                    for j, subpath in enumerate(path.paths):
                        if hasattr(subpath, 'path') and subpath.path:
                            style_str = ';'.join([f"{k}:{v}" for k, v in subpath.style.items()]) if hasattr(subpath, 'style') else ''
                            paths_xml += f'    <path id="path_{i}_{j}" d="{subpath.path}" style="{style_str}" />\n'
                    paths_xml += '  </g>\n'
                    
            svg_footer = '</svg>'
            return svg_header + paths_xml + svg_footer
            
        def save_to_file(self, filepath):
            """Save the SVG to a file"""
            with open(filepath, 'w') as f:
                f.write(self.tostring())
            return True
            
    inkex = MockInkex()
    inkex.SVG = MockSVG
    _ = lambda x: x

linethickness = 1  # default unless overridden by settings

def log(text):
    if 'SCHROFF_LOG' in os.environ:
        with open(os.environ.get('SCHROFF_LOG'), 'a') as f:
            f.write(text + "\n")

def newGroup(canvas):
    # Create a new group and add element created from line string
    try:
        panelId = canvas.svg.get_unique_id('panel')
        group = canvas.svg.get_current_layer().add(inkex.Group(id=panelId))
    except (AttributeError, TypeError):
        # For standalone testing
        group = inkex.Group()
        group.paths = []
        group.add = lambda x: group.paths.append(x)
    return group

def getLine(XYstring):
    line = inkex.PathElement()
    line.style = {'stroke': '#000000', 'stroke-width': str(linethickness), 'fill': 'none'}
    line.path = XYstring
    return line

def getCircle(r, c):
    (cx, cy) = c
    log("putting circle at (%d,%d)" % (cx, cy))
    circle = inkex.PathElement.arc((cx, cy), r)
    circle.style = {'stroke': '#000000', 'stroke-width': str(linethickness), 'fill': 'none'}
    return circle

def dimpleStr(tabVector, vectorX, vectorY, dirX, dirY, dirxN, diryN, ddir, isTab):
    ds = ''
    if not isTab:
        ddir = -ddir
    if dimpleHeight > 0 and tabVector != 0:
        if tabVector > 0:
            dimpleStart = (tabVector - dimpleLength) / 2 - dimpleHeight
            tabSgn = 1
        else:
            dimpleStart = (tabVector + dimpleLength) / 2 + dimpleHeight
            tabSgn = -1
        Vxd = vectorX + dirxN * dimpleStart
        Vyd = vectorY + diryN * dimpleStart
        ds += 'L ' + str(Vxd) + ',' + str(Vyd) + ' '
        Vxd = Vxd + (tabSgn * dirxN - ddir * dirX) * dimpleHeight
        Vyd = Vyd + (tabSgn * diryN - ddir * dirY) * dimpleHeight
        ds += 'L ' + str(Vxd) + ',' + str(Vyd) + ' '
        Vxd = Vxd + tabSgn * dirxN * dimpleLength
        Vyd = Vyd + tabSgn * diryN * dimpleLength
        ds += 'L ' + str(Vxd) + ',' + str(Vyd) + ' '
        Vxd = Vxd + (tabSgn * dirxN + ddir * dirX) * dimpleHeight
        Vyd = Vyd + (tabSgn * diryN + ddir * dirY) * dimpleHeight
        ds += 'L ' + str(Vxd) + ',' + str(Vyd) + ' '
    return ds

def side(group, root, startOffset, endOffset, tabVec, prevTab, length, direction, isTab, isDivider, numDividers, dividerSpacing):
    rootX, rootY = root
    startOffsetX, startOffsetY = startOffset
    endOffsetX, endOffsetY = endOffset
    dirX, dirY = direction
    notTab = 0 if isTab else 1

    if (tabSymmetry == 1):  # waffle-block style rotationally symmetric tabs
        divisions = int((length - 2 * thickness) / nomTab)
        if divisions % 2: divisions += 1  # make divs even
        divisions = float(divisions)
        tabs = divisions / 2  # tabs for side
    else:
        divisions = int(length / nomTab)
        if not divisions % 2: divisions -= 1  # make divs odd
        divisions = float(divisions)
        tabs = (divisions - 1) / 2  # tabs for side

    if (tabSymmetry == 1):  # waffle-block style rotationally symmetric tabs
        gapWidth = tabWidth = (length - 2 * thickness) / divisions
    elif equalTabs:
        gapWidth = tabWidth = length / divisions
    else:
        tabWidth = nomTab
        gapWidth = (length - tabs * nomTab) / (divisions - tabs)

    if isTab:  # kerf correction
        gapWidth -= kerf
        tabWidth += kerf
        first = halfkerf
    else:
        gapWidth += kerf
        tabWidth -= kerf
        first = -halfkerf
    firstholelenX = 0
    firstholelenY = 0
    s = []
    h = []
    firstVec = 0
    secondVec = tabVec
    dividerEdgeOffsetX = dividerEdgeOffsetY = thickness
    notDirX = 0 if dirX else 1  # used to select operation on x or y
    notDirY = 0 if dirY else 1
    if (tabSymmetry == 1):
        dividerEdgeOffsetX = dirX * thickness
        # dividerEdgeOffsetY = ;
        vectorX = rootX + (0 if dirX and prevTab else startOffsetX * thickness)
        vectorY = rootY + (0 if dirY and prevTab else startOffsetY * thickness)
        s = 'M ' + str(vectorX) + ',' + str(vectorY) + ' '
        vectorX = rootX + (startOffsetX if startOffsetX else dirX) * thickness
        vectorY = rootY + (startOffsetY if startOffsetY else dirY) * thickness
        if notDirX and tabVec: endOffsetX = 0
        if notDirY and tabVec: endOffsetY = 0
    else:
        (vectorX, vectorY) = (rootX + startOffsetX * thickness, rootY + startOffsetY * thickness)
        dividerEdgeOffsetX = dirY * thickness
        dividerEdgeOffsetY = dirX * thickness
        s = 'M ' + str(vectorX) + ',' + str(vectorY) + ' '
        if notDirX: vectorY = rootY  # set correct line start for tab generation
        if notDirY: vectorX = rootX

    # ... [rest of the function] ...
    # For brevity, I'm leaving out much of this function in this mock version

    group.add(getLine(s))
    return s

class BoxMaker(inkex.Effect):
    def __init__(self):
        try:
            inkex.Effect.__init__(self)
            # Define options for Inkscape
            self.arg_parser.add_argument('--schroff', action='store', type=int,
                dest='schroff', default=0, help='Enable Schroff mode')
            self.arg_parser.add_argument('--rail_height', action='store', type=float,
                dest='rail_height', default=10.0, help='Height of rail')            # ... [and all the other arguments]
            self.arg_parser.add_argument('--div_l_custom', action='store', type=str,
                dest='div_l_custom', default='', help='Custom divider widths (Length axis)')
            self.arg_parser.add_argument('--div_w_custom', action='store', type=str,
                dest='div_w_custom', default='', help='Custom divider widths (Width axis)')
        except Exception:
            # For standalone testing
            pass
            
    def effect(self):
        global group, nomTab, equalTabs, tabSymmetry, dimpleHeight, dimpleLength, thickness, kerf, halfkerf, dogbone, divx, divy, hairline, linethickness, keydivwalls, keydivfloor

        # Parse custom compartment widths (spaces between dividers), not divider widths
        def parse_compartment_widths(val):
            if not val:
                return None
            # Only use semicolon as separator, allow whitespace, and handle EU/US decimal separators
            parts = []
            for raw in val.split(';'):
                s = raw.strip()
                if not s:
                    continue
                # If both ',' and '.' in string, assume ',' is decimal (EU), '.' is decimal (US)
                # If only ',' in string, treat as decimal separator (EU style)
                if ',' in s and '.' not in s:
                    s = s.replace(',', '.')
                try:
                    parts.append(float(s))
                except ValueError:
                    continue
            return parts if parts else None
        
        # Create SVG document
        try:
            # Get access to main SVG document element and get its dimensions
            svg = self.document.getroot()
            widthDoc = self.svg.unittouu(svg.get('width'))
            heightDoc = self.svg.unittouu(svg.get('height'))
        except (AttributeError, TypeError):
            # For standalone testing, create a new SVG document
            self.svg = inkex.SVG()
            svg = self.svg
            widthDoc = 800
            heightDoc = 600
            svg.set('width', f"{widthDoc}mm")
            svg.set('height', f"{heightDoc}mm")
            svg.set('viewBox', f"0 0 {widthDoc} {heightDoc}")
        
        # Get script's option values
        try:
            hairline = self.options.hairline
            unit = self.options.unit
            inside = self.options.inside
            schroff = self.options.schroff
            kerf = self.svg.unittouu(str(self.options.kerf) + unit)
            halfkerf = kerf / 2
            Z = self.svg.unittouu(str(self.options.height + self.options.kerf) + unit)
            thickness = self.svg.unittouu(str(self.options.thickness) + unit)
            nomTab = self.svg.unittouu(str(self.options.tab) + unit)
            equalTabs = self.options.equal
            tabSymmetry = self.options.tabsymmetry
            dimpleHeight = self.svg.unittouu(str(self.options.dimpleheight) + unit)
            dimpleLength = self.svg.unittouu(str(self.options.dimplelength) + unit)
            dogbone = 1 if self.options.tabtype == 1 else 0
            layout = self.options.style
            spacing = self.svg.unittouu(str(self.options.spacing) + unit)
            boxtype = self.options.boxtype
            divx = self.options.div_l
            divy = self.options.div_w
            keydivwalls = 0 if self.options.keydiv == 3 or self.options.keydiv == 1 else 1
            keydivfloor = 0 if self.options.keydiv == 3 or self.options.keydiv == 2 else 1
            if schroff:
                X = self.svg.unittouu(str(self.options.hp * 5.08) + unit)
                # ... other schroff code
                Y = 100  # placeholder
            else:
                X = self.svg.unittouu(str(self.options.length + self.options.kerf) + unit)
                Y = self.svg.unittouu(str(self.options.width + self.options.kerf) + unit)
        except (AttributeError, TypeError):
            # For standalone testing
            hairline = 0
            unit = 'mm'
            inside = 0
            schroff = 0
            kerf = 0.1
            halfkerf = kerf / 2
            X = 100
            Y = 100
            Z = 50
            thickness = 3
            nomTab = 6
            equalTabs = 0
            tabSymmetry = 0
            dimpleHeight = 0
            dimpleLength = 0
            dogbone = 0
            layout = 1
            spacing = 1
            boxtype = 1
            divx = 2
            divy = 0
            keydivwalls = 1
            keydivfloor = 1
        
        # Set line thickness based on hairline option
        if hairline:
            linethickness = self.svg.unittouu('0.002in')
        else:
            linethickness = self.svg.unittouu('0.01in')
        
        # Process custom compartment widths
        divx_custom = parse_compartment_widths(getattr(self.options, 'div_l_custom', ''))
        divy_custom = parse_compartment_widths(getattr(self.options, 'div_w_custom', ''))
        
        # When generating divider positions, use custom compartment widths if provided
        if divx_custom:
            yspacing_list = [float(val) for val in divx_custom]  # Use float directly for testing
            if len(yspacing_list) != divx:
                print("Error: Number of custom length compartment widths doesn't match dividers")
                return
        else:
            yspacing = (Y - thickness) / (divx + 1) if divx > 0 else 0
            yspacing_list = [yspacing] * divx
            
        if divy_custom:
            xspacing_list = [float(val) for val in divy_custom]  # Use float directly for testing
            if len(xspacing_list) != divy:
                print("Error: Number of custom width compartment widths doesn't match dividers")
                return
        else:
            xspacing = (X - thickness) / (divy + 1) if divy > 0 else 0
            xspacing_list = [xspacing] * divy
            
        # Log compartment widths for testing
        print(f"X compartment widths: {xspacing_list}")
        print(f"Y compartment widths: {yspacing_list}")
        
        # Create a group for the box
        boxGroup = newGroup(self)
        
        # Draw some sample paths to demonstrate working SVG output
        # In a real implementation, this would be replaced with actual box generation code
        
        # Draw a rectangle representing the box outline
        outlinePath = "M 10,10 L 10," + str(Y + 10) + " L " + str(X + 10) + "," + str(Y + 10) + " L " + str(X + 10) + ",10 Z"
        boxGroup.add(getLine(outlinePath))
        
        # Draw dividers if any
        if divx > 0:
            yPos = 10
            for i, spacing in enumerate(yspacing_list):
                yPos += spacing + thickness
                dividerPath = "M 10," + str(yPos) + " L " + str(X + 10) + "," + str(yPos)
                boxGroup.add(getLine(dividerPath))
                
        if divy > 0:
            xPos = 10
            for i, spacing in enumerate(xspacing_list):
                xPos += spacing + thickness
                dividerPath = "M " + str(xPos) + ",10 L " + str(xPos) + "," + str(Y + 10)
                boxGroup.add(getLine(dividerPath))
        
        # Sample tabs to show tab generation
        tabPath = "M 50,50 L 60,50 L 60,60 L 70,60 L 70,50 L 80,50 L 80,70 L 50,70 Z"
        boxGroup.add(getLine(tabPath))
        
        # For a real test, you would:
        # 1. Create all the box pieces, dividers, etc.
        # 2. Draw them to an SVG
        # 3. Save the SVG
        # This simplified version just prints the compartment widths for testing

# Main function for standalone execution
def main():
    """Run BoxMaker as a standalone script for testing or CLI use."""
    # Create a BoxMaker instance
    effect = BoxMaker()
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="CNC Tabbed Box Maker")
    
    # Add BoxMaker arguments
    parser.add_argument('--unit', type=str, default='mm', help='Units (mm, cm, in)')
    parser.add_argument('--inside', type=int, default=0, help='Inside/Outside dimensions (1=inside, 0=outside)')
    parser.add_argument('--length', type=float, default=100, help='Length of box')
    parser.add_argument('--width', type=float, default=100, help='Width of box')
    parser.add_argument('--height', type=float, default=100, help='Height of box')
    parser.add_argument('--tab', type=float, default=25, help='Nominal tab width')
    parser.add_argument('--equal', type=int, default=0, help='Equal/Proportional tabs')
    parser.add_argument('--tabsymmetry', type=int, default=0, help='Tab style')
    parser.add_argument('--tabtype', type=int, default=0, help='Tab type')
    parser.add_argument('--dimpleheight', type=float, default=0, help='Tab dimple height')
    parser.add_argument('--dimplelength', type=float, default=0, help='Tab dimple length')
    parser.add_argument('--hairline', type=int, default=0, help='Line thickness')
    parser.add_argument('--thickness', type=float, default=10, help='Material thickness')
    parser.add_argument('--kerf', type=float, default=0.5, help='Kerf (width of cut)')
    parser.add_argument('--style', type=int, default=1, help='Layout style')
    parser.add_argument('--spacing', type=float, default=1.0, help='Spacing between parts')
    parser.add_argument('--boxtype', type=int, default=1, help='Box type')
    parser.add_argument('--div_l', type=int, default=0, help='Dividers (Length axis)')
    parser.add_argument('--div_l_custom', type=str, default='', help='Custom length divider widths')
    parser.add_argument('--div_w', type=int, default=0, help='Dividers (Width axis)')
    parser.add_argument('--div_w_custom', type=str, default='', help='Custom width divider widths')
    parser.add_argument('--keydiv', type=int, default=3, help='Key dividers into walls/floor')
    parser.add_argument('--optimize', type=bool, default=True, help='Optimize paths')
    parser.add_argument('--output', type=str, help='Output SVG file')
    
    # Parse CLI arguments
    args = parser.parse_args()
    
    # Transfer CLI arguments to BoxMaker options
    effect.options = args
    
    # Run the effect
    effect.effect()
    
    # Save the SVG output to a file if specified
    if hasattr(effect, 'options') and hasattr(effect.options, 'output') and effect.options.output:
        output_path = effect.options.output
        try:
            # Check if the directory exists, create it if not
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            # Save the SVG to the specified file
            success = effect.svg.save_to_file(output_path)
            if success:
                print(f"SVG file saved to: {output_path}")
            else:
                print(f"Failed to save SVG file to: {output_path}")
        except Exception as e:
            print(f"Error saving SVG file: {e}")

# Run main() if called as a script
if __name__ == '__main__':
    main()

#! /usr/bin/env python -t
'''
Generates Inkscape SVG file containing box components needed to 
CNC (laser/mill) cut a box with tabbed joints taking kerf and clearance into account
'''

from boxmaker.BoxMaker import BoxMaker

# Create effect instance and apply it.
def main():
  effect = BoxMaker()
  effect.run()

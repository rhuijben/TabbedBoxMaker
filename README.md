# TabbedBoxMaker: A free Inkscape extension for generating tab-jointed box patterns

[![CI - Test and Validate BoxMaker](https://github.com/rhuijben/TabbedBoxMaker/actions/workflows/ci.yml/badge.svg)](https://github.com/rhuijben/TabbedBoxMaker/actions/workflows/ci.yml)

_version 2.0 - 21 Jun 2025_

Original box maker by Elliot White (formerly of twot.eu, domain name now squatted)

Heavily modified by [Paul Hutchison](https://github.com/paulh-rnd)

Refactored for testability and CLI support by [Bert Huijben](https://github.com/rhuijben)

## What's New in Version 2.0

### ✨ New Features
- **🚀 CLI Support**: Generate box SVGs from command line without Inkscape
- **🎯 Custom Compartment Sizes**: Configure exact compartment dimensions instead of even spacing
- **🧪 Comprehensive Testing**: Automated test suite with 13 test scenarios
- **🔧 Same Inkscape Experience**: Identical behavior when used as extension
- **⚡ Continuous Integration**: Automated testing on every commit and PR
- **📊 Cross-Platform**: Tested on Ubuntu, Windows, and macOS
- **🛡️ Robust Validation**: Input validation with helpful error messages

### 🔧 Technical Improvements
- **Modular Architecture**: Core logic separated for testability
- **Error Handling**: Proper validation and clear error messages
- **Code Quality**: Clean, maintainable Python code with documentation
- **Automated Examples**: CLI examples that run automatically in CI

## About
 This tool is designed to simplify the process of making practical boxes from sheet material using almost any kind of CNC cutter (laser, plasma, water jet or mill). The box edges are "finger-jointed" or "tab-jointed", and may include press-fit dimples, internal dividers, dogbone corners (for endmill cutting), and more.

 The tool works by generating each side of the box with the tab and edge sizes corrected to account for the kerf (width of cut). Each box side is composed of a group of individual lines that make up each edge of the face, as well as any other cutouts for dividers. It is recommended that you join adjacent lines in your CNC software to cut efficiently.

 An additional extension which uses the same TabbedBoxMaker generator script is also included: Schroff Box Maker. The Schroff addition was created by [John Slee](https://github.com/jsleeio). If you create further derivative box generators, feel free to send me a pull request!

## Usage

### As Inkscape Extension (Original Usage)
Copy `boxmaker.py`, `boxmaker_core.py`, `boxmaker_constants.py`, `boxmaker_exceptions.py`, and `boxmaker.inx` to your Inkscape extensions folder. Use exactly as before - no changes to the interface or behavior.

### As CLI Tool (New!)
```bash
# Basic box (100x80x50mm, 3mm material, laser cutting)
python boxmaker.py --length 100 --width 80 --height 50 --thickness 3 --kerf 0.1 --output my_box.svg

# CNC milling with dogbone cuts
python boxmaker.py --length 100 --width 80 --height 50 --thickness 3 --tabtype 1 --output cnc_box.svg

# Box with dividers (2 length, 1 width)
python boxmaker.py --length 120 --width 100 --height 60 --div-l 2 --div-w 1 --output box_with_dividers.svg

# Custom compartment sizes (210mm wide with 63mm, 63mm, 50mm compartments + remainder)
python boxmaker.py --length 210 --width 150 --height 50 --div-l 3 --div-l-sizes "63; 63.0; 50" --inside --output custom_compartments.svg

# Thick material (6mm plywood)
python boxmaker.py --length 150 --width 100 --height 75 --thickness 6 --kerf 0.2 --tab 25 --output thick_box.svg

# Inside dimensions box (interior 100x80x50)
python boxmaker.py --length 100 --width 80 --height 50 --thickness 3 --inside --output inside_box.svg
```

### CLI Options
```
--length FLOAT      Length of box (mm)
--width FLOAT       Width of box (mm) 
--height FLOAT      Height of box (mm)
--thickness FLOAT   Material thickness (mm)
--kerf FLOAT        Kerf width (mm)
--tab FLOAT         Tab width (mm)
--style {1,2,3}     Layout style (1=diagramatic, 2=3-piece, 3=compact)
--boxtype {1-6}     Box type (1=full, 2=no top, etc.)
--tabtype {0,1}     Tab type (0=laser, 1=cnc/dogbone)
--div-l INT         Dividers along length
--div-w INT         Dividers along width
--div-l-sizes STR   Custom compartment sizes along length (e.g. "63; 63.0; 50")
--div-w-sizes STR   Custom compartment sizes along width (e.g. "70,5; 80")
--inside            Dimensions are inside measurements
--output FILE       Output SVG file
```

## Testing and Quality Assurance

This project includes comprehensive automated testing:

### Run Tests Locally
```bash
# Run the full test suite (11 tests)
python test_boxmaker.py

# Run CLI examples (6 examples)
python cli_examples.py

# Run pre-commit validation
python pre_commit_test.py
```

### Continuous Integration
- **Automated Testing**: Full test suite runs on Python 3.11 and 3.12
- **Cross-Platform**: Tested on Ubuntu, Windows, and macOS  
- **SVG Validation**: All generated files validated for correctness
- **Example Generation**: CLI examples run automatically to ensure they work

### Test Coverage
- ✅ Basic box generation (multiple sizes)
- ✅ Boxes with dividers (various configurations)
- ✅ Different material thicknesses (3mm, 6mm)
- ✅ Laser vs CNC cutting modes
- ✅ Layout styles and box types
- ✅ Inside vs outside dimensions
- ✅ Error handling and validation
- ✅ Edge cases (large boxes, thin/thick tabs)

## Use - Regular Tabbed Boxes (Inkscape Extension)

The interface is pretty self explanatory, the extension is 'Tabbed Box Maker' in the 'CNC Tools' group

Parameters in order of appearance:

* **Units** - unit of measurement used for drawing

* **Box Dimensions: Inside/Outside** - whether the box dimensions are internal or external measurements

* **Length / Width / Height** - the box dimensions

* **Tab Width: Fixed/Proportional** - for fixed the tab width is the value given in the Tab Width, for proportional the side of a piece is divided equally into tabs and 'spaces' with the tabs size greater or equal to the Tab Width setting

* **Minimum/Preferred Tab Width** - the size of the tabs used to hold the pieces together

* **Material Thickness** - as it says
 
* **Kerf** - this is the diameter/width of the cut. Typical laser cutters will be between 0.1 - 0.25mm, for CNC mills, this will be your end mill diameter. A larger kerf will assume more material is removed, hence joints will be tighter. Smaller or zero kerf will result in looser joints.

* **Layout** - controls how the pieces are laid out in the drawing

* **Box Type** - this allows you to choose how many jointed sides you want. Options are:
    * Fully enclosed (6 sides)
    * One side open (LxW) - one of the Length x Width panels will be omitted
    * Two sides open (LxW and LxH) - two adjacent panels will be omitted
    * Three sides open (LxW, LxH, HxW) - one of each panel omitted
    * Opposite ends open (LxW) - an open-ended "tube" with the LxW panels omitted
    * Two panels only (LxW and LxH) - two panels with a single joint down the Length axis
 			
* **Dividers (Length axis)** - use this to create additional LxH panels that mount inside the box along the length axis and have finger joints into the side panels and slots for Width dividers to slot into
				
* **Dividers (Width axis)** - use this to create additional WxH panels that mount inside the box along the width axis and have finger joints into the side panels and slots for Length dividers to slot into

* **Length Compartment Sizes** - 🆕 **NEW!** Custom sizes for compartments along the length axis. Enter sizes separated by semicolons (e.g. "63,0; 63.0; 50"). Both comma and dot decimal separators are supported. Remaining space is divided evenly if fewer sizes than dividers are specified.

* **Width Compartment Sizes** - 🆕 **NEW!** Custom sizes for compartments along the width axis. Same format as Length Compartment Sizes.
						 
* **Key the dividers into** - this allows you to choose if/how the dividers are keyed into the sides of the box. Options are:
	* None - no keying, dividers will be free to slide in and out
	* Walls - dividers will only be keyed into the side walls of the box
	* Floor/Ceiling - dividers will only be keyed into the top/bottom of the box
	* All Sides
				
* **Space Between Parts** - how far apart the pieces are in the drawing produced

## Technical Architecture

### Files Structure
- **`boxmaker.py`** - Main file (Inkscape extension + CLI)
- **`boxmaker_core.py`** - Core box generation logic (no Inkscape dependencies)
- **`boxmaker_constants.py`** - Enums and constants for maintainability
- **`boxmaker_exceptions.py`** - Custom exceptions for clear error handling
- **`boxmaker.inx`** - Inkscape interface definition (unchanged)
- **`test_boxmaker.py`** - Comprehensive test suite
- **`cli_examples.py`** - CLI usage examples
- **`test_assets/`** - Reference examples (tracked in git)
- **`test_results/`** - Test outputs (gitignored, regenerated on each test)

### Key Benefits

#### For Users
- **Same Inkscape experience** - No changes to existing workflow
- **CLI access** - Generate boxes in scripts, automation, web apps
- **Validation** - Comprehensive testing ensures reliability
- **Better error messages** - Clear feedback when inputs are invalid

#### For Developers  
- **Testable** - Core logic separated from UI
- **Modular** - Easy to extend or integrate
- **Maintainable** - Clear separation of concerns
- **CI/CD Ready** - Automated testing on every change

## Compatibility

- ✅ **Inkscape 1.0+** - Full compatibility maintained
- ✅ **Python 3.11+** - Works standalone or in Inkscape
- ✅ **Original interface** - All existing .inx options preserved
- ✅ **Same output** - Identical SVG generation
- ✅ **Cross-platform** - Windows, macOS, Linux

## Future Enhancements

The modular structure makes it easy to add:
- Web API endpoints
- Batch processing
- Custom material presets
- Advanced optimization algorithms
- Export to other formats

---

*The core functionality remains unchanged - this refactor just makes it more accessible and testable while maintaining 100% Inkscape compatibility.*

## License and Copyright

This software is licensed under the **GNU General Public License v2.0**.

**Copyright (C) 2025 Bert Huijben**

Based on original work by:
- Elliot White (original box maker)
- Paul Hutchison (significant modifications and improvements)

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

---

### Acknowledgments

The original tool was created by Elliot White. Significant improvements and modifications were made by [Paul Hutchison](https://github.com/paulh-rnd). If you'd like to support Paul's work, donations are gratefully received: [![](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.me/SparkItUp)

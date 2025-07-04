# TabbedBoxMaker: A free Inkscape extension for generating tab-jointed box patterns

[![CI - Test and Validate BoxMaker](https://github.com/rhuijben/TabbedBoxMaker/actions/workfl## Project Structure

```
TabbedBox2/
├── boxmaker.py              # CLI entry point
├── boxmaker_inkscape.py     # Inkscape extension entry point  
├── boxmaker.inx             # Inkscape interface definition
├── schroffmaker.inx         # Schroff rack box interface
├── src/boxmaker/            # Core library
│   ├── __init__.py          # Package initialization
│   ├── boxmaker_core.py     # Core box generation logic
│   ├── boxmaker_constants.py # Enums and constants
│   ├── boxmaker_exceptions.py # Custom exceptions
│   ├── boxmaker_parameters.py # Parameter definitions
│   └── boxmaker_config.py   # Configuration utilities
├── tests/                   # Test suite
├── scripts/                 # Demo and analysis scripts
├── docs/                    # Documentation
├── test_assets/            # Reference examples (tracked in git)
├── test_results/           # Test outputs (gitignored)
└── README.md
```

### Key Files

- **`boxmaker.py`** - Clean CLI interface with comprehensive help and examples
- **`boxmaker_inkscape.py`** - Dedicated Inkscape extension (no dual-mode complexity)
- **`src/boxmaker/`** - Core library package with proper imports
- **`tests/`** - Comprehensive test suite for CI/CD
- **`boxmaker.inx`** - Inkscape interface definition (references boxmaker_inkscape.py)l/badge.svg)](https://github.com/rhuijben/TabbedBoxMaker/actions/workflows/ci.yml)

_version 2.0 - 21 Jun 2025_

Original box maker by Elliot White (formerly of twot.eu, domain name squatted)

Heavily modified by [Paul Hutchison](https://github.com/paulh-rnd)

Refactored and modernized by [Bert Huijben](https://github.com/rhuijben)

## What's New in Version 2.0

### ✨ Major Improvements
- **🎯 Custom Compartment Control**: Specify exact compartment sizes with strict validation (no auto-fitting when all sizes provided)
- **🧪 Production-Ready Code**: Comprehensive test suite with design validation and error testing
- **🔧 Clean Architecture**: Separated design logic from manufacturing concerns for maintainability
- **⚡ Robust Validation**: Clear error messages guide users to correct inputs
- **📊 Modern Codebase**: Enum-based constants, type hints, and comprehensive documentation

### 🔧 Technical Excellence
- **Design-First Architecture**: Pure geometry separated from kerf compensation
- **Strict Compartment Validation**: Prevents user errors by requiring exact size matching
- **Comprehensive Testing**: 19 test scenarios covering all features and edge cases
- **Code Quality**: Clean, documented, maintainable Python with modern patterns
- **CI/CD Pipeline**: Automated testing ensures reliability

### 🚫 Removed Development Artifacts
- Cleaned up temporary test files and development tools
- Streamlined to essential core functionality
- Focused test suite on production scenarios

## About
 This tool is designed to simplify the process of making practical boxes from sheet material using almost any kind of CNC cutter (laser, plasma, water jet or mill). The box edges are "finger-jointed" or "tab-jointed", and may include press-fit dimples, internal dividers, dogbone corners (for endmill cutting), and more.

 The tool works by generating each side of the box with the tab and edge sizes corrected to account for the kerf (width of cut). Each box side is composed of a group of individual lines that make up each edge of the face, as well as any other cutouts for dividers. It is recommended that you join adjacent lines in your CNC software to cut efficiently.

## Key Design Decisions

### Custom Compartment Validation
- **All sizes provided**: Strict validation - must sum exactly to available space (no auto-fitting)
- **Partial sizes provided**: Auto-fit remaining compartments to fill space  
- **No sizes provided**: Divide space evenly among compartments

This prevents creating incorrect boxes by ensuring user intent is preserved.

### Kerf Compensation Strategy
- Design dimensions are pure geometry (kerf-free)
- Half-kerf expansion applied to all external piece edges
- Tab/slot dimensions properly compensated for tight fit
- Maintains design intent while ensuring proper assembly

## Usage

### As Inkscape Extension (Unchanged)
Copy `boxmaker.py`, `boxmaker_core.py`, `boxmaker_constants.py`, `boxmaker_exceptions.py`, `box_design.py`, and `boxmaker.inx` to your Inkscape extensions folder. Interface and behavior unchanged.
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

### Test Suite Components
- **Core functionality tests**: `test_boxmaker.py` (20 comprehensive tests)
- **Design system tests**: `test_design.py` (6 design validation tests)  
- **Updated core tests**: `test_updated_core.py` (core architecture tests)
- **CLI integration tests**: `test_cli_integration.py` (8 practical examples)

### Run Tests Locally
```bash
# Run the main test suite (20 comprehensive tests)
python test_boxmaker.py

# Run design system tests  
python test_design.py

# Run CLI integration tests (8 practical examples)
python test_cli_integration.py

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

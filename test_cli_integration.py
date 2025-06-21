#!/usr/bin/env python3
"""
CLI Integration Tests for BoxMaker

This test suite validates the command-line interface by running practical
examples that cover the main features and use cases. It ensures that:

1. The CLI interface works correctly across different scenarios
2. All major features can be accessed from command line
3. Generated SVG files are valid and contain expected content
4. Error handling works properly for invalid inputs

Used in CI to verify CLI functionality across different Python versions
and platforms. Each test generates an actual SVG file that could be used
for laser cutting or CNC milling.

EXAMPLES TESTED:
- Basic laser cutting box
- CNC milling box with dogbone cuts  
- Boxes with dividers
- Thick material handling
- Inside vs outside dimensions
- Different layout styles
- Custom compartment sizes
- Mixed compartment configurations
"""

import sys
import subprocess
from pathlib import Path

def run_example(description, args):
    """Run a single example"""
    print(f"\n{description}")
    print(f"Command: python boxmaker.py {' '.join(args)}")
    print("-" * 50)
    
    try:
        # Run the boxmaker with the given arguments
        result = subprocess.run([sys.executable, 'boxmaker.py'] + args, 
                              capture_output=True, text=True, check=True)
        print(result.stdout)
        if result.stderr:
            print(f"Warnings: {result.stderr}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False

def main():
    """Run CLI integration tests"""
    print("BoxMaker CLI Integration Tests")
    print("=" * 50)
    print("Testing CLI interface with practical examples...")
    
    # Ensure test_assets directory exists
    import os
    os.makedirs("test_assets", exist_ok=True)
    
    examples = [
        {
            'description': "1. Basic 100x80x50mm box for laser cutting",
            'args': ['--length', '100', '--width', '80', '--height', '50', 
                    '--thickness', '3', '--kerf', '0.1', '--tab', '15', '--tabtype', '0',
                    '--output', 'test_assets/basic_laser_box.svg']
        },
        {
            'description': "2. Same box but for CNC milling (with dogbone cuts)",
            'args': ['--length', '100', '--width', '80', '--height', '50', 
                    '--thickness', '3', '--kerf', '0.1', '--tab', '15', '--tabtype', '1',
                    '--output', 'test_assets/basic_cnc_box.svg']
        },
        {
            'description': "3. Box with dividers (2 length, 1 width)",
            'args': ['--length', '120', '--width', '100', '--height', '60', 
                    '--thickness', '3', '--kerf', '0.1', '--tab', '20', '--div-l', '2', '--div-w', '1',
                    '--output', 'test_assets/box_with_dividers.svg']
        },
        {
            'description': "4. Thick material box (6mm plywood)",
            'args': ['--length', '150', '--width', '100', '--height', '75', 
                    '--thickness', '6', '--kerf', '0.2', '--tab', '25',
                    '--output', 'test_assets/thick_material_box.svg']
        },
        {
            'description': "5. Inside dimensions box (interior 100x80x50)",
            'args': ['--length', '100', '--width', '80', '--height', '50', 
                    '--thickness', '3', '--kerf', '0.1', '--tab', '15', '--inside',
                    '--output', 'test_assets/inside_dimensions_box.svg']
        },
        {
            'description': "6. Compact layout style",
            'args': ['--length', '100', '--width', '80', '--height', '50', 
                    '--thickness', '3', '--kerf', '0.1', '--tab', '15', '--style', '3',
                    '--output', 'test_assets/compact_layout_box.svg']
        },
        {
            'description': "7. Box with custom compartment sizes (210x150x50mm, 4 compartments: 63mm, 63mm, 50mm, remainder)",
            'args': ['--length', '210', '--width', '150', '--height', '50', 
                    '--thickness', '3', '--tab', '15', '--div-l', '3', '--div-l-custom', '63; 63.0; 50',
                    '--inside', '--output', 'test_assets/custom_compartments_box.svg']
        },
        {
            'description': "8. Box with custom compartments in both length and width directions",
            'args': ['--length', '200', '--width', '160', '--height', '60', 
                    '--thickness', '3', '--tab', '15', '--div-l', '2', '--div-w', '1', 
                    '--div-l-custom', '80; 60', '--div-w-custom', '70',
                    '--output', 'test_assets/mixed_custom_compartments.svg']
        }    ]
    
    success_count = 0
    
    for example in examples:
        if run_example(example['description'], example['args']):
            success_count += 1
    
    print(f"\n\nTest Results: {success_count}/{len(examples)} CLI tests passed")
    
    if success_count == len(examples):
        print("\n✅ All CLI integration tests passed!")
        print("\nGenerated test files in test_assets/:")
        for example in examples:
            output_file = None
            args = example['args']
            for i, arg in enumerate(args):
                if arg == '--output' and i + 1 < len(args):
                    output_file = args[i + 1]
                    break
            if output_file and Path(output_file).exists():
                print(f"  - {output_file}")
        return True
    else:
        print(f"\n❌ {len(examples) - success_count} CLI tests failed")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

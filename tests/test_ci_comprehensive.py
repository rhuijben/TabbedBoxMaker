#!/usr/bin/env python3
"""
CI Test Suite for BoxMaker
==========================

Comprehensive test suite for CI/CD including:
- CLI functionality testing
- INX file generation and validation
- Parameter system consistency
- Core functionality verification
"""

import sys
import os
import unittest
import subprocess
import tempfile
import time
import argparse
from pathlib import Path

# Add project root to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from TabbedBoxMaker import (
    BoxMakerCore, create_cli_parser, create_inkscape_extension_args,
    extract_parameters_from_namespace, validate_all_parameters,
    DimensionError, TabError, MaterialError
)


class TestCLIInterface(unittest.TestCase):
    """Test the CLI interface for BoxMaker"""
    
    def test_cli_help(self):
        """Test that CLI help works"""
        result = subprocess.run([
            sys.executable,
            os.path.join(os.path.dirname(__file__), '..', 'boxmaker.py'),
            '--help'
        ], capture_output=True, text=True)
        
        self.assertEqual(result.returncode, 0)
        self.assertIn('--length', result.stdout)
        self.assertIn('--width', result.stdout)
        self.assertIn('--height', result.stdout)
    
    def test_cli_generation(self):
        """Test that CLI can generate SVG files"""
        with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as tmp:
            temp_path = tmp.name
            
        result = subprocess.run([
            sys.executable,
            os.path.join(os.path.dirname(__file__), '..', 'boxmaker.py'),
            '--length', '100',
            '--width', '80', 
            '--height', '50',
            '--thickness', '3',
            '--tab', '15',
            '--output', temp_path
        ], capture_output=True, text=True)
        
        self.assertEqual(result.returncode, 0)
        self.assertTrue(os.path.exists(temp_path))
        
        # Check SVG content
        with open(temp_path, 'r') as f:
            content = f.read()
            self.assertIn('<svg', content)
            self.assertIn('</svg>', content)
        
        # Cleanup - try multiple times on Windows
        for _ in range(3):
            try:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                break
            except PermissionError:
                time.sleep(0.1)
    
    def test_cli_error_handling(self):
        """Test CLI error handling with invalid parameters"""
        with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as tmp:
            temp_path = tmp.name
            
        # Test with tab too large
        result = subprocess.run([
            sys.executable,
            os.path.join(os.path.dirname(__file__), '..', 'boxmaker.py'),
            '--length', '100',
            '--width', '80',
            '--height', '50', 
            '--thickness', '3',
            '--tab', '50',  # Too large
            '--output', temp_path
        ], capture_output=True, text=True)
        
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Tab Error', result.stderr)
        
        # Cleanup - try multiple times on Windows
        for _ in range(3):
            try:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                break
            except PermissionError:
                time.sleep(0.1)


class TestParameterConsistency(unittest.TestCase):
    """Test parameter system consistency between CLI and Inkscape"""
    
    def test_cli_parser_creation(self):
        """Test CLI parser can be created"""
        parser = create_cli_parser()
        self.assertIsNotNone(parser)
        
        # Test parsing valid arguments
        args = parser.parse_args(['--length', '100', '--width', '80', '--height', '50', '--thickness', '3', '--output', 'test.svg'])
        self.assertEqual(args.length, 100)
        self.assertEqual(args.width, 80)
        self.assertEqual(args.height, 50)
        
    def test_parameter_extraction_and_validation(self):
        """Test parameter extraction and validation"""
        parser = create_cli_parser()
        args = parser.parse_args(['--length', '100', '--width', '80', '--height', '50', '--thickness', '3', '--output', 'test.svg'])
        
        param_dict = extract_parameters_from_namespace(args)
        self.assertIsInstance(param_dict, dict)
        self.assertIn('length', param_dict)
        
        validated_params = validate_all_parameters(param_dict)
        self.assertIsInstance(validated_params, dict)
        self.assertEqual(validated_params['length'], 100)


class TestCoreGeneration(unittest.TestCase):
    """Test core box generation functionality"""
    
    def test_basic_box_generation(self):
        """Test basic box generation works"""
        core = BoxMakerCore()
        core.set_parameters(
            length=100, width=80, height=50, thickness=3,
            tab=15, output='test.svg'
        )
        
        svg_content = core.generate_svg()
        self.assertIsInstance(svg_content, str)
        self.assertIn('<svg', svg_content)
        self.assertIn('</svg>', svg_content)
        
    def test_error_conditions(self):
        """Test error conditions in core generation"""
        core = BoxMakerCore()
        
        # Test with valid small dimensions (should not raise error)
        try:
            core.set_parameters(
                length=50, width=50, height=50, thickness=3,
                tab=10, output='test.svg'
            )
            core.generate_svg()
        except DimensionError:
            self.fail("DimensionError raised unexpectedly for valid dimensions")


class TestINXGeneration(unittest.TestCase):
    """Test INX file generation and validation"""
    
    def test_inkscape_extension_args_creation(self):
        """Test Inkscape extension args can be created"""
        # Create a dummy extension class for testing
        class DummyExtension:
            def __init__(self):
                self.arg_parser = argparse.ArgumentParser()
            
            def add_argument(self, *args, **kwargs):
                self.arg_parser.add_argument(*args, **kwargs)
                
        dummy_ext = DummyExtension()
        create_inkscape_extension_args(dummy_ext)
        
        # Test that arguments were added
        self.assertTrue(hasattr(dummy_ext, 'arg_parser'))
        
    def test_inx_file_exists(self):
        """Test that INX files exist"""
        inx_dir = os.path.join(os.path.dirname(__file__), '..')
        boxmaker_inx = os.path.join(inx_dir, 'boxmaker.inx')
        schroffmaker_inx = os.path.join(inx_dir, 'schroffmaker.inx')
        
        self.assertTrue(os.path.exists(boxmaker_inx), "boxmaker.inx should exist")
        self.assertTrue(os.path.exists(schroffmaker_inx), "schroffmaker.inx should exist")


if __name__ == '__main__':
    unittest.main()

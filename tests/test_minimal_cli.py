#!/usr/bin/env python3

import sys
print("Starting test...")

try:
    from boxmaker_config import create_cli_parser
    print("Import successful")
    
    parser = create_cli_parser()
    print("Parser created")
    
    # Test with minimal args
    sys.argv = ['test', '--length', '100', '--width', '80', '--height', '50', '--thickness', '3', '--output', 'test.svg']
    args = parser.parse_args()
    print(f"Args parsed: {args}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

#!/usr/bin/env python3
"""
Test CLI functionality with unified parameter system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from boxmaker_config import create_cli_parser
from boxmaker_core import BoxMakerCore
from boxmaker_config import extract_parameters_from_namespace, validate_all_parameters

def main():
    """Test CLI function"""
    parser = create_cli_parser()
    args = parser.parse_args()
    
    print("CLI parameters extracted:")
    param_dict = extract_parameters_from_namespace(args)
    for key, value in param_dict.items():
        print(f"  {key}: {value}")
    
    print("\nValidated parameters:")
    validated_params = validate_all_parameters(param_dict)
    for key, value in validated_params.items():
        print(f"  {key}: {value}")

if __name__ == '__main__':
    main()

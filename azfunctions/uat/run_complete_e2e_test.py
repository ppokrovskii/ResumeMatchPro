#!/usr/bin/env python
"""
Run the complete end-to-end UAT test that includes CV upload, JD upload, and matching.
"""
import os
import sys
import logging
import argparse
import pytest
from pathlib import Path

# Add the correct paths to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
azfunctions_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(azfunctions_dir)
sys.path.insert(0, root_dir)
sys.path.insert(0, azfunctions_dir)
sys.path.insert(0, current_dir)

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger("run_complete_e2e_test")
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run the complete end-to-end UAT test")
    parser.add_argument(
        "--function-url",
        default="http://localhost:7071/api",
        help="Base URL for function app endpoints (default: http://localhost:7071/api)"
    )
    args = parser.parse_args()
    
    # Set the FUNCTION_API_BASE_URL environment variable
    os.environ["FUNCTION_API_BASE_URL"] = args.function_url
    
    logger.info(f"Starting complete E2E test with API base URL: {args.function_url}")
    
    # Run the test using pytest
    test_result = pytest.main(["-xvs", "test_file_processing_e2e.py::test_complete_e2e_flow_with_matching"])
    
    if test_result == 0:
        logger.info("Complete E2E test completed successfully!")
        sys.exit(0)
    else:
        logger.error(f"Complete E2E test failed with exit code: {test_result}")
        sys.exit(1) 
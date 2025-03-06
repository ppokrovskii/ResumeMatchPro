"""
Runner script for User Acceptance Tests (UAT).

This script:
1. Ensures all emulators are running
2. Sets up the test environment
3. Runs all UAT tests
"""
import os
import sys
import subprocess
import logging
import time
import argparse
import socket
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
azfunctions_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(azfunctions_dir)
sys.path.insert(0, azfunctions_dir)

# Emulator services to check
EMULATORS = [
    {"name": "Cosmos DB Emulator", "host": "localhost", "port": 8081},
    {"name": "Azure Storage Emulator (Blob)", "host": "127.0.0.1", "port": 10000},
    {"name": "Azure Storage Emulator (Queue)", "host": "127.0.0.1", "port": 10001}
]

def is_service_available(host, port):
    """Check if a service is available at the given host and port."""
    try:
        socket.create_connection((host, port), timeout=1)
        return True
    except (socket.timeout, socket.error, ConnectionRefusedError):
        return False

def check_emulators():
    """Check if all required emulators are running."""
    all_running = True
    
    for emulator in EMULATORS:
        running = is_service_available(emulator["host"], emulator["port"])
        if running:
            logger.info(f"✅ {emulator['name']} is running")
        else:
            logger.error(f"❌ {emulator['name']} is NOT running")
            all_running = False
    
    return all_running

def run_tests(test_file=None):
    """Run the UAT tests."""
    # Check if all emulators are running
    if not check_emulators():
        logger.error("Not all emulators are running. Please start the missing emulators and try again.")
        return False
    
    # Build the pytest command with proper environment setup
    uat_dir = os.path.dirname(os.path.abspath(__file__))
    pytest_path = os.path.join(os.path.dirname(sys.executable), "pytest")
    
    # Set PYTHONPATH for the subprocess
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join([azfunctions_dir, root_dir, env.get("PYTHONPATH", "")])
    
    if test_file:
        # Run a specific test file
        test_path = os.path.join(uat_dir, test_file)
        cmd = [pytest_path, "-xvs", test_path]
    else:
        # Run all UAT tests
        cmd = [pytest_path, "-xvs", uat_dir]
    
    logger.info(f"Running command: {' '.join(cmd)}")
    
    # Run the tests with the updated environment
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    
    # Print output
    if result.stdout:
        logger.info(result.stdout)
    if result.stderr:
        logger.error(result.stderr)
    
    # Return success/failure
    return result.returncode == 0

def main():
    """Main entry point for running UAT tests."""
    parser = argparse.ArgumentParser(description="Run UAT tests for ResumeMatchPro")
    parser.add_argument("--test-file", help="Specific test file to run", required=False)
    args = parser.parse_args()
    
    # Run tests
    success = run_tests(args.test_file)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 
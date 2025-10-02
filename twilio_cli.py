#!/usr/bin/env python3
"""
Twilio CLI Tools - Launcher Script

Simple launcher script for the Twilio CLI Tools package.
This script can be run from the project root directory.
"""

import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from twilio_cli.cli import execute_number_command, menu

if __name__ == "__main__":
    # Check if first argument is a number (for number-based commands)
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        command_num = sys.argv[1]
        args = sys.argv[2:] if len(sys.argv) > 2 else []
        execute_number_command(command_num, args)
    else:
        # Run interactive menu automatically when no arguments
        menu()

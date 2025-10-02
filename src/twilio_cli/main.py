#!/usr/bin/env python3
"""
Twilio CLI Tools - Main Entry Point

This module provides the main entry point for the Twilio CLI Tools package.
It can be run directly or imported as a module.
"""

import sys
from pathlib import Path

# Add the src directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from twilio_cli.cli import menu

if __name__ == "__main__":
    # Automatically run interactive menu
    menu()

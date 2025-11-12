#!/usr/bin/env python3
"""
Run script for Academic Activity Report Generator
This script handles the Python path setup and launches the application.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / 'src'
sys.path.insert(0, str(src_path))

def main():
    """Main entry point"""
    try:
        # Import and run the application
        from main import main as app_main
        print("Starting Academic Activity Report Generator...")
        app_main()

    except ImportError as e:
        print(f"Import Error: {e}")
        print("\nPlease make sure you have installed all required dependencies:")
        print("pip install -r requirements.txt")
        sys.exit(1)

    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
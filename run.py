"""
Run script for Academic Activity Report Generator
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import from src folder
from src.main import main

if __name__ == "__main__":
    main()
    
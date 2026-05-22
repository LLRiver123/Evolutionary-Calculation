#!/usr/bin/env python3
"""
Entry point for analyzing results
"""

import sys
from pathlib import Path

# Add framework to path
sys.path.insert(0, str(Path(__file__).parent / "framework"))
sys.path.insert(0, str(Path(__file__).parent / "solvers"))

from analyze import main

if __name__ == "__main__":
    main()

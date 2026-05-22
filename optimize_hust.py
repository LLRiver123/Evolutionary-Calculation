#!/usr/bin/env python3
"""
Entry point for HUST optimization
"""

import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent / "optimization"))
sys.path.insert(0, str(Path(__file__).parent / "framework"))
sys.path.insert(0, str(Path(__file__).parent / "solvers"))

from hust_workflow import main

if __name__ == "__main__":
    main()

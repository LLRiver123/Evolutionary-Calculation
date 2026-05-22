#!/usr/bin/env python3
"""
Entry point for testing solvers
"""

import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent / "scripts"))
sys.path.insert(0, str(Path(__file__).parent / "framework"))
sys.path.insert(0, str(Path(__file__).parent / "solvers"))

from test_solvers import main

if __name__ == "__main__":
    main()

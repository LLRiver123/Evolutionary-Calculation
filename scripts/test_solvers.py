"""
Quick test script để kiểm tra các solvers hoạt động đúng
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from utils import read_cbus_file, calculate_route_cost, validate_route
from cbus_bnb import CBUSBnB


def test_single_instance(file_path: str):
    """Test một instance"""
    print(f"\nTesting: {file_path}")
    print("=" * 70)
    
    # Load data
    try:
        n, k, cost_matrix = read_cbus_file(file_path)
        print(f"✓ Loaded: n={n}, k={k}")
    except Exception as e:
        print(f"✗ Error loading: {e}")
        return
    
    # Test BnB
    print("\n[BnB Solver]")
    try:
        solver = CBUSBnB(n, k, cost_matrix)
        route, cost, elapsed = solver.solve(time_limit=10.0)
        
        if route:
            is_valid, msg = validate_route(route, n, k, cost_matrix)
            calculated_cost = calculate_route_cost(route, cost_matrix)
            
            print(f"  Route: {' '.join(map(str, route[:5]))}...")
            print(f"  Cost: {cost} (calculated: {calculated_cost})")
            print(f"  Time: {elapsed:.3f}s")
            print(f"  Valid: {'✓' if is_valid else '✗ ' + msg}")
        else:
            print(f"  No solution found")
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()


def main():
    # Find a test file
    test_dirs = [
        'd:\\Evolutionary Calculation\\cbus_output_20260517_222958',
        './cbus_output_20260517_222958'
    ]
    
    test_file = None
    for test_dir in test_dirs:
        candidate = os.path.join(test_dir, 'lc101_cbus.txt')
        if os.path.exists(candidate):
            test_file = candidate
            break
    
    if not test_file:
        print("Error: Could not find test file")
        print("Expected: cbus_output_20260517_222958/lc101_cbus.txt")
        sys.exit(1)
    
    test_single_instance(test_file)


if __name__ == "__main__":
    main()

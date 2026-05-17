#!/usr/bin/env python3
"""
Comprehensive experiment scenarios
"""

import subprocess
import sys
import os
from datetime import datetime


def run_cmd(cmd, description):
    """Run a command and report results"""
    print(f"\n{'='*70}")
    print(f"📊 {description}")
    print(f"{'='*70}")
    print(f"Command: {cmd}\n")
    
    result = subprocess.run(cmd, shell=True)
    return result.returncode == 0


def main():
    """Run different experiment scenarios"""
    
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║               CBUS Solver Comparison Experiments                     ║
║                                                                      ║
║  Choose a scenario to run:                                          ║
║                                                                      ║
║  1. Quick Test (3 instances, 10s each)                              ║
║  2. Standard Test (all instances, 30s each)                         ║
║  3. Extended Test (all instances, 60s each)                         ║
║  4. Deep Dive (specific instance with 120s)                         ║
║  5. Custom Test                                                      ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        choice = input("Enter choice (1-5): ").strip()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if choice == '1' or choice == 'quick':
        run_cmd(
            'python run.py --quick -t 10',
            'Quick Test - 3 instances, 10s per solver'
        )
    
    elif choice == '2' or choice == 'standard':
        run_cmd(
            f'python run.py -t 30 -o results_standard_{timestamp}',
            'Standard Test - All instances, 30s per solver'
        )
    
    elif choice == '3' or choice == 'extended':
        run_cmd(
            f'python run.py -t 60 -o results_extended_{timestamp}',
            'Extended Test - All instances, 60s per solver'
        )
    
    elif choice == '4' or choice == 'deepdive':
        instance = input("Enter instance name (e.g., lc101_cbus): ").strip()
        run_cmd(
            f'python run.py -i {instance} -t 120 -o results_deepdive_{timestamp}',
            f'Deep Dive - {instance}, 120s per solver'
        )
    
    elif choice == '5' or choice == 'custom':
        time_limit = input("Time limit per solver (seconds, default 30): ").strip() or '30'
        instances = input("Instances (comma-separated, or blank for all): ").strip()
        
        if instances:
            run_cmd(
                f'python run.py -i {instances} -t {time_limit} -o results_custom_{timestamp}',
                f'Custom Test - {instances}, {time_limit}s per solver'
            )
        else:
            run_cmd(
                f'python run.py -t {time_limit} -o results_custom_{timestamp}',
                f'Custom Test - All instances, {time_limit}s per solver'
            )
    
    else:
        print("Invalid choice")
        sys.exit(1)
    
    print("\n" + "="*70)
    print("✅ Experiment completed!")
    print("="*70)


if __name__ == "__main__":
    main()

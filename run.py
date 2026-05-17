#!/usr/bin/env python3
"""
Quick runner script - Chạy experiment trên dữ liệu có sẵn
"""

import os
import sys
import argparse
from pathlib import Path

# Ensure we can import modules
sys.path.insert(0, str(Path(__file__).parent))

from experiment import ExperimentRunner


def main():
    # Detect data directory
    data_dir = 'd:\\Evolutionary Calculation\\cbus_output_20260517_222958'
    if not os.path.exists(data_dir):
        data_dir = './cbus_output_20260517_222958'
    if not os.path.exists(data_dir):
        print("Error: Cannot find data directory cbus_output_20260517_222958")
        sys.exit(1)
    
    parser = argparse.ArgumentParser(
        description='CBUS Solver Comparison',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py                              # All instances, 30s per solver
  python run.py -t 60                        # All instances, 60s per solver
  python run.py -i lc101_cbus                # Single instance
  python run.py -i lc101_cbus,lc102_cbus    # Multiple instances
  python run.py -o results_exp1              # Save to specific output dir
        """
    )
    
    parser.add_argument('-t', '--time', type=float, default=30.0,
                        help='Time limit per solver in seconds (default: 30)')
    parser.add_argument('-i', '--instances', default=None,
                        help='Run specific instances (comma-separated, without .txt)')
    parser.add_argument('-o', '--output', default=None,
                        help='Output directory (default: auto-generated)')
    parser.add_argument('-q', '--quick', action='store_true',
                        help='Run quick test on first 3 instances')
    
    args = parser.parse_args()
    
    runner = ExperimentRunner(output_dir=args.output, time_limit=args.time)
    
    if args.quick:
        # Run quick test on first 3 instances
        print("\n🚀 Running quick test (3 instances, 10s per solver)...")
        runner.time_limit = 10.0
        
        # Find first 3 instances
        files = sorted([f for f in os.listdir(data_dir) if f.endswith('.txt')])[:3]
        
        for f in files:
            from utils import read_cbus_file
            file_path = os.path.join(data_dir, f)
            instance_name = f.replace('.txt', '')
            n, k, cost_matrix = read_cbus_file(file_path)
            result = runner.run_instance(instance_name, n, k, cost_matrix)
            runner.results['instances'][instance_name] = result
        
        runner._save_results()
    
    elif args.instances:
        # Run specific instances
        instance_names = args.instances.split(',')
        print(f"\n🎯 Running {len(instance_names)} selected instance(s)...")
        
        from utils import read_cbus_file
        
        for instance_name in instance_names:
            instance_name = instance_name.strip()
            file_path = os.path.join(data_dir, f"{instance_name}.txt")
            
            if not os.path.exists(file_path):
                print(f"⚠️  Instance not found: {instance_name}")
                continue
            
            n, k, cost_matrix = read_cbus_file(file_path)
            result = runner.run_instance(instance_name, n, k, cost_matrix)
            runner.results['instances'][instance_name] = result
        
        runner._save_results()
    
    else:
        # Run all instances
        print(f"\n📊 Running all instances ({args.time}s per solver)...")
        runner.run_all_instances(data_dir)


if __name__ == "__main__":
    main()

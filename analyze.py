"""
Results analyzer - Parse and visualize experiment results
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import statistics


def load_results(results_dir: str) -> Dict:
    """Load results.json from experiment"""
    results_file = os.path.join(results_dir, 'results.json')
    
    if not os.path.exists(results_file):
        print(f"Error: {results_file} not found")
        sys.exit(1)
    
    with open(results_file, 'r') as f:
        return json.load(f)


def analyze_results(results: Dict):
    """Analyze and print results"""
    
    print("\n" + "="*80)
    print("CBUS SOLVER COMPARISON ANALYSIS")
    print("="*80)
    
    instances = results['instances']
    solvers = set()
    
    # Collect all solver names
    for inst_data in instances.values():
        for solver_name in inst_data['solvers'].keys():
            solvers.add(solver_name)
    
    solvers = sorted(solvers)
    
    # Summary statistics
    summary_stats = {solver: {'costs': [], 'times': [], 'wins': 0} for solver in solvers}
    
    print(f"\nTotal instances: {len(instances)}")
    print(f"Solvers: {', '.join(solvers)}\n")
    
    # Instance-by-instance results
    print("-" * 80)
    print(f"{'Instance':<20} | {'N':<3} | {'K':<3} | {' '.join(f'{s:<15}' for s in solvers)}")
    print("-" * 80)
    print(f"{'':20} | {'':3} | {'':3} | {' '.join(f'Cost/Time' for _ in solvers)}")
    print("-" * 80)
    
    for inst_name in sorted(instances.keys()):
        inst_data = instances[inst_name]
        n = inst_data['n']
        k = inst_data['k']
        
        costs = {}
        times = {}
        valids = {}
        
        for solver in solvers:
            solver_result = inst_data['solvers'].get(solver, {})
            cost = solver_result.get('cost')
            time_val = solver_result.get('time')
            valid = solver_result.get('valid', False)
            
            costs[solver] = cost
            times[solver] = time_val
            valids[solver] = valid
            
            # Collect stats
            if cost is not None and valid:
                summary_stats[solver]['costs'].append(cost)
                summary_stats[solver]['times'].append(time_val)
        
        # Find best cost
        valid_costs = {s: c for s, c in costs.items() if c is not None and valids[s]}
        if valid_costs:
            best_cost = min(valid_costs.values())
            best_solver = [s for s, c in valid_costs.items() if c == best_cost][0]
            summary_stats[best_solver]['wins'] += 1
        
        # Print row
        cost_time_str = " | ".join(
            f"{costs.get(s) or 'X':<6}/{times.get(s) or 0:.1f}" 
            for s in solvers
        )
        print(f"{inst_name:<20} | {n:<3} | {k:<3} | {cost_time_str}")
    
    print("-" * 80)
    
    # Summary statistics
    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80)
    
    print(f"\n{'Solver':<15} | {'Instances':<10} | {'Avg Cost':<12} | {'Avg Time':<10} | {'Wins':<6}")
    print("-" * 80)
    
    for solver in solvers:
        stats = summary_stats[solver]
        
        if stats['costs']:
            avg_cost = statistics.mean(stats['costs'])
            avg_time = statistics.mean(stats['times'])
            num_instances = len(stats['costs'])
            wins = stats['wins']
        else:
            avg_cost = avg_time = num_instances = wins = 0
        
        print(f"{solver:<15} | {num_instances:<10} | {avg_cost:<12.1f} | {avg_time:<10.2f} | {wins:<6}")
    
    print("-" * 80)
    
    # Winner
    print("\n" + "="*80)
    print("RANKINGS")
    print("="*80)
    
    # By average cost
    print("\nBy Average Cost (lower is better):")
    sorted_by_cost = sorted(
        [(s, statistics.mean(summary_stats[s]['costs']) if summary_stats[s]['costs'] else float('inf')) 
         for s in solvers],
        key=lambda x: x[1]
    )
    for i, (solver, avg_cost) in enumerate(sorted_by_cost, 1):
        print(f"  {i}. {solver:<15} {avg_cost:>10.1f}")
    
    # By wins
    print("\nBy Number of Wins:")
    sorted_by_wins = sorted(
        [(s, summary_stats[s]['wins']) for s in solvers],
        key=lambda x: x[1],
        reverse=True
    )
    for i, (solver, wins) in enumerate(sorted_by_wins, 1):
        print(f"  {i}. {solver:<15} {wins:>3} wins")
    
    # By average time
    print("\nBy Average Time (lower is better):")
    sorted_by_time = sorted(
        [(s, statistics.mean(summary_stats[s]['times']) if summary_stats[s]['times'] else float('inf')) 
         for s in solvers],
        key=lambda x: x[1]
    )
    for i, (solver, avg_time) in enumerate(sorted_by_time, 1):
        print(f"  {i}. {solver:<15} {avg_time:>10.2f}s")
    
    print("\n" + "="*80)


def main():
    if len(sys.argv) < 2:
        # Find latest results directory
        results_dirs = [d for d in os.listdir('.') if d.startswith('results_')]
        if not results_dirs:
            print("Error: No results directories found")
            print("Usage: python analyze.py <results_directory>")
            sys.exit(1)
        
        results_dir = sorted(results_dirs)[-1]
        print(f"Using latest results directory: {results_dir}")
    else:
        results_dir = sys.argv[1]
    
    results = load_results(results_dir)
    analyze_results(results)


if __name__ == "__main__":
    main()

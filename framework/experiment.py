"""
Experiment runner để so sánh 3 phương pháp giải CBUS:
  1. Branch-and-Bound (BnB)
  2. OR-Tools Routing with GLS
  3. ALNS (Adaptive Large Neighborhood Search)
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import traceback

# Import solver methods
from cbus_bnb_fixed import CBUSBnBFixed as CBUSBnB
import main_routing  # OR-Tools GLS solver
import heuristic     # ALNS solver
from utils import read_cbus_file, load_data_directory, calculate_route_cost, validate_route


class ExperimentRunner:
    def __init__(self, output_dir: str = None, time_limit: float = 30.0):
        """
        Args:
            output_dir: thư mục lưu kết quả (mặc định: results_YYYYMMDDhhmmss)
            time_limit: giới hạn thời gian cho mỗi solver (giây)
        """
        self.time_limit = time_limit
        
        if output_dir is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = f"results_{timestamp}"
        
        # Ensure output goes to results folder if not absolute path
        if not os.path.isabs(output_dir):
            root_dir = Path(__file__).parent.parent
            results_dir = root_dir / 'results'
            results_dir.mkdir(exist_ok=True)
            output_dir = str(results_dir / output_dir)
        
        self.output_dir = output_dir
        Path(self.output_dir).mkdir(exist_ok=True)
        
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'time_limit': time_limit,
            'instances': {}
        }
    
    def run_bnb(self, n: int, k: int, cost_matrix: List[List[int]]) -> Dict:
        """Chạy Branch-and-Bound solver"""
        try:        
            solver = CBUSBnB(n, k, cost_matrix)
            route, cost, elapsed = solver.solve(time_limit=self.time_limit)
            if cost is None:
                return {
                    'method': 'BnB', 'cost': None, 'route': None,
                    'time': elapsed, 'valid': False,
                    'message': 'No feasible solution found'
                }
            is_valid, msg = self._validate(route, n, k, cost_matrix, cost)
            
            return {
                'method': 'BnB',
                'cost': cost,
                'route': route,
                'time': elapsed,
                'valid': is_valid,
                'message': msg,
                'nodes_explored': solver.nodes_explored,
                'timeout': solver.aborted
            }
        except Exception as e:
            return {
                'method': 'BnB',
                'cost': None,
                'route': None,
                'time': None,
                'valid': False,
                'message': f"Error: {str(e)}",
                'error': traceback.format_exc()
            }
    
    def run_ortools(self, n: int, k: int, cost_matrix: List[List[int]]) -> Dict:
        """Chạy OR-Tools GLS solver"""
        try:
            start_time = time.time()
            route = main_routing.solve(n, k, cost_matrix, time_limit_seconds=self.time_limit)
            elapsed = time.time() - start_time
            cost = calculate_route_cost(route, cost_matrix)
            
            is_valid, msg = self._validate(route, n, k, cost_matrix, cost)
            
            return {
                'method': 'OR-Tools-GLS',
                'cost': cost,
                'route': route,
                'time': elapsed,
                'valid': is_valid,
                'message': msg
            }
        except Exception as e:
            return {
                'method': 'OR-Tools-GLS',
                'cost': None,
                'route': None,
                'time': None,
                'valid': False,
                'message': f"Error: {str(e)}",
                'error': traceback.format_exc()
            }
    
    def run_alns(self, n: int, k: int, cost_matrix: List[List[int]]) -> Dict:
        """Chạy ALNS solver"""
        try:
            start_time = time.time()
            route = heuristic.initial_solution(n, k, cost_matrix)
            # alns_optimize returns (route, cost)
            iterations = max(50, min(200, 2000 // n))
            route, cost = heuristic.alns_optimize(route, cost_matrix, n, k, iterations=iterations, time_limit=self.time_limit)
            elapsed = time.time() - start_time
            
            is_valid, msg = self._validate(route, n, k, cost_matrix, cost)
            
            return {
                'method': 'ALNS',
                'cost': cost,
                'route': route,
                'time': elapsed,
                'valid': is_valid,
                'message': msg
            }
        except Exception as e:
            return {
                'method': 'ALNS',
                'cost': None,
                'route': None,
                'time': None,
                'valid': False,
                'message': f"Error: {str(e)}",
                'error': traceback.format_exc()
            }
    
    def _validate(self, route: List[int], n: int, k: int, cost_matrix: List[List[int]], cost: int) -> Tuple[bool, str]:
        """Kiểm tra route có hợp lệ"""
        if not route:
            return False, "Empty route"
        
        is_valid, msg = validate_route(route, n, k, cost_matrix)
        if not is_valid:
            return False, msg
        
        calculated_cost = calculate_route_cost(route, cost_matrix)
        if int(calculated_cost) != int(cost):
            return False, f"Cost mismatch: reported={cost}, calculated={calculated_cost}"
        
        return True, "Valid"
    
    def run_instance(self, instance_name: str, n: int, k: int, cost_matrix: List[List[int]]) -> Dict:
        """Chạy tất cả 3 solver trên một instance"""
        print(f"\n{'='*70}")
        print(f"Instance: {instance_name} (n={n}, k={k})")
        print(f"{'='*70}")
        
        results = {
            'instance': instance_name,
            'n': n,
            'k': k,
            'solvers': {}
        }
        
        # BnB
        print("  [1/3] Running Branch-and-Bound...")
        sys.stdout.flush()
        bnb_result = self.run_bnb(n, k, cost_matrix)
        results['solvers']['BnB'] = bnb_result
        if bnb_result['cost'] is not None:
            print(f"        Cost: {bnb_result['cost']}, Time: {bnb_result['time']:.2f}s, Valid: {bnb_result['valid']}")
        else:
            print(f"        Failed: {bnb_result['message']}")
        
        # OR-Tools
        print("  [2/3] Running OR-Tools GLS...")
        sys.stdout.flush()
        ortools_result = self.run_ortools(n, k, cost_matrix)
        results['solvers']['OR-Tools-GLS'] = ortools_result
        if ortools_result['cost'] is not None:
            print(f"        Cost: {ortools_result['cost']}, Time: {ortools_result['time']:.2f}s, Valid: {ortools_result['valid']}")
        else:
            print(f"        Failed: {ortools_result['message']}")
        
        # ALNS
        print("  [3/3] Running ALNS...")
        sys.stdout.flush()
        alns_result = self.run_alns(n, k, cost_matrix)
        results['solvers']['ALNS'] = alns_result
        if alns_result['cost'] is not None:
            print(f"        Cost: {alns_result['cost']}, Time: {alns_result['time']:.2f}s, Valid: {alns_result['valid']}")
        else:
            print(f"        Failed: {alns_result['message']}")
        
        # Comparison
        self._print_comparison(results)
        
        return results
    
    def _print_comparison(self, results: Dict):
        """In bảng so sánh kết quả"""
        print("\n" + "-" * 70)
        print("COMPARISON:")
        print("-" * 70)
        print(f"{'Method':<15} | {'Cost':<12} | {'Time':<10} | {'Valid':<8} | Status")
        print("-" * 70)
        
        costs = []
        for solver_name, result in results['solvers'].items():
            cost = result['cost'] if result['cost'] is not None else "N/A"
            time_val = f"{result['time']:.2f}s" if result['time'] is not None else "N/A"
            valid = "✓" if result['valid'] else "✗"
            
            if isinstance(cost, int):
                costs.append(cost)
            
            status = "OK" if result['valid'] else result['message']
            print(f"{solver_name:<15} | {str(cost):<12} | {time_val:<10} | {valid:<8} | {status}")
        
        if costs:
            best_cost = min(costs)
            print("-" * 70)
            print(f"Best cost: {best_cost}")
            for solver_name, result in results['solvers'].items():
                if result['cost'] == best_cost:
                    print(f"  Winner: {solver_name}")
    
    def run_all_instances(self, data_dir: str):
        """Chạy tất cả instances trong thư mục"""
        print(f"\nLoading instances from: {data_dir}")
        data = load_data_directory(data_dir)
        print(f"Found {len(data)} instances")
        
        for instance_name, (n, k, cost_matrix) in sorted(data.items()):
            result = self.run_instance(instance_name, n, k, cost_matrix)
            self.results['instances'][instance_name] = result
        
        self._save_results()
    
    def _save_results(self):
        """Lưu kết quả thành file JSON"""
        # Chuyển routes thành strings để save JSON
        results_to_save = self.results.copy()
        for instance_name, inst_result in results_to_save['instances'].items():
            for solver_name, solver_result in inst_result['solvers'].items():
                if solver_result.get('route'):
                    solver_result['route'] = ' '.join(map(str, solver_result['route']))
        
        results_file = os.path.join(self.output_dir, 'results.json')
        with open(results_file, 'w') as f:
            json.dump(results_to_save, f, indent=2)
        
        print(f"\nResults saved to: {results_file}")
        
        # Lưu CSV report
        self._save_csv_report()
    
    def _save_csv_report(self):
        """Lưu báo cáo dạng CSV"""
        csv_file = os.path.join(self.output_dir, 'results.csv')
        
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write("Instance,N,K,Method,Cost,Time(s),Valid,Message\n")
            
            for instance_name, inst_result in self.results['instances'].items():
                n = inst_result['n']
                k = inst_result['k']
                
                for solver_name, solver_result in inst_result['solvers'].items():
                    cost = solver_result['cost'] if solver_result['cost'] is not None else ""
                    time_val = f"{solver_result['time']:.3f}" if solver_result['time'] is not None else ""
                    valid = "Y" if solver_result['valid'] else "N"
                    msg = solver_result['message']
                    
                    f.write(f"{instance_name},{n},{k},{solver_name},{cost},{time_val},{valid},{msg}\n")
        
        print(f"CSV report saved to: {csv_file}")


def main():
    parser = argparse.ArgumentParser(description="CBUS Experiment Runner")
    parser.add_argument('data_dir', help='Directory containing CBUS input files')
    parser.add_argument('-o', '--output', help='Output directory', default=None)
    parser.add_argument('-t', '--time-limit', type=float, default=30.0, help='Time limit per solver (seconds)')
    parser.add_argument('-i', '--instance', help='Run specific instance only')
    
    args = parser.parse_args()
    
    runner = ExperimentRunner(output_dir=args.output, time_limit=args.time_limit)
    
    if args.instance:
        # Chạy một instance cụ thể
        try:
            n, k, cost_matrix = read_cbus_file(os.path.join(args.data_dir, f"{args.instance}.txt"))
            result = runner.run_instance(args.instance, n, k, cost_matrix)
            runner.results['instances'][args.instance] = result
            runner._save_results()
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        # Chạy tất cả instances
        runner.run_all_instances(args.data_dir)


if __name__ == "__main__":
    main()

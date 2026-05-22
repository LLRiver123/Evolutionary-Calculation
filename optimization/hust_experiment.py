"""
HUST Benchmark Experiment Runner
Run comprehensive comparison on HUST instances with optimized parameters
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).parent))

from utils import read_cbus_file, calculate_route_cost, validate_route
from cbus_bnb import CBUSBnB
import main_routing
import heuristic

from ortools.constraint_solver import routing_enums_pb2, pywrapcp


class HUSTExperimentRunner:
    def __init__(self, output_dir: str = None):
        if output_dir is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = f"hust_results_{timestamp}"
        
        self.output_dir = output_dir
        Path(self.output_dir).mkdir(exist_ok=True)
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'instances': {}
        }
    
    def run_ortools_optimized(self, n: int, k: int, cost_matrix: List[List[int]], 
                              time_limit: float = 30.0) -> Tuple[List[int], float]:
        """Run OR-Tools with optimized parameters"""
        
        node_count = 2 * n + 1
        max_c = max(max(row) for row in cost_matrix)
        max_dist = max_c * (2 * n + 1)

        manager = pywrapcp.RoutingIndexManager(node_count, 1, 0)
        routing = pywrapcp.RoutingModel(manager)

        flat = [0] * (node_count * node_count)
        for i in range(node_count):
            base = i * node_count
            row = cost_matrix[i]
            for j in range(node_count):
                flat[base + j] = row[j]

        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return flat[from_node * node_count + to_node]

        transit_cb_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_cb_index)

        def demand_callback(from_index):
            node = manager.IndexToNode(from_index)
            if 1 <= node <= n:
                return 1
            if n < node <= 2 * n:
                return -1
            return 0

        demand_cb_index = routing.RegisterUnaryTransitCallback(demand_callback)
        routing.AddDimensionWithVehicleCapacity(
            demand_cb_index, 0, [k], True, "Capacity"
        )

        routing.AddDimension(transit_cb_index, 0, max_dist, True, "Distance")
        routing.AddConstantDimension(1, 2 * n + 1, True, "Order")
        
        order_dimension = routing.GetDimensionOrDie("Order")
        solver = routing.solver()
        
        for i in range(1, n + 1):
            pickup = manager.NodeToIndex(i)
            delivery = manager.NodeToIndex(i + n)
            routing.AddPickupAndDelivery(pickup, delivery)
            solver.Add(routing.VehicleVar(pickup) == routing.VehicleVar(delivery))
            solver.Add(order_dimension.CumulVar(pickup) < order_dimension.CumulVar(delivery))

        # Optimized parameters
        search_params = pywrapcp.DefaultRoutingSearchParameters()
        search_params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION
        search_params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        search_params.time_limit.FromSeconds(int(time_limit))
        search_params.use_full_propagation = True
        search_params.lns_time_limit.FromSeconds(max(1, int(time_limit / 6)))
        search_params.log_search = False

        start_time = time.time()
        solution = routing.SolveWithParameters(search_params)
        elapsed = time.time() - start_time
        
        if solution is None:
            return main_routing.greedy_route(n, k, cost_matrix), elapsed

        route = []
        index = routing.Start(0)
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            if node != 0:
                route.append(node)
            index = solution.Value(routing.NextVar(index))

        return route if len(route) == 2 * n else main_routing.greedy_route(n, k, cost_matrix), elapsed
    
    def run_alns_optimized(self, n: int, k: int, cost_matrix: List[List[int]], 
                           time_limit: float = 30.0) -> Tuple[List[int], float]:
        """Run ALNS with optimized parameters"""
        
        import random
        import math
        
        start_time = time.time()
        
        # Optimized parameters for ALNS
        iterations = 300
        cooling_rate = 0.95
        initial_temp = 150.0
        
        route = heuristic.initial_solution(n, k, cost_matrix)
        best_route = route[:]
        best_cost = heuristic.calc_route_cost(route, cost_matrix)
        
        current_route = route[:]
        current_cost = best_cost
        T = initial_temp
        
        for iteration in range(iterations):
            if time.time() - start_time > time_limit:
                break
            
            num_remove = random.randint(1, min(40, max(1, n // 20)))
            repaired_route, removed_reqs = heuristic.random_removal(current_route, num_remove, n)
            
            full_route = [0] + repaired_route + [0]
            
            for req in removed_reqs:
                P, D = req, req + n
                
                loads = [0] * len(full_route)
                curr_load = 0
                for idx in range(1, len(full_route) - 1):
                    node = full_route[idx]
                    if node <= n: curr_load += 1
                    else: curr_load -= 1
                    loads[idx] = curr_load
                
                next_full = [len(full_route)] * len(full_route)
                last_full = len(full_route)
                for idx in range(len(full_route) - 1, -1, -1):
                    if loads[idx] == k:
                        last_full = idx
                    next_full[idx] = last_full
                
                best_req_cost = float('inf')
                best_x, best_y = -1, -1
                
                for x in range(1, len(full_route)):
                    prev_x = full_route[x-1]
                    node_x = full_route[x]
                    cost_P = cost_matrix[prev_x][P] + cost_matrix[P][node_x] - cost_matrix[prev_x][node_x]
                    
                    max_y = min(len(full_route), next_full[x] + 1)
                    for y in range(x, max_y):
                        if x == y:
                            cost = cost_matrix[prev_x][P] + cost_matrix[P][D] + cost_matrix[D][node_x] - cost_matrix[prev_x][node_x]
                        else:
                            prev_y = full_route[y-1]
                            node_y = full_route[y]
                            cost = cost_P + cost_matrix[prev_y][D] + cost_matrix[D][node_y] - cost_matrix[prev_y][node_y]
                        
                        if cost < best_req_cost:
                            best_req_cost = cost
                            best_x, best_y = x, y
                
                if best_x == best_y:
                    full_route.insert(best_x, D)
                    full_route.insert(best_x, P)
                else:
                    full_route.insert(best_y, D)
                    full_route.insert(best_x, P)
            
            repaired_route = full_route[1:-1]
            new_cost = heuristic.calc_route_cost(repaired_route, cost_matrix)
            
            if new_cost < current_cost:
                current_route = repaired_route
                current_cost = new_cost
                if new_cost < best_cost:
                    best_route = repaired_route[:]
                    best_cost = new_cost
            else:
                delta = new_cost - current_cost
                prob = math.exp(-delta / T)
                if random.random() < prob:
                    current_route = repaired_route
                    current_cost = new_cost
            
            T *= cooling_rate
        
        elapsed = time.time() - start_time
        return best_route, elapsed
    
    def run_bnb(self, n: int, k: int, cost_matrix: List[List[int]], 
                time_limit: float = 30.0) -> Tuple[List[int], float]:
        """Run BnB solver"""
        
        solver = CBUSBnB(n, k, cost_matrix)
        route, cost, elapsed = solver.solve(time_limit=time_limit)
        return route, elapsed
    
    def run_instance(self, instance_name: str, n: int, k: int, 
                     cost_matrix: List[List[int]], time_limit: float = 30.0):
        """Run all solvers on one instance"""
        
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
        try:
            route, elapsed = self.run_bnb(n, k, cost_matrix, time_limit)
            cost = calculate_route_cost(route, cost_matrix)
            is_valid, msg = validate_route(route, n, k, cost_matrix)
            
            results['solvers']['BnB'] = {
                'cost': cost,
                'time': elapsed,
                'valid': is_valid,
                'message': msg
            }
            print(f"        Cost: {cost}, Time: {elapsed:.2f}s, Valid: {is_valid}")
        except Exception as e:
            results['solvers']['BnB'] = {
                'cost': None,
                'time': None,
                'valid': False,
                'message': str(e)
            }
            print(f"        Error: {e}")
        
        # OR-Tools
        print("  [2/3] Running OR-Tools GLS...")
        try:
            route, elapsed = self.run_ortools_optimized(n, k, cost_matrix, time_limit)
            cost = calculate_route_cost(route, cost_matrix)
            is_valid, msg = validate_route(route, n, k, cost_matrix)
            
            results['solvers']['OR-Tools'] = {
                'cost': cost,
                'time': elapsed,
                'valid': is_valid,
                'message': msg
            }
            print(f"        Cost: {cost}, Time: {elapsed:.2f}s, Valid: {is_valid}")
        except Exception as e:
            results['solvers']['OR-Tools'] = {
                'cost': None,
                'time': None,
                'valid': False,
                'message': str(e)
            }
            print(f"        Error: {e}")
        
        # ALNS
        print("  [3/3] Running ALNS...")
        try:
            route, elapsed = self.run_alns_optimized(n, k, cost_matrix, time_limit)
            cost = calculate_route_cost(route, cost_matrix)
            is_valid, msg = validate_route(route, n, k, cost_matrix)
            
            results['solvers']['ALNS'] = {
                'cost': cost,
                'time': elapsed,
                'valid': is_valid,
                'message': msg
            }
            print(f"        Cost: {cost}, Time: {elapsed:.2f}s, Valid: {is_valid}")
        except Exception as e:
            results['solvers']['ALNS'] = {
                'cost': None,
                'time': None,
                'valid': False,
                'message': str(e)
            }
            print(f"        Error: {e}")
        
        # Comparison
        self._print_comparison(results)
        
        return results
    
    def _print_comparison(self, results: Dict):
        """Print comparison table"""
        
        print("\n" + "-" * 70)
        print("COMPARISON:")
        print("-" * 70)
        print(f"{'Method':<15} | {'Cost':<12} | {'Time':<10} | {'Valid':<8}")
        print("-" * 70)
        
        costs = []
        for solver_name, result in results['solvers'].items():
            cost = result['cost'] if result['cost'] is not None else "N/A"
            time_val = f"{result['time']:.2f}s" if result['time'] is not None else "N/A"
            valid = "✓" if result['valid'] else "✗"
            
            if isinstance(cost, int):
                costs.append(cost)
            
            print(f"{solver_name:<15} | {str(cost):<12} | {time_val:<10} | {valid:<8}")
        
        if costs:
            best_cost = min(costs)
            print("-" * 70)
            print(f"Best cost: {best_cost}")
            for solver_name, result in results['solvers'].items():
                if result['cost'] == best_cost:
                    print(f"  ⭐ {solver_name}")
    
    def run_all_hust(self, data_dir: str, time_limit: float = 30.0):
        """Run all HUST instances"""
        
        files = sorted([f for f in os.listdir(data_dir) if f.startswith('hust') and f.endswith('.txt')])
        
        print(f"\nFound {len(files)} HUST instances")
        
        for file_name in files:
            instance_name = file_name.replace('.txt', '')
            file_path = os.path.join(data_dir, file_name)
            
            try:
                n, k, cost_matrix = read_cbus_file(file_path)
                result = self.run_instance(instance_name, n, k, cost_matrix, time_limit)
                self.results['instances'][instance_name] = result
            except Exception as e:
                print(f"Error processing {instance_name}: {e}")
                import traceback
                traceback.print_exc()
        
        self._save_results()
    
    def _save_results(self):
        """Save results to JSON"""
        
        output_file = os.path.join(self.output_dir, 'hust_results.json')
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n✓ Results saved to: {output_file}")
        
        # Also save CSV summary
        self._save_csv()
    
    def _save_csv(self):
        """Save CSV summary"""
        
        csv_file = os.path.join(self.output_dir, 'hust_results.csv')
        
        with open(csv_file, 'w') as f:
            f.write("Instance,N,K,Method,Cost,Time(s),Valid\n")
            
            for instance_name, inst_result in self.results['instances'].items():
                n = inst_result['n']
                k = inst_result['k']
                
                for solver_name, solver_result in inst_result['solvers'].items():
                    cost = solver_result['cost'] if solver_result['cost'] is not None else ""
                    time_val = f"{solver_result['time']:.3f}" if solver_result['time'] is not None else ""
                    valid = "Y" if solver_result['valid'] else "N"
                    
                    f.write(f"{instance_name},{n},{k},{solver_name},{cost},{time_val},{valid}\n")
        
        print(f"✓ CSV saved to: {csv_file}")


def main():
    data_dir = 'd:\\Evolutionary Calculation\\cbus_output_20260517_222958'
    
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--time', type=float, default=30.0, help='Time limit per solver')
    parser.add_argument('-o', '--output', default=None, help='Output directory')
    args = parser.parse_args()
    
    runner = HUSTExperimentRunner(output_dir=args.output)
    runner.run_all_hust(data_dir, time_limit=args.time)


if __name__ == "__main__":
    main()

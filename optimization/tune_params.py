"""
Parameter tuning for OR-Tools and ALNS solvers
Tests different parameter combinations to find optimal configuration
"""

import json
import os
import sys
import time
import itertools
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import multiprocessing as mp

sys.path.insert(0, str(Path(__file__).parent))

from utils import read_cbus_file, calculate_route_cost, validate_route
from cbus_bnb import CBUSBnB
import main_routing
import heuristic


class ParameterTuner:
    def __init__(self, output_dir: str = None):
        if output_dir is None:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = f"tuning_results_{timestamp}"
        
        self.output_dir = output_dir
        Path(self.output_dir).mkdir(exist_ok=True)
        self.results = {}
    
    # OR-Tools parameter combinations
    ORTOOLS_PARAMS = {
        'first_solution_strategy': [
            'AUTOMATIC',
            'PATH_CHEAPEST_ARC',
            'NEAREST_NEIGHBOR',
            'CHEAPEST_INSERTION',
            'PARALLEL_CHEAPEST_INSERTION',
        ],
        'local_search_metaheuristic': [
            'AUTOMATIC',
            'GUIDED_LOCAL_SEARCH',
            'SIMULATED_ANNEALING',
            'TABU_SEARCH',
        ],
        'time_limit_multiplier': [0.5, 0.7, 1.0],  # Fraction of total time for first phase
    }
    
    # ALNS parameter combinations
    ALNS_PARAMS = {
        'iterations': [50, 100, 200, 300],
        'cooling_rate': [0.90, 0.92, 0.95, 0.98],
        'initial_temperature': [50.0, 100.0, 200.0],
        'removal_size_range': [(1, 10), (2, 20), (5, 40)],  # (min, max) percent
    }
    
    def tune_ortools(self, n: int, k: int, cost_matrix: List[List[int]], 
                     time_limit: float = 20.0) -> Dict:
        """Tune OR-Tools parameters"""
        
        from ortools.constraint_solver import routing_enums_pb2
        
        results = []
        strategy_names = [s for s in dir(routing_enums_pb2.FirstSolutionStrategy) if not s.startswith('_')]
        metaheuristic_names = [s for s in dir(routing_enums_pb2.LocalSearchMetaheuristic) if not s.startswith('_')]
        
        # Sample subset for quick tuning
        strategies_to_try = [
            routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION,
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC,
            routing_enums_pb2.FirstSolutionStrategy.NEAREST_NEIGHBOR,
        ]
        
        metaheuristics_to_try = [
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH,
            routing_enums_pb2.LocalSearchMetaheuristic.SIMULATED_ANNEALING,
        ]
        
        for strategy in strategies_to_try:
            for metaheuristic in metaheuristics_to_try:
                for time_mult in [0.7, 1.0]:
                    try:
                        start = time.time()
                        
                        # Create modified solve function
                        route = self._solve_ortools_custom(
                            n, k, cost_matrix, 
                            first_solution_strategy=strategy,
                            local_search_metaheuristic=metaheuristic,
                            time_limit_seconds=time_limit
                        )
                        
                        elapsed = time.time() - start
                        cost = calculate_route_cost(route, cost_matrix)
                        is_valid, _ = validate_route(route, n, k, cost_matrix)
                        
                        results.append({
                            'strategy': str(strategy),
                            'metaheuristic': str(metaheuristic),
                            'time_multiplier': time_mult,
                            'cost': cost,
                            'time': elapsed,
                            'valid': is_valid
                        })
                        
                        print(f"  OR-Tools config: cost={cost}, time={elapsed:.2f}s")
                        
                    except Exception as e:
                        print(f"  OR-Tools config failed: {e}")
        
        return results
    
    def _solve_ortools_custom(self, n, k, c, first_solution_strategy, 
                              local_search_metaheuristic, time_limit_seconds):
        """Custom OR-Tools solve with specific parameters"""
        from ortools.constraint_solver import pywrapcp, routing_enums_pb2
        
        node_count = 2 * n + 1
        max_c = max(max(row) for row in c)
        max_dist = max_c * (2 * n + 1)

        manager = pywrapcp.RoutingIndexManager(node_count, 1, 0)
        routing = pywrapcp.RoutingModel(manager)

        flat = [0] * (node_count * node_count)
        for i in range(node_count):
            base = i * node_count
            row = c[i]
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

        search_params = pywrapcp.DefaultRoutingSearchParameters()
        search_params.first_solution_strategy = first_solution_strategy
        search_params.local_search_metaheuristic = local_search_metaheuristic
        search_params.time_limit.FromSeconds(int(time_limit_seconds))
        search_params.use_full_propagation = True
        search_params.lns_time_limit.FromSeconds(max(1, int(time_limit_seconds / 6)))

        solution = routing.SolveWithParameters(search_params)
        
        if solution is None:
            return main_routing.greedy_route(n, k, c)

        route = []
        index = routing.Start(0)
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            if node != 0:
                route.append(node)
            index = solution.Value(routing.NextVar(index))

        return route if len(route) == 2 * n else main_routing.greedy_route(n, k, c)
    
    def tune_alns(self, n: int, k: int, cost_matrix: List[List[int]],
                  time_limit: float = 20.0) -> Dict:
        """Tune ALNS parameters"""
        
        results = []
        
        # Test different parameter combinations
        iterations_to_try = [50, 100, 200]
        cooling_rates = [0.92, 0.95, 0.98]
        temps = [50.0, 100.0, 150.0]
        
        for iterations in iterations_to_try:
            for cooling in cooling_rates:
                for temp in temps:
                    try:
                        start = time.time()
                        
                        route = heuristic.initial_solution(n, k, cost_matrix)
                        route = self._alns_optimize_custom(
                            route, cost_matrix, n, k,
                            iterations=iterations,
                            cooling_rate=cooling,
                            initial_temp=temp
                        )
                        
                        elapsed = time.time() - start
                        cost = calculate_route_cost(route, cost_matrix)
                        is_valid, _ = validate_route(route, n, k, cost_matrix)
                        
                        results.append({
                            'iterations': iterations,
                            'cooling_rate': cooling,
                            'initial_temp': temp,
                            'cost': cost,
                            'time': elapsed,
                            'valid': is_valid
                        })
                        
                        print(f"  ALNS config: cost={cost}, time={elapsed:.2f}s (iter={iterations}, cool={cooling}, temp={temp})")
                        
                    except Exception as e:
                        print(f"  ALNS config failed: {e}")
        
        return results
    
    def _alns_optimize_custom(self, route, c, n, k_cap, iterations, cooling_rate, initial_temp):
        """Custom ALNS with specific parameters"""
        import random
        import math
        
        best_route = route[:]
        best_cost = heuristic.calc_route_cost(route, c)
        
        current_route = route[:]
        current_cost = best_cost
        
        T = initial_temp
        
        for iteration in range(iterations):
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
                    if loads[idx] == k_cap:
                        last_full = idx
                    next_full[idx] = last_full
                
                best_req_cost = float('inf')
                best_x, best_y = -1, -1
                
                for x in range(1, len(full_route)):
                    prev_x = full_route[x-1]
                    node_x = full_route[x]
                    cost_P = c[prev_x][P] + c[P][node_x] - c[prev_x][node_x]
                    
                    max_y = min(len(full_route), next_full[x] + 1)
                    for y in range(x, max_y):
                        if x == y:
                            cost = c[prev_x][P] + c[P][D] + c[D][node_x] - c[prev_x][node_x]
                        else:
                            prev_y = full_route[y-1]
                            node_y = full_route[y]
                            cost = cost_P + c[prev_y][D] + c[D][node_y] - c[prev_y][node_y]
                        
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
            new_cost = heuristic.calc_route_cost(repaired_route, c)
            
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
        
        return best_route
    
    def run_tuning(self, data_dir: str, time_limit: float = 20.0):
        """Run parameter tuning on test instances"""
        
        files = sorted([f for f in os.listdir(data_dir) if f.startswith('hust') and f.endswith('.txt')])
        
        for file_name in files[:2]:  # Quick test: first 2 files
            instance_name = file_name.replace('.txt', '')
            file_path = os.path.join(data_dir, file_name)
            
            print(f"\n{'='*70}")
            print(f"Tuning: {instance_name}")
            print(f"{'='*70}")
            
            try:
                n, k, cost_matrix = read_cbus_file(file_path)
                print(f"n={n}, k={k}")
                
                # Tune OR-Tools
                print("\nTuning OR-Tools parameters...")
                ortools_results = self.tune_ortools(n, k, cost_matrix, time_limit)
                
                # Tune ALNS
                print("\nTuning ALNS parameters...")
                alns_results = self.tune_alns(n, k, cost_matrix, time_limit)
                
                self.results[instance_name] = {
                    'n': n,
                    'k': k,
                    'ortools': ortools_results,
                    'alns': alns_results
                }
                
            except Exception as e:
                print(f"Error processing {instance_name}: {e}")
                import traceback
                traceback.print_exc()
        
        self._save_results()
    
    def _save_results(self):
        """Save tuning results"""
        output_file = os.path.join(self.output_dir, 'tuning_results.json')
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\nTuning results saved to: {output_file}")


def main():
    data_dir = 'd:\\Evolutionary Calculation\\cbus_output_20260517_222958'
    
    tuner = ParameterTuner()
    tuner.run_tuning(data_dir, time_limit=20.0)


if __name__ == "__main__":
    main()

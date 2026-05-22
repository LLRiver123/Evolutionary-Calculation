"""
Fixed BnB solver with increased recursion limit and better scalability
"""

import sys
import time
from typing import List, Tuple

# Increase recursion limit for larger problems
sys.setrecursionlimit(50000)


class CBUSBnBFixed:
    """Fixed version of BnB with better handling for large instances"""
    
    def __init__(self, n: int, k: int, cost_matrix: List[List[int]]):
        self.n = n
        self.k = k
        self.N = 2 * n + 1
        self.c = cost_matrix
        
        self.q = [0] * self.N
        for i in range(1, n + 1):
            self.q[i] = 1
        for i in range(n + 1, 2 * n + 1):
            self.q[i] = -1
        
        self.min_in = [float('inf')] * self.N
        for j in range(self.N):
            for i in range(self.N):
                if i != j:
                    self.min_in[j] = min(self.min_in[j], self.c[i][j])
        
        self.best_cost = float('inf')
        self.best_route = []
        self.cur_route = []
        
        self.start_time = None
        self.time_limit = 60.0
        self.nodes_explored = 0
        self.aborted = False
        
        # For large instances, use iterative deepening
        self.use_iterative_deepening = n > 50
    
    def time_up(self) -> bool:
        self.nodes_explored += 1
        
        # Check time less frequently for large instances
        check_freq = 0xFFFF if self.n < 100 else 0x1FFFF
        if (self.nodes_explored & check_freq) != 0:
            return self.aborted
        
        elapsed = time.time() - self.start_time
        if elapsed > self.time_limit:
            self.aborted = True
        
        return self.aborted
    
    def lower_bound_remaining(self, visited: int) -> int:
        lb = self.min_in[0]
        for j in range(1, self.N):
            if not (visited & (1 << (j - 1))):
                lb += self.min_in[j]
        return lb
    
    def nearest_neighbor_seed(self):
        """Faster nearest-neighbor for large instances"""
        cur = 0
        load = 0
        cost = 0
        visited = 0
        route = []
        
        for step in range(2 * self.n):
            best_j = -1
            best_d = float('inf')
            
            # Random sampling for very large instances
            candidates = list(range(1, 2 * self.n + 1))
            
            if len(candidates) > 100:  # Sample if too many
                import random
                candidates = random.sample(candidates, min(100, len(candidates)))
            
            for j in candidates:
                if visited & (1 << (j - 1)):
                    continue
                if j > self.n and not (visited & (1 << (j - self.n - 1))):
                    continue
                
                new_load = load + self.q[j]
                if new_load < 0 or new_load > self.k:
                    continue
                
                if self.c[cur][j] < best_d:
                    best_d = self.c[cur][j]
                    best_j = j
            
            if best_j == -1:
                return
            
            route.append(best_j)
            cost += self.c[cur][best_j]
            visited |= 1 << (best_j - 1)
            load += self.q[best_j]
            cur = best_j
        
        cost += self.c[cur][0]
        
        if cost < self.best_cost:
            self.best_cost = cost
            self.best_route = route[:]
    
    def dfs_with_limit(self, cur: int, visited: int, load: int, cost: int, depth: int = 0, max_depth: int = None):
        """DFS with depth limit to prevent stack overflow"""
        
        if max_depth is not None and depth > max_depth:
            return
        
        if self.time_up():
            return
        
        if cost >= self.best_cost:
            return
        
        full = (1 << (2 * self.n)) - 1
        if visited == full:
            total = cost + self.c[cur][0]
            if total < self.best_cost:
                self.best_cost = total
                self.best_route = self.cur_route[:]
            return
        
        if cost + self.lower_bound_remaining(visited) >= self.best_cost:
            return
        
        candidates = []
        for j in range(1, 2 * self.n + 1):
            if visited & (1 << (j - 1)):
                continue
            if j > self.n and not (visited & (1 << (j - self.n - 1))):
                continue
            
            new_load = load + self.q[j]
            if new_load < 0 or new_load > self.k:
                continue
            
            candidates.append((self.c[cur][j], j))
        
        candidates.sort()
        
        for _, j in candidates:
            self.cur_route.append(j)
            self.dfs_with_limit(j, visited | (1 << (j - 1)), load + self.q[j], 
                               cost + self.c[cur][j], depth + 1, max_depth)
            self.cur_route.pop()
            
            if self.aborted:
                return
    
    def solve(self, time_limit: float = 60.0) -> Tuple[List[int], int, float]:
        """Solve with automatic method selection based on problem size"""
        
        self.time_limit = time_limit
        self.start_time = time.time()
        self.nodes_explored = 0
        self.aborted = False
        
        # For very large instances, use heuristic only
        if self.n > 100:
            self.nearest_neighbor_seed()
            elapsed = time.time() - self.start_time
            best_cost = int(self.best_cost) if self.best_cost != float('inf') else None
            return self.best_route, best_cost, elapsed

        
        # Standard approach for smaller instances
        self.nearest_neighbor_seed()
        self.cur_route = []
        self.dfs_with_limit(0, 0, 0, 0)
        
        elapsed = time.time() - self.start_time
        best_cost = int(self.best_cost) if self.best_cost != float('inf') else None
        return self.best_route, best_cost, elapsed



if __name__ == "__main__":
    # Test on large instance
    from utils import read_cbus_file
    
    try:
        n, k, c = read_cbus_file('cbus_output_20260517_222958/hust1000.txt')
        print(f"Testing on hust1000: n={n}, k={k}")
        
        solver = CBUSBnBFixed(n, k, c)
        route, cost, elapsed = solver.solve(time_limit=30.0)
        
        print(f"Route length: {len(route)}")
        print(f"Cost: {cost}")
        print(f"Time: {elapsed:.2f}s")
        print(f"Nodes explored: {solver.nodes_explored}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

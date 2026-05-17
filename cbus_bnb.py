"""
Branch-and-Bound solver for CBUS (Pickup and Delivery Problem)
Python port of cbus_bnb.cpp

Các ràng buộc:
  * Mỗi điểm trong {1..2n} ghé đúng một lần, xuất phát và quay về 0
  * Pickup i ghé trước Delivery i+n
  * Sức chứa [0, k] tại mọi bước
  * Tối thiểu hóa tổng quãng đường

Pruning:
  1. Cận dưới = chi phí hiện tại + Σ_j min_in[j] (j chưa thăm)
  2. Khởi tạo upper bound bằng nearest-neighbor
  3. Sắp xếp ứng viên theo chi phí tăng dần
"""

import time
from typing import List, Tuple, Optional


class CBUSBnB:
    def __init__(self, n: int, k: int, cost_matrix: List[List[int]]):
        """
        Khởi tạo solver Branch-and-Bound
        
        Args:
            n: số điểm đón (delivery nodes = 1..n, pickup nodes = n+1..2n)
            k: sức chứa xe
            cost_matrix: ma trận khoảng cách (2n+1) x (2n+1)
        """
        self.n = n
        self.k = k
        self.N = 2 * n + 1  # tổng số nodes (depot + n pickups + n deliveries)
        self.c = cost_matrix
        
        # q[i] = +1 (pickup), -1 (delivery), 0 (depot)
        self.q = [0] * self.N
        for i in range(1, n + 1):
            self.q[i] = 1
        for i in range(n + 1, 2 * n + 1):
            self.q[i] = -1
        
        # Tính min incoming edge cho mỗi node (dùng cho lower bound)
        self.min_in = [float('inf')] * self.N
        for j in range(self.N):
            for i in range(self.N):
                if i != j:
                    self.min_in[j] = min(self.min_in[j], self.c[i][j])
        
        # Kết quả tốt nhất
        self.best_cost = float('inf')
        self.best_route = []
        self.cur_route = []
        
        # Thống kê
        self.start_time = None
        self.time_limit = 60.0
        self.nodes_explored = 0
        self.aborted = False
    
    def time_up(self) -> bool:
        """Kiểm tra hết thời gian"""
        self.nodes_explored += 1
        if (self.nodes_explored & 0xFFFF) != 0:  # check every 65536 nodes
            return self.aborted
        elapsed = time.time() - self.start_time
        if elapsed > self.time_limit:
            self.aborted = True
        return self.aborted
    
    def lower_bound_remaining(self, visited: int) -> int:
        """Tính cận dưới dựa trên các edges chưa thăm"""
        lb = self.min_in[0]
        for j in range(1, self.N):
            if not (visited & (1 << (j - 1))):
                lb += self.min_in[j]
        return lb
    
    def nearest_neighbor_seed(self):
        """Tìm giải pháp khởi tạo bằng nearest-neighbor heuristic"""
        cur = 0
        load = 0
        cost = 0
        visited = 0
        route = []
        
        for step in range(2 * self.n):
            best_j = -1
            best_d = float('inf')
            
            # Tìm node tiếp theo tốt nhất
            for j in range(1, 2 * self.n + 1):
                # Bỏ qua nếu đã thăm
                if visited & (1 << (j - 1)):
                    continue
                
                # Nếu là delivery, kiểm tra pickup đã được thăm chưa
                if j > self.n and not (visited & (1 << (j - self.n - 1))):
                    continue
                
                # Kiểm tra sức chứa
                new_load = load + self.q[j]
                if new_load < 0 or new_load > self.k:
                    continue
                
                # Chọn edge rẻ nhất
                if self.c[cur][j] < best_d:
                    best_d = self.c[cur][j]
                    best_j = j
            
            if best_j == -1:
                return  # Không tìm được giải pháp khả thi
            
            route.append(best_j)
            cost += self.c[cur][best_j]
            visited |= 1 << (best_j - 1)
            load += self.q[best_j]
            cur = best_j
        
        # Quay về depot
        cost += self.c[cur][0]
        
        if cost < self.best_cost:
            self.best_cost = cost
            self.best_route = route[:]
    
    def dfs(self, cur: int, visited: int, load: int, cost: int):
        """
        DFS với pruning
        
        Args:
            cur: node hiện tại
            visited: bitmask các nodes đã thăm
            load: tải trọng xe hiện tại
            cost: chi phí hiện tại
        """
        if self.time_up():
            return
        
        # Pruning: nếu cost >= best_cost thì cắt nhánh
        if cost >= self.best_cost:
            return
        
        # Kiểm tra xem đã thăm hết tất cả nodes
        full = (1 << (2 * self.n)) - 1
        if visited == full:
            total = cost + self.c[cur][0]
            if total < self.best_cost:
                self.best_cost = total
                self.best_route = self.cur_route[:]
            return
        
        # Pruning: nếu lower bound >= best_cost thì cắt nhánh
        if cost + self.lower_bound_remaining(visited) >= self.best_cost:
            return
        
        # Tìm các node ứng viên
        candidates = []
        for j in range(1, 2 * self.n + 1):
            # Bỏ qua nếu đã thăm
            if visited & (1 << (j - 1)):
                continue
            
            # Nếu là delivery, kiểm tra pickup đã được thăm chưa
            if j > self.n and not (visited & (1 << (j - self.n - 1))):
                continue
            
            # Kiểm tra sức chứa
            new_load = load + self.q[j]
            if new_load < 0 or new_load > self.k:
                continue
            
            candidates.append((self.c[cur][j], j))
        
        # Sắp xếp theo chi phí tăng dần (best-first)
        candidates.sort()
        
        # Duyệt DFS
        for _, j in candidates:
            self.cur_route.append(j)
            self.dfs(j, visited | (1 << (j - 1)), load + self.q[j], cost + self.c[cur][j])
            self.cur_route.pop()
            if self.aborted:
                return
    
    def solve(self, time_limit: float = 60.0) -> Tuple[List[int], int, float]:
        """
        Giải bài toán CBUS
        
        Args:
            time_limit: giới hạn thời gian (giây)
        
        Returns:
            (route, best_cost, elapsed_time)
        """
        self.time_limit = time_limit
        self.start_time = time.time()
        self.nodes_explored = 0
        self.aborted = False
        
        # Bước 1: Khởi tạo với nearest-neighbor
        self.nearest_neighbor_seed()
        
        # Bước 2: DFS với pruning
        self.cur_route = []
        self.dfs(0, 0, 0, 0)
        
        elapsed = time.time() - self.start_time
        
        return self.best_route, int(self.best_cost), elapsed


def read_cbus_input(file_path: str) -> Tuple[int, int, List[List[int]]]:
    """Đọc input từ file định dạng: n k + ma trận cost"""
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    first_line = lines[0].split()
    n = int(first_line[0])
    k = int(first_line[1])
    
    size = 2 * n + 1
    c = []
    idx = 0
    
    for i in range(size):
        if i == 0:
            row = list(map(int, first_line[2:]))
            remaining = size - len(row)
            if remaining > 0:
                row.extend(map(int, lines[1].split()[:remaining]))
            idx = 1
        else:
            start_idx = idx
            while len(c) < i + 1:
                row = list(map(int, lines[start_idx].split()))
                c.append(row)
                start_idx += 1
                if start_idx >= len(lines):
                    break
    
    # Đảm bảo ma trận đúng kích thước
    assert len(c) == size
    for row in c:
        assert len(row) == size
    
    return n, k, c


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        time_limit = float(sys.argv[2]) if len(sys.argv) > 2 else 60.0
        
        n, k, c = read_cbus_input(file_path)
        solver = CBUSBnB(n, k, c)
        route, cost, elapsed = solver.solve(time_limit)
        
        print(f"n={n}")
        if route:
            print(" ".join(map(str, route)))
        else:
            print("-1")
        
        # Verbose output
        print(f"# cost={cost}", file=sys.stderr)
        print(f"# time={elapsed:.3f}s", file=sys.stderr)
        print(f"# nodes_explored={solver.nodes_explored}", file=sys.stderr)
        print(f"# status={'TIMEOUT' if solver.aborted else 'OPTIMAL'}", file=sys.stderr)

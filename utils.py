"""
Utility functions for CBUS experiments
"""

import os
import re
from typing import List, Tuple, Dict, Optional
from pathlib import Path


def read_cbus_file(file_path: str) -> Tuple[int, int, List[List[int]]]:
    """
    Đọc file định dạng: n k + ma trận cost (2n+1) x (2n+1)
    
    Args:
        file_path: đường dẫn tới file input
    
    Returns:
        (n, k, cost_matrix)
    """
    with open(file_path, 'r') as f:
        content = f.read().strip()
    
    data = content.split()
    n = int(data[0])
    k = int(data[1])
    
    size = 2 * n + 1
    expected_elements = 2 + size * size
    
    if len(data) < expected_elements:
        raise ValueError(f"Không đủ dữ liệu: cần {expected_elements}, nhận {len(data)}")
    
    # Parse cost matrix
    c = [[0] * size for _ in range(size)]
    idx = 2
    for i in range(size):
        for j in range(size):
            c[i][j] = int(data[idx])
            idx += 1
    
    return n, k, c


def write_cbus_file(file_path: str, n: int, k: int, cost_matrix: List[List[int]]):
    """Ghi file định dạng CBUS"""
    with open(file_path, 'w') as f:
        f.write(f"{n} {k}\n")
        size = 2 * n + 1
        for i in range(size):
            f.write(" ".join(map(str, cost_matrix[i])) + "\n")


def load_data_directory(directory: str) -> Dict[str, Tuple[int, int, List[List[int]]]]:
    """
    Tải tất cả file CBUS từ thư mục
    
    Returns:
        Dict[instance_name, (n, k, cost_matrix)]
    """
    data = {}
    
    if not os.path.isdir(directory):
        raise ValueError(f"Thư mục không tồn tại: {directory}")
    
    files = sorted([f for f in os.listdir(directory) if f.endswith('.txt')])
    
    for file_name in files:
        file_path = os.path.join(directory, file_name)
        try:
            n, k, c = read_cbus_file(file_path)
            instance_name = file_name.replace('.txt', '')
            data[instance_name] = (n, k, c)
        except Exception as e:
            print(f"Lỗi khi tải {file_name}: {e}")
    
    return data


def calculate_route_cost(route: List[int], cost_matrix: List[List[int]]) -> int:
    """Tính chi phí của một route"""
    if not route:
        return 0
    
    total = cost_matrix[0][route[0]]
    for i in range(len(route) - 1):
        total += cost_matrix[route[i]][route[i + 1]]
    total += cost_matrix[route[-1]][0]
    
    return total


def validate_route(route: List[int], n: int, k: int, cost_matrix: List[List[int]]) -> Tuple[bool, str]:
    """
    Kiểm tra xem route có hợp lệ không
    
    Returns:
        (is_valid, error_message)
    """
    if not route:
        return False, "Route rỗng"
    
    if len(route) != 2 * n:
        return False, f"Route sai kích thước: {len(route)} != {2 * n}"
    
    # Kiểm tra tất cả nodes 1..2n được ghé đúng 1 lần
    visited = set(route)
    expected = set(range(1, 2 * n + 1))
    if visited != expected:
        return False, f"Có nodes thiếu hoặc trùng lặp"
    
    # Kiểm tra precedence constraints (pickup i trước delivery i+n)
    for i in range(1, n + 1):
        pickup_idx = route.index(i)
        delivery_idx = route.index(i + n)
        if pickup_idx >= delivery_idx:
            return False, f"Pickup {i} phải trước Delivery {i + n}"
    
    # Kiểm tra capacity constraints
    load = 0
    for node in route:
        if node <= n:
            load += 1
        else:
            load -= 1
        
        if load < 0 or load > k:
            return False, f"Vượt quá sức chứa {k} ở node {node} (tải={load})"
    
    return True, "OK"


def print_route_details(route: List[int], cost_matrix: List[List[int]], n: int, k: int):
    """In chi tiết của route"""
    total_cost = calculate_route_cost(route, cost_matrix)
    
    print("\n" + "=" * 70)
    print(f"{'Node':<8} | {'Type':<20} | {'Load':<10} | {'Cumulative':<12}")
    print("-" * 70)
    
    current = 0
    cumulative = 0
    load = 0
    
    # Depot
    print(f"{0:<8} | {'Depot (Start)':<20} | {load}/{k:<8} | {cumulative:<12.0f}")
    
    for node in route:
        edge_cost = cost_matrix[current][node]
        cumulative += edge_cost
        
        if node <= n:
            node_type = f"Pickup {node}"
            load += 1
        else:
            node_type = f"Delivery {node - n}"
            load -= 1
        
        print(f"{node:<8} | {node_type:<20} | {load}/{k:<8} | {cumulative:<12.0f}")
        current = node
    
    # Return to depot
    edge_cost = cost_matrix[current][0]
    cumulative += edge_cost
    print(f"{0:<8} | {'Depot (End)':<20} | {load}/{k:<8} | {cumulative:<12.0f}")
    
    print("-" * 70)
    print(f"Total Cost: {total_cost}")
    print("=" * 70 + "\n")


def extract_instance_name(file_path: str) -> str:
    """Trích tên instance từ đường dẫn file"""
    return Path(file_path).stem

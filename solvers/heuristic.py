import sys
import math
import random


def read_input():
    input_data = sys.stdin.read().split()
    
    if not input_data:
        return 0, 0, []

    n = int(input_data[0])
    k = int(input_data[1])
    
    c = []
    idx = 2
    size = 2 * n + 1
    for i in range(size):
        row = [int(input_data[idx + j]) for j in range(size)]
        c.append(row)
        idx += size
        
    return n, k, c


def calc_route_cost(route, c):
    if not route: return 0
    cost = c[0][route[0]]
    for i in range(len(route) - 1):
        cost += c[route[i]][route[i+1]]
    cost += c[route[-1]][0]
    return cost

def initial_solution(n, k, c):
    route = []
    visited = set()
    current_node = 0
    current_load = 0

    for _ in range(2 * n):
        best_dist = float('inf')
        best_neighbor = -1

        if current_load < k:
            for i in range(1, n + 1):
                if i not in visited:
                    dist = c[current_node][i]
                    if dist < best_dist:
                        best_dist, best_neighbor = dist, i

        for i in range(n + 1, 2 * n + 1):
            if i not in visited and (i - n) in visited:
                dist = c[current_node][i]
                if dist < best_dist:
                    best_dist, best_neighbor = dist, i

        route.append(best_neighbor)
        visited.add(best_neighbor)
        current_node = best_neighbor

        if best_neighbor <= n:
            current_load += 1
        else:
            current_load -= 1

    return route


# ALNS
def random_removal(route, num_remove, n):
    new_route = route[:]
    reqs_in_route = [node for node in new_route if node <= n]
    
    if not reqs_in_route: return new_route, []
    
    num_to_remove = min(num_remove, len(reqs_in_route))
    to_remove = random.sample(reqs_in_route, num_to_remove)
    
    for req in to_remove:
        new_route.remove(req)
        new_route.remove(req + n)
        
    return new_route, to_remove

def alns_optimize(route, c, n, k_cap, iterations=150, time_limit=None):
    best_route = route[:]
    best_cost = calc_route_cost(route, c)
    
    current_route = route[:]
    current_cost = best_cost
    
    T = 100.0 
    cooling_rate = 0.95
    
    for iteration in range(iterations):
        num_remove = random.randint(1, min(40, max(1, n // 20)))
        repaired_route, removed_reqs = random_removal(current_route, num_remove, n)
        
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
                if loads[idx] >= k_cap:        # >= thay vì ==
                    last_full = idx
                next_full[idx] = last_full
                
            best_req_cost = float('inf')
            best_x, best_y = -1, -1
            
            for x in range(1, len(full_route)):
                if loads[x-1] >= k_cap:          
                    continue
                
                prev_x = full_route[x-1]
                node_x = full_route[x]
                
                cost_P = c[prev_x][P] + c[P][node_x] - c[prev_x][node_x]
                
                # FIX 1: Thêm + 1 để range() bao phủ được vị trí chặn cuối cùng
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
            
            # FIX 2: Bắt buộc phải có điều kiện bảo vệ tránh chèn bừa bãi khi best_x = -1
            if best_x != -1 and best_y != -1:
                if best_x == best_y:
                    full_route.insert(best_x, D)
                    full_route.insert(best_x, P)
                else:
                    # Chú ý logic index: insert y trước (vì y >= x), sau đó insert x 
                    # để không làm lệch index của y
                    full_route.insert(best_y, D)
                    full_route.insert(best_x, P)
            else:
                # Fallback an toàn cực đoan: Chèn ngay sau Depot nếu không tìm được cách (rất hiếm khi xảy ra nếu max_y fix đúng)
                full_route.insert(1, D)
                full_route.insert(1, P)
                
        repaired_route = full_route[1:-1]
        new_cost = calc_route_cost(repaired_route, c)
        
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
        
    return best_route, best_cost


def main():
    n, k, c = read_input()
    if n == 0:
        return

    init_route = initial_solution(n, k, c)
    

    best_route, best_cost = alns_optimize(init_route, c, n, k, iterations=150)
    
    print(n)
    print(" ".join(map(str, best_route)))

if __name__ == "__main__":
    random.seed(42) 
    main()
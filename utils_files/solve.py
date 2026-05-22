import math
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

# --- 1. DATA PARSER ---
class CBUSData:
    def __init__(self, n, k, matrix):
        self.n = n
        self.k = k
        self.matrix = matrix
        self.num_nodes = 2 * n + 1
        self.depot = 0
        self.pickups = list(range(1, n + 1))
        self.deliveries = list(range(n + 1, 2 * n + 1))

def load_homberger_to_cbus(file_path, k_capacity=50):
    nodes = {}
    with open(file_path, 'r') as f:
        lines = f.readlines()
        
        start_idx = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('0 '):
                start_idx = i
                break
                
        for line in lines[start_idx:]:
            parts = line.split()
            if len(parts) >= 3:
                node_id = int(parts[0])
                x = float(parts[1])
                y = float(parts[2])
                nodes[node_id] = (x, y)
                
    total_customers = len(nodes) - 1 
    n = total_customers // 2
    
    matrix = []
    for i in range(2 * n + 1):
        row = []
        for j in range(2 * n + 1):
            if i == j:
                row.append(0)
            else:
                x1, y1 = nodes[i]
                x2, y2 = nodes[j]
                dist = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
                row.append(int(dist))
        matrix.append(row)
        
    return CBUSData(n, k_capacity, matrix)

# --- 2. SOLVER (META-HEURISTICS) ---
def solve_cbus_metaheuristic(data, time_limit_seconds=60):
    # Khởi tạo Routing Index Manager & Model
    manager = pywrapcp.RoutingIndexManager(data.num_nodes, 1, data.depot)
    routing = pywrapcp.RoutingModel(manager)

    # Đăng ký hàm tính khoảng cách
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data.matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Thêm Dimension cho Quãng đường (Bắt buộc để check logic Đón trước Trả sau)
    dimension_name = 'Distance'
    routing.AddDimension(
        transit_callback_index,
        0,          # no slack
        30000000,   # maximum total distance (để thật lớn)
        True,       # start cumul to zero
        dimension_name)
    distance_dimension = routing.GetDimensionOrDie(dimension_name)

    # Đăng ký hàm sức chứa (Capacity)
    def demand_callback(from_index):
        node = manager.IndexToNode(from_index)
        if node in data.pickups: return 1
        elif node in data.deliveries: return -1
        else: return 0

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimension(
        demand_callback_index,
        0,          # null capacity slack
        data.k,     # vehicle capacity k
        True,       # start cumul to zero
        'Capacity')

    # Thiết lập Ràng buộc Đón & Trả (Pickup and Delivery)
    for i in range(1, data.n + 1):
        pickup_idx = manager.NodeToIndex(i)
        delivery_idx = manager.NodeToIndex(i + data.n)
        
        routing.AddPickupAndDelivery(pickup_idx, delivery_idx)
        # Bắt buộc đi chung 1 xe (Dù bài này chỉ có 1 xe nhưng OR-Tools bắt buộc cấu hình)
        routing.solver().Add(routing.VehicleVar(pickup_idx) == routing.VehicleVar(delivery_idx))
        # Bắt buộc: Đón phải diễn ra trước Trả
        routing.solver().Add(
            distance_dimension.CumulVar(pickup_idx) <= distance_dimension.CumulVar(delivery_idx)
        )

    # Cấu hình Meta-heuristics
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    
    # Chiến lược sinh nghiệm ban đầu: Cực kỳ quan trọng cho dữ liệu lớn
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION)
    
    # Chiến lược Meta-heuristic: Tránh kẹt ở Local Minima
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    
    search_parameters.time_limit.seconds = time_limit_seconds
    search_parameters.log_search = True # Bật log để quan sát thuật toán tìm kiếm

    print(f"Bắt đầu giải với bộ dữ liệu n={data.n}, giới hạn thời gian: {time_limit_seconds}s...")
    solution = routing.SolveWithParameters(search_parameters)

    # In kết quả
    if solution:
        print(f"\n✅ Đã tìm thấy lộ trình! Tổng chi phí: {solution.ObjectiveValue()}")
        # (Bạn có thể viết thêm vòng lặp while để in chi tiết lộ trình ra file txt)
    else:
        print("\n❌ Không tìm thấy giải pháp nào trong thời gian giới hạn.")

if __name__ == '__main__':
    # Giả định xe chứa được 50 người cùng lúc
    cbus_data = load_homberger_to_cbus('homberger_1000_customer_instances\C1_10_1.TXT', k_capacity=50)
    # Cấu hình chạy trong 1 phút để test
    solve_cbus_metaheuristic(cbus_data, time_limit_seconds=60)
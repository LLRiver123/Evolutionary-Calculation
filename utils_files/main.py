import math
import time
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

# ==========================================
# 1. DATA PARSER (Xử lý file lc101.txt)
# ==========================================
class CBUSData:
    def __init__(self, n, k, matrix):
        self.n = n
        self.k = k
        self.matrix = matrix
        self.num_nodes = 2 * n + 1
        self.depot = 0
        self.pickups = list(range(1, n + 1))
        self.deliveries = list(range(n + 1, 2 * n + 1))

def load_lilim_to_cbus(file_path, k_capacity):
    """
    Đọc file Li & Lim (như lc101.txt), lọc ra các điểm đón trả, 
    đánh số lại theo luật 1->n (Đón) và n+1->2n (Trả), và tính ma trận khoảng cách.
    """
    with open(file_path, 'r') as f:
        lines = f.readlines()
        
    nodes = {}
    for line in lines:
        parts = line.strip().split()
        
        # ĐÃ SỬA: Thêm điều kiện len(parts) < 9 để bỏ qua dòng "25 200 1" ở đầu file
        if not parts or not parts[0].isdigit() or len(parts) < 9: 
            continue
            
        nid = int(parts[0])
        x, y = float(parts[1]), float(parts[2])
        demand = int(parts[3])
        delivery_id = int(parts[8])
        nodes[nid] = {'x': x, 'y': y, 'demand': demand, 'delivery_id': delivery_id}
        
    pickups = [(nid, data['delivery_id']) for nid, data in nodes.items() if data['demand'] > 0]
    n = len(pickups)
    
    # Sắp xếp lại: 0 (Depot) -> 1..n (Pickups) -> n+1..2n (Deliveries)
    ordered_nodes = [nodes[0]] 
    for p_id, _ in pickups: ordered_nodes.append(nodes[p_id])
    for _, d_id in pickups: ordered_nodes.append(nodes[d_id])
        
    size = 2 * n + 1
    matrix = [[0] * size for _ in range(size)]
    for i in range(size):
        for j in range(size):
            if i != j:
                dx = ordered_nodes[i]['x'] - ordered_nodes[j]['x']
                dy = ordered_nodes[i]['y'] - ordered_nodes[j]['y']
                # Nhân 10 để giữ độ chính xác sau dấu phẩy khi ép kiểu int
                matrix[i][j] = int(math.sqrt(dx**2 + dy**2) * 10) 
                
    return CBUSData(n, k_capacity, matrix)

# ==========================================
# 2. IN KẾT QUẢ ĐẸP MẮT CHO BÁO CÁO
# ==========================================
def print_detailed_solution(data, manager, routing, solution, time_elapsed):
    print("\n" + "="*60)
    print(" KẾT QUẢ TỐI ƯU (META-HEURISTICS) ")
    print("="*60)
    print(f"⏱ Thời gian chạy  : {time_elapsed:.2f} giây")
    # Chia 10 vì lúc tạo ma trận ta đã nhân 10
    print(f"🛣 Tổng quãng đường: {solution.ObjectiveValue() / 10.0} đơn vị") 
    print("-" * 60)
    
    index = routing.Start(0)
    route_details = []
    current_load = 0
    current_distance = 0
    
    distance_dim = routing.GetDimensionOrDie('Distance')
    
    print(f"{'Node':<10} | {'Loại':<15} | {'Tải trọng xe':<15} | {'Quãng đường tích lũy'}")
    print("-" * 60)
    
    while not routing.IsEnd(index):
        node_index = manager.IndexToNode(index)
        
        # Xác định loại Node (Đón/Trả/Depot) và cập nhật tải trọng
        if node_index == 0:
            node_type = "🏭 Depot (Bắt đầu)"
        elif 1 <= node_index <= data.n:
            node_type = f"🟢 Đón khách {node_index}"
            current_load += 1
        else:
            node_type = f"🔴 Trả khách {node_index - data.n}"
            current_load -= 1
            
        dist_var = distance_dim.CumulVar(index)
        current_distance = solution.Value(dist_var) / 10.0
        
        print(f"{node_index:<10} | {node_type:<15} | {current_load:<5} / {data.k:<7} | {current_distance:.1f}")
        route_details.append(str(node_index))
        
        index = solution.Value(routing.NextVar(index))
        
    # In điểm kết thúc (Về lại Depot)
    node_index = manager.IndexToNode(index)
    dist_var = distance_dim.CumulVar(index)
    current_distance = solution.Value(dist_var) / 10.0
    print(f"{node_index:<10} | 🏁 Depot (Kết thúc)| {current_load:<5} / {data.k:<7} | {current_distance:.1f}")
    route_details.append(str(node_index))
    
    print("-" * 60)
    print("Lộ trình dạng mảng (Dùng để vẽ đồ thị):")
    print(" -> ".join(route_details))
    print("=" * 60 + "\n")

# ==========================================
# 3. MÔ HÌNH OR-TOOLS SOLVER
# ==========================================
def solve_cbus_project(data, time_limit_seconds=60):
    manager = pywrapcp.RoutingIndexManager(data.num_nodes, 1, data.depot)
    routing = pywrapcp.RoutingModel(manager)

    # 1. Hàm khoảng cách
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data.matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # 2. Dimension: Quãng đường
    routing.AddDimension(
        transit_callback_index,
        0, 300000000, True, 'Distance')
    distance_dimension = routing.GetDimensionOrDie('Distance')

    # 3. CHUẨN HÓA SỨC CHỨA (Khắc phục bùng nổ tổ hợp)
    def capacity_demand(from_index):
        node = manager.IndexToNode(from_index)
        if 1 <= node <= data.n: 
            return 1   # Đón 1 người
        elif data.n + 1 <= node <= 2 * data.n: 
            return -1  # Trả 1 người
        return 0       # Depot

    demand_callback_index = routing.RegisterUnaryTransitCallback(capacity_demand)
    routing.AddDimension(
        demand_callback_index,
        0,      # KHÓA SLACK = 0 (Bộ giải không cần tốn thời gian đoán slack)
        data.k, # Sức chứa tối đa
        True, 
        'Capacity')

    # 4. Ràng buộc Đón - Trả
    for i in range(1, data.n + 1):
        pickup_idx = manager.NodeToIndex(i)
        delivery_idx = manager.NodeToIndex(i + data.n)
        
        routing.AddPickupAndDelivery(pickup_idx, delivery_idx)
        routing.solver().Add(routing.VehicleVar(pickup_idx) == routing.VehicleVar(delivery_idx))
        
        # Bắt buộc: Đón trước Trả sau
        routing.solver().Add(
            distance_dimension.CumulVar(pickup_idx) <= distance_dimension.CumulVar(delivery_idx)
        )
        # BỎ ràng buộc Slack rườm rà cũ đi, Dimension Capacity tự xử lý logic tải trọng.

    # 5. Cấu hình tìm kiếm (Sửa chiến lược khởi tạo)
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    
    # CHIẾN LƯỢC TỐT NHẤT CHO PDP (Giúp tìm nghiệm đầu tiên ngay lập tức)
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION
    search_parameters.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    
    search_parameters.time_limit.seconds = time_limit_seconds
    search_parameters.log_search = True

    print(f"[*] Bắt đầu giải bài toán CBUS với N={data.n} hành khách...")
    print(f"[*] Sức chứa xe: {data.k}. Giới hạn thời gian: {time_limit_seconds}s")
    
    start_time = time.time()
    solution = routing.SolveWithParameters(search_parameters)
    end_time = time.time()

    if solution:
        print_detailed_solution(data, manager, routing, solution, end_time - start_time)
    else:
        print("\n❌ Lỗi: Không tìm thấy giải pháp.")

if __name__ == '__main__':
    # 1. Đọc dữ liệu từ file Li & Lim. Chọn sức chứa xe (VD: k = 20)
    cbus_data = load_lilim_to_cbus('lc101.txt', k_capacity=20)
    
    # 2. Giải quyết bài toán trong 30 giây (có thể tăng lên 300s cho kết quả xịn hơn)
    solve_cbus_project(cbus_data, time_limit_seconds=30)
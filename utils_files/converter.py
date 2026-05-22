import math

def convert_li_lim_to_matrix(input_file, output_file, k_capacity):
    with open(input_file, 'r') as f:
        lines = f.readlines()
        
    nodes = {}
    for line in lines:
        parts = line.strip().split()
        # Bỏ qua các dòng trống hoặc dòng header (không bắt đầu bằng số)
        if not parts or not parts[0].isdigit():
            continue
            
        # Cấu trúc Li & Lim: ID, X, Y, Demand, Ready, Due, Service, Pickup_ID, Delivery_ID
        nid = int(parts[0])
        x = float(parts[1])
        y = float(parts[2])
        demand = int(parts[3])
        delivery_id = int(parts[8]) # Cột cuối cùng là ID của điểm trả
        
        nodes[nid] = {'x': x, 'y': y, 'demand': demand, 'delivery_id': delivery_id}
        
    # Lọc ra các điểm đón (Demand > 0)
    pickups = []
    for nid, data in nodes.items():
        if data['demand'] > 0:
            pickups.append((nid, data['delivery_id']))
            
    n = len(pickups)
    
    # Sắp xếp lại danh sách đỉnh để tuân thủ quy luật i và i+n
    # Index 0: Depot
    # Index 1 -> n: Các điểm đón (Pickups)
    # Index n+1 -> 2n: Các điểm trả tương ứng (Deliveries)
    ordered_nodes = [nodes[0]] 
    
    for p_id, d_id in pickups:
        ordered_nodes.append(nodes[p_id])
        
    for p_id, d_id in pickups:
        ordered_nodes.append(nodes[d_id])
        
    # Tính ma trận khoảng cách
    size = 2 * n + 1
    matrix = [[0] * size for _ in range(size)]
    
    for i in range(size):
        for j in range(size):
            if i != j:
                dx = ordered_nodes[i]['x'] - ordered_nodes[j]['x']
                dy = ordered_nodes[i]['y'] - ordered_nodes[j]['y']
                # Khoảng cách làm tròn về số nguyên
                matrix[i][j] = int(math.sqrt(dx**2 + dy**2))
                
    # Ghi ra file theo chuẩn Input của đề bài
    with open(output_file, 'w') as f:
        f.write(f"{n} {k_capacity}\n")
        for row in matrix:
            f.write(" ".join(map(str, row)) + "\n")
            
    print(f"Đã tạo file {output_file} thành công! (n={n}, k={k_capacity})")

if __name__ == '__main__':
    # Chuyển đổi file lc101.txt sang input chuẩn với sức chứa k=50
    convert_li_lim_to_matrix("lc101.txt", "input.txt", 50)
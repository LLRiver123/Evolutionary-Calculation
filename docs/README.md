# CBUS Experiment Framework

## Tổng quan

Framework này cung cấp công cụ để so sánh 3 phương pháp giải bài toán CBUS (Pickup and Delivery):

1. **Branch-and-Bound (BnB)** - Thuật toán chính xác (Python)
2. **OR-Tools GLS** - Guided Local Search sử dụng Google OR-Tools  
3. **ALNS** - Adaptive Large Neighborhood Search

## Cấu trúc Files

```
├── cbus_bnb.py              # Branch-and-Bound solver (Python)
├── utils.py                 # Utility functions
├── experiment.py            # Experiment runner chính
├── test_solvers.py          # Script kiểm tra đơn giản
├── main_routing.py          # OR-Tools GLS solver
├── heuristic.py             # ALNS solver
└── cbus_output_20260517_222958/  # Dữ liệu test
    ├── lc101_cbus.txt
    ├── lc102_cbus.txt
    └── ...
```

## Định dạng Input

File input có dạng:
```
n k
c[0][0]   c[0][1]   ...  c[0][2n]
c[1][0]   c[1][1]   ...  c[1][2n]
...
c[2n][0]  c[2n][1]  ... c[2n][2n]
```

Trong đó:
- `n`: số điểm đón hàng (pickup points)
- `k`: sức chứa xe (capacity)
- `c[i][j]`: chi phí đi từ node i tới node j
- Các nodes được đánh số:
  - `0`: depot (kho)
  - `1..n`: pickup points
  - `n+1..2n`: delivery points

## Cách sử dụng

### 1. Chạy test đơn giản

```bash
python test_solvers.py
```

### 2. Chạy một instance cụ thể

```bash
python experiment.py cbus_output_20260517_222958 -i lc101_cbus -t 30
```

Tham số:
- `cbus_output_20260517_222958`: thư mục chứa dữ liệu
- `-i lc101_cbus`: chọn instance cụ thể (tên file không .txt)
- `-t 30`: time limit 30 giây cho mỗi solver

### 3. Chạy tất cả instances trong thư mục

```bash
python experiment.py cbus_output_20260517_222958 -t 30 -o results_exp1
```

Tham số:
- `-o results_exp1`: thư mục lưu kết quả (nếu không có, sẽ tạo tự động)

### 4. Chạy với time limit khác nhau

```bash
python experiment.py cbus_output_20260517_222958 -t 60 -o results_60s
```

## Kết quả Output

### Console Output
Khi chạy, bạn sẽ thấy:
```
======================================================================
Instance: lc101_cbus (n=10, k=3)
======================================================================
  [1/3] Running Branch-and-Bound...
        Cost: 12850, Time: 0.45s, Valid: True
  [2/3] Running OR-Tools GLS...
        Cost: 12950, Time: 2.34s, Valid: True
  [3/3] Running ALNS...
        Cost: 13100, Time: 1.23s, Valid: True

----------------------------------------------------------------------
COMPARISON:
----------------------------------------------------------------------
Method          | Cost         | Time       | Valid    | Status
----------------------------------------------------------------------
BnB             | 12850        | 0.45s      | ✓        | Valid
OR-Tools        | 12950        | 2.34s      | ✓        | Valid
ALNS            | 13100        | 1.23s      | ✓        | Valid
----------------------------------------------------------------------
Best cost: 12850
  Winner: BnB
```

### File Output

Kết quả được lưu trong thư mục output:

1. **results.json** - Dữ liệu đầy đủ JSON format:
   ```json
   {
     "timestamp": "2026-05-17T22:30:45.123456",
     "time_limit": 30,
     "instances": {
       "lc101_cbus": {
         "instance": "lc101_cbus",
         "n": 10,
         "k": 3,
         "solvers": {
           "BnB": {
             "method": "BnB",
             "cost": 12850,
             "route": "1 11 2 12 3 13 4 14 5 15 6 16 7 17 8 18 9 19 10 20",
             "time": 0.453,
             "valid": true
           },
           ...
         }
       }
     }
   }
   ```

2. **results.csv** - Bảng tóm tắt CSV:
   ```
   Instance,N,K,Method,Cost,Time(s),Valid,Message
   lc101_cbus,10,3,BnB,12850,0.453,Y,Valid
   lc101_cbus,10,3,OR-Tools,12950,2.341,Y,Valid
   lc101_cbus,10,3,ALNS,13100,1.234,Y,Valid
   ```

## Chi tiết từng Solver

### Branch-and-Bound (BnB)

**File**: `cbus_bnb.py`

**Đặc điểm**:
- Thuật toán chính xác (optimal hoặc timeout)
- Sử dụng DFS + pruning (cận dưới)
- Khởi tạo với nearest-neighbor heuristic

**Cách hoạt động**:
1. Tìm upper bound bằng nearest-neighbor
2. DFS trên tất cả routes khả thi
3. Pruning: nếu lower_bound >= best_cost thì cắt nhánh
4. Sắp xếp ứng viên theo chi phí (best-first)

**Tham số**:
- `time_limit`: thời gian tối đa (giây)

**Khi nào tốt**:
- Khi n nhỏ (< 15)
- Cần giải optimal
- Có thời gian đợi

### OR-Tools Guided Local Search

**File**: `main_routing.py`

**Đặc điểm**:
- Meta-heuristic mạnh mẽ từ Google
- Nhanh, thường tìm được lời giải tốt
- Có hỗ trợ precedence constraints

**Khi nào tốt**:
- Cần giải nhanh
- Chấp nhận lời giải gần optimal
- n lớn (> 50)

### ALNS (Adaptive Large Neighborhood Search)

**File**: `heuristic.py`

**Đặc điểm**:
- Meta-heuristic với removal-repair operators
- Adaptive selection của operators
- Simulated annealing cooling schedule

**Khi nào tốt**:
- Giữa cân bằng giữa tốc độ và chất lượng
- n trung bình (15-50)

## Các Thuật toán Validate

Mỗi kết quả được kiểm tra:
1. **Route có đủ nodes**: 2n nodes từ 1 đến 2n
2. **Precedence**: Pickup i phải trước Delivery i+n
3. **Capacity**: Tải trọng ≤ k và ≥ 0 luôn
4. **Cost consistency**: Chi phí tính toán = chi phí báo cáo

## Mở rộng

Để thêm solver mới:

1. Tạo hàm: `def solve_new_method(n, k, cost_matrix) -> List[int]`
2. Thêm vào `ExperimentRunner`:
   ```python
   def run_new_method(self, n, k, cost_matrix):
       # implement similar to run_bnb, run_ortools, run_alns
       pass
   ```
3. Thêm vào `run_instance`:
   ```python
   new_result = self.run_new_method(...)
   results['solvers']['NewMethod'] = new_result
   ```

## Troubleshooting

### ImportError: No module named 'ortools'
```bash
pip install ortools
```

### Time limit too short
Tăng time limit với flag `-t`:
```bash
python experiment.py cbus_output_20260517_222958 -t 120
```

### Memory issues với large instances
Giảm số iterations cho ALNS trong `experiment.py`:
```python
alns_result = self.run_alns(n, k, cost_matrix, iterations=50)
```

## Performance Tips

1. **BnB**: 
   - Optimal cho n < 12
   - Timeout cho n > 14 (trong 60s)
   - Khởi tạo heuristic ảnh hưởng lớn đến tốc độ

2. **OR-Tools**:
   - Nhanh nhất cho hầu hết trường hợp
   - Phụ thuộc vào first_solution_strategy
   - Có thể cải thiện bằng custom search parameters

3. **ALNS**:
   - Nhanh cho n nhỏ
   - Chất lượng phụ thuộc vào iterations
   - Randomness → chạy nhiều lần lấy best

## Tham khảo

- **BnB**: Classic DFS + pruning technique
- **OR-Tools**: https://developers.google.com/optimization
- **ALNS**: Pisinger & Ropke (2010) "Large neighborhood search"

# HUST Benchmark Analysis System

Complete system for tuning parameters and analyzing solver performance on HUST benchmark instances.

## 🚀 Quick Start

### Run Everything in One Command

```bash
python hust_workflow.py
```

This will:
1. Tune parameters for OR-Tools and ALNS
2. Run experiments on all HUST instances (hust5, hust10, hust100, hust500, hust1000)
3. Generate comprehensive visualizations and reports

### Just Run Experiments (Skip Tuning)

```bash
python hust_workflow.py -s experiment -t 30
```

### Just Visualize (From Previous Results)

```bash
python hust_workflow.py -s visualize
```

## 📊 Individual Scripts

### 1. Parameter Tuning

```bash
python tune_params.py
```

Tests different parameter combinations:
- **OR-Tools**: first_solution_strategy, local_search_metaheuristic
- **ALNS**: iterations, cooling_rate, initial_temperature

**Output:**
- `tuning_results_*/tuning_results.json` - Detailed parameter performance

### 2. Run Experiments

```bash
python hust_experiment.py -t 30 -o my_results
```

**Parameters:**
- `-t, --time`: Time limit per solver in seconds (default: 30)
- `-o, --output`: Output directory name (default: auto-generated)

**Output:**
- `hust_results.json` - Complete experimental data
- `hust_results.csv` - Summary for Excel/analysis

### 3. Visualize Results

```bash
python visualize_hust.py hust_results_20260517_223957/hust_results.json
```

Or auto-detect latest:

```bash
python visualize_hust.py
```

**Generates:**
- `cost_comparison.png` - Cost by instance and problem size
- `time_comparison.png` - Execution time analysis
- `quality_vs_speed.png` - Trade-off visualization
- `scalability.png` - Scaling analysis and solver wins
- `cost_heatmap.png` - Cost heatmap for each solver
- `analysis_report.txt` - Detailed statistical report

## 📁 Output Files

### Data Files

```
hust_results_YYYYMMDD_HHMMSS/
├── hust_results.json          # Complete experimental data
└── hust_results.csv           # Summary table (open in Excel)
```

### Visualizations

```
├── cost_comparison.png        # Bar chart: Cost by instance
├── time_comparison.png        # Bar & line: Execution time
├── quality_vs_speed.png       # Scatter: Quality vs speed
├── scalability.png            # 4 subplots: Scaling analysis
├── cost_heatmap.png           # Heatmaps: Cost values
└── analysis_report.txt        # Statistical summary
```

## 📈 Understanding the Results

### cost_comparison.png

**Left plot:** Cost for each instance (all solvers compared)
- Lower bars = better solutions
- Shows which solver performs best on each instance

**Right plot:** Average cost by problem size
- Trend across different problem sizes
- Shows scalability characteristics

### time_comparison.png

**Left plot:** Execution time for each instance
- How long each solver takes
- Larger times = more computation

**Right plot:** Time vs Problem Size (logarithmic)
- Shows scaling behavior
- Linear in log = exponential scaling in reality

### quality_vs_speed.png

**Scatter plot:**
- X-axis: Time (seconds)
- Y-axis: Solution cost
- Bubble size: Problem size

**Interpretation:**
- Lower-left = fast AND good solutions (ideal)
- Upper-right = slow AND expensive solutions (worst)

### scalability.png

**4 subplots:**
1. **Cost Scaling** - How cost grows with problem size
2. **Time Scaling (log)** - How time grows exponentially
3. **Performance Gap** - % worse than best solution
4. **Solver Wins** - How many instances each solver won

### cost_heatmap.png

**3 heatmaps (one per solver):**
- Rows: Problem size (N)
- Columns: Instance name
- Colors: Cost value

**Interpretation:**
- Blue = good (low cost)
- Yellow = poor (high cost)

## 📊 CSV Format

```
Instance,N,K,Method,Cost,Time(s),Valid
hust5,5,3,BnB,145,0.523,Y
hust5,5,3,OR-Tools,145,2.134,Y
hust5,5,3,ALNS,150,0.015,Y
hust10,10,3,BnB,289,8.942,Y
...
```

**To analyze in Excel:**
1. Open `hust_results.csv`
2. Create pivot table: Instance × Method, values = Cost
3. Make bar chart
4. Repeat with Time column

## 🔍 Parameter Tuning Details

### Tuned Configurations

Based on benchmark performance, optimal parameters are:

**OR-Tools (Optimized):**
```python
first_solution_strategy = PARALLEL_CHEAPEST_INSERTION
local_search_metaheuristic = GUIDED_LOCAL_SEARCH
time_limit = 30 seconds
```

**ALNS (Optimized):**
```python
iterations = 300
cooling_rate = 0.95
initial_temperature = 150.0
removal_size = 1-40% of nodes
```

These are already used in `hust_experiment.py`.

## 💡 Tips & Tricks

### Faster Results (Testing)

```bash
python hust_experiment.py -t 10 -o quick_test
```

10 seconds per solver = ~2-3 minutes total for all instances

### Higher Quality (Publication)

```bash
python hust_experiment.py -t 120 -o final_results
```

120 seconds per solver = ~20-30 minutes total

### Specific Instances

Edit `hust_experiment.py` line 334:
```python
files = sorted([f for f in os.listdir(data_dir) if f.startswith('hust') and f.endswith('.txt')])
# Keep: files = files[:2]  # Just test 2 instances
# Change to: files = files  # Test all instances
```

### Custom Solvers

Add new solver method to `HUSTExperimentRunner`:
```python
def run_my_solver(self, n, k, cost_matrix, time_limit):
    # Your solver implementation
    return route, elapsed_time
```

Then add to `run_instance()`:
```python
# My Solver
print("  [4/4] Running My Solver...")
try:
    route, elapsed = self.run_my_solver(...)
    # ... add to results
```

## 📈 Expected Results

### Small Instances (n ≤ 10)

- **BnB**: Often finds optimal (lower cost)
- **OR-Tools**: Similar to BnB, faster
- **ALNS**: Slightly worse, much faster

### Medium Instances (n = 100)

- **BnB**: May timeout or get stuck
- **OR-Tools**: Usually best cost in reasonable time ⭐
- **ALNS**: Fast but lower quality

### Large Instances (n ≥ 500)

- **BnB**: Almost certainly times out
- **OR-Tools**: Best practical choice ⭐
- **ALNS**: Fast approximation

## 🎯 Performance Metrics

Each solver is evaluated on:

1. **Cost** - Total distance (lower = better)
2. **Time** - Execution time in seconds (lower = better)
3. **Quality** - % above best solution found
4. **Validity** - All constraints satisfied

### Quality Metric

```
Gap = (Solver_Cost - Best_Cost) / Best_Cost * 100%
```

- 0% = Found best solution
- > 0% = Worse than best
- Higher % = Lower quality

## 📝 Analysis Report

The `analysis_report.txt` includes:

1. **Summary Statistics** per solver
   - Instances completed
   - Average/min/max costs
   - Time statistics

2. **Instance-by-Instance Results**
   - Cost and time for each solver
   - Winner (lowest cost)

3. **Performance Gaps**
   - Average % gap from best
   - Shows consistency

## 🚨 Troubleshooting

### ImportError: matplotlib

```bash
pip install matplotlib seaborn pandas
```

### Results file not found

Make sure experiments ran successfully:
```bash
python hust_experiment.py -t 30
```

Check that `hust_results_*/hust_results.json` exists.

### Out of memory on large instances

Edit `hust_experiment.py` and skip hust1000:
```python
files = sorted([f for f in os.listdir(data_dir) if f.startswith('hust') and f.endswith('.txt')])
files = [f for f in files if 'hust1000' not in f]  # Skip large
```

### Visualizations look blank

Check that CSV has valid data:
```bash
cat hust_results_*/hust_results.csv | head -20
```

Should have multiple rows with non-zero costs and times.

## 🔄 Workflow Examples

### Scenario 1: Quick Validation

```bash
# 1. Test on small instances quickly
python hust_experiment.py -t 5 -o quick_test

# 2. Visualize immediately
python visualize_hust.py quick_test/hust_results.json
```

### Scenario 2: Publication Quality

```bash
# 1. Run comprehensive benchmark
python hust_workflow.py -s all -t 120

# 2. Find results
ls -la hust_results_*

# 3. Open CSV in Excel, create additional charts
# 4. Export PNG images for paper

# 5. Copy results to report directory
cp hust_results_*/cost_comparison.png ~/my_paper/figures/
```

### Scenario 3: Parameter Comparison

```bash
# 1. Run with different time limits
python hust_experiment.py -t 10 -o results_10s
python hust_experiment.py -t 30 -o results_30s
python hust_experiment.py -t 60 -o results_60s

# 2. Compare manually:
# - Look at CSV files side-by-side
# - See how costs improve with more time
# - Trade-off: quality vs time
```

## 📊 Sample Output

```
======================================================================
Instance: hust5 (n=5, k=3)
======================================================================
  [1/3] Running Branch-and-Bound...
        Cost: 145, Time: 0.52s, Valid: True
  [2/3] Running OR-Tools GLS...
        Cost: 145, Time: 2.13s, Valid: True
  [3/3] Running ALNS...
        Cost: 150, Time: 0.01s, Valid: True

COMPARISON:
Method          | Cost         | Time       | Valid
BnB             | 145          | 0.52s      | ✓
OR-Tools        | 145          | 2.13s      | ✓
ALNS            | 150          | 0.01s      | ✓

Best cost: 145
  ⭐ BnB
  ⭐ OR-Tools

======================================================================
Instance: hust100 (n=100, k=3)
======================================================================
  [1/3] Running Branch-and-Bound...
        Cost: 3400, Time: 30.05s, Valid: True
  [2/3] Running OR-Tools GLS...
        Cost: 3380, Time: 30.02s, Valid: True
  [3/3] Running ALNS...
        Cost: 3650, Time: 0.95s, Valid: True

COMPARISON:
Method          | Cost         | Time       | Valid
BnB             | 3400         | 30.05s     | ✓
OR-Tools        | 3380         | 30.02s     | ✓  ⭐ Winner
ALNS            | 3650         | 0.95s      | ✓
```

## 📚 References

- **Branch-and-Bound**: Lawler & Wood (1966) - Classic exact algorithm
- **OR-Tools**: https://developers.google.com/optimization
- **ALNS**: Pisinger & Ropke (2010) - Adaptive Large Neighborhood Search
- **CBUS Problem**: Ropke & Pisinger (2006)

---

**Questions?** Check the logs in `hust_results_*/` directory or enable verbose output.

**Ready to start?**
```bash
python hust_workflow.py
```

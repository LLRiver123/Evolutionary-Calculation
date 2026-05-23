# CBUS Evolutionary Calculation Framework

## 📁 Project Structure

```
Evolutionary Calculation/
│
├── 📂 solvers/                    # Solver implementations
│   ├── cbus_bnb.py               # Branch-and-Bound (exact)
│   ├── main_routing.py           # OR-Tools GLS (meta-heuristic)
│   └── heuristic.py              # ALNS (meta-heuristic)
│
├── 📂 framework/                 # Core framework
│   ├── experiment.py             # Experiment runner
│   ├── utils.py                  # Utility functions
│   ├── run.py                    # CLI interface
│   └── analyze.py                # Results analyzer
│
├── 📂 optimization/              # Parameter optimization
│   ├── param_optimization.py     # Tuning framework
│   ├── hust_runner.py            # HUST instance runner
│   ├── hust_workflow.py          # Full workflow
│   ├── visualize_hust.py         # Result visualizations
│   └── [various tuning scripts]
│
├── 📂 scripts/                   # Utility scripts
│   ├── test_solvers.py           # Solver tests
│   ├── test_bnb.py               # BnB tester
│   ├── scenarios.py              # Scenario selector
│   └── hust_quickstart.py        # Quick start
│
├── 📂 data/                      # Input datasets
│   ├── cbus_output_20260517_222958/    # CBUS instances
│   ├── pdp_100/                        # PDP instances
│   └── homberger_1000_customer_instances/
│
├── 📂 results/                   # Output & results
│   ├── results_20260517_223957/
│   ├── results_20260517_224406/
│   └── hust_demo_results/
│
├── 📂 docs/                      # Documentation
│   ├── README.md                 # Main documentation
│   ├── USAGE_GUIDE.md            # Detailed usage guide
│   ├── QUICK_REFERENCE.md        # Quick reference
│   ├── README_HUST.md            # HUST-specific guide
│   └── [other docs]
│
├── 📂 legacy/                    # Legacy code
│   └── cbus_bnb.cpp              # Original C++ BnB
│
├── 📂 utils_files/               # Utilities
│   ├── convert.py
│   └── [other utils]
│
└── Entry Points (run from root)
    ├── run_experiment.py         # Run experiments
    ├── run_scenarios.py          # Interactive scenarios
    ├── analyze_results.py        # Analyze results
    ├── optimize_hust.py          # HUST optimization
    └── test_all.py               # Test solvers
```

## 🚀 Quick Start

### Run Experiments
```bash
# Test everything works
python test_all.py

# Run quick experiment (5 min)
python run_experiment.py --quick

# Run specific instance
python run_experiment.py -i lc101_cbus -t 30

# Run all instances
python run_experiment.py -t 60 -o my_experiment

# Analyze results
python analyze_results.py
```

### HUST Optimization (New)
```bash
# Run full HUST workflow
python optimize_hust.py

# Interactive scenario selector
python run_scenarios.py
```

## 📊 Solvers Available

| Solver | Type | Location | Speed | Quality |
|--------|------|----------|-------|---------|
| **BnB** | Exact | `solvers/cbus_bnb.py` | Slow | Optimal |
| **OR-Tools** | Meta-heuristic | `solvers/main_routing.py` | Medium | High |
| **ALNS** | Meta-heuristic | `solvers/heuristic.py` | Fast | Good |

## 📖 Documentation

- **Getting Started** → Read `docs/README.md`
- **Detailed Guide** → Read `docs/USAGE_GUIDE.md`
- **Quick Tips** → Read `docs/QUICK_REFERENCE.md`
- **HUST Benchmarking** → Read `docs/README_HUST.md`

## 💡 Common Tasks

### Test Setup
```bash
python test_all.py
```

### Run Experiments with Different Settings
```bash
# Quick test
python run_experiment.py --quick

# Standard test (30s per solver)
python run_experiment.py -t 30

# Extended test (60s per solver)
python run_experiment.py -t 60 -o extended_results
```

### Analyze Results
```bash
python analyze_results.py my_experiment_name
```

### Interactive Scenarios
```bash
python run_scenarios.py
```

### HUST Parameter Optimization
```bash
python optimize_hust.py
```

## 📂 Where Things Are

| What | Where |
|------|-------|
| Input data | `data/` |
| Output results | `results/` |
| Core solvers | `solvers/` |
| Framework | `framework/` |
| Scripts | `scripts/` |
| Optimization | `optimization/` |
| Documentation | `docs/` |

## ⚙️ Parameter Optimization Guide

### Overview
Each solver has different parameters that can be optimized based on problem size and available time:

```
Solvers & Parameters:
├── Branch-and-Bound (BnB)
│   └── Minimal parameters (exact algorithm)
├── OR-Tools GLS
│   ├── first_solution_strategy
│   ├── local_search_metaheuristic
│   ├── time_limit_seconds
│   └── lns_time_limit
└── ALNS
    ├── iterations
    ├── cooling_rate
    ├── initial_temperature
    └── removal_size_range
```

### 1️⃣ Branch-and-Bound (BnB) Parameters

**Location:** `solvers/cbus_bnb.py`

**Characteristics:**
- Exact algorithm (guarantees optimal solution)
- Time-dependent (grows exponentially with n)
- Best for: small instances (n ≤ 10)

**Key Parameters:**
```python
# No optimization parameters needed
# Built-in timeout mechanism:
time_limit: int = 30  # seconds, hard limit for all instances
recursion_depth_limit: int = auto-adjusted based on n
```

**Usage:**
```bash
# Default: 30 second timeout
python run_experiment.py -i lc101_cbus -t 30
```

**Notes:**
- Timeout prevents infinite recursion
- Quality: Always optimal (within time limit)
- Speed: Unpredictable, depends on instance structure

---

### 2️⃣ OR-Tools GLS Parameters

**Location:** `solvers/main_routing.py`

**Characteristics:**
- Meta-heuristic (Guided Local Search)
- Time-balanced algorithm
- Best for: general purpose (n ≤ 1000)

**Key Parameters:**

| Parameter | Default | Range | Effect |
|-----------|---------|-------|--------|
| `first_solution_strategy` | PARALLEL_CHEAPEST_INSERTION | See below | Initial solution quality |
| `local_search_metaheuristic` | GUIDED_LOCAL_SEARCH | See below | Search direction |
| `time_limit_seconds` | Adjustable | 5-120s | Total search time |
| `lns_time_limit` | time_limit / 6 | 1-20s | Large neighborhood search |
| `use_full_propagation` | True | bool | Constraint propagation |

**First Solution Strategies:**
```python
PARALLEL_CHEAPEST_INSERTION  # ⭐ Default - best initial solution
PATH_CHEAPEST_ARC            # Fast, reasonable quality
NEAREST_NEIGHBOR             # Very fast, okay quality
CHEAPEST_INSERTION           # Moderate, good quality
AUTOMATIC                    # Auto-select
```

**Local Search Metaheuristics:**
```python
GUIDED_LOCAL_SEARCH    # ⭐ Default - best quality improvement
SIMULATED_ANNEALING    # Slower but can escape local optima
TABU_SEARCH            # Good for medium instances
AUTOMATIC              # Auto-select
```

**Tuning Strategy by Problem Size:**

| Instance Size | Strategy | Metaheuristic | Time Limit | Expected Quality |
|---------------|----------|---------------|------------|-----------------|
| **Small** (n≤10) | PARALLEL_CHEAPEST_INSERTION | GUIDED_LOCAL_SEARCH | 30-60s | High (near optimal) |
| **Medium** (n=100) | PARALLEL_CHEAPEST_INSERTION | GUIDED_LOCAL_SEARCH | 20-40s | High |
| **Large** (n=500) | PATH_CHEAPEST_ARC | SIMULATED_ANNEALING | 10-20s | Good |
| **Very Large** (n≥1000) | NEAREST_NEIGHBOR | SIMULATED_ANNEALING | 5-10s | Fair |

**Usage Examples:**
```bash
# Quick tuning (5 min total)
python hust_experiment.py -t 15  # 15s per solver, 5 instances

# Balanced tuning (15 min total)
python hust_experiment.py -t 30  # 30s per solver, 5 instances

# Deep tuning (30+ min total)
python hust_experiment.py -t 60  # 60s per solver, 5 instances
```

**Code Configuration (in hust_experiment.py):**
```python
# Optimized parameters
search_params = pywrapcp.DefaultRoutingSearchParameters()
search_params.first_solution_strategy = \
    routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION
search_params.local_search_metaheuristic = \
    routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
search_params.time_limit.FromSeconds(int(time_limit))
search_params.use_full_propagation = True
search_params.lns_time_limit.FromSeconds(max(1, int(time_limit / 6)))
```

---

### 3️⃣ ALNS (Adaptive Large Neighborhood Search) Parameters

**Location:** `solvers/heuristic.py`

**Characteristics:**
- Meta-heuristic (Local Search with Simulated Annealing)
- Fast and adaptive
- Best for: large instances (n ≥ 100)

**Key Parameters:**

| Parameter | Default | Range | Effect |
|-----------|---------|-------|--------|
| `iterations` | 300 | 50-500 | Total iterations |
| `cooling_rate` | 0.95 | 0.90-0.98 | Temperature decrease rate |
| `initial_temperature` | 150.0 | 50-500 | Initial acceptance threshold |
| `removal_size_range` | (1, 40) | (1, 5) to (10, 100) | Destruction size (% of customers) |

**Tuning Strategy by Problem Size:**

| Size | Iterations | Cooling Rate | Initial Temp | Removal Range | Expected Quality |
|------|------------|--------------|--------------|---------------|-----------------|
| **Small** (n≤10) | 500 | 0.90 | 100.0 | (1, 20) | Very Good |
| **Medium** (n=100) | 300 | 0.95 | 150.0 | (1, 40) | Good |
| **Large** (n=500) | 200 | 0.97 | 200.0 | (2, 80) | Fair-Good |
| **Very Large** (n≥1000) | 100 | 0.98 | 250.0 | (5, 150) | Fair |

**Parameter Meanings:**

- **iterations**: 
  - Higher = better quality, slower
  - Default 300 = good balance
  
- **cooling_rate** (α):
  - T(t+1) = α × T(t)
  - 0.90 = aggressive cooling (quick convergence)
  - 0.98 = slow cooling (explores more)
  
- **initial_temperature**:
  - Controls acceptance of worse solutions initially
  - Higher = more exploration
  
- **removal_size_range**:
  - (min%, max%) of customers to remove in each iteration
  - Larger range = more exploration, slower

**Usage Examples:**
```bash
# Quick run (5 min)
python hust_quickstart.py
# Choose option 1: Quick (5 min)

# Balanced run (15 min)
python hust_workflow.py -s all -t 30

# Deep tuning (30+ min)
python hust_workflow.py -s all -t 60
```

**Code Configuration (in hust_experiment.py):**
```python
# Optimized ALNS parameters
iterations = 300
cooling_rate = 0.95
initial_temp = 150.0
removal_size_range = (1, 40)

# Parameter adjustment by instance size
if n <= 10:
    iterations = 500
    cooling_rate = 0.90
    initial_temp = 100.0
elif n >= 500:
    iterations = 200
    cooling_rate = 0.97
    initial_temp = 200.0
```

---

### 🎯 Comparison: When to Use Which Parameters

**For Publication/Paper:**
```bash
# Recommended for research
python hust_workflow.py -s all -t 120  # 2 min per solver
# Time per instance: ~6 minutes (BnB + OR-Tools + ALNS)
# Quality: Very high with sufficient time
```

**For Class Projects:**
```bash
python optimize_hust.py
# Interactive menu guides you through all options
```

**For Quick Testing:**
```bash
python run_experiment.py --quick
# ~5 min total, all solvers on 5 instances
# Sufficient for testing implementation
```

**For Production Benchmarking:**
```bash
# Small instances (n ≤ 20)
python run_experiment.py -t 60 -o benchmark_small

# Medium instances (n = 100)
python run_experiment.py -t 30 -o benchmark_medium

# Large instances (n ≥ 500)
python run_experiment.py -t 15 -o benchmark_large
```

---

### 📊 Parameter Optimization Workflow

**Location:** `optimization/tune_params.py`

The framework provides an automatic tuning system:

```bash
# Automated parameter tuning
python optimization/tune_params.py
```

**What It Does:**
1. Tests different parameter combinations
2. Runs on sample instances
3. Measures quality vs. time trade-off
4. Recommends best configuration
5. Saves results to `tuning_results_*/`

**Example Output:**
```
Tuning Results for lc101_cbus (n=10):

OR-Tools Combinations:
  Strategy: PARALLEL_CHEAPEST_INSERTION
  Metaheuristic: GUIDED_LOCAL_SEARCH
  Time: 30s → Cost: 12850 (Optimal) ✓

ALNS Combinations:
  Iterations: 300, Cooling: 0.95, Temp: 150
  Time: 30s → Cost: 12950 (0.78% gap)

Recommendation:
  → Use ALNS for speed (6s)
  → Use OR-Tools for quality (slightly better)
  → Use BnB only for proof of optimality
```

---

### 📈 Results by Problem Type

**Based on HUST Benchmark Results:**

```
Small Instances (n=5, 10):
├── BnB: ✓ Optimal, fast (< 1s)
├── OR-Tools: ✓ Optimal/near-optimal, medium (1-5s)
└── ALNS: ✓ Very good, instant (< 0.5s)

Medium Instances (n=100):
├── BnB: ✗ Timeout (recursion limit)
├── OR-Tools: ✓ High quality (15-20s)
└── ALNS: ✓✓ Best quality, fast (5-10s)

Large Instances (n=500, 1000):
├── BnB: ✗ Cannot run
├── OR-Tools: ✓ Moderate quality (20-30s)
└── ALNS: ✓✓ Best quality AND speed (10-20s)
```

---

## 🔧 File Organization Benefits

✅ **Clear Separation** - Each type of file in its own folder
✅ **Easy Navigation** - Know where to find everything
✅ **Modular Design** - Easy to add new components
✅ **Entry Points** - Simple root-level commands
✅ **Scalable** - Works as project grows

## 📝 Entry Point Scripts

All scripts below run from root directory:

| Script | Purpose |
|--------|---------|
| `run_experiment.py` | Run CBUS experiments |
| `analyze_results.py` | Analyze experiment results |
| `run_scenarios.py` | Interactive scenario selector |
| `optimize_hust.py` | HUST optimization workflow |
| `test_all.py` | Test solver implementations |

## 🎯 Workflow Examples

### Example 1: Basic Experiment
```bash
python test_all.py                    # Verify setup
python run_experiment.py --quick      # Quick test
python analyze_results.py             # View results
```

### Example 2: Full Benchmark
```bash
python run_experiment.py -t 60 -o benchmark
python analyze_results.py benchmark
```

### Example 3: HUST Optimization
```bash
python optimize_hust.py
# Follow interactive prompts
```

## 🐛 Troubleshooting

### "Module not found" error
All entry points (run_experiment.py, etc.) handle path setup automatically.
Just run from root directory.

### "ortools not installed"
```bash
pip install ortools
```

### Directory structure questions
Check the tree structure above or run:
```bash
tree /F  # On Windows
```

## 📊 Project Statistics

- **3 Solver Algorithms** (Exact + 2 Meta-heuristics)
- **50+ Test Instances** (CBUS, PDP, HUST)
- **Multiple Benchmark Types** (Speed, Quality, Scalability)
- **Complete Framework** (Experiment, Analysis, Optimization)
- **Well Documented** (README, Guides, Quick Reference)

## 🚀 Next Steps

1. **First time?** Run `python test_all.py`
2. **Want to test?** Run `python run_experiment.py --quick`
3. **Need help?** Read `docs/USAGE_GUIDE.md`
4. **Want optimization?** Run `python optimize_hust.py`

## 📞 Support

- Documentation: `docs/`
- Quick help: `docs/QUICK_REFERENCE.md`
- Detailed guide: `docs/USAGE_GUIDE.md`
- HUST guide: `docs/README_HUST.md`

---

**Ready to run experiments? Start with:**
```bash
python test_all.py
```

**Happy experimenting! 🎉**

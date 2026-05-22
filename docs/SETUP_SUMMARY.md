# CBUS Experiment Framework - Setup Summary

## ✅ What's Been Created

This framework provides a complete system for comparing three methods to solve the CBUS (Pickup-Delivery) problem:

### 1. **Solver Implementations**

- **cbus_bnb.py** (NEW)
  - Python port of C++ Branch-and-Bound exact algorithm
  - Finds optimal solutions (or best feasible within time limit)
  - Uses DFS + pruning with lower bound calculations

- **main_routing.py** (MODIFIED)
  - Added time_limit_seconds parameter (was hardcoded to 30s)
  - OR-Tools Guided Local Search meta-heuristic
  - Fast, practical solutions

- **heuristic.py** (EXISTING)
  - ALNS (Adaptive Large Neighborhood Search)
  - Adaptive removal/repair operators
  - Very fast, good quality solutions

### 2. **Utility & Framework**

- **utils.py** (NEW)
  - read_cbus_file() - Parse input files
  - write_cbus_file() - Save solutions
  - load_data_directory() - Batch load instances
  - calculate_route_cost() - Verify solutions
  - validate_route() - Check all constraints
  - print_route_details() - Pretty print solutions

- **experiment.py** (NEW)
  - ExperimentRunner class - Main orchestrator
  - Runs all 3 solvers on instances
  - Validates results
  - Generates JSON + CSV reports

- **run.py** (NEW)
  - Easy-to-use command-line interface
  - Supports single/multiple/all instances
  - Different timeout configurations

- **analyze.py** (NEW)
  - Parse and analyze experiment results
  - Generate summary statistics
  - Rankings and performance analysis

- **scenarios.py** (NEW)
  - Interactive experiment scenario selector
  - Pre-configured test profiles
  - Consistent result naming/organization

- **test_solvers.py** (NEW)
  - Quick validation script
  - Tests BnB solver on sample instance
  - Verifies route validity

### 3. **Documentation**

- **README.md** (NEW)
  - Framework overview
  - File structure and definitions
  - Usage instructions
  - Performance tips
  - Extending with new solvers

- **USAGE_GUIDE.md** (NEW)
  - Step-by-step quick start
  - Detailed result interpretation
  - Experiment scenarios
  - Solver comparisons
  - Troubleshooting guide

- **SETUP_SUMMARY.md** (THIS FILE)
  - What was created
  - File relationships
  - Getting started steps

## 📁 File Structure

```
d:\Evolutionary Calculation\
├── Solvers (Core Implementations)
│   ├── cbus_bnb.py              # NEW: Branch-and-Bound (Python)
│   ├── main_routing.py          # MODIFIED: Added time_limit parameter
│   └── heuristic.py             # EXISTING: ALNS heuristic
│
├── Framework (Orchestration)
│   ├── experiment.py            # NEW: Main experiment runner
│   ├── utils.py                 # NEW: Utility functions
│   └── run.py                   # NEW: CLI interface
│
├── Analysis & Scenarios
│   ├── analyze.py               # NEW: Results analyzer
│   └── scenarios.py             # NEW: Scenario selector
│
├── Testing
│   ├── test_solvers.py          # NEW: Quick test
│   └── test_bnb.py              # NEW: BnB tester
│
├── Documentation
│   ├── README.md                # NEW: Main documentation
│   ├── USAGE_GUIDE.md           # NEW: Detailed usage
│   └── SETUP_SUMMARY.md         # NEW: This file
│
├── Data
│   ├── cbus_output_20260517_222958/  # Test instances
│   │   ├── lc101_cbus.txt
│   │   ├── lc102_cbus.txt
│   │   └── ... (50+ more instances)
│   └── pdp_100/                      # Other test data
│
└── Results (Generated)
    ├── results_20260517_223957/      # Auto-generated after each run
    │   ├── results.json
    │   └── results.csv
    └── ...
```

## 🚀 Getting Started

### Step 1: Quick Test (1 minute)

```bash
cd d:\Evolutionary\ Calculation
python test_solvers.py
```

**Expected Output:**
```
✓ Loaded: n=10, k=3
[BnB Solver]
  Route: 2 12 4 14 6 7 17 9 10 20 8 18 19 5 3 15 1 13 16 11
  Cost: 122 (calculated: 122)
  Time: 10.025s
  Valid: ✓
```

### Step 2: Run Interactive Scenarios (Varies)

```bash
python scenarios.py
```

Choose:
1. Quick Test (5 min) - 3 instances, 10s each
2. Standard Test (15 min) - All instances, 30s each
3. Extended Test (30 min) - All instances, 60s each
4. Deep Dive - One instance, 120s detailed analysis

### Step 3: Analyze Results (1 minute)

```bash
python analyze.py
```

This automatically finds the latest results and generates a summary:
- Performance rankings by cost
- Win statistics
- Average computation times

### Step 4: Review Reports

Check the generated `results_*/` directory:
- **results.csv** - Import into Excel for charts
- **results.json** - Raw data for further analysis

## 📊 What Each Solver Does

| Solver | Method | Speed | Quality | Notes |
|--------|--------|-------|---------|-------|
| **BnB** | Exact | Slow | Optimal (or best found) | Good for n≤12, proof of optimality |
| **OR-Tools** | Meta-heuristic | Medium | High quality | Best practical choice for most cases |
| **ALNS** | Meta-heuristic | Very Fast | Good | Excellent for quick approximate solutions |

## 🔧 Key Features

✅ **Easy to Use**
- Simple CLI interface
- Interactive scenario selector
- Automatic result organization

✅ **Comprehensive**
- Tests all 3 methods on same instances
- Automatic solution validation
- Detailed performance metrics

✅ **Extensible**
- Easy to add new solvers
- Modular architecture
- Clear interfaces

✅ **Well-Documented**
- README with technical details
- USAGE_GUIDE with examples
- Inline code documentation

## 💡 Common Commands

### Test a Single Instance
```bash
python run.py -i lc101_cbus -t 30
```

### Test Multiple Instances
```bash
python run.py -i lc101_cbus,lc102_cbus,lc103_cbus -t 30
```

### Quick Test (Recommended First)
```bash
python run.py --quick -t 10
```

### Full Experiment
```bash
python run.py -t 60 -o my_experiment_name
```

### Analyze Results
```bash
python analyze.py results_YYYYMMDD_hhmmss
```

## 📈 Example Workflow

### Scenario: Compare solvers on benchmark

1. **Run Quick Test First**
   ```bash
   python run.py --quick
   # Results: results_20260517_223957/
   ```

2. **Review Results**
   ```bash
   python analyze.py results_20260517_223957
   # See: which solver is best for different instance sizes
   ```

3. **Run Extended Test**
   ```bash
   python run.py -t 60 -o final_benchmark
   # Get more comprehensive results
   ```

4. **Analyze Final Results**
   ```bash
   python analyze.py final_benchmark
   # Generate final report
   ```

5. **Export Results**
   - Open `final_benchmark/results.csv` in Excel
   - Create charts comparing solvers
   - Generate research report

## 🎯 Next Steps

1. **Immediate**: Run `python test_solvers.py` to verify everything works
2. **Quick**: Run `python run.py --quick` for a 5-minute test
3. **Full**: Run `python scenarios.py` to explore all options
4. **Analysis**: Use `analyze.py` to interpret results

## 📝 Notes

- **Time Limits**: Adjust with `-t` flag (in seconds)
  - 10s: Very fast, good for testing
  - 30s: Balanced (default)
  - 60s: Extended search, better quality
  - 120s: Deep dive, very thorough

- **Data**: 50+ instances in `cbus_output_20260517_222958/`
  - lc101-109: Small instances (n=10)
  - lc201-208: Medium instances (n=20)
  - lr101-112: Random large (n=5-13)
  - And more...

- **Results**: Each run auto-generates timestamped directory
  - results.json - Complete data
  - results.csv - Summary for Excel
  - Useful for reproducibility

## ✨ Features You Can Now Use

✅ Compare 3 solvers on same problem instances
✅ Automatic constraint validation
✅ Generate publication-ready reports
✅ Analyze performance trends
✅ Extend with new solvers easily
✅ Batch process multiple instances
✅ Configure time limits per solver

## 🎓 Learning Resources

- **README.md** - Technical algorithm details
- **USAGE_GUIDE.md** - Practical examples
- **Source code** - Well-commented implementation
- **Results files** - Actual performance data

---

**Ready to run experiments? Start with:**
```bash
python test_solvers.py  # Verify setup
python run.py --quick   # Quick 5-min test
```

**Questions? Check USAGE_GUIDE.md or README.md**

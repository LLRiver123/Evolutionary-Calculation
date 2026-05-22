# PROJECT INDEX

## 🎯 Entry Points (Run these from root!)

```bash
python run_experiment.py          # Main experiment runner
python analyze_results.py         # Analyze results  
python run_scenarios.py           # Interactive scenario selector
python optimize_hust.py           # HUST optimization workflow
python test_all.py                # Test solver setup
```

## 📂 Folder Structure

```
.
├── 📖 Documentation
│   ├── README_ROOT.md             ← START HERE for overview
│   ├── PROJECT_STRUCTURE.md       ← Folder organization
│   └── docs/
│       ├── QUICK_REFERENCE.md     ← One-liners
│       ├── USAGE_GUIDE.md         ← Complete guide
│       ├── README.md              ← Technical details
│       └── README_HUST.md         ← HUST-specific
│
├── 🎯 Solvers (algorithms)
│   └── solvers/
│       ├── cbus_bnb.py            ← Branch-and-Bound
│       ├── main_routing.py        ← OR-Tools GLS
│       └── heuristic.py           ← ALNS
│
├── 🧬 Framework (core)
│   └── framework/
│       ├── experiment.py          ← Experiment runner
│       ├── utils.py               ← Utilities
│       ├── run.py                 ← CLI interface
│       └── analyze.py             ← Results analyzer
│
├── 🔬 Optimization (parameter tuning)
│   └── optimization/
│       ├── param_optimization.py
│       ├── tune_params.py
│       ├── hust_experiment.py
│       ├── hust_workflow.py
│       └── visualize_hust.py
│
├── 📝 Scripts (utilities)
│   └── scripts/
│       ├── test_solvers.py
│       ├── test_bnb.py
│       ├── scenarios.py
│       └── hust_quickstart.py
│
├── 📊 Data (inputs)
│   └── data/
│       ├── cbus_output_20260517_222958/  (50+ CBUS instances)
│       ├── pdp_100/                      (PDP instances)
│       └── homberger_1000_customer_instances/
│
├── 💾 Results (outputs)
│   └── results/
│       ├── results_20260517_223957/
│       ├── results_20260517_224406/
│       └── hust_demo_results/
│
├── 🏛️ Legacy
│   └── legacy/
│       └── cbus_bnb.cpp            (Original C++ version)
│
└── 🛠️ Utils
    └── utils_files/
        ├── convert.py
        ├── converter.py
        ├── main.py
        └── solve.py
```

## 🚀 Quick Start Commands

### Test Everything Works
```bash
python test_all.py
```

### Run Quick Experiment (5 min)
```bash
python run_experiment.py --quick
```

### View Results
```bash
python analyze_results.py
```

### Interactive Scenarios
```bash
python run_scenarios.py
```

### HUST Optimization
```bash
python optimize_hust.py
```

## 📚 Documentation Map

| If you want to... | Read this file |
|------------------|----------------|
| Get started quickly | README_ROOT.md (this directory) |
| Understand folder structure | PROJECT_STRUCTURE.md |
| Quick commands & tips | docs/QUICK_REFERENCE.md |
| Detailed usage guide | docs/USAGE_GUIDE.md |
| Technical details | docs/README.md |
| HUST benchmarking | docs/README_HUST.md |

## 🎯 Common Workflows

### Workflow 1: Verify Setup (5 min)
```bash
python test_all.py
```

### Workflow 2: Quick Experiment (5-10 min)
```bash
python run_experiment.py --quick
python analyze_results.py
```

### Workflow 3: Full Benchmark (30+ min)
```bash
python run_experiment.py -t 60 -o my_benchmark
python analyze_results.py my_benchmark
```

### Workflow 4: HUST Optimization (20+ min)
```bash
python optimize_hust.py
```

### Workflow 5: Custom Test
```bash
python run_experiment.py -i lc101_cbus,lc102_cbus -t 30 -o custom_test
python analyze_results.py custom_test
```

## 🧪 3 Solver Algorithms Available

1. **Branch-and-Bound (BnB)**
   - Type: Exact algorithm
   - Speed: Slow (exponential)
   - Quality: Optimal or best found
   - Best for: n ≤ 12, proof of optimality
   - Location: `solvers/cbus_bnb.py`

2. **OR-Tools Guided Local Search**
   - Type: Meta-heuristic
   - Speed: Medium
   - Quality: High-quality solutions
   - Best for: General purpose, any size
   - Location: `solvers/main_routing.py`

3. **ALNS (Adaptive Large Neighborhood Search)**
   - Type: Meta-heuristic
   - Speed: Very fast
   - Quality: Good approximations
   - Best for: Quick solutions
   - Location: `solvers/heuristic.py`

## 📊 Test Instances Available

- **CBUS Instances**: 50+ problems of various sizes
- **HUST Benchmarks**: Specialized sets (5, 10, 100, 500, 1000)
- **PDP Instances**: Pickup-Delivery benchmarks
- **Homberger**: Large-scale instances (1000+ customers)

All located in: `data/`

## 🗂️ Key Files

### Entry Points (run from root)
- `run_experiment.py` - Main entry point
- `analyze_results.py` - Results analysis
- `run_scenarios.py` - Interactive menu
- `optimize_hust.py` - HUST optimization
- `test_all.py` - Test setup

### Core Solvers
- `solvers/cbus_bnb.py` - Branch-and-Bound
- `solvers/main_routing.py` - OR-Tools
- `solvers/heuristic.py` - ALNS

### Framework
- `framework/experiment.py` - Experiment runner
- `framework/utils.py` - Utilities
- `framework/analyze.py` - Analysis

## 💡 First Time?

1. Read: `README_ROOT.md` (this directory)
2. Run: `python test_all.py`
3. Read: `docs/QUICK_REFERENCE.md`
4. Run: `python run_experiment.py --quick`
5. Check: `results/` folder for output

## 🆘 Help

- Questions about structure? → PROJECT_STRUCTURE.md
- Questions about usage? → docs/USAGE_GUIDE.md
- Quick tips? → docs/QUICK_REFERENCE.md
- HUST-specific? → docs/README_HUST.md

---

**Start here:** `README_ROOT.md`
**Quick start:** `python test_all.py`
**Get help:** Check the docs folder

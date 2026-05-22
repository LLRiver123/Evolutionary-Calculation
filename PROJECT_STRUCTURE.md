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

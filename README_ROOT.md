# 🚀 CBUS Evolutionary Calculation Framework

Welcome to the CBUS (Capacitated Pickup-Delivery) solver framework. This project provides a complete system for comparing exact and heuristic algorithms on optimization problems.

## 📊 Quick Overview

```
Evolutionary Calculation/
├── 🎯 Entry Points (start here!)
│   ├── run_experiment.py          ← Run experiments
│   ├── analyze_results.py         ← Analyze results  
│   ├── run_scenarios.py           ← Interactive scenarios
│   ├── optimize_hust.py           ← HUST optimization
│   └── test_all.py                ← Test setup
│
├── 📁 solvers/                    ← Algorithm implementations
│   ├── cbus_bnb.py                (Branch-and-Bound - Exact)
│   ├── main_routing.py            (OR-Tools - Meta-heuristic)
│   └── heuristic.py               (ALNS - Meta-heuristic)
│
├── 📁 framework/                  ← Core framework
├── 📁 optimization/               ← Parameter tuning & HUST tests
├── 📁 data/                       ← Input datasets (50+ instances)
├── 📁 results/                    ← Output results & reports
└── 📁 docs/                       ← Documentation
```

## 🎯 Start Here

### For First-Time Users
```bash
# Test that everything works
python test_all.py

# Run a quick experiment (5 min)
python run_experiment.py --quick

# View results
python analyze_results.py
```

### For HUST Optimization (NEW!)
```bash
# Run full parameter tuning and benchmarking
python optimize_hust.py

# Or use interactive selector
python run_scenarios.py
```

### For Full Experiments
```bash
# Run all instances with 60s per solver
python run_experiment.py -t 60 -o my_experiment

# Analyze specific experiment
python analyze_results.py my_experiment
```

## 🧪 What's Included

### 3 Solver Algorithms

| Algorithm | Type | Speed | Quality | Best For |
|-----------|------|-------|---------|----------|
| **Branch-and-Bound** | Exact | ⏱️ Slow | ⭐⭐⭐ Optimal | n ≤ 12, proof of optimality |
| **OR-Tools GLS** | Meta-heuristic | ⏱️ Medium | ⭐⭐⭐ High | General purpose |
| **ALNS** | Meta-heuristic | ⏱️ Fast | ⭐⭐ Good | Quick approximate |

### 50+ Test Instances
- **CBUS**: 10, 20, 50+ customer instances
- **HUST**: Specialized benchmark sets (5, 10, 100, 500, 1000)
- **PDP/Homberger**: Additional benchmarks

### Complete Framework
- ✅ Automatic constraint validation
- ✅ JSON + CSV result exports
- ✅ Performance visualization
- ✅ Parameter optimization
- ✅ Batch processing
- ✅ Statistics & ranking

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| **PROJECT_STRUCTURE.md** | Overview of folder organization |
| **docs/QUICK_REFERENCE.md** | One-liners and quick tips |
| **docs/USAGE_GUIDE.md** | Detailed usage guide with examples |
| **docs/README.md** | Technical details |
| **docs/README_HUST.md** | HUST-specific benchmarking |

## 💡 Common Tasks

### Run Single Instance (30s per solver)
```bash
python run_experiment.py -i lc101_cbus -t 30
```

### Run Multiple Instances
```bash
python run_experiment.py -i lc101_cbus,lc102_cbus,lc103_cbus -t 30
```

### Run All Instances (60s per solver)
```bash
python run_experiment.py -t 60 -o benchmark_60s
```

### Analyze Results
```bash
python analyze_results.py benchmark_60s
```

### Interactive Mode
```bash
python run_scenarios.py
```

Choose from:
1. Quick Test (5 min)
2. Standard Test (15 min)
3. Extended Test (30 min)
4. Deep Dive (120s on one instance)
5. Custom parameters

## 🗂️ Folder Organization

### Main Folders

```
solvers/              Solver implementations (BnB, OR-Tools, ALNS)
framework/            Core framework (experiments, utils, analysis)
optimization/         Parameter tuning, HUST workflows
scripts/              Utility scripts (tests, scenarios)
data/                 Input datasets
results/              Output experiments & visualizations
docs/                 Documentation
```

### Where Things Are

| What | Where |
|------|-------|
| Input data | `data/cbus_output_20260517_222958/` |
| HUST data | `data/` (in subfolders) |
| Results | `results/` (auto-organized) |
| Solvers | `solvers/*.py` |
| Framework | `framework/*.py` |
| Documentation | `docs/*.md` |

## 🚀 Workflow Examples

### Example 1: Basic Test
```bash
python test_all.py                      # Verify setup (1 min)
python run_experiment.py --quick        # Quick test (5 min)
python analyze_results.py               # View results (1 min)
```

### Example 2: Full Benchmark
```bash
python run_experiment.py -t 60 -o benchmark    # All instances (30+ min)
python analyze_results.py benchmark            # Generate report (1 min)
```

### Example 3: HUST Optimization
```bash
python optimize_hust.py                 # Full workflow (20+ min)
# Includes: tuning, experiments, visualization
```

### Example 4: Custom Experiment
```bash
python run_experiment.py -i lc201_cbus,lc202_cbus -t 120 -o my_test
python analyze_results.py my_test
```

## 📊 Understanding Results

### Output Format

```
Instance: lc101_cbus (n=10, k=3)

Method          | Cost         | Time       | Valid
BnB             | 122          | 20.20s     | ✓
OR-Tools        | 120          | 20.05s     | ✓
ALNS            | 131          | 0.01s      | ✓

Best cost: 120 (Winner: OR-Tools)
```

**What it means:**
- **Cost**: Total distance (lower = better)
- **Time**: Computation time in seconds
- **Valid**: Solution satisfies all constraints (✓ = yes, ✗ = no)

### Exported Files

Each experiment generates:
- `results.json` - Complete data in JSON format
- `results.csv` - Summary table (open in Excel)

## 🔧 Configuration

### Time Limits
- Default: 30 seconds per solver
- Quick: 10 seconds (testing)
- Extended: 60 seconds (better quality)
- Deep: 120+ seconds (thorough search)

### Running Headless
```bash
cd "d:\Evolutionary Calculation"
python run_experiment.py -t 30
```

No interactive prompts, results saved automatically.

## 📈 Performance Guide

### BnB (Branch-and-Bound)
- **Best for**: n ≤ 12 instances
- **Time**: Exponential (becomes slow quickly)
- **Quality**: Optimal or best found within timeout

### OR-Tools
- **Best for**: General purpose, any size
- **Time**: Polynomial, practical
- **Quality**: High-quality solutions

### ALNS
- **Best for**: Quick solutions
- **Time**: Linear, very fast
- **Quality**: Good approximate solutions

## 🎓 Next Steps

1. **First time?** → Run `python test_all.py`
2. **Quick test?** → Run `python run_experiment.py --quick`
3. **Full benchmark?** → Run `python optimize_hust.py`
4. **Need help?** → Read `docs/USAGE_GUIDE.md`
5. **Need details?** → Check `docs/README.md`

## 🆘 Troubleshooting

### "Module not found"
All entry points set up paths automatically. Just run from root.

### "ImportError: ortools"
```bash
pip install ortools
```

### Results not saving
Check `results/` folder. All experiments auto-save there.

### Slow performance
- Reduce time limit: `-t 10` instead of `-t 60`
- Test fewer instances
- Use ALNS for quick results

## 📞 Support

- **Quick help**: See `QUICK_REFERENCE.md` in root
- **Detailed guide**: Read `docs/USAGE_GUIDE.md`
- **Technical details**: Check `docs/README.md`
- **HUST guide**: See `docs/README_HUST.md`

## 🎉 Key Features

✅ **Easy to Use** - Simple entry points, interactive modes
✅ **Well Organized** - Clear folder structure
✅ **Comprehensive** - 3 solvers, 50+ instances
✅ **Extensible** - Easy to add new solvers
✅ **Well Documented** - Multiple guides
✅ **Production Ready** - Validated constraints, robust error handling

## 📝 Citation

If using in research:
```
CBUS Solver Comparison Framework
- Branch-and-Bound (exact algorithm)
- Google OR-Tools Guided Local Search (meta-heuristic)
- Adaptive Large Neighborhood Search (meta-heuristic)
```

## 🚀 Quick Commands Reference

```bash
# Testing & Validation
python test_all.py                          # Test setup

# Running Experiments
python run_experiment.py --quick            # Quick 5-min test
python run_experiment.py -t 30              # 30s per solver
python run_experiment.py -t 60 -o bench     # Extended benchmark
python run_experiment.py -i lc101_cbus      # Single instance

# Analysis & Reports
python analyze_results.py                   # Latest results
python analyze_results.py bench             # Specific experiment

# Advanced
python run_scenarios.py                     # Interactive menu
python optimize_hust.py                     # HUST optimization
```

---

**Ready? Start here:**
```bash
python test_all.py
```

**Then:**
```bash
python run_experiment.py --quick
python analyze_results.py
```

**Happy experimenting! 🎉**

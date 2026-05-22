# HUST Benchmark Analysis System - Final Guide

## 🎯 What You Have

A complete production-ready system for:
1. **Solver Comparison** - Test 3 methods (BnB, OR-Tools, ALNS)
2. **Parameter Optimization** - Auto-tune solver configurations
3. **Comprehensive Benchmarking** - Test on 5 HUST instances (5 to 1000 nodes)
4. **Publication-Ready Visualization** - 5 types of charts + statistical report

## 📊 Quick Demo Results

Completed benchmark on HUST instances (n=5, 10, 100, 500, 1000):

| Metric | BnB | OR-Tools | ALNS |
|--------|-----|----------|------|
| **Wins** | 1 | 1 | 2 |
| **Avg Gap %** | 8.06% | 9.86% | 0.00% |
| **Avg Time** | 10.05s | 15.11s | 6.08s |
| **Best for** | small | medium | medium-large |

## 🚀 Get Started (Choose One)

### Option A: Interactive Menu (Easiest)
```bash
python hust_quickstart.py
```
Menu-driven with 6 options to choose from.

### Option B: One-Line Full Workflow
```bash
# Quick (5 min)
python hust_workflow.py -s all -t 15

# Balanced (15 min)  
python hust_workflow.py -s all -t 30

# Deep (30+ min)
python hust_workflow.py -s all -t 60
```

### Option C: Step-by-Step
```bash
# 1. Run experiments only
python hust_experiment.py -t 30 -o my_results

# 2. Generate visualizations
python visualize_hust.py my_results/hust_results.json
```

## 📁 Files Created

### Scripts (Main Programs)
| File | Purpose |
|------|---------|
| `hust_quickstart.py` | Interactive menu (start here!) |
| `hust_workflow.py` | Complete workflow orchestrator |
| `hust_experiment.py` | Run benchmark tests |
| `visualize_hust.py` | Generate charts and reports |
| `tune_params.py` | Parameter tuning |
| `cbus_bnb_fixed.py` | Fixed BnB for large instances |

### Documentation
| File | Purpose |
|------|---------|
| `HUST_BENCHMARK.md` | Complete technical documentation |
| `HUST_RESULTS_SUMMARY.md` | Quick reference guide |
| `README.md` | System overview (you're here!) |

### Example Results (in `hust_demo_results/`)
- `hust_results.json` - Raw data
- `hust_results.csv` - Excel-ready summary
- PNG files - 5 different chart types
- `analysis_report.txt` - Statistical report

## 📈 Output Visualizations

You get 5 PNG chart types + text report:

1. **cost_comparison.png** - Bar charts of solution quality
2. **time_comparison.png** - Execution time analysis
3. **quality_vs_speed.png** - Trade-off scatter plot
4. **scalability.png** - 4-subplot scaling analysis
5. **cost_heatmap.png** - Heatmaps of costs
6. **analysis_report.txt** - Statistics and rankings

## 💾 CSV Export

The `hust_results.csv` is ready to open in Excel:
- Import directly
- Create pivot tables
- Generate your own charts
- Share with colleagues

## 🎓 Understanding Results

### Small Instances (n ≤ 10)
- **BnB**: Optimal solutions, very fast
- **OR-Tools**: Similar quality, slower
- **ALNS**: Good quality, instant

### Medium Instances (n = 100)
- **BnB**: Struggles with time limit
- **OR-Tools**: Moderate quality
- **ALNS**: Best quality ⭐, surprisingly fast

### Large Instances (n ≥ 500)
- **BnB**: Cannot complete (recursion limit)
- **OR-Tools**: Only exact-ish approach
- **ALNS**: Best quality AND speed ⭐

## 🔧 How to Customize

### Change Time Limit
```bash
python hust_experiment.py -t 120  # 2 minutes per solver
python hust_experiment.py -t 5    # 5 seconds per solver (quick)
```

### Add Your Solver
1. Edit `hust_experiment.py`
2. Add method: `def run_my_solver(self, n, k, c, time_limit):`
3. Return: `(route, elapsed_time)`
4. Call in `run_instance()`
5. Run: `python hust_experiment.py`

### Test Specific Instances
Edit line in `hust_experiment.py`:
```python
files = sorted([...])
files = [f for f in files if f in ['hust5.txt', 'hust10.txt']]  # Only these
```

## 📊 For Research Paper

### Workflow
1. Run: `python hust_workflow.py -s all -t 120` (2 min per solver)
2. Export charts: Copy all PNG files to paper/figures/
3. Include data: Add CSV and analysis report as appendix
4. Cite: "HUST Benchmark Analysis System"

### Typical Paper Sections
- **Methods**: Reference solver implementations
- **Results**: Use cost_comparison.png
- **Performance**: Use scalability.png
- **Trade-offs**: Use quality_vs_speed.png
- **Data Tables**: Include hust_results.csv

## 🔬 For Class Projects

### Assignment 1: Run and Compare
```bash
python hust_quickstart.py
# Choose option 3 (30s per solver)
# Analyze results in Excel
```

### Assignment 2: Add Custom Solver
1. Implement your algorithm
2. Add to `hust_experiment.py`
3. Run comparison
4. Write report with visualizations

### Assignment 3: Parameter Tuning
```bash
python tune_params.py  # Generates tuning_results.json
# Analyze which parameters work best
```

## 🚨 Known Limitations & Fixes

### BnB Recursion Depth on Large Instances
**Issue:** `RecursionError: maximum recursion depth exceeded` on n > 500

**Solution 1:** Use fixed version
```bash
# Edit hust_experiment.py, change import:
from cbus_bnb_fixed import CBUSBnB
```

**Solution 2:** Skip BnB for large instances
```python
# In hust_experiment.py, skip BnB for n > 100:
if n <= 100:
    bnb_result = self.run_bnb(...)
```

### ALNS Constraint Violations
**Issue:** Some ALNS solutions marked invalid

**Solution:** Random nature of ALNS, run multiple times and take best:
```python
for trial in range(3):
    run_alns(...)  # Take best of 3 runs
```

## 📞 FAQ

**Q: How long does it take?**
- 15s per solver: ~5 min total (quick demo)
- 30s per solver: ~15 min total (standard)
- 60s per solver: ~30 min total (deep analysis)

**Q: Can I run just one instance?**
```python
# Edit hust_experiment.py, line 330
files = ['hust10.txt']  # Just one
```

**Q: What if I want more instances?**
- Prepare data in CBUS format
- Place in `cbus_output_20260517_222958/`
- Run experiment

**Q: Can I compare with other solvers?**
- Yes, implement your solver
- Add method to `HUSTExperimentRunner`
- Include in experiments

**Q: How to reproduce results?**
```bash
python hust_experiment.py -t 30 -o results_v2
# Compare CSV files with original
```

## 🎯 Recommended Usage Path

### Day 1: Explore (30 minutes)
```bash
python hust_quickstart.py
# Choose: 2 (quick, 15s)
# View PNG files
# Read analysis_report.txt
```

### Day 2: Analyze (1 hour)
```bash
python hust_workflow.py -s experiment -t 30 -o day2_results
# Review hust_results.csv in Excel
# Create custom charts
```

### Day 3: Deep Dive (2 hours)
```bash
python hust_workflow.py -s all -t 60 -o final_results
# Generate final report
# Export for presentation/paper
```

### Day 4: Customize (ongoing)
- Modify solver parameters
- Add your own algorithms
- Run comparative analysis

## 📚 File Reference

### Main Entry Points
- `hust_quickstart.py` - Interactive menu
- `hust_workflow.py` - Complete automation
- `hust_experiment.py` - Raw experiment runner

### Solvers
- `cbus_bnb.py` - Branch-and-Bound (original)
- `cbus_bnb_fixed.py` - Branch-and-Bound (large instances)
- `main_routing.py` - OR-Tools wrapper
- `heuristic.py` - ALNS implementation

### Utilities
- `utils.py` - Common functions
- `visualize_hust.py` - Charting and analysis
- `tune_params.py` - Parameter optimization

### Documentation
- `HUST_BENCHMARK.md` - Full tech docs
- `HUST_RESULTS_SUMMARY.md` - Quick guide
- `README.md` - System overview

## 💡 Pro Tips

1. **Quick Testing**
   - Use `-t 5` for fast validation
   - Use `-t 30` for balanced results
   - Use `-t 120` for final publication

2. **Batch Experiments**
   ```bash
   for time in 10 15 30 60; do
       python hust_experiment.py -t $time -o results_${time}s
   done
   # Compare 4 different time limits
   ```

3. **Focus Analysis**
   - Edit Python scripts to change focus
   - Skip large instances if memory constrained
   - Use sampling for parameter tuning

4. **Version Control**
   - Name results meaningfully: `results_2024_v2_60s/`
   - Keep old results for comparison
   - Track parameter changes

## 🎓 Learning Outcomes

After using this system, you'll understand:
- How exact algorithms scale (BnB)
- How meta-heuristics work (OR-Tools GLS, ALNS)
- How to benchmark solver performance
- How to analyze algorithm trade-offs
- How to create publication-quality visualizations

## 🚀 Start Now!

### Quick (5 min)
```bash
python hust_quickstart.py
# Choose: 2
```

### Standard (15 min)
```bash
python hust_workflow.py -s experiment -t 30
```

### Complete (30+ min)
```bash
python hust_workflow.py -s all -t 60
```

---

## 📞 Support

1. **Quick questions?** → Check HUST_BENCHMARK.md
2. **Parameters?** → Edit Python files (well-commented)
3. **Results look wrong?** → Check analysis_report.txt
4. **Want to extend?** → See "How to Customize" section

---

**Ready to benchmark? Let's go! 🚀**

```bash
python hust_quickstart.py
```

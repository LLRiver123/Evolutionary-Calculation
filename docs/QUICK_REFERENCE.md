# 🚀 QUICK REFERENCE CARD

## One-Line Commands

### Test Everything Works
```bash
python test_solvers.py
```

### Run Quick Experiment (5 min)
```bash
python run.py --quick
```

### Test Specific Instance (30 sec per solver)
```bash
python run.py -i lc101_cbus
```

### Test Multiple Instances (60 sec per solver)
```bash
python run.py -i lc101_cbus,lc102_cbus,lc103_cbus -t 60
```

### Test All Instances (30 sec per solver)
```bash
python run.py -t 30
```

### Analyze Latest Results
```bash
python analyze.py
```

### Interactive Scenario Selector
```bash
python scenarios.py
```

## Result Interpretation

### What Do The Numbers Mean?

```
Instance: lc101_cbus (n=10, k=3)
  Cost: 122              ← Total distance (lower = better)
  Time: 20.2s            ← Computation time
  Valid: ✓               ← All constraints satisfied

Winner: OR-Tools
```

### Costs Comparison

```
BnB:      122  ←─ Baseline (100%)
OR-Tools: 120  ←─ 1.6% better
ALNS:     131  ←─ 7.4% worse
```

## File Locations

| What | Where |
|------|-------|
| Data | `cbus_output_20260517_222958/` |
| Results | `results_YYYYMMDD_hhmmss/` |
| CSV Export | `results_*/results.csv` |
| JSON Data | `results_*/results.json` |

## Common Issues & Fixes

| Problem | Solution |
|---------|----------|
| `ImportError: ortools` | `pip install ortools` |
| Instance not found | Use filename without `.txt` |
| Too slow | Reduce `-t` value |
| Too fast | Increase `-t` value |

## Timeout Recommendations

```
n = 5-10   → 30s  (find optimal)
n = 10-20  → 30s  (good solution)
n = 20-50  → 60s  (quality solution)
n > 50     → 60s  (heuristic fine)
```

## Export to Excel

1. Run experiment:
   ```bash
   python run.py -t 60 -o my_results
   ```

2. Open in Excel:
   - File: `my_results/results.csv`
   - Create pivot table
   - Make charts

## Solver Strengths

| Need | Use |
|------|-----|
| Proof of optimality | **BnB** |
| Best practical solution | **OR-Tools** |
| Blazing speed | **ALNS** |
| All of above | Run all 3 |

## Performance Guide

```
BnB:      Slow  ··· Fast  ████░░░░░░
OR-Tools: Slow  ░░░░ Fast  ██████░░░░
ALNS:     Slow  ░░░░░ Fast ██████████
          Quality bad         good

       Cost Quality
BnB:   Best  Best
Tools:  Good  Good
ALNS:   OK    OK
```

## Quick Experiment Plan

### Day 1: Validate Setup (1 hour)
```bash
python test_solvers.py        # 5 min
python run.py --quick         # 5 min
python analyze.py             # 5 min
```

### Day 2: Benchmark (1 hour)
```bash
python run.py -t 30 -o day2_results    # 30+ min
python analyze.py day2_results         # 5 min
```

### Day 3: Deep Dive (2 hours)
```bash
python scenarios.py                    # Choose #4
# Pick interesting instance
# Run with 120s timeout for detailed analysis
```

## Results Checklist

After running experiments, verify:

- [ ] `results_*/results.json` exists
- [ ] `results_*/results.csv` exists
- [ ] All 3 solvers have results
- [ ] Solutions marked Valid (✓)
- [ ] Costs are reasonable (not 0 or inf)
- [ ] Times are positive numbers
- [ ] CSV can open in Excel

## Tweaking Performance

**For faster results:**
```bash
python run.py -i lc101_cbus -t 10
```

**For better quality:**
```bash
python run.py -i lc101_cbus -t 120
```

**For all instances:**
```bash
python run.py -t 30 -o benchmark
```

## Next Level

### Modify solver parameters:
- Edit `experiment.py` line 98: Change ALNS iterations
- Edit `main_routing.py` line 79: Change first_solution_strategy
- Edit `cbus_bnb.py` line 24: Adjust pruning bounds

### Add custom solvers:
1. Create `my_solver.py`
2. Add method to `ExperimentRunner`
3. Call it in `run_instance()`

### Run headless (no output):
```bash
python -c "from experiment import ExperimentRunner; \
           r = ExperimentRunner(); \
           r.run_all_instances('cbus_output_20260517_222958')"
```

## Troubleshoot

```bash
# Test one instance in detail
python test_solvers.py

# Profile performance
python -m cProfile -s cumtime test_bnb.py

# See detailed errors
python -i experiment.py  # Interactive mode
```

## Citation

If using in paper:
```
CBUS Solver Comparison Framework
- Branch-and-Bound (exact algorithm)
- OR-Tools Guided Local Search (meta-heuristic)
- ALNS (adaptive large neighborhood search)
```

---

**TL;DR:** 
```bash
python test_solvers.py    # Verify
python run.py --quick     # Try it
python analyze.py         # See results
```

**For help:** Read `USAGE_GUIDE.md`

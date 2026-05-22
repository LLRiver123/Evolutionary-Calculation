#!/usr/bin/env python3
"""
Quick start script for HUST benchmark analysis
"""

import os
import sys
import subprocess
from pathlib import Path


def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                 HUST BENCHMARK QUICK START                          ║
║                                                                      ║
║  This script runs parameter tuning and experiments on HUST instances║
║  and generates comparison charts and analysis.                       ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)


def main():
    print_banner()
    
    print("""
Choose an option:

1. 🚀 Run Everything (Tune + Experiment + Visualize)
2. ⚡ Just Run Experiments (15s per solver, quick)
3. 📊 Just Run Experiments (30s per solver, balanced)
4. 🔬 Deep Analysis (60s per solver, quality)
5. 📉 Visualize Latest Results
6. 📝 View Analysis Report

Enter choice (1-6): """, end="")
    
    choice = input().strip()
    
    if choice == '1':
        subprocess.run('python hust_workflow.py', shell=True)
    
    elif choice == '2':
        subprocess.run('python hust_workflow.py -s experiment -t 15', shell=True)
    
    elif choice == '3':
        subprocess.run('python hust_workflow.py -s experiment -t 30', shell=True)
    
    elif choice == '4':
        subprocess.run('python hust_workflow.py -s experiment -t 60', shell=True)
    
    elif choice == '5':
        subprocess.run('python visualize_hust.py', shell=True)
    
    elif choice == '6':
        # Find latest report
        import glob
        reports = sorted(glob.glob('hust_results_*/analysis_report.txt'))
        if reports:
            report_file = reports[-1]
            print(f"\n📄 Reading: {report_file}\n")
            with open(report_file, 'r') as f:
                print(f.read())
        else:
            print("No analysis reports found. Run experiments first.")
    
    else:
        print("Invalid choice")
        sys.exit(1)


if __name__ == "__main__":
    main()

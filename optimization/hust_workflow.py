#!/usr/bin/env python3
"""
Master script to run complete HUST benchmark workflow
1. Tune parameters
2. Run experiments
3. Generate visualizations
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime


def run_command(cmd, description, cwd=None):
    """Run a command and report status"""
    print(f"\n{'='*70}")
    print(f"📊 {description}")
    print(f"{'='*70}\n")
    
    result = subprocess.run(cmd, shell=True, cwd=cwd)
    
    if result.returncode != 0:
        print(f"\n❌ Command failed: {description}")
        return False
    
    print(f"\n✓ Completed: {description}")
    return True


def main():
    parser = argparse.ArgumentParser(description='HUST Benchmark Workflow')
    parser.add_argument('-s', '--step', choices=['all', 'tune', 'experiment', 'visualize'],
                       default='all', help='Which step to run')
    parser.add_argument('-t', '--time', type=float, default=30.0,
                       help='Time limit per solver (seconds)')
    parser.add_argument('-o', '--output', default=None,
                       help='Output directory')
    
    args = parser.parse_args()
    
    # Get path relative to script location
    script_dir = Path(__file__).parent.parent  # Go up from optimization/ to root
    data_dir = script_dir / 'data' / 'cbus_output_20260517_222958'
    
    if not data_dir.exists():
        print(f"Error: Data directory not found: {data_dir}")
        print(f"\nAvailable data directories in {script_dir / 'data'}:")
        data_parent = script_dir / 'data'
        if data_parent.exists():
            for item in data_parent.iterdir():
                if item.is_dir():
                    print(f"  - {item.name}")
        sys.exit(1)
    
    print(f"""
╔══════════════════════════════════════════════════════════════════════╗
║                  HUST BENCHMARK WORKFLOW                            ║
║                                                                      ║
║  Configuration:                                                      ║
║  - Data directory: {str(data_dir)}
║  - Time limit: {args.time}s per solver
║  - Steps: {args.step}
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Get path to optimization directory
    opt_dir = Path(__file__).parent
    
    # Step 1: Parameter Tuning (optional)
    if args.step in ['all', 'tune']:
        # Dùng sys.executable thay vì 'python' cứng và truyền args.time
        success = run_command(
            f'"{sys.executable}" tune_params.py -t {args.time}',
            'Parameter Tuning - Finding optimal solver configurations',
            cwd=str(opt_dir)
        )
        
        if not success and args.step == 'tune':
            print("\nParameter tuning had issues, but continuing...")
    
    # Step 2: Run Experiments
    if args.step in ['all', 'experiment']:
        if args.output:
            output_dir = args.output
        else:
            output_dir = f"hust_results_{timestamp}"
        
        import glob
        tuning_files = sorted(glob.glob(str(opt_dir / 'tuning_results_*/tuning_results.json')))
        params_arg = f' --params "{tuning_files[-1]}"' if tuning_files else ""
        
        cmd = f'"{sys.executable}" hust_experiment.py -t {args.time} -o "{output_dir}"{params_arg}'
        success = run_command(
            cmd,
            f'Running HUST Experiments - All instances with {args.time}s per solver',
            cwd=str(opt_dir)
        )
        
        if not success:
            print("\n❌ Experiment failed")
            sys.exit(1)
        
        # Store output directory for visualization
        results_file = os.path.join(output_dir, 'hust_results.json')
        
    else:
        # Find latest results
        import glob
        search_pattern = str(opt_dir / 'hust_results_*' / 'hust_results.json')
        results_files = sorted(glob.glob(search_pattern))
        if not results_files:
            print("Error: No results found. Run experiments first.")
            sys.exit(1)
        results_file = results_files[-1]
        output_dir = os.path.dirname(results_file)
    
    # Step 3: Visualization
    if args.step in ['all', 'visualize']:
        if not os.path.exists(results_file):
            print(f"Error: Results file not found: {results_file}")
            sys.exit(1)
        
        success = run_command(
            f'"{sys.executable}" visualize_hust.py "{results_file}"',
            f'Generating Visualizations - Creating charts and analysis',
            cwd=str(opt_dir)
        )
        if not success:
            print("\n⚠️  Visualization had some issues")
    
    # Summary
    print(f"\n{'='*70}")
    print("📋 WORKFLOW COMPLETE")
    print(f"{'='*70}\n")
    
    print(f"Results directory: {output_dir}")
    print("\nGenerated files:")
    print("  📊 hust_results.json      - Complete experimental data")
    print("  📈 hust_results.csv       - Summary for Excel")
    print("  📉 cost_comparison.png    - Cost comparison by instance")
    print("  ⏱️  time_comparison.png     - Execution time comparison")
    print("  📍 quality_vs_speed.png   - Quality vs speed trade-off")
    print("  📈 scalability.png        - Scalability analysis")
    print("  🔥 cost_heatmap.png       - Cost heatmap visualization")
    print("  📝 analysis_report.txt    - Detailed text report")
    
    print("\n💡 Next steps:")
    print("  1. Review CSV: Open hust_results.csv in Excel")
    print("  2. View charts: Check all .png files")
    print("  3. Read report: See analysis_report.txt for details")
    print("  4. Export: Share PNG files and CSV for presentations")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    main()

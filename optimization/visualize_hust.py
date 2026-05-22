"""
Visualization of HUST experiment results
Create comparison charts and performance analysis
"""

import json
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pathlib import Path
from typing import Dict, List

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10


class ResultsVisualizer:
    def __init__(self, results_file: str):
        self.results_file = results_file
        self.output_dir = os.path.dirname(results_file)
        
        with open(results_file, 'r') as f:
            self.results = json.load(f)
        
        # Convert to DataFrame
        self.df = self._create_dataframe()
    
    def _create_dataframe(self) -> pd.DataFrame:
        """Create DataFrame from results"""
        
        rows = []
        for instance_name, inst_data in self.results['instances'].items():
            n = inst_data['n']
            k = inst_data['k']
            
            for solver_name, solver_data in inst_data['solvers'].items():
                rows.append({
                    'Instance': instance_name,
                    'N': n,
                    'K': k,
                    'Method': solver_name,
                    'Cost': solver_data['cost'],
                    'Time': solver_data['time'],
                    'Valid': solver_data['valid']
                })
        
        return pd.DataFrame(rows)
    
    def plot_cost_comparison(self):
        """Plot cost comparison across instances"""
        
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        # Plot 1: Cost by instance
        ax1 = axes[0]
        df_valid = self.df[self.df['Valid'] == True]
        
        pivot_cost = df_valid.pivot_table(values='Cost', index='Instance', columns='Method', aggfunc='first')
        pivot_cost.plot(kind='bar', ax=ax1, width=0.8)
        ax1.set_title('Cost Comparison by Instance', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Instance', fontsize=12)
        ax1.set_ylabel('Total Distance', fontsize=12)
        ax1.legend(title='Solver', loc='best')
        ax1.grid(True, alpha=0.3)
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Plot 2: Average cost by N
        ax2 = axes[1]
        df_avg = df_valid.groupby(['N', 'Method'])['Cost'].mean().unstack()
        df_avg.plot(kind='bar', ax=ax2, width=0.8)
        ax2.set_title('Average Cost by Problem Size (N)', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Problem Size (N)', fontsize=12)
        ax2.set_ylabel('Average Total Distance', fontsize=12)
        ax2.legend(title='Solver', loc='best')
        ax2.grid(True, alpha=0.3)
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=0)
        
        plt.tight_layout()
        output_file = os.path.join(self.output_dir, 'cost_comparison.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_file}")
        plt.close()
    
    def plot_time_comparison(self):
        """Plot execution time comparison"""
        
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        # Plot 1: Time by instance
        ax1 = axes[0]
        df_valid = self.df[self.df['Valid'] == True]
        
        pivot_time = df_valid.pivot_table(values='Time', index='Instance', columns='Method', aggfunc='first')
        pivot_time.plot(kind='bar', ax=ax1, width=0.8, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
        ax1.set_title('Execution Time by Instance', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Instance', fontsize=12)
        ax1.set_ylabel('Time (seconds)', fontsize=12)
        ax1.legend(title='Solver', loc='best')
        ax1.grid(True, alpha=0.3, axis='y')
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Plot 2: Time vs Problem Size
        ax2 = axes[1]
        for method in df_valid['Method'].unique():
            df_method = df_valid[df_valid['Method'] == method].sort_values('N')
            ax2.plot(df_method['N'], df_method['Time'], marker='o', label=method, linewidth=2, markersize=8)
        
        ax2.set_title('Execution Time vs Problem Size', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Problem Size (N)', fontsize=12)
        ax2.set_ylabel('Time (seconds)', fontsize=12)
        ax2.legend(title='Solver', loc='best')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        output_file = os.path.join(self.output_dir, 'time_comparison.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_file}")
        plt.close()
    
    def plot_quality_vs_speed(self):
        """Plot quality vs speed trade-off"""
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        df_valid = self.df[self.df['Valid'] == True]
        
        colors = {'BnB': '#FF6B6B', 'OR-Tools': '#4ECDC4', 'ALNS': '#45B7D1'}
        sizes_map = {5: 50, 10: 100, 100: 200, 500: 300, 1000: 400}
        
        for method in df_valid['Method'].unique():
            for instance in df_valid['Instance'].unique():
                df_point = df_valid[(df_valid['Method'] == method) & (df_valid['Instance'] == instance)]
                
                if not df_point.empty:
                    row = df_point.iloc[0]
                    n_val = row['N']
                    size = sizes_map.get(n_val, 100)
                    
                    ax.scatter(row['Time'], row['Cost'], 
                             s=size, alpha=0.6, 
                             color=colors.get(method, 'gray'),
                             label=method if instance == df_valid['Instance'].unique()[0] else "",
                             edgecolors='black', linewidth=1.5)
                    
                    # Add instance label
                    ax.annotate(row['Instance'], 
                              (row['Time'], row['Cost']),
                              fontsize=8, alpha=0.7,
                              xytext=(5, 5), textcoords='offset points')
        
        ax.set_xlabel('Execution Time (seconds)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Total Distance (Cost)', fontsize=12, fontweight='bold')
        ax.set_title('Solution Quality vs Speed Trade-off', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # Create custom legend
        from matplotlib.patches import Patch
        legend_elements = [Patch(facecolor=colors[m], edgecolor='black', label=m) for m in colors.keys()]
        ax.legend(handles=legend_elements, loc='best', fontsize=11)
        
        plt.tight_layout()
        output_file = os.path.join(self.output_dir, 'quality_vs_speed.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_file}")
        plt.close()
    
    def plot_scalability(self):
        """Plot scalability analysis"""
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        df_valid = self.df[self.df['Valid'] == True]
        
        # Plot 1: Cost scaling
        ax1 = axes[0, 0]
        for method in df_valid['Method'].unique():
            df_method = df_valid[df_valid['Method'] == method].sort_values('N')
            avg_by_n = df_method.groupby('N')['Cost'].mean()
            ax1.plot(avg_by_n.index, avg_by_n.values, marker='o', label=method, linewidth=2, markersize=8)
        
        ax1.set_title('Average Cost Scaling', fontsize=12, fontweight='bold')
        ax1.set_xlabel('Problem Size (N)', fontsize=11)
        ax1.set_ylabel('Cost', fontsize=11)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Time scaling (log)
        ax2 = axes[0, 1]
        for method in df_valid['Method'].unique():
            df_method = df_valid[df_valid['Method'] == method].sort_values('N')
            avg_by_n = df_method.groupby('N')['Time'].mean()
            ax2.plot(avg_by_n.index, avg_by_n.values, marker='s', label=method, linewidth=2, markersize=8)
        
        ax2.set_title('Average Time Scaling (log scale)', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Problem Size (N)', fontsize=11)
        ax2.set_ylabel('Time (seconds)', fontsize=11)
        ax2.set_yscale('log')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Relative performance (vs best)
        ax3 = axes[1, 0]
        df_relative = df_valid.copy()
        
        for instance in df_relative['Instance'].unique():
            df_inst = df_relative[df_relative['Instance'] == instance]
            min_cost = df_inst['Cost'].min()
            df_inst_rel = df_inst.copy()
            df_inst_rel['Relative'] = (df_inst_rel['Cost'] / min_cost - 1) * 100
            
            for _, row in df_inst_rel.iterrows():
                if row['Relative'] > 0:
                    ax3.bar(f"{row['Instance']}\n{row['Method']}", row['Relative'], alpha=0.7)
        
        ax3.set_title('Performance Gap from Best Solution (%)', fontsize=12, fontweight='bold')
        ax3.set_ylabel('Gap (%)', fontsize=11)
        ax3.grid(True, alpha=0.3, axis='y')
        plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Plot 4: Solver wins
        ax4 = axes[1, 1]
        wins = {}
        for method in df_valid['Method'].unique():
            wins[method] = 0
        
        for instance in df_valid['Instance'].unique():
            df_inst = df_valid[df_valid['Instance'] == instance]
            best_method = df_inst.loc[df_inst['Cost'].idxmin(), 'Method']
            wins[best_method] += 1
        
        methods = list(wins.keys())
        win_counts = list(wins.values())
        colors_list = [{'BnB': '#FF6B6B', 'OR-Tools': '#4ECDC4', 'ALNS': '#45B7D1'}.get(m, 'gray') for m in methods]
        
        ax4.bar(methods, win_counts, color=colors_list, alpha=0.7, edgecolor='black', linewidth=2)
        ax4.set_title('Number of Instances Won', fontsize=12, fontweight='bold')
        ax4.set_ylabel('Wins', fontsize=11)
        ax4.grid(True, alpha=0.3, axis='y')
        
        for i, (method, count) in enumerate(zip(methods, win_counts)):
            ax4.text(i, count + 0.1, str(count), ha='center', fontweight='bold')
        
        plt.tight_layout()
        output_file = os.path.join(self.output_dir, 'scalability.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_file}")
        plt.close()
    
    def plot_heatmap(self):
        """Create heatmap of costs"""
        
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        
        df_valid = self.df[self.df['Valid'] == True]
        
        for i, method in enumerate(['BnB', 'OR-Tools', 'ALNS']):
            df_method = df_valid[df_valid['Method'] == method]
            pivot = df_method.pivot_table(values='Cost', index='N', columns='Instance', aggfunc='first')
            
            if not pivot.empty:
                sns.heatmap(pivot, annot=True, fmt='.0f', cmap='YlGnBu', ax=axes[i], 
                          cbar_kws={'label': 'Cost'})
                axes[i].set_title(f'{method} - Cost Heatmap', fontsize=12, fontweight='bold')
                axes[i].set_xlabel('Instance', fontsize=11)
                axes[i].set_ylabel('Problem Size (N)', fontsize=11)
        
        plt.tight_layout()
        output_file = os.path.join(self.output_dir, 'cost_heatmap.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_file}")
        plt.close()
    
    def generate_report(self):
        """Generate text report"""
        
        report_file = os.path.join(self.output_dir, 'analysis_report.txt')
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write("HUST BENCHMARK ANALYSIS REPORT\n")
            f.write("="*70 + "\n\n")
            
            df_valid = self.df[self.df['Valid'] == True]
            
            # Summary statistics
            f.write("SUMMARY STATISTICS\n")
            f.write("-"*70 + "\n")
            
            for method in df_valid['Method'].unique():
                df_method = df_valid[df_valid['Method'] == method]
                
                f.write(f"\n{method}:\n")
                f.write(f"  Instances completed: {df_method['Instance'].nunique()}\n")
                f.write(f"  Average cost:        {df_method['Cost'].mean():.1f}\n")
                f.write(f"  Min cost:            {df_method['Cost'].min():.1f}\n")
                f.write(f"  Max cost:            {df_method['Cost'].max():.1f}\n")
                f.write(f"  Std dev:             {df_method['Cost'].std():.1f}\n")
                f.write(f"  Average time:        {df_method['Time'].mean():.2f}s\n")
                f.write(f"  Min time:            {df_method['Time'].min():.2f}s\n")
                f.write(f"  Max time:            {df_method['Time'].max():.2f}s\n")
            
            # Instance-by-instance
            f.write("\n\nINSTANCE RESULTS\n")
            f.write("-"*70 + "\n")
            
            for instance in sorted(df_valid['Instance'].unique()):
                df_inst = df_valid[df_valid['Instance'] == instance]
                n = df_inst['N'].iloc[0]
                k = df_inst['K'].iloc[0]
                
                f.write(f"\n{instance} (n={n}, k={k}):\n")
                
                for _, row in df_inst.iterrows():
                    f.write(f"  {row['Method']:<12} Cost={row['Cost']:<8} Time={row['Time']:.2f}s\n")
                
                best_cost = df_inst['Cost'].min()
                best_method = df_inst.loc[df_inst['Cost'].idxmin(), 'Method']
                f.write(f"  ⭐ Winner: {best_method} (cost={best_cost})\n")
            
            # Performance gaps
            f.write("\n\nPERFORMANCE GAPS\n")
            f.write("-"*70 + "\n")
            f.write("Gap from best solution (%):\n\n")
            
            for method in df_valid['Method'].unique():
                total_gap = 0
                count = 0
                
                for instance in df_valid['Instance'].unique():
                    df_inst = df_valid[df_valid['Instance'] == instance]
                    
                    df_method_inst = df_inst[df_inst['Method'] == method]
                    if not df_method_inst.empty:
                        best_cost = df_inst['Cost'].min()
                        method_cost = df_method_inst['Cost'].iloc[0]
                        gap = (method_cost - best_cost) / best_cost * 100
                        total_gap += gap
                        count += 1
                
                avg_gap = total_gap / count if count > 0 else 0
                f.write(f"{method:<12}: {avg_gap:>6.2f}%\n")
        
        print(f"✓ Saved: {report_file}")
    
    def create_all_charts(self):
        """Create all charts"""
        
        print("\nGenerating visualizations...\n")
        
        print("Creating cost comparison chart...")
        self.plot_cost_comparison()
        
        print("Creating time comparison chart...")
        self.plot_time_comparison()
        
        print("Creating quality vs speed chart...")
        self.plot_quality_vs_speed()
        
        print("Creating scalability analysis...")
        self.plot_scalability()
        
        print("Creating cost heatmap...")
        self.plot_heatmap()
        
        print("Generating text report...")
        self.generate_report()
        
        print("\n✓ All visualizations created!")


def main():
    if len(sys.argv) < 2:
        # Find latest results file
        import glob
        results_files = glob.glob('hust_results_*/hust_results.json')
        if not results_files:
            print("Error: No results file found")
            print("Usage: python visualize.py <results_json_file>")
            sys.exit(1)
        
        results_file = sorted(results_files)[-1]
        print(f"Using latest results: {results_file}")
    else:
        results_file = sys.argv[1]
    
    if not os.path.exists(results_file):
        print(f"Error: File not found: {results_file}")
        sys.exit(1)
    
    visualizer = ResultsVisualizer(results_file)
    visualizer.create_all_charts()


if __name__ == "__main__":
    main()

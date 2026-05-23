# ============================================
# File: results/optimization/visualize_tuning.py
# ============================================

import json
import os
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# =========================================================
# CONFIG
# =========================================================

JSON_FILE = "optimization/tuning_results_20260523_152544/tuning_results.json"   # đổi path nếu cần
OUTPUT_DIR = "results/optimization"

os.makedirs(OUTPUT_DIR, exist_ok=True)


# =========================================================
# LOAD JSON
# =========================================================

with open(JSON_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)


# =========================================================
# HELPERS
# =========================================================

def save_plot(name):
    path = os.path.join(OUTPUT_DIR, name)
    plt.tight_layout()
    plt.savefig(path, dpi=300)
    print(f"Saved: {path}")
    plt.close()


# =========================================================
# PROCESS EACH INSTANCE
# =========================================================

for instance_name, instance_data in data.items():

    print(f"\nProcessing {instance_name}...")

    n = instance_data["n"]
    k = instance_data["k"]

    # =====================================================
    # ORTOOLS
    # =====================================================

    ortools_data = pd.DataFrame(instance_data["ortools"])

    if not ortools_data.empty:

        # ---------------------------------------------
        # Cost comparison
        # ---------------------------------------------

        plt.figure(figsize=(10, 5))

        labels = (
            "S"
            + ortools_data["strategy"].astype(str)
            + "_M"
            + ortools_data["metaheuristic"].astype(str)
            + "_T"
            + ortools_data["time_multiplier"].astype(str)
        )

        plt.bar(labels, ortools_data["cost"])

        plt.xticks(rotation=45)
        plt.ylabel("Cost")
        plt.title(f"{instance_name} - ORTools Cost Comparison")

        save_plot(f"{instance_name}_ortools_cost.png")

        # ---------------------------------------------
        # Runtime comparison
        # ---------------------------------------------

        plt.figure(figsize=(10, 5))

        plt.bar(labels, ortools_data["time"])

        plt.xticks(rotation=45)
        plt.ylabel("Runtime (s)")
        plt.title(f"{instance_name} - ORTools Runtime")

        save_plot(f"{instance_name}_ortools_runtime.png")

        # ---------------------------------------------
        # Scatter cost vs runtime
        # ---------------------------------------------

        plt.figure(figsize=(7, 6))

        plt.scatter(
            ortools_data["time"],
            ortools_data["cost"],
        )

        for i, txt in enumerate(labels):
            plt.annotate(
                txt,
                (
                    ortools_data["time"].iloc[i],
                    ortools_data["cost"].iloc[i],
                ),
                fontsize=8,
            )

        plt.xlabel("Runtime (s)")
        plt.ylabel("Cost")
        plt.title(f"{instance_name} - ORTools Cost vs Runtime")

        save_plot(f"{instance_name}_ortools_scatter.png")

    # =====================================================
    # ALNS
    # =====================================================

    alns_data = pd.DataFrame(instance_data["alns"])

    if not alns_data.empty:

        # ---------------------------------------------
        # Iterations vs cost
        # ---------------------------------------------

        plt.figure(figsize=(10, 5))

        grouped = (
            alns_data.groupby("iterations")["cost"]
            .mean()
            .reset_index()
        )

        plt.plot(
            grouped["iterations"],
            grouped["cost"],
            marker="o",
        )

        plt.xlabel("Iterations")
        plt.ylabel("Average Cost")
        plt.title(f"{instance_name} - ALNS Iterations vs Cost")

        save_plot(f"{instance_name}_alns_iterations_cost.png")

        # ---------------------------------------------
        # Cooling rate vs cost
        # ---------------------------------------------

        plt.figure(figsize=(10, 5))

        grouped = (
            alns_data.groupby("cooling_rate")["cost"]
            .mean()
            .reset_index()
        )

        plt.plot(
            grouped["cooling_rate"],
            grouped["cost"],
            marker="o",
        )

        plt.xlabel("Cooling Rate")
        plt.ylabel("Average Cost")
        plt.title(f"{instance_name} - ALNS Cooling Rate vs Cost")

        save_plot(f"{instance_name}_alns_cooling_cost.png")

        # ---------------------------------------------
        # Temperature vs cost
        # ---------------------------------------------

        plt.figure(figsize=(10, 5))

        grouped = (
            alns_data.groupby("initial_temp")["cost"]
            .mean()
            .reset_index()
        )

        plt.plot(
            grouped["initial_temp"],
            grouped["cost"],
            marker="o",
        )

        plt.xlabel("Initial Temperature")
        plt.ylabel("Average Cost")
        plt.title(f"{instance_name} - ALNS Temperature vs Cost")

        save_plot(f"{instance_name}_alns_temp_cost.png")

        # ---------------------------------------------
        # Runtime vs cost scatter
        # ---------------------------------------------

        plt.figure(figsize=(7, 6))

        plt.scatter(
            alns_data["time"],
            alns_data["cost"],
        )

        for i, row in alns_data.iterrows():

            label = (
                f"I{row['iterations']}"
                f"_C{row['cooling_rate']}"
                f"_T{row['initial_temp']}"
            )

            plt.annotate(
                label,
                (row["time"], row["cost"]),
                fontsize=7,
            )

        plt.xlabel("Runtime (s)")
        plt.ylabel("Cost")
        plt.title(f"{instance_name} - ALNS Cost vs Runtime")

        save_plot(f"{instance_name}_alns_scatter.png")

    # =====================================================
    # SUMMARY CSV
    # =====================================================

    summary_rows = []

    # ORTOOLS BEST
    if not ortools_data.empty:

        best_ort = ortools_data.loc[ortools_data["cost"].idxmin()]

        summary_rows.append({
            "solver": "ORTools",
            "best_cost": best_ort["cost"],
            "runtime": best_ort["time"],
            "config": (
                f"strategy={best_ort['strategy']}, "
                f"meta={best_ort['metaheuristic']}, "
                f"time_mult={best_ort['time_multiplier']}"
            )
        })

    # ALNS BEST
    if not alns_data.empty:

        best_alns = alns_data.loc[alns_data["cost"].idxmin()]

        summary_rows.append({
            "solver": "ALNS",
            "best_cost": best_alns["cost"],
            "runtime": best_alns["time"],
            "config": (
                f"iter={best_alns['iterations']}, "
                f"cool={best_alns['cooling_rate']}, "
                f"temp={best_alns['initial_temp']}"
            )
        })

    summary_df = pd.DataFrame(summary_rows)

    csv_path = os.path.join(
        OUTPUT_DIR,
        f"{instance_name}_summary.csv"
    )

    summary_df.to_csv(csv_path, index=False)

    print(f"Saved: {csv_path}")


print("\n====================================")
print("Visualization complete.")
print(f"Output folder: {OUTPUT_DIR}")
print("====================================")
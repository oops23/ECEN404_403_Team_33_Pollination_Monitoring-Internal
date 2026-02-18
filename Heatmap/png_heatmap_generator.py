# png_heatmap_generator.py

import json
import numpy as np
import matplotlib.pyplot as plt
import math
from ML.bee_classifier import BeeClassifier

# ===============================
# LIDAR CONFIG
# ===============================
ANGLE_START_DEG = 0.0
ANGLE_INCREMENT_DEG = 0.5

# ===============================
# LOAD CLASSIFIER
# ===============================
classifier = BeeClassifier()

# ===============================
# POLAR TO XY
# ===============================
def polar_to_xy(distance_m, angle_index):
    angle_deg = ANGLE_START_DEG + angle_index * ANGLE_INCREMENT_DEG
    angle_rad = math.radians(angle_deg)

    x = distance_m * math.cos(angle_rad)
    y = distance_m * math.sin(angle_rad)

    return x, y

# ===============================
# PROCESS EVENTS
# ===============================
def process_file(filepath):
    bee_positions = []

    with open(filepath, "r") as f:
        for line in f:
            event = json.loads(line)

            # classify
            is_bee = classifier.predict(event)

            if not is_bee:
                continue

            angles = event["angles"]
            distance_series = event["distance_series"]

            # average across event
            avg_distances = np.mean(distance_series, axis=0)

            # compute center position of this visit
            xs = []
            ys = []

            for angle_index, distance in zip(angles, avg_distances):
                x, y = polar_to_xy(distance, angle_index)
                xs.append(x)
                ys.append(y)

            # store center of cluster
            bee_positions.append((np.mean(xs), np.mean(ys)))

    return bee_positions

# ===============================
# PLOT
# ===============================
def show_map(bee_positions):

    if len(bee_positions) == 0:
        print("No bees detected")
        return

    xs = [p[0] for p in bee_positions]
    ys = [p[1] for p in bee_positions]

    fig, ax = plt.subplots(figsize=(8, 8))

    # soft background
    ax.set_facecolor("#f8fafc")
    fig.patch.set_facecolor("#ffffff")

    # pollinator hits
    ax.scatter(
        xs,
        ys,
        s=350,
        alpha=0.75,
        edgecolors="white",
        linewidth=1.5
    )

    # remove top and right borders
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # clean axes
    ax.set_xlabel("Distance X (m)", fontsize=11)
    ax.set_ylabel("Distance Y (m)", fontsize=11)

    ax.set_title(
        f"Pollinator Activity Map\nTotal Visits: {len(bee_positions)}",
        fontsize=14,
        pad=20
    )

    ax.set_aspect("equal", adjustable="box")

    # slight padding around points
    padding = 0.2
    ax.set_xlim(min(xs) - padding, max(xs) + padding)
    ax.set_ylim(min(ys) - padding, max(ys) + padding)

    plt.tight_layout()
    plt.savefig("pollinator_heatmap.png", dpi=300) 
    plt.show()

# ===============================
# MAIN
# ===============================
if __name__ == "__main__":
    bees = process_file("./flower_setup/flower_events_02-01-2026_13.56.56.jsonl")
    show_map(bees)
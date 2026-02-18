import json
import numpy as np
import math
import webbrowser
import os
import plotly.graph_objects as go
from ML.bee_classifier import BeeClassifier

# ===============================
# LIDAR CONFIG
# ===============================
ANGLE_START_DEG = 0.0
ANGLE_INCREMENT_DEG = 0.5
LIDAR_HEIGHT = 0.5  # meters

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

            if not classifier.predict(event):
                continue

            angles = event["angles"]
            distance_series = event["distance_series"]

            avg_distances = np.mean(distance_series, axis=0)

            xs = []
            ys = []

            for angle_index, distance in zip(angles, avg_distances):
                x, y = polar_to_xy(distance, angle_index)
                xs.append(x)
                ys.append(y)

            bee_positions.append((np.mean(xs), np.mean(ys)))

    return bee_positions

# ===============================
# CREATE INTERACTIVE PLOT
# ===============================
def create_interactive_plot(bee_positions):

    xs = np.array([p[0] for p in bee_positions])
    ys = np.array([p[1] for p in bee_positions])
    zs = np.full_like(xs, LIDAR_HEIGHT)

    max_range = max(
        np.max(np.abs(xs)) if len(xs) > 0 else 1,
        np.max(np.abs(ys)) if len(ys) > 0 else 1
    ) + 0.5

    fig = go.Figure()

    # Bees
    fig.add_trace(go.Scatter3d(
        x=xs,
        y=ys,
        z=zs,
        mode="markers",
        marker=dict(
            size=8,
            opacity=0.9
        ),
        name="Pollinator Hits"
    ))

    # Lidar pole
    fig.add_trace(go.Scatter3d(
        x=[0, 0],
        y=[0, 0],
        z=[0, LIDAR_HEIGHT],
        mode="lines",
        line=dict(width=8),
        name="LiDAR Stand"
    ))

    # Lidar head
    fig.add_trace(go.Scatter3d(
        x=[0],
        y=[0],
        z=[LIDAR_HEIGHT],
        mode="markers",
        marker=dict(size=12),
        name="LiDAR Sensor"
    ))

    fig.update_layout(
        title=f"3D Pollinator Activity Map | Total Visits: {len(bee_positions)}",
        scene=dict(
            xaxis=dict(range=[-max_range, max_range], title="X (m)"),
            yaxis=dict(range=[-max_range, max_range], title="Y (m)"),
            zaxis=dict(range=[0, LIDAR_HEIGHT + 0.5], title="Height (m)")
        ),
        margin=dict(l=0, r=0, b=0, t=50)
    )

    return fig

# ===============================
# MAIN
# ===============================
if __name__ == "__main__":

    bees = process_file("./flower_setup/flower_events_02-01-2026_13.56.56.jsonl")

    fig = create_interactive_plot(bees)

    # Save interactive HTML
    fig.write_html("pollinator_3d_dashboard.html")

    file_path = os.path.abspath("pollinator_3d_dashboard.html")
    webbrowser.open(f"file://{file_path}")

    print("Interactive 3D dashboard saved as pollinator_3d_dashboard.html")
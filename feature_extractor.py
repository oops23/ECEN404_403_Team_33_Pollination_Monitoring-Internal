import json
import numpy as np
import pandas as pd

# ---------------------------------------------------
# Adjust these paths
# ---------------------------------------------------

INPUT_FILE = "./flower_setup/flower_events_02-02-2026_17.00.55.jsonl"      # your event_detector output
OUTPUT_FILE = "event_features.csv"

# If you have background distances per flower from setup_flower
# Replace these values with your real ones
FLOWER_BACKGROUND = {
    "flower_1": 0.36,
}

# ---------------------------------------------------
# Helper functions
# ---------------------------------------------------

def count_local_minima(signal):
    count = 0
    for i in range(1, len(signal) - 1):
        if signal[i] < signal[i - 1] and signal[i] < signal[i + 1]:
            count += 1
    return count


def count_sign_changes(diff_signal):
    count = 0
    for i in range(1, len(diff_signal)):
        if diff_signal[i - 1] * diff_signal[i] < 0:
            count += 1
    return count


# ---------------------------------------------------
# Main feature extraction
# ---------------------------------------------------

def extract_features(event):
    event_id = event["event_id"]
    flower_id = event["flower_id"]
    start_time = event["start_time"]
    end_time = event["end_time"]
    num_scans = event["num_scans"]
    angles = event["angles"]
    distance_series = np.array(event["distance_series"])

    num_angles = len(angles)
    visit_duration = end_time - start_time

    # background distance for this flower
    background_distance = FLOWER_BACKGROUND.get(flower_id, None)

    # ---- Core signals ----

    min_dist = np.min(distance_series, axis=1)
    mean_dist = np.mean(distance_series, axis=1)
    spread = np.max(distance_series, axis=1) - np.min(distance_series, axis=1)

    # ---- Temporal features ----

    min_distance_reached = np.min(min_dist)
    mean_distance_during_visit = np.mean(min_dist)

    if background_distance is not None:
        depth_of_interaction = background_distance - min_distance_reached
    else:
        depth_of_interaction = 0.0

    idx_min = np.argmin(min_dist)

    # avoid division by zero
    if visit_duration > 0 and num_scans > 1:
        time_to_min = visit_duration * (idx_min / num_scans)
        time_from_min = visit_duration - time_to_min

        if time_to_min > 0:
            approach_speed = (min_dist[0] - min_dist[idx_min]) / time_to_min
        else:
            approach_speed = 0.0

        if time_from_min > 0:
            departure_speed = (min_dist[-1] - min_dist[idx_min]) / time_from_min
        else:
            departure_speed = 0.0
    else:
        approach_speed = 0.0
        departure_speed = 0.0

    symmetry = abs(approach_speed - departure_speed)

    # ---- Oscillation and jitter ----

    std_min_dist = np.std(min_dist)

    local_minima_count = count_local_minima(min_dist)

    diff_signal = np.diff(min_dist)
    sign_change_count = count_sign_changes(diff_signal)

    total_movement_energy = np.sum(np.abs(diff_signal))

    # ---- Spatial features ----

    mean_spread = np.mean(spread)
    spread_variance = np.var(spread)

    # angle stability
    angle_std = np.std(distance_series, axis=0)
    angle_stability = np.mean(angle_std)

    # ---- Build feature dictionary ----

    features = {
        "event_id": event_id,
        "flower_id": flower_id,
        "visit_duration": visit_duration,
        "num_scans": num_scans,
        "num_angles": num_angles,
        "min_distance_reached": min_distance_reached,
        "mean_distance_during_visit": mean_distance_during_visit,
        "depth_of_interaction": depth_of_interaction,
        "approach_speed": approach_speed,
        "departure_speed": departure_speed,
        "symmetry": symmetry,
        "std_min_dist": std_min_dist,
        "local_minima_count": local_minima_count,
        "sign_change_count": sign_change_count,
        "total_movement_energy": total_movement_energy,
        "mean_spread": mean_spread,
        "spread_variance": spread_variance,
        "angle_stability": angle_stability,
    }

    return features


# ---------------------------------------------------
# Run extraction on entire file
# ---------------------------------------------------

def main():
    feature_rows = []

    with open(INPUT_FILE, "r") as f:
        for line in f:
            event = json.loads(line.strip())
            features = extract_features(event)
            feature_rows.append(features)

    df = pd.DataFrame(feature_rows)

    # Save CSV
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"Saved features to {OUTPUT_FILE}")
    print(f"Total events processed: {len(df)}")


if __name__ == "__main__":
    main()
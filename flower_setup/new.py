import socket
import json
import time
from datetime import datetime

HOST = "169.254.251.84"
PORT = 2112

CMD_START = b"\x02sEN LMDscandata 1\x03"
CMD_STOP = b"\x02sEN LMDscandata 0\x03"

DROP_THRESHOLD = 0.2
MIN_BLOCK_SIZE = 3


def parse_scan(telegram):
    parts = telegram.strip().split(" ")

    if "DIST1" not in parts:
        return None

    try:
        num_index = parts.index("DIST1") + 5
        num_values = int(parts[num_index], 16)

        distances = [
            int(v, 16) / 1000.0
            for v in parts[num_index + 1 : num_index + 1 + num_values]
        ]

        return distances

    except Exception:
        return None


def find_blocks(indices):
    if not indices:
        return []

    blocks = []
    current = [indices[0]]

    for idx in indices[1:]:
        if idx == current[-1] + 1:
            current.append(idx)
        else:
            if len(current) >= MIN_BLOCK_SIZE:
                blocks.append(current)
            current = [idx]

    if len(current) >= MIN_BLOCK_SIZE:
        blocks.append(current)

    return blocks


def main():
    timestamp = datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
    out_file = f"lidar_log_{timestamp}.jsonl"

    baseline_scan = None
    scan_count = 0

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(CMD_START)

        print("Connected to LiDAR")
        print("Waiting for baseline scan\n")

        buffer = ""

        with open(out_file, "w") as f:
            try:
                while True:
                    data = s.recv(4096).decode(errors="ignore")
                    buffer += data

                    while "\x03" in buffer:
                        telegram, buffer = buffer.split("\x03", 1)
                        telegram = telegram.replace("\x02", "").strip()

                        distances = parse_scan(telegram)
                        if not distances:
                            continue

                        scan_count += 1

                        if baseline_scan is None:
                            baseline_scan = distances
                            print(f"Baseline captured with {len(distances)} points")
                            continue

                        changed_indices = [
                            i
                            for i, (b, d) in enumerate(zip(baseline_scan, distances))
                            if (b - d) > DROP_THRESHOLD
                        ]

                        blocks = find_blocks(changed_indices)

                        if blocks:
                            print(f"\nScan {scan_count}")
                            for block in blocks:
                                values = [distances[i] for i in block]
                                print(f"Detected block indices {block}")
                                print(f"Distances {['%.2f' % v for v in values]}")

                        scan = {
                            "timestamp": time.time(),
                            "num_points": len(distances),
                            "ranges": distances,
                            "changed_blocks": blocks,
                        }

                        f.write(json.dumps(scan) + "\n")

            except KeyboardInterrupt:
                print("\nStopping stream")

            finally:
                s.sendall(CMD_STOP)
                print(f"\nSaved log to {out_file}")
                print(f"Total scans {scan_count}")


if __name__ == "__main__":
    main()

import math
import sys
import os
from pathlib import Path
import glob
from datetime import datetime


def euclidean(a, b):
    return round(math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2))


def parse_lilim(filepath):
    with open(filepath, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    # Header
    vehicle_num, capacity, _ = map(int, lines[0].split())

    nodes = {}

    for line in lines[1:]:
        parts = line.split()

        if len(parts) < 9:
            continue

        node_id = int(parts[0])
        x = int(parts[1])
        y = int(parts[2])
        demand = int(parts[3])
        ready = int(parts[4])
        due = int(parts[5])
        service = int(parts[6])
        pickup = int(parts[7])
        delivery = int(parts[8])

        nodes[node_id] = {
            "x": x,
            "y": y,
            "demand": demand,
            "pickup": pickup,
            "delivery": delivery
        }

    return capacity, nodes


def extract_pairs(nodes):
    pairs = []

    for node_id, node in nodes.items():
        if node["demand"] > 0 and node["delivery"] != 0:
            pickup_id = node_id
            dropoff_id = node["delivery"]

            if dropoff_id in nodes:
                pairs.append((pickup_id, dropoff_id))

    return pairs


def build_cbus_matrix(nodes, pairs):
    coords = []

    # depot
    coords.append((nodes[0]["x"], nodes[0]["y"]))

    # pickups
    for p, d in pairs:
        coords.append((nodes[p]["x"], nodes[p]["y"]))

    # dropoffs
    for p, d in pairs:
        coords.append((nodes[d]["x"], nodes[d]["y"]))

    size = len(coords)

    matrix = []
    for i in range(size):
        row = []
        for j in range(size):
            row.append(euclidean(coords[i], coords[j]))
        matrix.append(row)

    return matrix


def save_cbus(output_path, n, k, matrix):
    with open(output_path, "w") as f:
        f.write(f"{n} {k}\n")

        for row in matrix:
            f.write(" ".join(map(str, row)) + "\n")


def convert_single_file(input_file, output_file, n=10, k=3):
    """
    Convert a single LILIM file to CBUS format
    Returns: True if successful, False otherwise
    """
    try:
        capacity, nodes = parse_lilim(input_file)
        pairs = extract_pairs(nodes)

        if len(pairs) < n:
            print(f"  ⚠ Warning: Only found {len(pairs)} valid pickup-delivery pairs (need {n})")
            # Use all available pairs if less than n
            selected = pairs[:len(pairs)]
            actual_n = len(selected)
        else:
            selected = pairs[:n]
            actual_n = n

        if len(selected) == 0:
            print(f"  ✗ Error: No valid pairs found")
            return False

        matrix = build_cbus_matrix(nodes, selected)
        save_cbus(output_file, actual_n, k, matrix)

        print(f"  ✓ Converted successfully")
        print(f"    Output: {output_file}")
        print(f"    Requests: {actual_n}")
        print(f"    Bus capacity: {k}")
        return True

    except Exception as e:
        print(f"  ✗ Error converting {input_file}: {str(e)}")
        return False


def convert_all_in_folder(input_folder, output_folder=None, n=10, k=3):
    """
    Convert all .txt files in input_folder to CBUS format
    """
    # Create output folder if not specified
    if output_folder is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_folder = f"cbus_output_{timestamp}"

    # Create output directory
    Path(output_folder).mkdir(parents=True, exist_ok=True)

    # Find all .txt files in input folder
    input_path = Path(input_folder)
    txt_files = list(input_path.glob("*.txt"))

    if not txt_files:
        print(f"No .txt files found in {input_folder}")
        return

    print(f"Found {len(txt_files)} .txt file(s) in {input_folder}")
    print(f"Output folder: {output_folder}")
    print(f"Settings: max_requests={n}, bus_capacity={k}")
    print("-" * 60)

    success_count = 0
    fail_count = 0

    for i, txt_file in enumerate(txt_files, 1):
        print(f"\n[{i}/{len(txt_files)}] Processing: {txt_file.name}")

        # Generate output filename
        stem = txt_file.stem
        output_file = Path(output_folder) / f"{stem}_cbus.txt"

        if convert_single_file(str(txt_file), str(output_file), n, k):
            success_count += 1
        else:
            fail_count += 1

    print("\n" + "=" * 60)
    print(f"Conversion complete!")
    print(f"  ✓ Successful: {success_count}")
    print(f"  ✗ Failed: {fail_count}")
    print(f"  Output folder: {output_folder}")


def print_usage():
    print(
        "Usage:\n"
        "  Single file mode:\n"
        "    python convert_lilim_to_cbus.py -f input.txt output.txt [n] [k]\n"
        "  Batch folder mode:\n"
        "    python convert_lilim_to_cbus.py -d input_folder [output_folder] [n] [k]\n\n"
        "Options:\n"
        "  -f, --file       Convert a single file\n"
        "  -d, --directory  Convert all .txt files in directory\n"
        "  n                Number of requests (default: 10)\n"
        "  k                Bus capacity (default: 3)"
    )


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print_usage()
        sys.exit(1)

    mode = sys.argv[1]

    if mode in ["-f", "--file"]:
        # Single file mode (backward compatible)
        if len(sys.argv) < 4:
            print("Error: Input and output files required for single file mode")
            print_usage()
            sys.exit(1)

        input_file = sys.argv[2]
        output_file = sys.argv[3]
        n = int(sys.argv[4]) if len(sys.argv) > 4 else 10
        k = int(sys.argv[5]) if len(sys.argv) > 5 else 3

        convert_single_file(input_file, output_file, n, k)

    elif mode in ["-d", "--directory"]:
        # Batch folder mode
        input_folder = sys.argv[2]
        output_folder = sys.argv[3] if len(sys.argv) > 3 else None
        n = int(sys.argv[4]) if len(sys.argv) > 4 else 10
        k = int(sys.argv[5]) if len(sys.argv) > 5 else 3

        convert_all_in_folder(input_folder, output_folder, n, k)

    else:
        print(f"Unknown mode: {mode}")
        print_usage()
        sys.exit(1)
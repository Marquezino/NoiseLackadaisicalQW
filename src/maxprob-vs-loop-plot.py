import argparse
import matplotlib.pyplot as plt
from shared_utils import format_bl_label, load_json, merge_nested_float_dict, require_consistent_metadata


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Plot maxprob-vs-loop data from JSON file(s).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("files", nargs="*", default=["maxprob-vs-loop-data.json"], help="JSON data files to load and merge.")
    parser.add_argument("--output", "-o", default="maxprob-vs-loop.pdf", help="Output PDF filename.")
    args = parser.parse_args()

    merged = {}
    metadata = {}
    for filename in args.files:
        payload = load_json(filename)
        if payload is None:
            raise FileNotFoundError(f"Data file {filename} not found.")
        merged = merge_nested_float_dict(merged, payload.get("data", {}))
        metadata = require_consistent_metadata(payload, filename, metadata, ("grid_size",), cast=int)

    grid_size = metadata["grid_size"]

    for bl_prob in sorted(merged.keys()):
        by_ell = merged[bl_prob]
        ordered = sorted(by_ell.items(), key=lambda kv: kv[0])
        x_vals = [k for k, _ in ordered]
        y_vals = [entry["max_prob"] for _, entry in ordered]
        plt.plot(x_vals, y_vals, "-x", label=format_bl_label(bl_prob))

    plt.xlabel("Self-loop weight ($\\ell$)")
    plt.ylabel("Maximum success probability ($P_{max}$)")
    plt.xscale('log')
    plt.axvline(x=4 / (grid_size ** 2), linestyle=":", label="$4/N$")
    plt.legend(loc="upper right")
    plt.tight_layout()
    plt.savefig(args.output)
    print(f"Plot saved to {args.output}")

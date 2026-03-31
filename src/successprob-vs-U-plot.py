import argparse
import matplotlib.pyplot as plt
import numpy as np

from shared_utils import format_ell_label, load_json, require_consistent_metadata


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Plot successprob-vs-U data from JSON file(s).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("files", nargs="*", default=["successprob-vs-U-data.json"], help="JSON data files to load and merge.")
    parser.add_argument("--output", "-o", default="successprob-vs-U.pdf", help="Output PDF filename.")
    args = parser.parse_args()

    merged = {}
    metadata = {}
    for filename in args.files:
        payload = load_json(filename)
        if payload is None:
            raise FileNotFoundError(f"Data file {filename} not found.")
        merged.update(payload.get("data", {}))
        metadata = require_consistent_metadata(payload, filename, metadata, ("n_sites",), cast=int)

    n_sites = metadata["n_sites"]

    style_cycle = ["k-", "b--", "r-.", "g:"]
    plt.figure()
    for i, key in enumerate(sorted(merged.keys(), key=lambda k: merged[k]["ell"])):
        branch = merged[key]
        probs = np.array(branch["probs"])
        branch_label = branch.get("ell_label", branch.get("label", format_ell_label(branch["ell"], n_sites)))
        plt.plot(probs, style_cycle[i % len(style_cycle)], label=f"$\\ell={branch_label}$")

    plt.xlabel("Steps")
    plt.ylabel("Success probability")
    plt.legend(loc="upper right")
    plt.tight_layout()
    plt.savefig(args.output)
    print(f"Plot saved to {args.output}")

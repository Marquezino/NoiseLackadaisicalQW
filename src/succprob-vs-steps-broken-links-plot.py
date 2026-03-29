import argparse
import matplotlib.pyplot as plt
import numpy as np
from shared_utils import format_bl_label, load_json


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot succprob-vs-steps-broken-links data from JSON file(s).")
    parser.add_argument("files", nargs="*", default=["succprob-vs-steps-broken-links-data.json"])
    parser.add_argument("--output", "-o", default="succprob-vs-steps-broken-links.pdf")
    args = parser.parse_args()

    merged = {}
    metadata = {}
    for filename in args.files:
        payload = load_json(filename)
        if payload is None:
            raise FileNotFoundError(f"Data file {filename} not found.")
        merged.update(payload.get("data", {}))
        metadata = payload

    n_sites = metadata["n_sites"]
    ordering = sorted(merged.keys(), key=lambda k: merged[k]["bl_prob"])
    style_cycle = ["k-", "b--", "r-.", "g:"]

    plt.figure()
    for i, key in enumerate(ordering):
        branch = merged[key]
        probs = np.array(branch["probs"])
        stds = np.array(branch["stds"])
        line = style_cycle[i % len(style_cycle)]
        plt.plot(probs, line, label=format_bl_label(branch["bl_prob"]))
        if branch["shots"] > 1:
            color = line[0]
            plt.fill_between(range(len(probs)), probs - stds, probs + stds, alpha=0.15, color=color)

    plt.axhline(y=1 / n_sites, linestyle=":", label="uniform")
    plt.xlabel("Steps")
    plt.ylabel("Success probability")
    plt.legend(loc="upper right")
    plt.tight_layout()
    plt.savefig(args.output)
    print(f"Plot saved to {args.output}")

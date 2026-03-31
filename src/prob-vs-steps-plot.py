import argparse

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

from shared_utils import format_ell_label, load_json, require_consistent_metadata


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Plot prob-vs-steps data from JSON file(s).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("files", nargs="*", default=["prob-vs-steps-data.json"], help="JSON data files to load and merge.")
    parser.add_argument("--output", "-o", default="prob-vs-steps.pdf", help="Output PDF filename.")
    args = parser.parse_args()

    merged = {}
    metadata = {}
    for filename in args.files:
        payload = load_json(filename)
        if payload is None:
            raise FileNotFoundError(f"Data file {filename} not found.")
        merged.update(payload.get("data", {}))
        metadata = require_consistent_metadata(payload, filename, metadata, ("grid_size", "n_sites"), cast=int)

    grid_size = metadata["grid_size"]
    n_sites = metadata["n_sites"]

    style_cycle = [("k-", "k"), ("b--", "b"), ("r-.", "r"), ("g:", "g")]
    plt.figure()
    for i, key in enumerate(sorted(merged.keys(), key=lambda k: merged[k]["ell"])):
        branch = merged[key]
        probs = np.array(branch["probs"])
        stds = np.array(branch["stds"])
        linestyle, color = style_cycle[i % len(style_cycle)]
        branch_label = branch.get("ell_label", branch.get("label", format_ell_label(branch["ell"], n_sites)))
        label = f"$\\ell={branch_label}$"
        plt.plot(probs, linestyle, label=label)
        plt.fill_between(range(len(probs)), probs - stds, probs + stds, alpha=0.15, color=color)

    plt.axhline(y=1 / n_sites, linestyle=":", label="uniform")
    plt.xlabel("Steps")
    plt.ylabel("Success probability")
    plt.legend(loc="upper left")

    ax_inset = inset_axes(plt.gca(), width="45%", height="45%", loc="upper right")
    for i, key in enumerate(sorted(merged.keys(), key=lambda k: merged[k]["ell"])):
        branch = merged[key]
        probs = np.array(branch["probs"])
        linestyle, _ = style_cycle[i % len(style_cycle)]
        inset_end = max(1, len(probs) // 8)
        ax_inset.plot(probs[:inset_end], linestyle)
    ax_inset.axhline(y=1 / n_sites, linestyle=":", color="gray")
    ax_inset.tick_params(labelsize=8)

    plt.tight_layout()
    plt.savefig(args.output)
    print(f"Plot saved to {args.output}")

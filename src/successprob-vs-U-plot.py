import argparse
import matplotlib.pyplot as plt
import numpy as np

from shared_utils import load_json


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot successprob-vs-U data from JSON file(s).")
    parser.add_argument("files", nargs="*", default=["successprob-vs-U-data.json"])
    parser.add_argument("--output", "-o", default="successprob-vs-U.pdf")
    args = parser.parse_args()

    merged = {}
    for filename in args.files:
        payload = load_json(filename)
        if payload is None:
            raise FileNotFoundError(f"Data file {filename} not found.")
        merged.update(payload.get("data", {}))

    style_cycle = ["k-", "b--", "r-.", "g:"]
    plt.figure()
    for i, key in enumerate(sorted(merged.keys(), key=lambda k: merged[k]["ell"])):
        branch = merged[key]
        probs = np.array(branch["probs"])
        plt.plot(probs, style_cycle[i % len(style_cycle)], label=f"$\\ell={branch['label']}$")

    plt.xlabel("Steps")
    plt.ylabel("Success probability")
    plt.legend(loc="upper right")
    plt.tight_layout()
    plt.savefig(args.output)
    print(f"Plot saved to {args.output}")

import argparse
import matplotlib.pyplot as plt
import numpy as np
from shared_utils import load_json, merge_nested_num_dict


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot convergence-vs-grid data from JSON file(s).")
    parser.add_argument("files", nargs="*", default=["convergence-vs-grid-data.json"])
    parser.add_argument("--output", "-o", default="convergence-vs-grid.pdf")
    args = parser.parse_args()

    data_dict = {}
    for filename in args.files:
        data = load_json(filename)
        if data is None:
            raise FileNotFoundError(f"Data file {filename} not found.")
        data_dict = merge_nested_num_dict(data_dict, data["data"])

    bl_probs = sorted(data_dict.keys())
    grid_sizes = sorted({grid for by_grid in data_dict.values() for grid in by_grid})

    vals_by_bl = {
        bl: [data_dict[bl].get(grid, {}).get("val", np.nan) for grid in grid_sizes]
        for bl in bl_probs
    }
    std_by_bl = {
        bl: [data_dict[bl].get(grid, {}).get("std", np.nan) for grid in grid_sizes]
        for bl in bl_probs
    }

    plt.figure()
    colors = plt.cm.viridis(np.linspace(0, 1, len(bl_probs)))
    for i, bl_prob in enumerate(bl_probs):
        vals = vals_by_bl[bl_prob]
        stds = std_by_bl[bl_prob]
        plt.plot(grid_sizes, vals, "o-", label=f"$p={bl_prob}$", markersize=6, color=colors[i])
        plt.fill_between(
            grid_sizes,
            [v - s for v, s in zip(vals, stds)],
            [v + s for v, s in zip(vals, stds)],
            alpha=0.15,
            color=colors[i],
        )

    plt.plot(grid_sizes, [1 / (gs * gs) for gs in grid_sizes], "k:", label="$1/N$")
    plt.xlabel("Grid size")
    plt.ylabel("Converged success probability")
    plt.title("Converged probability vs grid size ($\\ell=4/N$)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(args.output)
    print(f"Plot saved to {args.output}")

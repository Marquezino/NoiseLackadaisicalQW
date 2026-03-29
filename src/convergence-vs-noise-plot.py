import argparse

import matplotlib.pyplot as plt
import numpy as np

from shared_utils import (
    load_json,
    merge_nested_num_dict,
)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Plot convergence data from JSON file(s)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "files",
        nargs="*",
        default=["convergence-vs-noise-data.json"],
        help="JSON data file(s) to load and merge (default: convergence-vs-noise-data.json)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="convergence-vs-noise.pdf",
        help="Output PDF filename (default: convergence-vs-noise.pdf)",
    )

    args = parser.parse_args()

    # Start with empty data dict
    data_dict = {}

    # Load and merge all files in order
    for filename in args.files:
        print(f"Loading data from {filename}...")
        data = load_json(filename)
        if data is None:
            raise FileNotFoundError(f"Data file {filename} not found. Please run convergence-vs-noise-generate.py first.")

        # Load data format: {bl_prob: {grid_size: {'val': float, 'std': float}}}
        file_data = data["data"]

        # Merge into combined data_dict (later files override earlier ones)
        data_dict = merge_nested_num_dict(data_dict, file_data)

    print(f"Loaded and merged data from {len(args.files)} file(s)")

    # Get all unique grid_sizes and bl_probs from the data
    all_grid_sizes = set()
    for bl_prob_data in data_dict.values():
        all_grid_sizes.update(bl_prob_data.keys())
    grid_sizes = sorted(all_grid_sizes)
    bl_probs = sorted(data_dict.keys())

    # Reorganize data: now we want grid_size as the key, bl_prob as x-axis
    # Create: {grid_size: {bl_prob: {'val': float, 'std': float}}}
    grid_dict = {}
    for grid_size in grid_sizes:
        grid_dict[grid_size] = {}
        for bl_prob in bl_probs:
            if grid_size in data_dict[bl_prob]:
                grid_dict[grid_size][bl_prob] = data_dict[bl_prob][grid_size]

    # Convert to arrays for plotting (fill in missing values as NaN)
    convergence_vals = {}
    convergence_stds = {}
    for grid_size in grid_sizes:
        convergence_vals[grid_size] = [grid_dict[grid_size].get(bp, {}).get("val", np.nan) for bp in bl_probs]
        convergence_stds[grid_size] = [grid_dict[grid_size].get(bp, {}).get("std", np.nan) for bp in bl_probs]

    print(f"Generating {args.output}...")

    plt.figure()
    # Use a color cycle that can handle any number of grid_sizes
    colors = plt.cm.viridis(np.linspace(0, 1, len(grid_sizes)))
    for i, grid_size in enumerate(grid_sizes):
        vals = convergence_vals[grid_size]
        stds = convergence_stds[grid_size]
        plt.plot(bl_probs, vals, "o-", label=f"$N={grid_size}\\times{grid_size}$", markersize=6, color=colors[i])
        plt.fill_between(
            bl_probs,
            [v - s for v, s in zip(vals, stds)],
            [v + s for v, s in zip(vals, stds)],
            alpha=0.15,
            color=colors[i],
        )

    plt.axhline(y=0.25, color="k", linestyle=":", linewidth=1.5)  # , label='$0.25$')
    plt.xlabel("Broken link probability $(p)$")
    plt.ylabel("Converged success probability $(P_{max})$")
    #plt.title('Converged probability vs noise level ($\\ell=4/N$)')
    plt.xscale("log")
    plt.legend(loc="lower left")
    plt.tight_layout()
    plt.savefig(args.output)
    print(f"Plot saved to {args.output}")
import argparse
import noisylack as nl
from shared_utils import (
    as_str_keyed_nested,
    compute_convergence_value,
    compute_tail_std,
    load_json,
    should_compute,
    parse_float_list,
    parse_int_list,
    save_json,
    steps_from_factor,
)


def save_progress(filename, grid_sizes, bl_probs, data_dict, step_factor):
    payload = {
        "grid_sizes": grid_sizes,
        "bl_probs": bl_probs,
        "step_factor": step_factor,
        "data": as_str_keyed_nested(data_dict),
    }
    save_json(filename, payload)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate convergence-vs-grid simulation data and save/update JSON.",
    )
    parser.add_argument("--grid-sizes", type=parse_int_list, default="6,8,10,12,14")
    parser.add_argument("--bl-probs", type=parse_float_list, default="0.01,0.1,0.2,0.5")
    parser.add_argument("--output", "-o", type=str, default="convergence-vs-grid-data.json")
    parser.add_argument("--shots", type=int, default=50)
    parser.add_argument("--step-factor", type=float, default=8.0)
    parser.add_argument("--force", action="store_true", help="Recompute entries even if already present")
    args = parser.parse_args()

    grid_sizes = args.grid_sizes
    bl_probs = args.bl_probs

    existing = load_json(args.output)
    data_dict = {}
    if existing and "data" in existing:
        data_dict = {
            float(k1): {int(k2): v for k2, v in v1.items()}
            for k1, v1 in existing["data"].items()
        }

    for bl_prob in bl_probs:
        if bl_prob not in data_dict:
            data_dict[bl_prob] = {}

        for grid_size in grid_sizes:
            if not should_compute(args.force, grid_size, data_dict[bl_prob]):
                cached = data_dict[bl_prob][grid_size]
                print(
                    f"Skipping bl_prob={bl_prob}, grid_size={grid_size}; "
                    f"cached val={cached['val']:.5g}, std={cached['std']:.3e}"
                )
                continue

            n_sites = grid_size * grid_size
            steps = steps_from_factor(grid_size, args.step_factor)
            print(
                f"Running bl_prob={bl_prob}, grid_size={grid_size}, "
                f"N={n_sites}, steps={steps}, shots={args.shots}"
            )
            w_probs, _, _ = nl.experiment(
                L=grid_size,
                ell=4 / n_sites,
                bl_prob=bl_prob,
                num_steps=steps,
                shots=args.shots,
                save_all_steps=False,
            )
            conv_val = compute_convergence_value(w_probs)
            tail_std = compute_tail_std(w_probs)

            data_dict[bl_prob][grid_size] = {
                "val": float(conv_val),
                "std": float(tail_std),
                "steps": int(steps),
                "shots": int(args.shots),
            }

            save_progress(args.output, grid_sizes, bl_probs, data_dict, args.step_factor)

    save_progress(args.output, grid_sizes, bl_probs, data_dict, args.step_factor)
    print(f"Saved data to {args.output}")

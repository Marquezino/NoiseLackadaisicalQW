import argparse
import numpy as np
import noisylack as nl
from shared_utils import (
    as_str_keyed_nested,
    load_json,
    parse_float_list,
    save_json,
    shots_for_prob,
    steps_from_factor,
)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate maxprob-vs-loop data and save/update JSON.")
    parser.add_argument("--grid-size", type=int, default=32)
    parser.add_argument("--ell-min", type=float, default=0.0)
    parser.add_argument("--ell-max", type=float, default=0.02)
    parser.add_argument("--ell-points", type=int, default=21)
    parser.add_argument("--bl-probs", type=parse_float_list, default="0.0,0.001,0.002,0.004")
    parser.add_argument("--step-factor", type=float, default=1.0)
    parser.add_argument("--shots-noiseless", type=int, default=1)
    parser.add_argument("--shots-noisy", type=int, default=80)
    parser.add_argument("--output", "-o", type=str, default="maxprob-vs-loop-data.json")
    parser.add_argument("--force", action="store_true", help="Recompute entries even if already present")
    args = parser.parse_args()

    ell_values = np.linspace(args.ell_min, args.ell_max, args.ell_points)
    bl_probs = args.bl_probs
    steps = steps_from_factor(args.grid_size, args.step_factor)

    payload = load_json(args.output)
    data = {}
    if payload and "data" in payload:
        data = {
            float(k): {float(e): v for e, v in by_ell.items()}
            for k, by_ell in payload["data"].items()
        }

    for bl_prob in bl_probs:
        if bl_prob not in data:
            data[bl_prob] = {}

        for ell in ell_values:
            ell_key = float(ell)
            if not args.force and ell_key in data[bl_prob]:
                cached = data[bl_prob][ell_key]
                print(
                    f"Skipping p={bl_prob}, ell={ell_key:.6g}; "
                    f"cached max_prob={cached['max_prob']:.5g}"
                )
                continue

            shots = shots_for_prob(bl_prob, args.shots_noiseless, args.shots_noisy)
            print(
                f"Running p={bl_prob}, ell={ell_key:.6g}, grid={args.grid_size}, "
                f"steps={steps}, shots={shots}"
            )
            w_probs, w_stds, _ = nl.experiment(
                L=args.grid_size,
                ell=ell_key,
                bl_prob=bl_prob,
                num_steps=steps,
                shots=shots,
                save_all_steps=False,
            )
            idx = int(np.argmax(w_probs))
            data[bl_prob][ell_key] = {
                "max_prob": float(w_probs[idx]),
                "std_at_max": float(w_stds[idx]),
                "step_at_max": idx,
                "steps": int(steps),
                "shots": int(shots),
            }

            data_to_save = {
                "grid_size": int(args.grid_size),
                "step_factor": float(args.step_factor),
                "ell_values": [float(v) for v in ell_values],
                "bl_probs": [float(v) for v in bl_probs],
                "data": as_str_keyed_nested(data),
            }
            save_json(args.output, data_to_save)

    # Final save handles the edge case where all points were already cached and
    # the inner save never ran, ensuring the output file is always written.
    data_to_save = {
        "grid_size": int(args.grid_size),
        "step_factor": float(args.step_factor),
        "ell_values": [float(v) for v in ell_values],
        "bl_probs": [float(v) for v in bl_probs],
        "data": as_str_keyed_nested(data),
    }
    save_json(args.output, data_to_save)
    print(f"Saved data to {args.output}")

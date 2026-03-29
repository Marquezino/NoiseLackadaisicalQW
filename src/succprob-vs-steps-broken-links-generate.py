import argparse
import noisylack as nl
from shared_utils import (
    format_bl_label,
    load_json,
    parse_float_list,
    save_json,
    shots_for_prob,
    steps_from_factor,
)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate succprob-vs-steps-broken-links data and save/update JSON.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--grid-size", type=int, default=16, help="Grid side length L.")
    parser.add_argument("--ell", type=float, default=0.0, help="Self-loop weight ell.")
    parser.add_argument("--bl-probs", type=parse_float_list, default="0.0,0.001,0.01", help="Comma-separated broken-link probabilities.")
    parser.add_argument(
        "--step-factor",
        type=float,
        default=1.0,
        help="Step multiplication factor in steps = L * log2(N) * factor.",
    )
    parser.add_argument("--shots-noiseless", type=int, default=1, help="Shots for bl_prob=0.")
    parser.add_argument("--shots-noisy", type=int, default=50, help="Shots for bl_prob>0.")
    parser.add_argument("--output", "-o", type=str, default="succprob-vs-steps-broken-links-data.json", help="Output JSON filename.")
    parser.add_argument("--force", action="store_true", help="Recompute entries even if already present")
    args = parser.parse_args()

    n_sites = args.grid_size * args.grid_size
    steps = steps_from_factor(args.grid_size, args.step_factor)

    payload = load_json(args.output) or {}
    data = payload.get("data", {})

    for bl_prob in args.bl_probs:
        key = f"{bl_prob:.12g}"
        if not args.force and key in data:
            cached = data[key]
            print(f"Skipping p={bl_prob}; cached {len(cached['probs'])} points")
            continue

        shots = shots_for_prob(bl_prob, args.shots_noiseless, args.shots_noisy)
        print(
            f"Running p={bl_prob}, grid={args.grid_size}, ell={args.ell}, "
            f"steps={steps}, shots={shots}"
        )
        w_probs, w_stds, _ = nl.experiment(
            L=args.grid_size,
            ell=args.ell,
            bl_prob=bl_prob,
            num_steps=steps,
            shots=shots,
            save_all_steps=False,
        )

        data[key] = {
            "bl_prob": float(bl_prob),
            "probs": [float(x) for x in w_probs],
            "stds": [float(x) for x in w_stds],
            "steps": int(steps),
            "shots": int(shots),
        }

        data_to_save = {
            "grid_size": args.grid_size,
            "n_sites": n_sites,
            "ell": float(args.ell),
            "bl_probs": [float(v) for v in args.bl_probs],
            "bl_labels": [format_bl_label(p) for p in args.bl_probs],
            "step_factor": args.step_factor,
            "data": data,
        }
        save_json(args.output, data_to_save)

    data_to_save = {
        "grid_size": args.grid_size,
        "n_sites": n_sites,
        "ell": float(args.ell),
        "bl_probs": [float(v) for v in args.bl_probs],
        "bl_labels": [format_bl_label(p) for p in args.bl_probs],
        "step_factor": args.step_factor,
        "data": data,
    }
    save_json(args.output, data_to_save)
    print(f"Saved data to {args.output}")

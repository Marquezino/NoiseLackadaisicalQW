import argparse
import noisylack as nl
from shared_utils import (
    format_bl_label,
    format_ell_label,
    load_json,
    parse_ell_values,
    save_json,
    steps_from_factor,
)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate successprob-vs-U simulation data and save/update JSON.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--grid-size", type=int, default=64, help="Grid side length L.")
    parser.add_argument("--bl-prob", type=float, default=0.0, help="Broken-link probability p.")
    parser.add_argument("--ells", type=str, default="0,1/N,4/N", help="Comma-separated ell values.")
    parser.add_argument(
        "--step-factor",
        type=float,
        default=1.0,
        help="Step multiplication factor in steps = L * log2(N) * factor.",
    )
    parser.add_argument("--shots", type=int, default=1, help="Shots per experiment.")
    parser.add_argument("--output", "-o", type=str, default="successprob-vs-U-data.json", help="Output JSON filename.")
    parser.add_argument("--force", action="store_true", help="Recompute entries even if already present")
    args = parser.parse_args()

    n_sites = args.grid_size * args.grid_size
    ell_values = parse_ell_values(args.ells, n_sites)
    steps = steps_from_factor(args.grid_size, args.step_factor)

    payload = load_json(args.output) or {}
    data = payload.get("data", {})

    for ell in ell_values:
        key = f"{ell:.12g}"
        if not args.force and key in data:
            cached = data[key]
            print(f"Skipping ell={format_ell_label(ell, n_sites)}; cached {len(cached['probs'])} points")
            continue

        print(
            f"Running ell={format_ell_label(ell, n_sites)} ({ell:.12g}), "
            f"grid={args.grid_size}, bl_prob={args.bl_prob}, steps={steps}, shots={args.shots}"
        )
        w_probs, w_stds, _ = nl.experiment(
            L=args.grid_size,
            ell=ell,
            bl_prob=args.bl_prob,
            num_steps=steps,
            shots=args.shots,
            save_all_steps=False,
        )

        data[key] = {
            "ell_label": format_ell_label(ell, n_sites),
            "ell": float(ell),
            "probs": [float(x) for x in w_probs],
            "stds": [float(x) for x in w_stds],
            "steps": int(steps),
            "shots": int(args.shots),
        }

        data_to_save = {
            "grid_size": args.grid_size,
            "n_sites": n_sites,
            "bl_prob": args.bl_prob,
            "bl_label": format_bl_label(args.bl_prob),
            "step_factor": args.step_factor,
            "ell_values": [float(v) for v in ell_values],
            "ell_labels": [format_ell_label(v, n_sites) for v in ell_values],
            "data": data,
        }
        save_json(args.output, data_to_save)

    data_to_save = {
        "grid_size": args.grid_size,
        "n_sites": n_sites,
        "bl_prob": args.bl_prob,
        "bl_label": format_bl_label(args.bl_prob),
        "step_factor": args.step_factor,
        "ell_values": [float(v) for v in ell_values],
        "ell_labels": [format_ell_label(v, n_sites) for v in ell_values],
        "data": data,
    }
    save_json(args.output, data_to_save)
    print(f"Saved data to {args.output}")

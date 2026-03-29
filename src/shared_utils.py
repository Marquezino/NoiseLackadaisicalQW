import json
import os
from typing import Any

import numpy as np


def compute_convergence_value(w_probs, tail_frac=0.1):
    """Compute the converged value as the mean of the tail of w_probs."""
    num_tail = max(1, int(len(w_probs) * tail_frac))
    return float(np.mean(w_probs[-num_tail:]))


def compute_tail_std(w_probs, tail_frac=0.1):
    """Compute the standard deviation on the tail of w_probs."""
    num_tail = max(1, int(len(w_probs) * tail_frac))
    return float(np.std(w_probs[-num_tail:]))


def load_json(filename):
    """Load JSON from disk or return None when file does not exist."""
    if not os.path.exists(filename):
        return None
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(filename, payload):
    """Persist JSON payload to disk with stable indentation."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def parse_float_list(raw):
    """Parse comma-separated float list."""
    if isinstance(raw, list):
        return [float(x) for x in raw]
    return [float(x.strip()) for x in str(raw).split(",") if x.strip()]


def parse_int_list(raw):
    """Parse comma-separated integer list."""
    if isinstance(raw, list):
        return [int(x) for x in raw]
    return [int(x.strip()) for x in str(raw).split(",") if x.strip()]


def as_str_keyed_nested(data_dict):
    """Convert nested numeric dict keys to strings for JSON compatibility."""
    return {str(k1): {str(k2): v for k2, v in v1.items()} for k1, v1 in data_dict.items()}


def merge_nested_num_dict(existing, incoming):
    """Merge dict[float][int] structures from JSON string-keyed content."""
    incoming_conv = {float(k1): {int(k2): v for k2, v in v1.items()} for k1, v1 in incoming.items()}
    for outer_key, inner_map in incoming_conv.items():
        if outer_key not in existing:
            existing[outer_key] = {}
        existing[outer_key].update(inner_map)
    return existing


def merge_nested_float_dict(existing, incoming):
    """Merge dict[float][float] structures from JSON string-keyed content."""
    incoming_conv = {float(k1): {float(k2): v for k2, v in v1.items()} for k1, v1 in incoming.items()}
    for outer_key, inner_map in incoming_conv.items():
        if outer_key not in existing:
            existing[outer_key] = {}
        existing[outer_key].update(inner_map)
    return existing


def steps_from_factor(grid_size, step_factor, round_to=100):
    """Compute step count using L * log2(N) * factor and round to nearest round_to."""
    n_sites = grid_size * grid_size
    steps = int(grid_size * np.log2(n_sites) * step_factor)
    if round_to and round_to > 1 and steps >= round_to:
        steps = round(steps, -int(np.log10(round_to)))
    return max(1, int(steps))


def shots_for_prob(bl_prob, shots_noiseless, shots_noisy):
    """Return shot count for an experiment: noiseless (bl_prob=0) uses shots_noiseless, others shots_noisy."""
    if abs(bl_prob) < 1e-15:
        return shots_noiseless
    return shots_noisy


def should_compute(force, key, inner_map):
    """Return True when computation should run for key under force/skip policy."""
    return force or key not in inner_map


def parse_ell_values(raw, n_sites):
    """Parse comma-separated ell values, supporting fractional notation like 4/N or 1/N."""
    values = []
    for token in str(raw).split(","):
        token = token.strip().lower()
        if not token:
            continue
        if token.endswith("/n"):
            values.append(float(token[:-2]) / n_sites)
        else:
            values.append(float(token))
    return values


def ell_label(ell, n_sites):
    """Return a human-readable label for an ell value relative to N=n_sites."""
    if abs(ell - 4 / n_sites) < 1e-12:
        return "4/N"
    if abs(ell - 1 / n_sites) < 1e-12:
        return "1/N"
    if abs(ell) < 1e-12:
        return "0"
    return f"{ell:.12g}"


def format_bl_label(bl_prob):
    """Format broken-link probability labels with readable decimal/scientific notation."""
    if abs(bl_prob) < 1e-15:
        return "$p=0$"

    mantissa_str, exp_str = f"{bl_prob:.3e}".split("e")
    mantissa = float(mantissa_str)
    exponent = int(exp_str)

    if -2 <= exponent <= 2:
        return f"$p={bl_prob:.3g}$"

    if abs(mantissa - 1.0) < 1e-12:
        return f"$p=10^{{{exponent}}}$"

    if abs(mantissa - round(mantissa)) < 1e-12:
        mantissa_text = str(int(round(mantissa)))
    else:
        mantissa_text = f"{mantissa:.3g}"
    return f"$p={mantissa_text} \\times 10^{{{exponent}}}$"


def json_copy(payload: Any):
    """Deep-copy JSON-compatible content via serialization."""
    return json.loads(json.dumps(payload))

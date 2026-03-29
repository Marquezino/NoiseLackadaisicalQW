# NoiseLackadaisicalQW
Python code used in the research paper "Noise-Resilient Spatial Search with Lackadaisical Quantum Walks", https://arxiv.org/abs/2508.13462.

## Jupyter Notebook

`Noisy-Lackadaisical-QW.ipynb` provides the foundational implementation used to build intuition and produce exploratory plots. Its primary purpose is educational — it is not optimized for performance. The production code used for the final experiments lives in `src/`.

## Workflow

All analysis scripts now follow a two-step CLI workflow:

1. Run `*-generate.py` to compute simulations and incrementally save/update a JSON file.
2. Run `*-plot.py` to read JSON data and generate a PDF plot.

Generate scripts skip entries already present in the JSON file by default so interrupted runs can resume. Use `--force` to recompute existing entries.

## Script Pairs

- `src/convergence-vs-noise-generate.py` and `src/convergence-vs-noise-plot.py`
- `src/convergence-vs-grid-generate.py` and `src/convergence-vs-grid-plot.py`
- `src/prob-vs-steps-generate.py` and `src/prob-vs-steps-plot.py`
- `src/successprob-vs-U-generate.py` and `src/successprob-vs-U-plot.py`
- `src/succprob-vs-steps-broken-links-generate.py` and `src/succprob-vs-steps-broken-links-plot.py`
- `src/maxprob-vs-loop-generate.py` and `src/maxprob-vs-loop-plot.py`

## Examples

```bash
python src/convergence-vs-grid-generate.py --shots 20
python src/convergence-vs-grid-plot.py

python src/prob-vs-steps-generate.py --grid-size 16 --bl-prob 0.01
python src/prob-vs-steps-plot.py

python src/maxprob-vs-loop-generate.py --ell-points 9
python src/maxprob-vs-loop-plot.py
```

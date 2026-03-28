import noisylack as nl
import numpy as np
import matplotlib.pyplot as plt
from concurrent.futures import ProcessPoolExecutor
import os

if __name__ == '__main__':
    grid_size = 64
    N = grid_size * grid_size
    steps = round(int(grid_size * np.log2(N)), -2) # round to nearest multiple of 100

    print("Generating successprob-vs-U.pdf...")
    print(f"Steps: {steps}")
    print(f"Grid size: {grid_size} x {grid_size}")
    print(f"Number of sites: {N}")

    # Run the three experiments in parallel
    # Each experiment uses max_workers=1 since shots=1
    # Outer pool uses min(3, cpu_count()) to avoid oversubscription
    max_outer_workers = min(3, os.cpu_count() or 1)

    with ProcessPoolExecutor(max_workers=max_outer_workers) as executor:
        future_A = executor.submit(nl.experiment, L=grid_size, ell=0.00, bl_prob=0.0, 
                                    num_steps=steps, shots=1, save_all_steps=False)
        future_B = executor.submit(nl.experiment, L=grid_size, ell=1/N, bl_prob=0.0, 
                                    num_steps=steps, shots=1, save_all_steps=False)
        future_C = executor.submit(nl.experiment, L=grid_size, ell=4/N, bl_prob=0.0, 
                                    num_steps=steps, shots=1, save_all_steps=False)
        
        w_probs_A, w_stds_A, _ = future_A.result()
        w_probs_B, w_stds_B, _ = future_B.result()
        w_probs_C, w_stds_C, _ = future_C.result()

    # With shots=1, standard deviations should be zero (within floating point precision)
    np.testing.assert_allclose(w_stds_A, np.zeros_like(w_stds_A), atol=1e-7)
    np.testing.assert_allclose(w_stds_B, np.zeros_like(w_stds_B), atol=1e-7)
    np.testing.assert_allclose(w_stds_C, np.zeros_like(w_stds_C), atol=1e-7)

    plt.plot(w_probs_A, 'k-', label=f'$\\ell=0.00$')
    plt.plot(w_probs_B, 'b--', label=f'$\\ell=1/N$')
    plt.plot(w_probs_C, 'r-.', label=f'$\\ell=4/N$')
    plt.xlabel('Steps')
    plt.ylabel('Success probability')
    plt.legend(loc='upper right')
    plt.savefig('successprob-vs-U.pdf')


import noisylack as nl
import numpy as np
import matplotlib.pyplot as plt

if __name__ == '__main__':
    grid_size = 16
    N = grid_size * grid_size
    steps = round(int(grid_size * np.log2(N)), -2) # round to nearest multiple of 100

    print("Generating succprob-vs-steps-broken-links.pdf...")
    print(f"Grid size: {grid_size} x {grid_size}")
    print(f"Number of sites: {N}")
    print(f"Steps: {steps}")

    w_probs_A, w_stds_A, _ = nl.experiment(L = grid_size, ell=0.00, bl_prob = 0.0, num_steps = steps, shots = 1, save_all_steps=False)
    w_probs_B, w_stds_B, _ = nl.experiment(L = grid_size, ell=0.00, bl_prob = 0.001, num_steps = steps, shots = 50, save_all_steps=False)
    w_probs_C, w_stds_C, _ = nl.experiment(L = grid_size, ell=0.00, bl_prob = 0.01, num_steps = steps, shots = 50, save_all_steps=False)

    plt.plot(w_probs_A, 'k-', label='$p=0$')

    plt.plot(w_probs_B, 'b--', label='$p=10^{-3}$')
    plt.fill_between(range(len(w_probs_B)), w_probs_B - w_stds_B, w_probs_B + w_stds_B, alpha=0.15, color='b')

    plt.plot(w_probs_C, 'r-.', label='$p=10^{-2}$')
    plt.fill_between(range(len(w_probs_C)), w_probs_C - w_stds_C, w_probs_C + w_stds_C, alpha=0.15, color='r')

    plt.axhline(y=1/N, linestyle=':', label='uniform')
    plt.xlabel('Steps')
    plt.ylabel('Success probability')
    plt.legend(loc='upper right')
    plt.savefig('succprob-vs-steps-broken-links.pdf')
    #plt.show()
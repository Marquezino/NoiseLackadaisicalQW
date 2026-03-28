import noisylack as nl
import numpy as np
import matplotlib.pyplot as plt

if __name__ == '__main__':
    grid_size = 16
    N = grid_size * grid_size
    steps = round(int(grid_size * np.log2(N)*8), -2) # round to nearest multiple of 100

    print("Generating prob-vs-steps.pdf...")
    print(f"Grid size: {grid_size} x {grid_size}")
    print(f"Number of sites: {N}")
    print(f"Steps: {steps}")

    w_probs_A, w_stds_A, _ = nl.experiment(L = grid_size, ell=4/N, bl_prob = 0.01, num_steps = steps, shots = 50, save_all_steps=False)
    w_probs_B, w_stds_B, _ = nl.experiment(L = grid_size, ell=1/N, bl_prob = 0.01, num_steps = steps, shots = 50, save_all_steps=False)
    w_probs_C, w_stds_C, _ = nl.experiment(L = grid_size, ell=0.000, bl_prob = 0.01, num_steps = steps, shots = 50, save_all_steps=False)

    from mpl_toolkits.axes_grid1.inset_locator import inset_axes

    # Main plot
    plt.plot(w_probs_A, 'k-', label='$\\ell=4/N$')
    plt.fill_between(range(len(w_probs_A)), w_probs_A - w_stds_A, w_probs_A + w_stds_A, alpha=0.15, color='k')

    plt.plot(w_probs_B, 'b--', label='$\\ell=1/N$')
    plt.fill_between(range(len(w_probs_B)), w_probs_B - w_stds_B, w_probs_B + w_stds_B, alpha=0.15, color='b')

    plt.plot(w_probs_C, 'r-.', label='$\\ell=0$')
    plt.fill_between(range(len(w_probs_C)), w_probs_C - w_stds_C, w_probs_C + w_stds_C, alpha=0.15, color='r')

    plt.axhline(y=1/N, linestyle=':', label='uniform')
    plt.xlabel('Steps')
    plt.ylabel('Success probability')
    plt.legend(loc='upper left')

    # Inset axes
    ax_inset = inset_axes(plt.gca(), width="45%", height="45%", loc='upper right')
    ax_inset.plot(w_probs_A[:steps//8], 'k-', label='$\\ell=4/N$')
    ax_inset.plot(w_probs_B[:steps//8], 'b--', label='$\\ell=1/N$')
    ax_inset.plot(w_probs_C[:steps//8], 'r-.', label='$\\ell=0$')
    ax_inset.axhline(y=1/N, linestyle=':', color='gray')
    #ax_inset.set_title('First 100 steps', fontsize=9)
    ax_inset.tick_params(labelsize=8)

    plt.tight_layout()
    plt.savefig('prob-vs-steps.pdf')


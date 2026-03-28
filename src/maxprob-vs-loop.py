import noisylack as nl
import numpy as np
import matplotlib.pyplot as plt

if __name__ == '__main__':
    grid_size = 32
    N = grid_size * grid_size
    steps = int(grid_size * np.log2(N))

    print("Generating maxprob-vs-loop.pdf...")
    print(f"Grid size: {grid_size} x {grid_size}")
    print(f"Number of sites: {N}")
    print(f"Steps: {steps}")

    results_partialA = {}
    results_partialB = {}
    results_partialC = {}
    results_partialD = {}
    for ell in np.linspace(0.0, 0.02, 21):
        print(f'ell = {ell:e}')
        w_probsA, w_stdsA, _ = nl.experiment(L = grid_size, ell=ell, bl_prob = 0.0, num_steps = steps, shots = 1)
        w_probsB, w_stdsB, _ = nl.experiment(L = grid_size, ell=ell, bl_prob = 0.001, num_steps = steps, shots = 80)
        w_probsC, w_stdsC, _ = nl.experiment(L = grid_size, ell=ell, bl_prob = 0.002, num_steps = steps, shots = 80)
        w_probsD, w_stdsD, _ = nl.experiment(L = grid_size, ell=ell, bl_prob = 0.004, num_steps = steps, shots = 80)
        
        results_partialA[ell] = np.max(w_probsA)
        results_partialB[ell] = np.max(w_probsB)
        results_partialC[ell] = np.max(w_probsC)
        results_partialD[ell] = np.max(w_probsD)
    max_keyA = max(results_partialA, key=results_partialA.get)
    max_keyB = max(results_partialB, key=results_partialB.get)
    max_keyC = max(results_partialC, key=results_partialC.get)
    max_keyD = max(results_partialD, key=results_partialD.get)

    plt.plot(*zip(*sorted(results_partialA.items())), '-', label='$p=0.0$')
    plt.plot(*zip(*sorted(results_partialB.items())), '-', label='$p=10^{-3}$')
    plt.plot(*zip(*sorted(results_partialC.items())), '-', label='$p=2 \\times 10^{-3}$')
    plt.plot(*zip(*sorted(results_partialD.items())), '-', label='$p=4 \\times 10^{-3}$')
    plt.xlabel('Self-loop weight ($\\ell$)')
    plt.ylabel('Maximum success probability ($P_{max}$)')
    plt.axvline(x=4/(32**2), linestyle=':', label='$4/N$')
    #plt.axvline(x=max_keyA, linestyle='--', label='optimal $\\ell$ (noisy case)')
    plt.legend(loc='upper right')
    plt.savefig('maxprob-vs-loop.pdf')
    

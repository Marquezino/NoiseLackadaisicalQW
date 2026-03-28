import noisylack as nl
import numpy as np
import matplotlib.pyplot as plt

def compute_convergence_value(w_probs, tail_frac=0.1):
    """
    Compute the 'converged' value as the mean of the last tail_frac fraction of the probability array.
    """
    num_tail = max(1, int(len(w_probs) * tail_frac))
    return np.mean(w_probs[-num_tail:])

if __name__ == '__main__':
    print("Generating convergence-vs-grid.pdf...")

    grid_sizes = range(6, 15, 2)  # You can increase max if you have the RAM/CPU for it
    
    # Run experiments for different bl_prob values
    bl_probs = [0.01, 0.1, 0.2, 0.5]
    all_convergence_vals = {bl_prob: [] for bl_prob in bl_probs}
    all_convergence_stds = {bl_prob: [] for bl_prob in bl_probs}
    
    for bl_prob in bl_probs:
        print(f"\n=== Running experiments with bl_prob={bl_prob} ===")
        convergence_vals = []
        convergence_stds = []  # Standard deviation of tail
        
        for grid_size in grid_sizes:
            N = grid_size * grid_size
            steps = int(grid_size * np.log2(N) * 8)  # Large enough to see convergence
            steps = round(steps, -2) 
            print(f"Running experiment for grid_size={grid_size}, N={N}, steps={steps}")
            w_probs, w_stds, _ = nl.experiment(L=grid_size, ell=4/N, bl_prob=bl_prob, num_steps=steps, shots=50, save_all_steps=False)
            
            conv_val = compute_convergence_value(w_probs)
            
            # Compute standard deviation of the tail
            tail_frac = 0.1
            num_tail = max(1, int(len(w_probs) * tail_frac))
            tail = w_probs[-num_tail:]
            tail_std = np.std(tail)
            
            convergence_vals.append(conv_val)
            convergence_stds.append(tail_std)
            
            print(f"Grid size {grid_size}: convergence prob ~ {conv_val:.5g}, tail std: {tail_std:.3e}")
        
        all_convergence_vals[bl_prob] = convergence_vals
        all_convergence_stds[bl_prob] = convergence_stds

    plt.figure()
    colors = ['blue', 'red', 'green', 'orange']
    for i, bl_prob in enumerate(bl_probs):
        convergence_vals = all_convergence_vals[bl_prob]
        convergence_stds = all_convergence_stds[bl_prob]
        plt.plot(grid_sizes, convergence_vals, 'o-', 
                label=f'$p={bl_prob}$', markersize=6, color=colors[i])
        plt.fill_between(grid_sizes, 
                         [v - s for v, s in zip(convergence_vals, convergence_stds)],
                         [v + s for v, s in zip(convergence_vals, convergence_stds)],
                         alpha=0.15, color=colors[i])
    
    plt.plot(grid_sizes, [1/(gs*gs) for gs in grid_sizes], 'k:', label='$1/N$')
    plt.xlabel('Grid size')
    plt.ylabel('Converged success probability')
    plt.title('Converged probability vs grid size ($\\ell=4/N$)')
    plt.legend()
    plt.tight_layout()
    plt.savefig('convergence-vs-grid.pdf')
    print("\nPlot saved to convergence-vs-grid.pdf")
    

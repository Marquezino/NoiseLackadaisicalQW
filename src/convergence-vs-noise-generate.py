import noisylack as nl
import argparse
from shared_utils import (
    as_str_keyed_nested,
    compute_convergence_value,
    compute_tail_std,
    load_json,
    parse_float_list,
    parse_int_list,
    save_json,
    steps_from_factor,
)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate convergence data for quantum walk spatial search with broken links',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python convergence-vs-noise-generate.py --grid-sizes 6,8,10,12,14 --bl-probs 0.01,0.1,0.2,0.5
  python convergence-vs-noise-generate.py --grid-sizes 16,20,24 --bl-probs 0.3,0.4
  python convergence-vs-noise-generate.py --output my_data.json --shots 100
        """)
    
    parser.add_argument('--grid-sizes', type=parse_int_list, 
                       default='6,8,10,12,14',
                       help='Comma-separated list of grid sizes (default: 6,8,10,12,14)')
    
    parser.add_argument('--bl-probs', type=parse_float_list,
                       default='0.01,0.1,0.2,0.5',
                       help='Comma-separated list of broken link probabilities (default: 0.01,0.1,0.2,0.5)')
    
    parser.add_argument('--output', '-o', type=str,
                       default='convergence-vs-noise-data.json',
                       help='Output JSON filename (default: convergence-vs-noise-data.json)')
    
    parser.add_argument('--shots', type=int, default=40,
                       help='Number of shots per experiment (default: 40)')
    
    parser.add_argument('--step-factor', type=float, default=6.0,
                       help='Multiplication factor for number of steps: steps = grid_size * log2(N) * factor (default: 6.0)')
    
    args = parser.parse_args()
    
    data_filename = args.output
    grid_sizes = args.grid_sizes
    bl_probs = args.bl_probs
    
    print(f"Grid sizes: {grid_sizes}")
    print(f"Broken link probabilities: {bl_probs}")
    print(f"Output file: {data_filename}")
    print(f"Shots per experiment: {args.shots}")
    print(f"Step factor: {args.step_factor}")
    
    # Load existing data if it exists
    existing_data = load_json(data_filename)
    
    # Initialize data structures - use dict of dicts: {bl_prob: {grid_size: (val, std)}}
    # This allows flexible addition of new grid_sizes and bl_probs
    data_dict = {}  # {bl_prob: {grid_size: {'val': float, 'std': float}}}
    
    if existing_data is not None:
        print(f"\nLoading existing data from {data_filename}...")
        data_dict = existing_data['data']
        # Convert string keys back to floats/ints (JSON stores keys as strings)
        data_dict = {float(k1): {int(k2): v for k2, v in v1.items()} 
                    for k1, v1 in data_dict.items()}
    else:
        print(f"\nNo existing data found. Starting fresh...")
    
    # Run experiments - iterate over grid_sizes first to get complete data for smaller grids sooner
    for grid_size in grid_sizes:
        print(f"\n=== Processing grid_size={grid_size} ===")
        
        for bl_prob in bl_probs:
            # Initialize dict for this bl_prob if not present
            if bl_prob not in data_dict:
                data_dict[bl_prob] = {}
            
            # Check if we already have data for this (bl_prob, grid_size) combination
            if grid_size in data_dict[bl_prob]:
                existing_val = data_dict[bl_prob][grid_size]['val']
                existing_std = data_dict[bl_prob][grid_size]['std']
                print(f"  bl_prob={bl_prob}: using existing data (convergence prob ~ {existing_val:.5g}, tail std: {existing_std:.3e})")
                continue
            
            # Need to run experiment for this combination
            N = grid_size * grid_size
            steps = steps_from_factor(grid_size, args.step_factor)
            print(f"  Running experiment for bl_prob={bl_prob}, N={N}, steps={steps}")
            w_probs, w_stds, _ = nl.experiment(L=grid_size, ell=4/N, bl_prob=bl_prob, 
                                              num_steps=steps, shots=args.shots, save_all_steps=False)
            
            conv_val = compute_convergence_value(w_probs)
            tail_std = compute_tail_std(w_probs)
            
            # Store the result
            data_dict[bl_prob][grid_size] = {'val': float(conv_val), 'std': float(tail_std)}
            
            print(f"  bl_prob={bl_prob}: convergence prob ~ {conv_val:.5g}, tail std: {tail_std:.3e}")
            
            # Save after each experiment to avoid losing progress
            # Convert to format suitable for JSON (strings for keys)
            data_to_save = {
                'grid_sizes': grid_sizes,
                'bl_probs': bl_probs,
                'data': as_str_keyed_nested(data_dict)
            }
            save_json(data_filename, data_to_save)
    
    # Final save
    data_to_save = {
        'grid_sizes': grid_sizes,
        'bl_probs': bl_probs,
        'data': as_str_keyed_nested(data_dict)
    }
    save_json(data_filename, data_to_save)
    print(f"\nData saved to {data_filename}")
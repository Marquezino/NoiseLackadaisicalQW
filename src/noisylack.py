import numpy as np
from numpy import sqrt
import matplotlib.pyplot as plt
from concurrent.futures import ProcessPoolExecutor

# Define the indices of the coin.
up = 0
down = 1
left = 2
right = 3
stay = 4

def generate_adjacency(L, bl_prob):
    """Generates an adjacenty matrix with broken links.

    Generates an adjacency matrix for the two-dimensional LxL grid with broken links (or edges).
    The probability of breaking each edge is given by parameter bl_prob. The
    quantum walker can use the output matrix to decide if it can move to a
    certain site or not. If entry (i,j,k,l) is set to True then the shift operator
    is allowed to move the walker from site (i,j) to (k,l) -- even though it doesn't
    have to. If entry (i,j,k,l) is set to False then the shift operator must make sure that
    the walker will not move from site (i,j) to (k,l).

    Args:
        L (int): the grid size
        bl_prob (float): the probability of breaking each edge

    Returns:
        numpy.ndarray: a four-dimensional boolean matrix
    """

    adjacency = np.random.rand(L*L, L*L)
    adjacency[adjacency >= bl_prob] = 1
    adjacency[adjacency < bl_prob] = 0
    adjacency = np.tril(adjacency) + np.triu(adjacency.T, 1)
    adjacency = np.reshape(adjacency,(L,L,L,L))
    return adjacency.astype(bool)


def grover_coin(psi, L, ell = 0.0):
    """Aplies the Grover coin operator with self-loop.

    Applies the Grover coin operator with self-loop to a state vector corresponding
    to a quantum walk on the LxL grid.

    Args:
        psi (numpy.ndarray): a three-dimensional array (two dimensions for space and the last one for coin)
        L (int): the grid size
        ell (float): the weight of the self-loop

    Returns:
        a three-dimensional array (two dimensions for space and the last one for coin)
    """

    # Vectorized weighted Grover coin.
    # Calculate the "funny average" (according to source code made available by Tom Wong)
    bar = (psi[:, :, up] + psi[:, :, down] + psi[:, :, left] + psi[:, :, right] + sqrt(ell)*psi[:, :, stay]) / (4 + ell)

    # Do the inversions (broadcast bar to all coin states)
    tmp = np.empty_like(psi)
    tmp[:, :, up] = 2*bar - psi[:, :, up]
    tmp[:, :, down] = 2*bar - psi[:, :, down]
    tmp[:, :, left] = 2*bar - psi[:, :, left]
    tmp[:, :, right] = 2*bar - psi[:, :, right]
    tmp[:, :, stay] = 2*bar*sqrt(ell) - psi[:, :, stay]

    return tmp


def ff_shift(before, after, L, bl_prob = 0.0):
    """Performs the flip-flop shift operation on a state vector of a
    quantum walk on an LxL grid.

    The shift operation updates the state vector according to the adjacency matrix
    generated with the given grid size and broken link probability.

    Args:
        before (numpy.ndarray): The input state vector before the shift operation.
        after (numpy.ndarray): The output state vector after the shift operation.
        L (int): The grid size.
        bl_prob (float): The probability of breaking each edge. Defaults to 0.0.

    Returns:
        None
    """

    adjacency = generate_adjacency(L, bl_prob)

    for x in range(L):
        for y in range(L):

            if adjacency[x, y, x, (y+1) % L]:
                after[x, y, up] = before[x, (y+1) % L, down]
            else:
                after[x, y, up] = before[x, y, up]

            if adjacency[x, y, x, y-1]:
                after[x, y, down] = before[x, y-1, up]
            else:
                after[x, y, down] = before[x, y, down]

            if adjacency[x, y, x-1, y]:
                after[x, y, left] = before[x-1, y, right]
            else:
                after[x, y, left] = before[x, y, left]

            if adjacency[x, y, (x+1) % L, y]:
                after[x, y, right] = before[(x+1) % L, y, left]
            else:
                after[x, y, right] = before[x, y, right]

            after[x, y, stay] = before[x, y, stay]


def _run_single_shot(L, num_steps, ell, bl_prob, wx, wy, save_all_steps, initial_psi, N):
    """Helper function to run a single shot of the experiment."""
    # Define the initial state. The first two indices are the (x,y)
    # coordinate and the last is the coin.
    if initial_psi is None:
        psi = np.tile(np.array([
            1 / sqrt(N * (4 + ell)),
            1 / sqrt(N * (4 + ell)),
            1 / sqrt(N * (4 + ell)),
            1 / sqrt(N * (4 + ell)),
            sqrt(ell) / sqrt(N * (4 + ell))
            ]), (L, L, 1))
    else:
        psi = np.copy(initial_psi)

    w_probs = np.zeros(num_steps)
    w_probs_sq = np.zeros(num_steps)
    
    if save_all_steps:
        all_steps = [np.zeros((L, L)) for _ in range(num_steps)]
    else:
        all_steps = None

    # Simulate the quantum walk.
    for t in range(num_steps):
        psi[wx, wy] *= -1  # Oracle query.
        tmp = grover_coin(psi, L, ell)  # Grover coin.
        ff_shift(tmp, psi, L, bl_prob)  # Flip-flop shift.

        np.testing.assert_allclose(np.linalg.norm(psi), 1.0, rtol=1e-7)

        # Save the current success probability for the next iteration.
        last_prob = (psi[wx, wy]**2).sum()
        w_probs[t] = last_prob
        w_probs_sq[t] = last_prob**2

        if save_all_steps:
            all_steps[t] = np.sum(psi**2, axis=2)

    return w_probs, w_probs_sq, all_steps


def experiment(L = 16,
               num_steps = 100,
               ell = None,
               bl_prob = 0.0,
               wx = None,
               wy = None,
               save_all_steps = False,
               initial_psi = None,
               shots = 1,
               max_workers = None):
    """Simulates an experiment of a quantum walk on an LxL grid.

    The function performs a simulation of a quantum walk experiment on an LxL grid,
    with options to control various parameters such as the number of steps, self-loop weight,
    broken link probability, marked vertex coordinates, and more.

    Args:
        L (int): The size of the grid. Defaults to 16.
        num_steps (int): The number of steps to simulate. Defaults to 100.
        ell (float): The weight of the self-loop. If None, it is calculated as 4/N. Defaults to None.
        bl_prob (float): The probability of breaking each edge. Defaults to 0.0.
        wx (int): The x-coordinate of the marked vertex. If None, it is set to floor(L/2). Defaults to None.
        wy (int): The y-coordinate of the marked vertex. If None, it is set to floor(L/2). Defaults to None.
        save_all_steps (bool): Whether to save the state at each step. Defaults to False.
        initial_psi (numpy.ndarray): The initial state vector. If None, a default state is used. Defaults to None.
        shots (int): The number of times to repeat the experiment. Defaults to 1.
        max_workers (int, optional): The maximum number of worker processes to use. If None, defaults to the number of CPU cores. Defaults to None.

    Returns:
        Tuple[numpy.ndarray, numpy.ndarray, Union[None, List[numpy.ndarray]]]: A tuple containing three elements.
            - w_probs (numpy.ndarray): The success probabilities for each step, averaged over all shots.
            - w_stds: standard deviation of success probabilities per step.
            - all_steps (Union[None, List[numpy.ndarray]]): If save_all_steps is True, a list of state vectors at each step
              averaged over all shots. Otherwise, None.
    """

    # Calculate the number of vertices.
    N = L*L

    # Calculate the weight of the self-loop.
    if ell is None:
        ell = 4/N   # Tom Wong uses l, but I think it is easily confused with 1 in some fonts.

    # Without loss of generality, let the marked vertex be "in the middle" of the lattice.
    if wx is None:
        wx = L // 2
    if wy is None:
        wy = L // 2

    w_probs = np.zeros(num_steps)
    w_probs_sq = np.zeros(num_steps)  # for std deviation calculation

    if save_all_steps:
        all_steps = [np.zeros((L, L)) for _ in range(num_steps)]
    else:
        all_steps = None

    # If shots=1, run directly without ProcessPoolExecutor to avoid nested parallelism issues
    if shots == 1:
        shot_probs, shot_probs_sq, shot_steps = _run_single_shot(L, num_steps, ell, bl_prob, wx, wy, save_all_steps, initial_psi, N)
        w_probs += shot_probs
        w_probs_sq += shot_probs_sq
        if save_all_steps:
            for t in range(num_steps):
                all_steps[t] += shot_steps[t]
    else:
        # Run shots in parallel
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(_run_single_shot, L, num_steps, ell, bl_prob, wx, wy, save_all_steps, initial_psi, N) 
                       for _ in range(shots)]
            for future in futures:
                shot_probs, shot_probs_sq, shot_steps = future.result()
                w_probs += shot_probs
                w_probs_sq += shot_probs_sq
                if save_all_steps:
                    for t in range(num_steps):
                        all_steps[t] += shot_steps[t]

    w_probs /= shots
    w_probs_sq /= shots

    var = w_probs_sq - w_probs**2
    var = np.maximum(var, 0)  # replaces negative tiny values with 0
    w_stds = np.sqrt(var)

    if save_all_steps:
        for t in range(num_steps):
            all_steps[t] /= shots

    return w_probs, w_stds, all_steps



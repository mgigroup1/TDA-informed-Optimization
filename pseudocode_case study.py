# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# """
# Created on Thu Sep  5 11:16:51 2024

# @author: wenchingmei
# """

# - Import the required libraries:
#   - `numpy` for numerical operations.
#   - `gudhi` for computing persistence diagrams.
#   - `matplotlib.pyplot` for plotting graphs.
#   - `matlab.engine` to interface with MATLAB.

# - Start MATLAB engine:
#   - `eng = matlab.engine.start_matlab()`

# - Add the path containing the MATLAB function to the MATLAB engine:
#   - `eng.addpath('/path/to/matlab/functions')`

# - Define a function `matlab_objective_function(x)`:
#   - Convert Python list `x` to MATLAB format using `matlab.double()`.
#   - Call the MATLAB function `cost_total_D2sto_objcon_test()` using the engine.
#   - Convert the result from MATLAB back to Python format (assumed float).
#   - Return the result (objective function value).


import matlab.engine
import numpy as np

# Start MATLAB engine
eng = matlab.engine.start_matlab()
# Add the directory containing the MATLAB function to the MATLAB path
eng.addpath('/Users/.....')

def matlab_objective_function(x):
    # Convert Python list 'x' to MATLAB data type
    x_matlab = matlab.double(x.tolist())
    # Call the MATLAB function and get the result
    y_obj = eng.cost_total_D2sto_objcon_test(x_matlab)
    # Convert the result to a Python type if necessary, assuming y_obj is a float
    y_obj = float(y_obj)
    return y_obj


# - Define a function `compute_persistence_diagram(points)`:
#   - Create a Rips complex from the input `points` with max edge length.
#   - Create a simplex tree from the complex.
#   - Compute persistence pairs (birth and death of topological features).
#   - Return the persistence diagram containing birth and death values where death is finite.
def compute_persistence_diagram(points):
    """
    Compute the persistence diagram for a given set of points.
    """
    rips_complex = gd.RipsComplex(points=points, max_edge_length=0.5)
    simplex_tree = rips_complex.create_simplex_tree(max_dimension=1)
    diag = simplex_tree.persistence()
    return np.array([[birth, death] for (_, (birth, death)) in diag if death < float('inf')])

def compute_density_based_coefficient(persistence_pairs, sigma):
    """
    Compute the density-based coefficient (c2) for PSO from the persistence diagram,
    and return a scalar by averaging the densities.
    """
    D = persistence_pairs
    N_e = len(D)  # Number of features in the center diagram
    if N_e == 0:  # Avoid division by zero if no features are present
        return 0.5  # Default or fallback value of c2 if no persistence pairs are found

    densities = np.zeros(N_e)
    for index, (b, d) in enumerate(D):
        for (b_i, d_i) in D:
            densities[index] += np.exp(-0.5 * (((b - (b_i+d_i)/2) ** 2 + (d - (b_i+d_i)/2) ** 2) / sigma ** 2))
        densities[index] *= (1 / (N_e * np.sqrt(np.pi * 2) * sigma ** 2))
    
    c2 = np.mean(densities)  # Averaging densities to get a scalar value
    c2 = np.clip(c2, 0, 1)  # Ensure c2 is within [0, 1] bounds
    return c2


# - Define a function `compute_density_based_coefficient(persistence_pairs, sigma)`:
#   - Initialize a list of densities for each persistence pair.
#   - For each feature (birth-death pair):
#     - Calculate the density contribution from all other features using a Gaussian kernel.
#   - Average the densities to compute the coefficient `c2`.
#   - Clip `c2` between 0 and 1.
#   - Return `c2`.

# - Define a function `update_velocity(velocity, personal_best_position, global_best_position, current_position, c1, c2)`:
#   - Set inertia weight `w` to 0.5.
#   - Generate random values `r1` and `r2`.
#   - Update the velocity using the formula:
#     - new_velocity = (inertia * velocity) + (c1 * random * (personal_best - current_position)) + (c2 * random * (global_best - current_position)).
#   - Return updated velocity.

# - Define `pso_optimize(objective_function, num_particles, dimensions, bounds, num_iterations)`:
  
#   1. **Initialize Particles**:
#      - Randomly initialize `positions` of particles within the given `bounds`.
#      - Set `velocities` to zero.
#      - Set personal best positions as current positions.
#      - Evaluate objective function for all particles, storing the personal best scores.
#      - Set global best position as the one with the best (min) score.

#   2. **Main Optimization Loop**:
#      - For each iteration:
#        - Compute the persistence diagram for current particle positions.
#        - Compute `c2` from persistence diagram and `c1 = 1 - c2`.
#        - Store `c1` and `c2` values for analysis.

#        - For each particle:
#          - Update the velocity using `update_velocity()`.
#          - Update the position using the velocity, ensuring it stays within `bounds`.
#          - Compute persistence diagram for updated positions.
#          - Evaluate the objective function for the new position.

#          - **Update Personal Best**:
#            - If the current score is better than personal best, update the personal best position and score.

#          - **Update Global Best**:
#            - If the current score is better than global best, update the global best position and score.

#      - Print best score for each iteration.
  
#   3. **Return Results**:
#      - After completing iterations, return global best position, best score, `c1`, `c2` values, and persistence diagrams.

# - Optionally, plot particle positions during iterations:
#   - Every 10 iterations, plot particle positions on a scatter plot.
#   - Highlight the global best position with a special marker.
#   - Use a color gradient to differentiate between iterations.

# - After optimization, plot `c1` and `c2` values over iterations to observe their evolution.


# ************ Example Usage ************
# - Set number of particles, dimensions, bounds, and number of iterations.
# - Call the `pso_optimize()` function with the `matlab_objective_function` and the defined parameters.
# - Print the best position and score after optimization.

# Example usage:
num_particles = 100
dimensions = 8
# Assuming 8 variables based on your provided information
bounds = np.array([
    [2.85, 3.15],     # FR_API
    [25.365, 28.035], # FR_Exp
    [1064, 1176],     # RPM_co_mill
    [237.5, 262.5],   # RPM_blender
    [0.0095, 0.0105], # FillDepth
    [0.002375, 0.002625], # Thickness
    [10, 70],         # RS_API
    [10, 70]          # RS_Exp
])


# - The algorithm returns:
#   - Best particle position (optimal solution).
#   - Best score (minimal value of the objective function).
#   - Evolution of `c1` and `c2` values.
#   - Persistence diagrams for analysis.

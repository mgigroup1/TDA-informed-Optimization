# -*- coding: utf-8 -*-
"""
Created on Mon Apr 29 11:29:23 2024

@author: cmwen
"""

import numpy as np
import gudhi as gd
import matplotlib.pyplot as plt


np.random.seed(700)

# type "matlabroot" in commend windoe in matlab   ->> /Applications/MATLAB_R2021a.app
# cd /Program Files/MATLAB/R2022a/extern/engines/python
# python setup.py install
# cd "C:\Program Files\MATLAB\R2022a\extern\engines\python"
# "C:\Users\cmwen\AppData\Local\Programs\Python\Python39\python.exe" setup.py install


import matlab.engine
import numpy as np

# Start MATLAB engine
eng = matlab.engine.start_matlab()
# Add the directory containing the MATLAB function to the MATLAB path
eng.addpath('/Users/wenchingmei/Desktop/supply chain')


def matlab_objective_function(x):
    # Convert Python list 'x' to MATLAB data type
    x_matlab = matlab.double(x.tolist())
    # Call the MATLAB function and get the result
    y_obj = eng.cost_total_D2sto_objcon_test(x_matlab)
    # Convert the result to a Python type if necessary, assuming y_obj is a float
    y_obj = float(y_obj)
    return y_obj



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






def update_velocity(velocity, personal_best_position, global_best_position, current_position, c1, c2):
    """
    Update the velocity of particles.
    """
    w = 0.5  # Inertia weight
    r1, r2 = np.random.rand(), np.random.rand()
    # Ensure all operations are element-wise and the shapes are compatible
    new_velocity = w * velocity + c1 * r1 * (personal_best_position - current_position) + c2 * r2 * (global_best_position - current_position)
    return new_velocity



def pso_optimize(objective_function, num_particles, dimensions, bounds, num_iterations):
    positions = np.random.rand(num_particles, dimensions) * (bounds[:, 1] - bounds[:, 0]) + bounds[:, 0]
    velocities = np.zeros_like(positions)
    personal_best_positions = np.copy(positions)
    personal_best_scores = objective_function(personal_best_positions)
    global_best_position = personal_best_positions[np.argmin(personal_best_scores)]
    global_best_score = np.min(personal_best_scores)
    
    c1_values = []
    c2_values = []
    
    plt.figure(figsize=(10, 8))
    colors = plt.cm.jet(np.linspace(0, 1, num_iterations // 10 + 1))  # Color map to cycle through
    persistence_diagrams = []  # To store the persistence diagrams of each iteration


    for iteration in range(num_iterations):
        persistence_pairs = compute_persistence_diagram(positions)
        c2 = compute_density_based_coefficient(persistence_pairs, sigma=1)
        c1 = 1 - c2
        
        c1_values.append(c1)
        c2_values.append(c2)
        
        for i in range(num_particles):
            velocities[i] = update_velocity(velocities[i], personal_best_positions[i], global_best_position, positions[i], c1, c2)
            positions[i] += velocities[i]
            positions[i] = np.clip(positions[i], bounds[:, 0], bounds[:, 1])
            
            # After updating positions and before updating personal and global bests:
            persistence_diagram = compute_persistence_diagram(positions)
            persistence_diagrams.append(persistence_diagram)  # Store the persistence diagram
 
            current_score = objective_function(np.array([positions[i]]))[0]
            if current_score < personal_best_scores[i]:
                personal_best_scores[i] = current_score
                personal_best_positions[i] = positions[i]
                
                if current_score < global_best_score:
                    global_best_position = positions[i]
                    global_best_score = current_score

        # if iteration % 10 == 0:
        #     # Plot particles for this iteration
        #     color = colors[iteration // 10]
        #     plt.scatter(positions[:, 0], positions[:, 1], color=color, label=f'Iteration {iteration}')
        #     plt.scatter(global_best_position[0], global_best_position[1], color='black', marker='*', s=200, label='Global Best' if iteration == 0 else "")
        #     plt.xlim(bounds[0, 0], bounds[0, 1])
        #     plt.ylim(bounds[1, 0], bounds[1, 1])

        print(f"Iteration {iteration}: Best Score = {global_best_score}")
        print(f"Iteration {iteration}: Best Score = {global_best_score}, c1 = {c1}, c2 = {c2}")


    plt.title('Particle Movements Over Iterations')
    plt.xlabel('X')
    plt.ylabel('Y')
    #plt.legend()  # Optional: Enable if you want to show legend
    plt.show()

    
    return global_best_position, global_best_score, c1_values, c2_values, persistence_diagrams

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

num_iterations = 50

# The PSO optimization in Python will call this function
best_position, best_score = pso_optimize(matlab_objective_function, num_particles, dimensions, bounds, num_iterations)
print(f"Best Position: {best_position}, Best Score: {best_score}")

#Best Position: [-0.01144258  0.00291557], Best Score: 0.03710737315282486
#Best Position: [-0.17211242  0.02297347], Best Score: 0.10215462326581815


# eason: max 2 dim 2 

# # After running PSO optimization
# plt.figure(figsize=(10, 5))
# plt.subplot(1, 2, 1)
# plt.plot(c1_values, label='c1')
# plt.title('c1 values over iterations')
# plt.xlabel('Iteration')
# plt.ylabel('c1')
# plt.legend()

# plt.subplot(1, 2, 2)
# plt.plot(c2_values, label='c2')
# plt.title('c2 values over iterations')
# plt.xlabel('Iteration')
# plt.ylabel('c2')
# plt.legend()

# plt.tight_layout()
# plt.show()

import sys
sys.path.append(r"C:\GAMS\40\apifiles\Python\gams")
import gams
print(gams.__version__)



import sys
sys.path.append(r"C:\GAMS\40\apifiles\Python\gams")  # Ensure correct path
import gams

# Initialize GAMS Workspace
ws = gams.GamsWorkspace(system_directory="C:\\GAMS\\40")

# Print confirmation
print("GAMS API is working!")






import sys
sys.path.append(r"C:\GAMS\40\apifiles\Python\gams")  # Adjust the path if needed





import sys
sys.path.append(r"C:\Users\cmwen\AppData\Local\Programs\Python\Python38\Lib\site-packages\gams")

import gams
ws = gams.GamsWorkspace(system_directory="C:\\GAMS\\40")

print("GAMS API is successfully connected!")


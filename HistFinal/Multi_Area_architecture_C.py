# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 11:13:30 2024

@author: esnow
"""


import numpy as np
import os
import matplotlib.pyplot as plt
from scipy.sparse import random as sparse_random
from skimage.transform import resize
import math

# Function to load retinal wave data
def load_retinal_wave_data(wave_directory):
    wave_files = [os.path.join(wave_directory, f) for f in os.listdir(wave_directory) if f.endswith('.npy')]
    waves = [np.load(wave_file) for wave_file in wave_files]
    return waves

# Function to resize data
def resize_data(data, new_size):
    T = data.shape[2]
    resized_data = np.zeros((new_size[0], new_size[1], T))
    for t in range(T):
        resized_frame = resize(data[:, :, t], new_size, anti_aliasing=True, mode='reflect')
        threshold = 0.01
        resized_data[:, :, t] = (resized_frame > threshold).astype(int)
    return resized_data

# Function to normalize data
def normalize_data(data):
    min_val = np.min(data)
    max_val = np.max(data)
    if max_val - min_val == 0:
        return data
    return (data - min_val) / (max_val - min_val)

# Function to initialize variables
def initialize_variables(N, g, p, alpha):
    scale = 1.0 / np.sqrt(p * N)
    sparse_matrix = sparse_random(N, N, density=p, format='csr', data_rvs=np.random.randn)
    J_d = sparse_matrix.toarray() * g * scale
    u_in = np.random.uniform(-1, 1, size=(N, N))
    u = np.random.uniform(-1, 1, size=(N, N))
    P = np.eye(N) / alpha
    x_0 = 0.5 * np.random.randn(N)
    return J_d, u_in, u, P, x_0

# Function to downsample data
def downsample_data(data, original_dt, new_dt):
    factor = int(new_dt / original_dt)
    return data[:, ::factor]

# Load Retinal Wave Data
wave_directory = 'data/generated_waves/Trial0_Directional/numpy_waves/'
waves = load_retinal_wave_data(wave_directory)
retinal_data = waves[1]  # Using the second wave file (index starts from 0)

# Determine Frame Dimensions
frame_height, frame_width, T = retinal_data.shape
print(f"Frame dimensions: {frame_height}x{frame_width}, Number of frames: {T}")

# Load the excitatory data
exc_data = np.load('D:/MA/activity_code/activity_code/data/rates_exc_Htriggered_Hampdirect_trial0.npy')

# Downsample the excitatory data to match the retinal data's temporal resolution
original_dt = 1  # Original temporal resolution of exc_data is 1 ms
new_dt = 10    # New temporal resolution is 10 ms
exc_data_downsampled = downsample_data(exc_data, original_dt, new_dt)

# Resizing the excitatory data frames from 40x40 to 10x10
new_size = (40, 40)
T_resized = retinal_data.shape[2]
resized_exc_data = np.zeros((new_size[0] * new_size[1], T_resized))

for t in range(T_resized):
    frame = exc_data_downsampled[:, t].reshape(40, 40)  # Assuming original size of exc_data frames is 40x40
    resized_frame = resize(frame, new_size, anti_aliasing=True, mode='reflect')
    resized_exc_data[:, t] = resized_frame.reshape(new_size[0] * new_size[1])

print(f"Resized excitatory data dimensions: {resized_exc_data.shape}")

# Resizing the retinal data frames from 64x64 to 10x10
resized_retinal_data = resize_data(retinal_data, new_size)
print(f"Resized retinal data dimensions: {resized_retinal_data.shape}")

# Normalize the data
normalized_exc_data = normalize_data(resized_exc_data)
normalized_retinal_data = normalize_data(resized_retinal_data)
a = normalized_exc_data
# Vectorize retinal data
vectorized_retinal_data = normalized_retinal_data.reshape(new_size[0] * new_size[1], T_resized)
N, T = vectorized_retinal_data.shape
g = 1.5  # g greater than 1 leads to chaotic networks.
alpha = 1.0
dt = 1
tau = 1
t_vec = np.linspace(0, T, int(T/dt))

# Initialize variables
W = np.zeros((N, N))
W_d = np.zeros((N, N))
# Assuming p, N, and g are defined
p = 1 # example value for p
u = np.random.uniform(-1, 1, size=(N))
# Calculate scale
scale = 1.0 / np.sqrt(p * N)

# Generate a sparse random matrix with normally distributed values
# The random function generates values in [0, 1), so we need to use a normal distribution
sparse_matrix = sparse_random(N, N, density=p, format='csr', data_rvs=np.random.randn)

# Convert to dense matrix and scale
J = sparse_matrix.toarray() * g * scale
P = np.eye(N) / alpha  # Initialize learning update matrix P
x = np.zeros((N, len(t_vec)))
x_0 = 0.5 * np.random.randn(N)
z_0 = 0.5 * np.random.randn()

x[:, 0] = x_0
r = np.tanh(x_0)
r_1 = r
r_2 = r
r_3 = r
r_d = r
z = z_0
ps_vec = []
x_1 = x
x_2 = x
x_3 = x
x_d = x
J_1 = J
J_2 = J
J_3 = J
J_d = J
P_1 = P
P_2 = P
P_3 = P
P_d = P
# Initialize feed-forward connection matrix
C1 = np.random.randn(N, N) / np.sqrt(N)
C2 = np.random.randn(N, N) / np.sqrt(N)
C_d = np.random.randn(N, N) / np.sqrt(N)
# The data is generated from a normal distribution with a small variance
sparsity = 0.1
rvs = lambda x: np.random.randn(x) / np.sqrt(N)   
C_sparse = sparse_random(N, N, density=sparsity, data_rvs=rvs)
C_sparse = C_sparse.toarray()
# Training Loop only time loop
for t in range(1, len(t_vec)):
    # Update neuron state
    x_1[:, t] = (1 - dt / tau) * x_1[:, t-1] + (dt / tau) * (np.dot(J_1, r_1)) + u*vectorized_retinal_data[:, t-1]
    # Update firing rate
    r_1 = np.tanh(x_1[:, t])  # Ensure r is (N,)
    y_input_1 = np.dot(C1, r_1)
    
    x_2[:, t] = (1 - dt / tau) * x_2[:, t-1] + (dt / tau) * (np.dot(J_2, r_2)) + u * y_input_1
    # Update firing rate
    r_2 = np.tanh(x_2[:, t])  # Ensure r is (N,)
    
    y_input_2 = np.dot(C2, r_2)
    x_3[:, t] = (1 - dt / tau) * x_3[:, t-1] + (dt / tau) * (np.dot(J_3, r_3)) + u * y_input_2
    # Update firing rate
    r_3 = np.tanh(x_3[:, t])  # Ensure r is (N,)
    # Update network output
    z = np.dot(W.T, r_3)  # Ensure z is a scalar
    
    # Compute error
    e_minus = z - a[:,t-1]
    
    #### comment out to check the simple mode
    k1 = np.dot(P_1, r_1)
    rPr_1 = np.dot(r_1.T, k1)
    c1 = 1.0 / (1.0 + rPr_1)
    # C1 -=  c1 * np.outer(k1, e_minus)
    J_1 = J_1 - c1 * np.outer(e_minus, k1)
    P_1 = P_1 - c1 * np.outer(k1, k1)
    k2 = np.dot(P_2, r_2)
    rPr = np.dot(r_2.T, k2)
    c2 = 1.0 / (1.0 + rPr)
    # C2 -=  c2 * np.outer(k2, e_minus)
    J_2 = J_2 - np.outer(e_minus, k2)*c2
    P_2 = P_2 - c2 * np.outer(k2, k2)
    ####
    
    k3 = np.dot(P_3, r_3)
    rPr = np.dot(r_3.T, k3)
    c = 1.0 / (1.0 + rPr)
    W -= c * np.outer(k3, e_minus) #key training process #sensitive to errorc * np.outer(k, e)
    J_3 = J_3 - np.outer(e_minus, k3)*c
    P_3 = P_3 - c * np.outer(k3, k3)
    
    ###############
    y_input_d = y_input_2
    x_d[:, t] = (1 - dt / tau) * x_d[:, t-1] + (dt / tau) * (np.dot(J_d, r_d)) + u * y_input_d
    # Update firing rate
    r_d = np.tanh(x_d[:, t])  # Ensure r is (N,)
    # Update network output
    z_d = np.dot(W_d.T, r_d)  # Ensure z is a scalar
    
    # Compute error
    e_d = z_d - a[:,t-1]
    k_d = np.dot(P_d, r_d)
    rPr_d = np.dot(r_d.T, k_d)
    c_d = 1.0 / (1.0 + rPr_d)
    W_d -= c_d * np.outer(k_d, e_d) #key training process #sensitive to errorc * np.outer(k, e)
    J_d = J_d - np.outer(e_d, k_d)*c_d
    P_d = P_d - c * np.outer(k_d, k_d)
    
# Testing Phase
simtime_len = len(t_vec)
zpt = np.zeros((N,simtime_len))
zpt_d = np.zeros((N,simtime_len))
x_test_1 = x_1[:, 0]
x_test_3 = x_3[:, 0]
x_test_2 = x_2[:, 0]
x_test_d = x_d[:, 0]
r_test_1 = np.tanh(x_test_1)
r_test_3 = np.tanh(x_test_3)
r_test_2 = np.tanh(x_test_2)
r_test_d = np.tanh(x_test_d)
z = z_0
for ti in range(simtime_len):
    x_test_1 = (1.0 - dt) * x_test_1 + np.dot(J_1, r_test_1 * dt)  + u*vectorized_retinal_data[:, ti-1]
    r_test_1 = np.tanh(x_test_1)
    y_test_input_1 = np.dot(C1, r_test_1)
    x_test_2 = (1.0 - dt) * x_test_2 + np.dot(J_2, r_test_2 * dt) +  u*y_test_input_1
    r_test_2 = np.tanh(x_test_2)
    # y_test_input_2 = np.dot(C2 * 0.1, r_test_2)
    y_test_input_2 = np.dot(C_sparse, r_test_2)
    x_test_3 = (1.0 - dt) * x_test_3+ np.dot(J_3, r_test_3 * dt) +  u*y_test_input_2
    r_test_3 = np.tanh(x_test_3)
    zpt[:, ti] = np.dot(W.T, r_test_3)  # Use the final trained weights
    y_test_input_d = y_test_input_2
    x_test_d = (1.0 - dt) * x_test_d+ np.dot(J_d, r_test_d * dt) +  u*y_test_input_d
    r_test_d = np.tanh(x_test_d)
    zpt_d[:, ti] = np.dot(W_d.T, r_test_d)  # Use the final trained weights


error_avg_v = np.mean(np.abs(zpt - a))
print(f'Testing MAE v: {error_avg_v:.3f}')
error_avg_d = np.mean(np.abs(zpt_d - a))
print(f'Testing MAE d: {error_avg_d:.3f}')


for iter in range(simtime_len):
    fig, axes = plt.subplots(2, 2, figsize = (10, 8))
    fig_1 = axes[0, 0].imshow(zpt[:, iter].reshape(new_size))
    axes[0, 0].set_title(f'Out frame {iter} branch vHVA')
    cbar_1 = fig.colorbar(fig_1, ax=axes[0, 0]) 
    fig_2 = axes[0, 1].imshow(a[:, iter].reshape(new_size))
    axes[0, 1].set_title(f'Targeting frame {iter}')
    cbar_2 = fig.colorbar(fig_2, ax=axes[0, 1]) 
    fig_3 = axes[1, 0].imshow(zpt_d[:, iter].reshape(new_size))
    axes[1, 0].set_title(f'Out frame {iter} branch dHVA')
    cbar_3 = fig.colorbar(fig_3, ax=axes[1, 0]) 
    fig_4 = axes[1, 1].imshow(a[:, iter].reshape(new_size))
    axes[1, 1].set_title(f'Targeting frame {iter}')
    cbar_4 = fig.colorbar(fig_4, ax=axes[1, 1]) 
    plt.tight_layout()
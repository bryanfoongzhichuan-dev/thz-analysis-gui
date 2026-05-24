# -*- coding: utf-8 -*-
"""
Created on Sun Aug 31 19:49:39 2025

@author: bryan_foong
"""

import matplotlib.pyplot as plt
import numpy as np

def make_plot_list(x, y):
    """
    Convert x and y (1D or 2D arrays) into a list of (x_array, y_array) pairs
    suitable for plot_multiple.
    """
    # Ensure x and y are at least 2D
    x_list = [xi.squeeze() for xi in np.atleast_2d(x)]
    y_list = [yi.squeeze() for yi in np.atleast_2d(y)]
    return list(zip(x_list, y_list))

def plot_multiple(datasets, labels=None, title="Multiple Signals", xlabel="X", ylabel="Y", styles=None, grid=True, show=True, save_path=None):
    """
    Plot multiple 1D datasets on the same axes.
    
    Parameters:
        datasets (list of tuples): [(x1, y1), (x2, y2), ...]
        labels (list of str): Legend labels for each dataset
        title (str): Plot title
        xlabel (str): X-axis label
        ylabel (str): Y-axis label
        styles (list of str): Line styles for each dataset
        grid (bool): Show grid
        show (bool): Display plot
        save_path (str): Save figure to file if provided
    """
    plt.figure()
    for i, (x, y) in enumerate(datasets):
        label = labels[i] if labels and i < len(labels) else None
        style = styles[i] if styles and i < len(styles) else "-"
        plt.plot(x, y, style, label=label)
    
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    
    if labels:
        plt.legend()
    if grid:
        plt.grid(True)
    if save_path:
        plt.savefig(save_path, dpi=300)
    if show:
        plt.show()

def plot_parameters(parameters, state, show=True):
    """
    Plot all THz parameters against frequency.

    parameters: tuple
        (freq, n, k, alpha, e_r, e_i)
    show: bool
        Whether to display the plots immediately
    """
    freq, n, k, alpha, e_r, e_i, cond_r, cond_i = parameters

    plots = [
        ("n", n, "Refractive Index n"),
        ("k", k, "Extinction Coefficient k"),
        ("alpha", alpha, "Absorption Coefficient α"),
        ("eps_r", e_r, "Dielectric Constant ε_r"),
        ("eps_i", e_i, "Dielectric Constant ε_i"),
        ("cond_r", cond_r, "Conductivity real"),
        ("cond_i", cond_i, "Conductivity imag")
    ]
    
    for key, y, ylabel in plots:
        if state.get(key, False):
            plot_1d(
                freq[0],
                y,
                title=f"{ylabel} vs Frequency",
                xlabel="Frequency (THz)",
                ylabel=ylabel,
                show=show
                )
    
    """for y, ylabel in plots:
        plot_1d(freq[0], y, title=f"{ylabel} vs Frequency", xlabel="Frequency (THz)", ylabel=ylabel, show=show)"""
        

        
def plot_1d(x, y, title="Plot", xlabel="X", ylabel="Y", labels=None, style="-", grid=True, show=True, save_path=None):
    """
    General-purpose 1D plot function.

    Parameters:
        x (array-like): X-axis data
        y (array-like): Y-axis data
        title (str): Plot title
        xlabel (str): X-axis label
        ylabel (str): Y-axis label
        label (str): Legend label
        style (str): Line style
        grid (bool): Show grid
        show (bool): Display plot immediately
        save_path (str): If provided, save plot to file
    """

    y = np.atleast_2d(y)  # ensures 2D
    plt.figure()
    for i, row in enumerate(y):
        label = labels[i] if labels else None
        plt.plot(x, row, style, label=label)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    if labels:
        plt.legend()
    if grid:
        plt.grid(True)
    if save_path:
        plt.savefig(save_path, dpi=300)
    if show:
        plt.show()
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 29 21:17:01 2025

@author: bryan_foong
"""

# dataset.py
import numpy as np

class THzDataset:
    def __init__(self, time, signal):
        self.time = np.array(time)
        self.signal = np.array(signal)

    @classmethod
    def from_file(cls, filepath, delimiter=None):
        data = np.loadtxt(filepath)
        time = data[:, 0]
        signal = data[:, 1]
        return cls(time, signal)

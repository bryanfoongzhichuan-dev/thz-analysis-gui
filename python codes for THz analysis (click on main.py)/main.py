# -*- coding: utf-8 -*-
"""
Created on Fri Aug 29 21:18:29 2025

@author: bryan_foong
"""

# main.py

from core.dataset import THzDataset
#from core.visualization import plot_signal, plot_spectrum
from analysis.core_parameters import *
from core.visualisation import plot_multiple
#from analysis.peaks import find_main_peak

#GUI part
from gui.thz_gui import *
import sys
from PyQt5.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = THzGUI()
    gui.show()
    sys.exit(app.exec_())
#GUI part



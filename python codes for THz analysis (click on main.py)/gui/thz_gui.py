# -*- coding: utf-8 -*-
"""
Created on Sun Aug 31 17:35:59 2025

@author: bryan_foong
"""
import sys
import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QPushButton, QFileDialog, QLabel, QInputDialog, QMessageBox
)

from core.dataset import THzDataset
from analysis.core_parameters import *
from core.visualisation import plot_multiple, plot_parameters, make_plot_list
#from thz_analysis import fft  # <-- your analysis code
from gui.advanced_options import AdvancedOptionsWindow


class THzGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("THz Analysis GUI")
        self.setGeometry(200, 200, 400, 200)

        # Central widget
        widget = QWidget()
        self.setCentralWidget(widget)

        # Layout
        layout = QVBoxLayout()
        widget.setLayout(layout)

        # Buttons
        self.load_button_sample = QPushButton("Load Data (Sample)")
        self.load_button_blank = QPushButton("Load Data (Blank)")
        self.extract_parameters_button = QPushButton("Extract Parameters")
        self.save_parameters_button = QPushButton("Save Parameters")
        self.advanced_button = QPushButton("Advanced Options")

        # Info label
        self.info_label1 = QLabel("Sample file: No data loaded.")
        self.info_label2 = QLabel("Blank file: No data loaded.")
        self.info_label = QLabel("")

        # Add widgets to layout
        layout.addWidget(self.load_button_sample)
        layout.addWidget(self.load_button_blank)
        layout.addWidget(self.extract_parameters_button)
        layout.addWidget(self.save_parameters_button)
        layout.addWidget(self.advanced_button)
        layout.addWidget(self.info_label1)
        layout.addWidget(self.info_label2)
        layout.addWidget(self.info_label)
        
        # Data storage
        self.time_s = None
        self.time_b = None
        self.signal_s = None
        self.signal_b = None

        # Connect buttons
        self.load_button_sample.clicked.connect(self.load_data_sample)
        self.load_button_blank.clicked.connect(self.load_data_blank)
        self.extract_parameters_button.clicked.connect(self.extract_para)
        self.save_parameters_button.clicked.connect(self.save_parameters)
        self.advanced_button.clicked.connect(self.open_advanced_options)
        
        self.parameter_state = {
            "n": True,
            "k": True,
            "alpha": True,
            "eps_r": True,
            "eps_i": True,
            "cond_r": False,
            "cond_i": False
            }

    def load_data_sample(self):
        """Load sample dataset from file"""
        #for bookkeeping
        '''fname, _ = QFileDialog.getOpenFileName(self, "Open File", "","All Files (*.*);;CSV Files (*.csv);;Text Files (*.txt)")
        if fname:
            dataset = THzDataset.from_file(fname)
            self.time_s, self.signal_s = dataset.time, dataset.signal
            self.info_label1.setText(f"Sample file: {fname}")'''
        
        fnames, _ = QFileDialog.getOpenFileNames(
            self,
            "Open Files",
            "",
            "All Files (*.*);;CSV Files (*.csv);;Text Files (*.txt)"
            )

        if fnames:
            time_list = []
            signal_list = []

        for fname in fnames:
            dataset = THzDataset.from_file(fname)
            time_list.append(dataset.time)
            signal_list.append(dataset.signal)

        # Convert lists to 2D arrays (each row = one file)
        self.time_s = np.array(time_list)
        self.signal_s = np.array(signal_list)
        self.info_label1.setText(f"Loaded {len(fnames)} sample files")
        self.time_s = np.squeeze(np.array(time_list))
        self.signal_s = np.squeeze(np.array(signal_list))

    
    def load_data_blank(self):
        """Load blank dataset from file"""
        fname, _ = QFileDialog.getOpenFileName(self, "Open File", "","All Files (*.*);;CSV Files (*.csv);;Text Files (*.txt)")
        if fname:
            dataset = THzDataset.from_file(fname)
            self.time_b, self.signal_b = dataset.time, dataset.signal
            self.info_label2.setText(f"Blank file: {fname}")
    
    def get_thickness(self, prompt="Enter thickness(mm):"):
        """Ask the user for a numeric input and return it as a float."""
        text, ok = QInputDialog.getText(self, "Input Required", prompt)
        
        if not ok:  # User cancelled
            return None
        
        try:
            value = float(text)  # Convert to float
            return value
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid number.")
            return self.get_numeric_input(prompt)  # Ask again recursively    
    
    def extract_para(self):
        """Run FFT using your thz_analysis.fft function"""
        if self.time_s is not None and self.signal_s is not None and self.time_b is not None and self.signal_b is not None:
            thickness = self.get_thickness()
            (y_s ,freq, p_s) = fft(self.time_s, self.signal_s) 
            (y_b, freq2, p_b) = fft(self.time_b, self.signal_b)
            self.fftresults = (freq, y_s, p_s, freq2, y_b, p_b)
            
            
            n = n_f(freq, p_s, p_b, thickness)
            k = k_f(freq, np.abs(y_s), np.abs(y_b), n, thickness)
            a = a_f(freq, k)
            e_r, e_i = dielec(freq, n, a)
            cond_r, cond_i = conductivity(freq, e_r, e_i)
            
            #maybe add parameters 2
            self.parameters = (freq, n, k, a, e_r, e_i)
            self.parameters2 = (cond_r, cond_i)
            self.fullparameters = (freq, n, k, a, e_r, e_i, cond_r, cond_i)
            
            '''
            tds_var = [(self.time_s, self.signal_s),(self.time_b, self.signal_b)]
            fds_var = [(freq, np.abs(y_s)), (freq2, np.abs(y_b))]
            plot_multiple(tds_var, labels=None, title="TDS plots", xlabel="Time", ylabel="Signal", styles=None, grid=True, show=True, save_path=None)
            plot_multiple(fds_var, labels=None, title="FDS plots", xlabel="Freq", ylabel="Signal", styles=None, grid=True, show=True, save_path=None)
            '''
            # Prepare TDS and FDS lists
            tds_var = make_plot_list(self.time_s, self.signal_s) + make_plot_list(self.time_b, self.signal_b)
            fds_var = make_plot_list(freq if freq.ndim>1 else np.atleast_2d(freq), np.abs(y_s)) + \
                make_plot_list(freq2 if freq2.ndim>1 else np.atleast_2d(freq2), np.abs(y_b))
                
            # Plot
            plot_multiple(tds_var, labels=None, title="TDS plots", xlabel="Time", ylabel="Signal", styles=None, grid=True, show=True)
            plot_multiple(fds_var, labels=None, title="FDS plots", xlabel="Freq", ylabel="Signal", styles=None, grid=True, show=True)
            
            plot_parameters(self.fullparameters, self.parameter_state, show=True)
        else:
            self.info_label.setText("Please load data first.")

    def save_parameters(self):
        # Ask the user where to save
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Data",
            "",  # default directory (empty = current)
            "Text Files (*.txt);;All Files (*)"
            )
        if not file_path:
            return
        
        try:
            
            #freq, n, k, alpha, e_r, e_i = self.parameters
            freq, n, k, alpha, e_r, e_i, cond_r, cond_i = self.fullparameters
            data_map = {
                "n": n,
                "k": k,
                "alpha": alpha,
                "eps_r": e_r,
                "eps_i": e_i,
                "cond_r": cond_r,
                "cond_i":cond_i
                }
            for i in range(n.shape[0]):
                
                cols = [freq[i]]  # always include frequency
                labels = ["Frequency(THz)"]
            
                for key, data in data_map.items():
                    if self.parameter_state.get(key, False):
                        cols.append(data[i])
                        labels.append(key)
                    
                file_name = f"{file_path}_trace{i+1}.txt"
                    
                np.savetxt(
                    file_name,
                    np.column_stack(cols),
                    delimiter="\t",
                    header="\t".join(labels),
                    comments=''
                    )
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save data:\n{e}")
            
        """
        header = "Frequency(THz)\tn\tk\talpha\te_r\te_i"
        if file_path:
            try:
                [np.savetxt(f"{file_path}_trace{i+1}.txt", np.column_stack([freq[i], n[i], k[i], alpha[i], e_r[i], e_i[i]]),
                    delimiter="\t", header=header, comments='') for i in range(n.shape[0])]
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save data:\n{e}")
        else:
            QMessageBox.warning(self, "Cancelled", "Save cancelled")"""
    
    def open_advanced_options(self):
        self.advanced_window = AdvancedOptionsWindow(self.parameter_state, self)
        self.advanced_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = THzGUI()
    gui.show()
    sys.exit(app.exec_())


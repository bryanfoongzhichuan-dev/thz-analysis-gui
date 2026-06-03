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
import re

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
            "cond_i": False,
            "mode": "Transmission"
            }
    def parse_header(self, header_line):
        result = {"R": np.nan, "X": np.nan, "Y": np.nan, "Z": np.nan}
            
        matches = re.findall(r'([RXYZ])=([-+]?\d*\.?\d+(?:[Ee][-+]?\d+)?)', header_line)

        for key, val in matches:
            result[key] = float(val)

        return result
    def load_data_sample(self):

        fnames, _ = QFileDialog.getOpenFileNames(
            self,
            "Open Files",
            "",
            "All Files (*.*);;CSV Files (*.csv);;Text Files (*.txt)"
            )
        
        if not fnames:
            return
        
        time_list = []
        signal_list = []
        name_list = []
        header_list = []
        
        for fname in fnames:
            with open(fname, "r") as f:
                lines = f.readlines()
                
            # ---- detect header safely ----
            header = None
            data_lines = lines
            
            first_line = lines[0].strip()
            
            # safer check: if it contains letters → treat as header
            if any(c.isalpha() for c in first_line):
                header = first_line
                data_lines = lines[1:]
                
            # ---- parse numeric data safely ----
            data = []
            for line in data_lines:
                parts = line.strip().split()
                if len(parts) >= 2:
                    try:
                        data.append([float(parts[0]), float(parts[1])])
                    except:
                        pass  # skip bad lines safely
                        
            data = np.array(data)

            if data.size == 0:
                continue  # skip broken file

            time_list.append(data[:, 0])
            signal_list.append(data[:, 1])
            if first_line.startswith("Stage_Position"):
                header_dict = self.parse_header(first_line)
            else:
                header_dict = {"R": np.nan, "X": np.nan, "Y": np.nan, "Z": np.nan}
                
            header_list.append(header_dict)
            
            print(header_dict)
            name_list.append(fname)
            
        self.time_s = np.squeeze(np.array(time_list))
        self.signal_s = np.squeeze(np.array(signal_list))
        
        self.name_list = name_list
        self.header_list = header_list
        
        self.info_label1.setText(f"Loaded {len(name_list)} sample files")
        
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
        
    def get_angle(self, prompt="Enter angle (degrees):"):
        """Ask the user for an angle in degrees and return it as a float."""
        text, ok = QInputDialog.getText(self, "Input Required", prompt)
        
        if not ok:  # User cancelled
            return None
        
        try:
            value = float(text)  # Convert to float
            return value
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid number.")
            return self.get_angle(prompt)  # retry safely
    
    def extract_para(self):
        """Run FFT using your thz_analysis.fft function"""
        if self.time_s is not None and self.signal_s is not None and self.time_b is not None and self.signal_b is not None:
            (y_s ,freq, p_s) = fft(self.time_s, self.signal_s) 
            (y_b, freq2, p_b) = fft(self.time_b, self.signal_b)
            self.fftresults = (freq, y_s, p_s, freq2, y_b, p_b)
            if self.parameter_state["mode"] == "Transmission":
                thickness = self.get_thickness()
                n = n_transmission(freq, p_s, p_b, thickness)
                k = k_transmission(freq, np.abs(y_s), np.abs(y_b), n, thickness)
                a = a_transmission(freq, k)
                e_r, e_i = dielec_transmission(freq, n, a)
            
            elif self.parameter_state["mode"] == "Reflection":
                angle = self.get_angle()
                n = n_reflection(freq, p_s, p_b, angle)
                k = k_reflection(freq, n, np.abs(y_s), np.abs(y_b), angle)
                a = alpha_reflection(freq, k)
                e_r, e_i = dielec_reflection(n, k)

                
            cond_r, cond_i = conductivity(freq, e_r, e_i)
            
            #maybe add parameters 2
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
                
                original_name = self.name_list[i] if hasattr(self, "name_list") else f"trace{i+1}"
                    
                np.savetxt(
                    file_name,
                    np.column_stack(cols),
                    delimiter="\t",
                    header=f"File: {original_name}\n" + "\t".join(labels),
                    comments=''
                    )
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save data:\n{e}")
            

    
    def open_advanced_options(self):
        self.advanced_window = AdvancedOptionsWindow(self.parameter_state, self)
        self.advanced_window.show()
    




if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = THzGUI()
    gui.show()
    sys.exit(app.exec_())


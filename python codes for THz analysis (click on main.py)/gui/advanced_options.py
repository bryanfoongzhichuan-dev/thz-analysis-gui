# -*- coding: utf-8 -*-
"""
Created on Fri May 22 23:32:28 2026

@author: bryan_54tjivr
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel,
    QTabWidget, QWidget,
    QComboBox, QPushButton, QFormLayout, QCheckBox, QLineEdit, QFileDialog, QHBoxLayout, QSpinBox
)
from analysis.models import *
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class AdvancedOptionsWindow(QDialog):
    def __init__(self, state, parent=None):
        super().__init__(parent)
        self.state = state

        self.setWindowTitle("Advanced Options")
        self.setGeometry(300, 300, 400, 250)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Create tab widget (this is the "Chrome tabs")
        self.tabs = QTabWidget()

        # -------------------------
        # TAB 1: PARAMETERS
        # -------------------------
    
        self.tab_parameters = QWidget()
        param_layout = QVBoxLayout()
        
        # Measurement mode selector
        param_layout.addWidget(QLabel("Measurement mode:"))
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Transmission", "Reflection"])
        self.mode_combo.setCurrentText(
            self.state.get("mode", "Transmission")
            )
        param_layout.addWidget(self.mode_combo)
        
        param_layout.addWidget(QLabel("Select parameters to include:"))
        
        # Tick boxes (parameters)
        self.cb_n = QCheckBox("Refractive index (n)")
        self.cb_n.setChecked(self.state["n"])
        
        self.cb_k = QCheckBox("Extinction coefficient (k)")
        self.cb_k.setChecked(self.state["k"])
        
        self.cb_alpha = QCheckBox("Absorption coefficient (α)")
        self.cb_alpha.setChecked(self.state["alpha"])
        
        self.cb_eps_r = QCheckBox("Dielectric real (εr)")
        self.cb_eps_r.setChecked(self.state["eps_r"])
        
        self.cb_eps_i = QCheckBox("Dielectric imag (εi)")
        self.cb_eps_i.setChecked(self.state["eps_i"])
        
        self.cb_cond_r = QCheckBox("Conductivity real (σr)")
        self.cb_cond_r.setChecked(self.state["cond_r"])
        
        self.cb_cond_i = QCheckBox("Conductivity imag (σi)")
        self.cb_cond_i.setChecked(self.state["cond_i"])
            
        # Default: all unchecked (or you can set True if you want)
        # self.cb_n.setChecked(True)
        
        # Add to layout
        param_layout.addWidget(self.cb_n)
        param_layout.addWidget(self.cb_k)
        param_layout.addWidget(self.cb_alpha)
        param_layout.addWidget(self.cb_eps_r)
        param_layout.addWidget(self.cb_eps_i)
        param_layout.addWidget(self.cb_cond_r)
        param_layout.addWidget(self.cb_cond_i)
        
        self.tab_parameters.setLayout(param_layout)

        # -------------------------
        # TAB 2: MODEL FIT
        # -------------------------
        fit_layout = QVBoxLayout()
        self.tab_model_fit = QWidget()
        self.tab_model_fit.setLayout(fit_layout)
        self.fit_window = FitPlotWindow()

        
        # =========================
        # MODEL SELECTION
        # =========================
        fit_layout.addWidget(QLabel("Select conductivity model:"))
        
        self.model_box = QComboBox()
        self.model_box.addItems([
            "Drude",
            "Drude_smith",
            "Cole_drude"
            ])
        
        fit_layout.addWidget(self.model_box)
        
        
        # =========================
        # FIT TARGET
        # =========================
        fit_layout.addWidget(QLabel("Fit target:"))
        
        self.fit_target_box = QComboBox()
        self.fit_target_box.addItems([
            "Conductivity Real",
            "Conductivity Imag",
            "Both"
            ])
        
        fit_layout.addWidget(self.fit_target_box)
        
        # =========================
        # FREQUENCY RANGE
        # =========================
        freq_form = QFormLayout()
        
        self.freq_min = QLineEdit("0.1")
        self.freq_max = QLineEdit("3.0")

        freq_form.addRow("Min Frequency (THz):", self.freq_min)
        freq_form.addRow("Max Frequency (THz):", self.freq_max)
        
        fit_layout.addLayout(freq_form)
        
        # =========================
        # INITIAL GUESSES
        # =========================
        guess_form = QFormLayout()
        
        self.guess_sigma0 = QLineEdit("1000")
        self.guess_tau = QLineEdit("1e-13")
        
        
        guess_form.addRow("Initial σ₀:", self.guess_sigma0)
        guess_form.addRow("Initial τ (s):", self.guess_tau)
        
        # =========================
        # DRUDE-SMITH EXTRA PARAM
        # =========================
        self.guess_c1 = QLineEdit("-0.5")
        
        self.c1_row_label = QLabel("Initial c₁:")
        guess_form.addRow(self.c1_row_label, self.guess_c1)
        self.model_box.currentTextChanged.connect(self.update_model_ui)

        fit_layout.addLayout(guess_form)
        
        # =========================
        # RUN FIT BUTTON
        # =========================
        self.run_fit_button = QPushButton("Run Fit")
    
        fit_layout.addWidget(self.run_fit_button)
        
        self.run_fit_button.clicked.connect(self.run_fit)
        
        # =========================
        # DISPLAY OPTIONS
        # =========================
        self.cb_show_all = QCheckBox("Display all graphs")
        self.cb_show_all.setChecked(True)  # default ON or OFF, your choice
        
        fit_layout.addWidget(self.cb_show_all)

        # =========================
        # RESULTS DISPLAY
        # =========================
        self.fit_results = QLabel("Fit results will appear here.")
        
        fit_layout.addWidget(self.fit_results)
        
        # =========================
        # PLOT AREA (REAL FIGURE)
        # =========================
        
        
        #self.tabs.addTab(self.tab_model_fit, "Model Fit")
        
        
        
        # -------------------------
        # TAB 3: SAVING FORMAT
        # -------------------------
        self.tab_saving_format = QWidget()
        save_layout = QVBoxLayout()
        
        save_layout.addWidget(QLabel("Select saving format:"))
        
        self.save_format_box = QComboBox()
        self.save_format_box.addItems([
            "3D datasets",
            "Random datasets"
            ])
        self.save_format_box.setCurrentIndex(1)  # default = Random datasets
        save_layout.addWidget(self.save_format_box)
        # -------------------------
        # AXIS CHECKBOXES (R, X, Y, Z)
        # -------------------------
        save_layout.addWidget(QLabel("Select up to 2 axes:"))
        
        self.axis_checkboxes = {}
        
        self.cb_R = QCheckBox("R")
        self.cb_X = QCheckBox("X")
        self.cb_Y = QCheckBox("Y")
        self.cb_Z = QCheckBox("Z")
        self.axis_order = deque()
        
        self.axis_checkboxes = {
            "R": self.cb_R,
            "X": self.cb_X,
            "Y": self.cb_Y,
            "Z": self.cb_Z
            }
        
        # Horizontal layout for checkboxes
        axis_layout = QHBoxLayout()
        
        for cb in self.axis_checkboxes.values():
            axis_layout.addWidget(cb)
            cb.stateChanged.connect(lambda state, name=cb.text(): self.limit_axis_selection(name, state))
        
        # Add horizontal checkbox layout
        save_layout.addLayout(axis_layout)
        
        # -------------------------
        # COLUMN NUMBER INPUT
        # -------------------------
        save_layout.addWidget(QLabel("Select column number:"))
        
        self.column_number_box = QSpinBox()
        self.column_number_box.setMinimum(1)
        self.column_number_box.setMaximum(1000)
        self.column_number_box.setValue(1)
        
        save_layout.addWidget(self.column_number_box)
        
        # -------------------------
        # BUTTON BELOW CHECKBOXES
        # -------------------------
        self.convert_to_image_btn = QPushButton("Convert data to image")
        self.convert_to_image_btn.clicked.connect(self.on_convert_data_to_image)
        save_layout.addWidget(self.convert_to_image_btn)


        # Push everything to the top
        save_layout.addStretch()

        self.tab_saving_format.setLayout(save_layout)
        
        # Set layout
        self.tab_model_fit.setLayout(fit_layout)
        
        # Add tabs to widget
        self.tabs.addTab(self.tab_parameters, "Parameters")
        self.tabs.addTab(self.tab_model_fit, "Model Fit")
        self.tabs.addTab(self.tab_saving_format, "Saving Format")

        # IMPORTANT: default tab = Model Fit (index 1)
        self.tabs.setCurrentIndex(1)

        main_layout.addWidget(self.tabs)
        

        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        main_layout.addWidget(close_button)
        self.update_model_ui()

    def get_selected_model(self):
        return self.model_box.currentText()
    
    def closeEvent(self, event):
        self.state["mode"] = self.mode_combo.currentText()
        
        self.state["n"] = self.cb_n.isChecked()
        self.state["k"] = self.cb_k.isChecked()
        self.state["alpha"] = self.cb_alpha.isChecked()
        self.state["eps_r"] = self.cb_eps_r.isChecked()
        self.state["eps_i"] = self.cb_eps_i.isChecked()
        self.state["cond_r"] = self.cb_cond_r.isChecked()
        self.state["cond_i"] = self.cb_cond_i.isChecked()
        
        event.accept()
        
    def run_drude_fit(self):

        try:
            
            # =========================
            # GET FREQUENCY RANGE
            # =========================
            fmin = float(self.freq_min.text())
            fmax = float(self.freq_max.text())
            
            # =========================
            # GET INITIAL GUESSES
            # =========================
            sigma0_guess = float(self.guess_sigma0.text())
            tau_guess = float(self.guess_tau.text())
            
            # =========================
            # GET DATA FROM PARENT GUI
            # =========================
            freq, n, k, alpha, e_r, e_i, cond_r, cond_i = self.parent().fullparameters
            
            results = []
            for i in range(cond_r.shape[0]):
            
                sigma = cond_r[i] + 1j * cond_i[i]
                
                mask = (freq[i] >= fmin) & (freq[i] <= fmax)
                
                freq_fit = freq[i][mask]
                sigma_fit = sigma[mask]
                
                if self.fit_target_box.currentText() == "Both":
                    sigma0_fit, tau_fit = fit_model_drude(
                        freq_fit,
                        sigma_fit,
                        p0=[sigma0_guess, tau_guess]
                        )
                elif self.fit_target_box.currentText() == "Conductivity Real":
                    # Call the real-only fitting function we just created
                    sigma0_fit, tau_fit = fit_model_drude_real_only(
                        freq_fit,
                        sigma_fit,
                        p0=[sigma0_guess, tau_guess]
                        )
                
                elif self.fit_target_box.currentText() == "Conductivity Imag":
                    # Call the real-only fitting function we just created
                    sigma0_fit, tau_fit = fit_model_drude_imag_only(
                        freq_fit,
                        sigma_fit,
                        p0=[sigma0_guess, tau_guess]
                        )
                
                results.append((sigma0_fit, tau_fit))
                
            text = ""
        
            for i, (sigma0_fit, tau_fit) in enumerate(results):
                
                text += (
                    f"Trace {i+1}\n"
                    f"σ₀ = {sigma0_fit:.3e} S/m\n"
                    f"τ = {tau_fit:.3e} s\n\n"
                    )
                
                self.fit_results.setText(text)
            


            # =========================
            # PLOT ALL TRACES IN SEPARATE POP-UPS
            # =========================
            # Keep track of window instances so Python's garbage collector doesn't destroy them
            if not hasattr(self, 'pop_out_windows'):
                self.pop_out_windows = []
            
            if self.cb_show_all.isChecked():
                indices = range(len(results))
            else:
                indices = []   # or current selected trace if you want later
                
            for i in indices:
                sigma0_fit, tau_fit = results[i]
                sigma = cond_r[i] + 1j * cond_i[i]
                
                mask = (freq[i] >= fmin) & (freq[i] <= fmax)
                freq_fit = freq[i][mask]
                sigma_exp = sigma[mask]
                
                sigma_fit = drude(freq_fit, sigma0_fit, tau_fit)
                
                # Create a completely new, independent window instance for this trace
                win = FitPlotWindow()
                win.setWindowTitle(f"Fit Plot - Trace {i+1}")
                win.plot(freq_fit, sigma_exp, sigma_fit)
                win.show()
                win.raise_()
                
                # Save the reference so the window stays open
                self.pop_out_windows.append(win)
                
            
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Results",
                "",
                "Text Files (*.txt);;All Files (*)"
                )
            # -------------------------
            # extract columns WITHOUT changing your results structure
            # -------------------------
            sigma0, tau = zip(*results)
            
            sigma0 = np.array(sigma0)
            tau = np.array(tau)
            
            names = np.array(self.parent().name_list)
            #names = np.array(self.name_list)
            
            # -------------------------
            # MODE SWITCH (you will define this later)
            # -------------------------
            mode = self.save_format_box.currentText()
            headers = self.parent().header_list
            
            if mode == "Random datasets":
                data = np.column_stack([names, sigma0, tau])
                header = "file_name\tsigma0\ttau"
            
            elif mode == "3D datasets":

                selected_axes = list(self.axis_order)
                
                if len(selected_axes) != 2:
                    raise ValueError("Please select exactly 2 axes for 3D datasets")
                    
                axis1, axis2 = selected_axes

                col1 = np.array([h.get(axis1, np.nan) for h in headers])
                col2 = np.array([h.get(axis2, np.nan) for h in headers])
                print(col1)
                
                
                data = np.column_stack([col1, col2, sigma0, tau])
                header = f"{selected_axes[0]}\t{selected_axes[1]}\tsigma0\ttau"
                
                
            """# Convert everything into strings for safe saving
            data = np.column_stack([
                names,
                sigma0,
                tau
                ])
            
            header = "file_name\tsigma0\ttau"
            """
            np.savetxt(
                file_path,
                data,
                fmt="%s",          # IMPORTANT: allows strings + numbers
                delimiter="\t",
                header=header,
                comments=""
                )
            
            
            if not file_path:
                return
            
                
        except Exception as e:
            self.fit_results.setText(f"Fit failed:\n{e}")
    
    def run_drude_smith_fit(self):
        
        try:
            
            # =========================
            # GET FREQUENCY RANGE
            # =========================
            fmin = float(self.freq_min.text())
            fmax = float(self.freq_max.text())
            
            # =========================
            # GET INITIAL GUESSES
            # =========================
            sigma0_guess = float(self.guess_sigma0.text())
            tau_guess = float(self.guess_tau.text())
            c1_guess = float(self.guess_c1.text())   # <-- NEW
            
            # =========================
            # GET DATA FROM PARENT GUI
            # =========================
            freq, n, k, alpha, e_r, e_i, cond_r, cond_i = self.parent().fullparameters
            
            results = []
            
            for i in range(cond_r.shape[0]):
                
                sigma = cond_r[i] + 1j * cond_i[i]
                
                mask = (freq[i] >= fmin) & (freq[i] <= fmax)
                
                freq_fit = freq[i][mask]
                sigma_fit = sigma[mask]
                
                # Make sure you have extracted c1_guess from your QLineEdit above this block:
                # c1_guess = float(self.guess_c1.text())

                if self.fit_target_box.currentText() == "Both":
                    sigma0_fit, tau_fit, c1_fit = fit_model_drude_smith(
                        freq_fit,
                        sigma_fit,
                        p0=[sigma0_guess, tau_guess, c1_guess]
                    )
                    
                elif self.fit_target_box.currentText() == "Conductivity Real":
                    sigma0_fit, tau_fit, c1_fit = fit_model_drude_smith_real_only(
                        freq_fit,
                        sigma_fit,
                        p0=[sigma0_guess, tau_guess, c1_guess]
                    )
                
                elif self.fit_target_box.currentText() == "Conductivity Imag":
                    sigma0_fit, tau_fit, c1_fit = fit_model_drude_smith_imag_only(
                        freq_fit,
                        sigma_fit,
                        p0=[sigma0_guess, tau_guess, c1_guess]
                    )
                
                results.append((sigma0_fit, tau_fit, c1_fit))
            
            #    
            text = ""
                
            for i, (sigma0_fit, tau_fit, c1_fit) in enumerate(results):
            
                text += (
                    f"Trace {i+1}\n"
                    f"σ₀ = {sigma0_fit:.3e} S/m\n"
                    f"τ = {tau_fit:.3e} s\n"
                    f"c₁ = {c1_fit:.3f}\n\n"
                    )
                    
                self.fit_results.setText(text)
        
            # =========================
            # PLOT ALL TRACES IN SEPARATE POP-UPS
            # =========================
            if not hasattr(self, 'pop_out_windows'):
                self.pop_out_windows = []
                
            if self.cb_show_all.isChecked():
                indices = range(len(results))
            else:
                indices = [0]   # or current selected trace if you want later
                
            for i in indices:
                sigma0_fit, tau_fit, c1_fit = results[i]
                sigma = cond_r[i] + 1j * cond_i[i]
                
                mask = (freq[i] >= fmin) & (freq[i] <= fmax)
                freq_fit = freq[i][mask]
                sigma_exp = sigma[mask]
                
                # Swap this with your actual drude_smith function definition
                sigma_fit = drude_smith(freq_fit, sigma0_fit, tau_fit, c1_fit) 
                
                win = FitPlotWindow()
                win.setWindowTitle(f"Fit Plot - Trace {i+1}")
                win.plot(freq_fit, sigma_exp, sigma_fit)
                win.show()
                win.raise_()
                
                self.pop_out_windows.append(win)
                
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Results",
                "",
                "Text Files (*.txt);;All Files (*)"
                )
            # -------------------------
            # extract columns WITHOUT changing your results structure
            # -------------------------
            sigma0, tau, c1 = zip(*results)
            mode = self.save_format_box.currentText()
            
            sigma0 = np.array(sigma0)
            tau = np.array(tau)
            c1 = np.array(c1)
            
            names = np.array(self.parent().name_list)
            headers = self.parent().header_list
            
            if mode == "Random datasets":
                data = np.column_stack([names, sigma0, tau, c1])
                header = "file_name\tsigma0\ttau\tc1"
            
            elif mode == "3D datasets":

                selected_axes = list(self.axis_order)
                
                if len(selected_axes) != 2:
                    raise ValueError("Please select exactly 2 axes for 3D datasets")
                    
                axis1, axis2 = selected_axes
                
                col1 = np.array([h.get(axis1, np.nan) for h in headers])
                col2 = np.array([h.get(axis2, np.nan) for h in headers])
                
                data = np.column_stack([col1, col2, sigma0, tau, c1])
                header = f"{axis1}\t{axis2}\tsigma0\ttau\tc1"
            
            np.savetxt(
                file_path,
                data,
                fmt="%s",          # IMPORTANT: allows strings + numbers
                delimiter="\t",
                header=header,
                comments=""
                )
            
            
            if not file_path:
                return
            
        except Exception as e:
            self.fit_results.setText(f"Fit failed:\n{e}")
    
    def run_cole_drude_fit(self):
        pass
    
    def run_fit(self):
        model = self.model_box.currentText()
        
        if model == "Drude":
            self.run_drude_fit()
        elif model == "Drude_smith":
            self.run_drude_smith_fit()
        elif model == "Cole_drude":
            self.run_cole_drude_fit()
            
    def update_model_ui(self):
        model = self.model_box.currentText()
        
        if model == "Drude_smith":
            self.c1_row_label.show()
            self.guess_c1.show()
        else:
            self.c1_row_label.hide()
            self.guess_c1.hide()
            
    def limit_axis_selection(self, name, state):
        cb = self.axis_checkboxes[name]
        
        # If checked, record it
        if cb.isChecked():
            if name in self.axis_order:
                self.axis_order.remove(name)
            self.axis_order.append(name)

        # If more than 2 selected → remove oldest
        if len(self.axis_order) > 2:
            oldest = self.axis_order.popleft()
            
            old_cb = self.axis_checkboxes[oldest]
            old_cb.blockSignals(True)
            old_cb.setChecked(False)
            old_cb.blockSignals(False)
    
    def on_convert_data_to_image2(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select data file",
            "",
            "All Files (*.*)"
            )
        
        # User cancelled
        if not file_path:
            return
        

        
        print(f"Selected file: {file_path}")
        
        
    def on_convert_data_to_image(self):
        

    

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select data file",
            "",
            "All Files (*.*)"
            )
        
        # User cancelled
        if not file_path:
            return
        
        # =========================
        # LOAD DATA
        # =========================
        data = np.loadtxt(file_path, skiprows=1)
        
        # First 2 columns = coordinates
        x = data[:, 0]
        y = data[:, 1]
        
        # User-selected column = color axis
        column_number = self.column_number_box.value()
        
        # Convert to zero-based indexing
        z = data[:, column_number - 1]
        
        # =========================
        # CREATE GRID
        # =========================
        x_unique = np.unique(x)
        y_unique = np.unique(y)
        
        X, Y = np.meshgrid(x_unique, y_unique)
        
        Z = np.full_like(X, np.nan, dtype=float)
        
        # Fill grid
        for xi, yi, zi in zip(x, y, z):
            
            x_idx = np.where(x_unique == xi)[0][0]
            y_idx = np.where(y_unique == yi)[0][0]
            
            Z[y_idx, x_idx] = zi
            
        # =========================
        # PLOT CONTOUR
        # =========================
        plt.figure(figsize=(6, 5))
        
        contour = plt.contourf(X, Y, Z, levels=100)
            
        plt.xlabel("Column 1")
        plt.ylabel("Column 2")
        
        plt.colorbar(contour, label=f"Column {column_number}")
        
        plt.tight_layout()
        plt.show()
            
        # =========================
        # SAVE PNG
        # =========================
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save contour image",
            "",
            "PNG Files (*.png)"
            )
        
        if save_path:
            plt.savefig(save_path, dpi=300)
            
        plt.show()
        
    def plot_fit(self, freq, sigma_exp, sigma_fit):
        self.fit_window.plot(freq, sigma_exp, sigma_fit)
        self.fit_window.show()
        self.fit_window.raise_()
        
class FitPlotWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Fit Plot")
        self.resize(800, 600)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        layout.addWidget(self.canvas)

        self.ax = self.figure.add_subplot(111)

    def plot(self, freq, sigma_exp, sigma_fit):
        self.ax.clear()

        self.ax.scatter(freq, sigma_exp.real, s=10, label="Re(Exp)", alpha=0.7)
        self.ax.scatter(freq, sigma_exp.imag, s=10, label="Im(Exp)", alpha=0.7)

        self.ax.plot(freq, sigma_fit.real, label="Re(Fit)")
        self.ax.plot(freq, sigma_fit.imag, label="Im(Fit)")

        self.ax.set_xlabel("Frequency (THz)")
        self.ax.set_ylabel("Conductivity")
        self.ax.legend()
        self.ax.grid(True)

        self.canvas.draw()
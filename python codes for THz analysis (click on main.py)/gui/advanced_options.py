# -*- coding: utf-8 -*-
"""
Created on Fri May 22 23:32:28 2026

@author: bryan_54tjivr
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel,
    QTabWidget, QWidget,
    QComboBox, QPushButton, QFormLayout, QCheckBox
)


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
        self.tab_model_fit = QWidget()
        fit_layout = QFormLayout()

        fit_layout.addRow(QLabel("Select conductivity model:"))

        self.model_box = QComboBox()
        self.model_box.addItems([
            "Drude",
            "Drude_smith",
            "Cole_drude"
        ])

        fit_layout.addRow(self.model_box)

        self.tab_model_fit.setLayout(fit_layout)

        # Add tabs to widget
        self.tabs.addTab(self.tab_parameters, "Parameters")
        self.tabs.addTab(self.tab_model_fit, "Model Fit")

        # IMPORTANT: default tab = Model Fit (index 1)
        self.tabs.setCurrentIndex(1)

        main_layout.addWidget(self.tabs)

        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        main_layout.addWidget(close_button)

    def get_selected_model(self):
        return self.model_box.currentText()
    
    def closeEvent(self, event):
        self.state["n"] = self.cb_n.isChecked()
        self.state["k"] = self.cb_k.isChecked()
        self.state["alpha"] = self.cb_alpha.isChecked()
        self.state["eps_r"] = self.cb_eps_r.isChecked()
        self.state["eps_i"] = self.cb_eps_i.isChecked()
        self.state["cond_r"] = self.cb_cond_r.isChecked()
        self.state["cond_i"] = self.cb_cond_i.isChecked()
        
        event.accept()
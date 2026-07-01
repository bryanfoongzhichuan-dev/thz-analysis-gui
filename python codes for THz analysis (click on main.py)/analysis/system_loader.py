import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QPushButton, QFileDialog, QLabel, QInputDialog, QMessageBox
)
import pandas as pd

def load_melo_data(fnames, parse_header_func):
    time_list = []
    signal_list = []
    name_list = []
    header_list = []

    for fname in fnames:
        with open(fname, "r") as f:
            lines = f.readlines()

        first_line = lines[0].strip()

        if any(c.isalpha() for c in first_line):
            data_lines = lines[1:]
        else:
            data_lines = lines

        data = []
        for line in data_lines:
            parts = line.strip().split()
            if len(parts) >= 2:
                try:
                    data.append([float(parts[0]), float(parts[1])])
                except:
                    pass

        data = np.array(data)

        if data.size == 0:
            continue

        time_list.append(data[:, 0])
        signal_list.append(data[:, 1])

        if first_line.startswith("Stage_Position"):
            header_dict = parse_header_func(first_line)
        else:
            header_dict = {"R": np.nan, "X": np.nan, "Y": np.nan, "Z": np.nan}

        header_list.append(header_dict)
        name_list.append(fname)

    return time_list, signal_list, name_list, header_list




def load_startera_data(fnames, parent=None):
    """
    Startera format:
    x, y, signal(t1...tn)
    Each row = one spatial point
    """

    fname = fnames[0]

    # =========================
    # LOAD SPATIAL + SIGNAL DATA
    # =========================
    data = np.loadtxt(fname)

    x_s = data[:, 0]
    y_s = data[:, 1]
    signal_s = data[:, 9:]

    # =========================
    # LOAD TIME AXIS (ROBUST)
    # =========================
    time_file, _ = QFileDialog.getOpenFileName(
        parent,
        "Load Time Axis File",
        "",
        "All Files (*.*);;Excel Files (*.xlsx);;CSV Files (*.csv);;Text Files (*.txt)"
    )

    if not time_file:
        raise ValueError("Time axis file is required for Startera")

    # ---- Excel ----
    if time_file.endswith(".xlsx"):
        df = pd.read_excel(time_file, engine="openpyxl")

    # ---- CSV / TXT (handles headers automatically) ----
    else:
        df = pd.read_csv(time_file, sep=None, engine="python")

    # =========================
    # CLEAN DATA (removes headers safely)
    # =========================
    df = df.apply(pd.to_numeric, errors="coerce").dropna()

    if df.shape[0] == 0:
        raise ValueError("Time axis file contains no valid numeric data")

    time_s = df.iloc[:, 0].to_numpy()
    # Duplicate time axis for every signal trace
    time_s = np.tile(time_s, (signal_s.shape[0], 1))

    # =========================
    # VALIDATION
    # =========================
    if signal_s.shape != time_s.shape:
        raise ValueError(
            f"Mismatch: time shape {time_s.shape} "
            f"vs signal shape {signal_s.shape}"
            )

    # =========================
    # OUTPUT
    # =========================
    name_list = [fname]

    return time_s, signal_s, x_s, y_s, name_list
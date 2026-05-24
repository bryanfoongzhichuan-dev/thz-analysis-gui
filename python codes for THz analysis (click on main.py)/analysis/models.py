# -*- coding: utf-8 -*-
"""
Created on Sun May 24 08:39:39 2026

@author: bryan_54tjivr
"""

import numpy as np
from scipy.optimize import curve_fit

def drude(freq_thz, sigma0, tau):
    """
    Drude complex conductivity model

    Parameters
    ----------
    freq_thz : array
        Frequency in THz
    sigma0 : float
        DC conductivity
    tau : float
        Scattering time (seconds)

    Returns
    -------
    sigma : complex array
    """

    omega = 2 * np.pi * freq_thz * 1e12  # THz → rad/s

    return sigma0 / (1 - 1j * omega * tau)



def fit_model(freq_thz, sigma_exp, p0):
    """
    Fit Drude model to complex conductivity data
    """

    def model(freq, sigma0, tau):
        sigma = drude(freq, sigma0, tau)
        return np.concatenate([sigma.real, sigma.imag])

    ydata = np.concatenate([sigma_exp.real, sigma_exp.imag])

    popt, pcov = curve_fit(
        model,
        freq_thz,
        ydata,
        p0
    )
    #p0 is initial guess

    sigma0, tau = popt
    return sigma0, tau

if __name__ == "__main__":
    import matplotlib.pyplot as plt

    freq = np.linspace(0.1, 3, 200)

    sigma0_true = 1000
    tau_true = 2e-13

    sigma = drude(freq, sigma0_true, tau_true)

    plt.plot(freq, sigma.real, label="Re(σ)")
    plt.plot(freq, sigma.imag, label="Im(σ)")
    plt.legend()
    plt.xlabel("Frequency (THz)")
    plt.show()

    #sigma is the model, freq is the THz
    sigma0_fit, tau_fit = fit_model(freq, sigma)

    print("Fitted sigma0 =", sigma0_fit)
    print("Fitted tau =", tau_fit)
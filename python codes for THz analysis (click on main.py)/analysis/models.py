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



def fit_model_drude(freq_thz, sigma_exp, p0):
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




def drude_smith(freq_thz, sigma0, tau, c):
    """
    Drude–Smith complex conductivity model

    Parameters
    ----------
    freq_thz : array
        Frequency in THz
    sigma0 : float
        DC conductivity
    tau : float
        Scattering time (seconds)
    c : float
        Backscattering / memory parameter (-1 to 0 typically)

    Returns
    -------
    sigma : complex array
    """

    omega = 2 * np.pi * freq_thz * 1e12  # THz → rad/s

    denom = 1 - 1j * omega * tau

    sigma = (sigma0 / denom) * (1 + c / denom)

    return sigma

def fit_model_drude_smith(freq_thz, sigma_exp, p0):
    """
    Fit Drude-Smith model to complex conductivity data
    """

    def model(freq, sigma0, tau, c1):
        sigma = drude_smith(freq, sigma0, tau, c1)
        return np.concatenate([sigma.real, sigma.imag])

    ydata = np.concatenate([sigma_exp.real, sigma_exp.imag])

    popt, pcov = curve_fit(
        model,
        freq_thz,
        ydata,
        p0=p0
    )

    sigma0, tau, c1 = popt
    return sigma0, tau, c1


def cole_drude_model(ep_inf, delta_ep, tau, alpha,
                     sigma_dc, tau_drude, nu):

    ep0 = 8.8541878176e-12  # vacuum permittivity
    omega = 2 * np.pi * nu

    # =========================
    # Cole–Cole dielectric part
    # =========================
    ep_cole = ep_inf + delta_ep / (1 + 1j * omega * tau)**(1 - alpha)

    # =========================
    # Drude conductivity part
    # =========================
    sigma = sigma_dc / (1 + 1j * omega * tau_drude)
    ep_drude = 1j * sigma / (omega * ep0)

    # =========================
    # Combined permittivity
    # =========================
    ep = ep_cole - ep_drude

    ep_re = np.real(ep)
    ep_im = np.imag(ep)

    # =========================
    # Convert permittivity → refractive index
    # =========================
    n_re = np.sqrt((ep_re + np.sqrt(ep_re**2 + ep_im**2)) / 2)
    n_im = -np.sqrt((-ep_re + np.sqrt(ep_re**2 + ep_im**2)) / 2)

    return n_re, n_im

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
    sigma0_fit, tau_fit = fit_model_drude(freq, sigma)

    print("Fitted sigma0 =", sigma0_fit)
    print("Fitted tau =", tau_fit)
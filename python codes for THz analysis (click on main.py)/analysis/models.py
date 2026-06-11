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

def fit_model_drude_real_only(freq_thz, sigma_exp, p0):
    """
    Fit the Drude model using ONLY the real component of conductivity.
    """

    # 1. Strip away the imaginary part from the model
    def model_real(freq, sigma0, tau):
        sigma_complex = drude(freq, sigma0, tau)
        return sigma_complex.real  # <--- Only return the real array

    # 2. Extract only the real experimental data points
    ydata_real = sigma_exp.real


    print("Running Fit on Real Component Only...")
    
    popt, pcov = curve_fit(
        model_real,
        freq_thz,
        ydata_real,  # Matching real model output to real data
        p0=p0,
    )

    sigma0_fit, tau_fit = popt

    # =========================================================
    # MAINTENANCE LOG (Evaluating Real-Only Performance)
    # =========================================================
    y_fit = model_real(freq_thz, sigma0_fit, tau_fit)
    rmse_real = np.sqrt(np.mean((ydata_real - y_fit)**2))
    
    print("\n========= REAL-ONLY MAINTENANCE LOG =========")
    print(f"Optimized σ₀:               {sigma0_fit:.3e} S/m")
    print(f"Optimized τ:                {tau_fit:.3e} s")
    print(f"Real-Component RMSE:        {rmse_real:.5f} S/m")
    print("===============================================\n")

    return sigma0_fit, tau_fit

def fit_model_drude_imag_only(freq_thz, sigma_exp, p0):
    """
    Fit the Drude model using ONLY the imaginary component of conductivity.
    """

    # 1. Strip away the real part from the model
    def model_imag(freq, sigma0, tau):
        sigma_complex = drude(freq, sigma0, tau)
        return sigma_complex.imag  # <--- Only return the imaginary array

    # 2. Extract only the imaginary experimental data points
    ydata_imag = sigma_exp.imag

    # 3. Restrict bounds to physical values
    # sigma0 must be positive (> 0)
    # tau must be positive and realistically capped (e.g., 1e-11 s)
    bounds = ([0, 0], [np.inf, 1e-11])

    print("Running Bounded Fit on Imaginary Component Only...")
    
    popt, pcov = curve_fit(
        model_imag,
        freq_thz,
        ydata_imag,  # Matching imaginary model output to imaginary data
        p0=p0
    )

    sigma0_fit, tau_fit = popt

    # =========================================================
    # MAINTENANCE LOG (Evaluating Imaginary-Only Performance)
    # =========================================================
    y_fit = model_imag(freq_thz, sigma0_fit, tau_fit)
    rmse_imag = np.sqrt(np.mean((ydata_imag - y_fit)**2))
    
    print("\n========= IMAGINARY-ONLY MAINTENANCE LOG =========")
    print(f"Optimized σ₀:               {sigma0_fit:.3e} S/m")
    print(f"Optimized τ:                {tau_fit:.3e} s")
    print(f"Imaginary-Component RMSE:   {rmse_imag:.5f} S/m")
    print("===================================================\n")

    return sigma0_fit, tau_fit

def fit_model_drude(freq_thz, sigma_exp, p0):
    """
    Fit Drude model to complex conductivity data
    """

    def model(freq, sigma0, tau):
        sigma = drude(freq, sigma0, tau)
        return np.concatenate([sigma.real, sigma.imag])

    ydata = np.concatenate([sigma_exp.real, sigma_exp.imag])
    #print("its working")
    popt, pcov = curve_fit(
        model,
        freq_thz,
        ydata,
        p0         #after this delete
    )
    
    #p0 is initial guess
    sigma0, tau = popt
    
    # =========================================================
    # CALCULATE AND PRINT FITTING ERRORS (RESIDUALS)
    # =========================================================
    # 1. Get the predicted y-values using the optimized parameters
    y_fit = model(freq_thz, sigma0, tau)
    
    # 2. Calculate raw residuals (differences)
    residuals = ydata - y_fit
    
    # 3. Calculate distinct error metrics
    ss_res = np.sum(residuals**2)             # Residual Sum of Squares (Absolute error)
    mse = np.mean(residuals**2)               # Mean Squared Error
    rmse = np.sqrt(mse)                       # Root Mean Squared Error (in S/m units)
    
    # 4. Print maintenance logs
    print("\n================ MAINTENANCE LOG ================")
    print(f"Residual Sum of Squares (SS_res): {ss_res:.5e}")
    print(f"Mean Squared Error (MSE):         {mse:.5e}")
    print(f"Root Mean Squared Error (RMSE):    {rmse:.5f} S/m")
    print("=================================================\n")


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

def fit_model_drude_smith_real_only(freq_thz, sigma_exp, p0):
    """
    Fit Drude-Smith model using ONLY the real component of conductivity.
    """
    def model_real(freq, sigma0, tau, c1):
        sigma_complex = drude_smith(freq, sigma0, tau, c1)
        return sigma_complex.real

    ydata_real = sigma_exp.real

    popt, pcov = curve_fit(
        model_real,
        freq_thz,
        ydata_real,
        p0=p0
    )

    sigma0, tau, c1 = popt
    
    # Optional Maintenance Log
    y_fit = model_real(freq_thz, sigma0, tau, c1)
    rmse = np.sqrt(np.mean((ydata_real - y_fit)**2))
    print(f"\n--- DRUDE-SMITH REAL-ONLY RMSE: {rmse:.5f} S/m ---")
    
    return sigma0, tau, c1

def fit_model_drude_smith_imag_only(freq_thz, sigma_exp, p0):
    """
    Fit Drude-Smith model using ONLY the imaginary component of conductivity.
    """
    def model_imag(freq, sigma0, tau, c1):
        sigma_complex = drude_smith(freq, sigma0, tau, c1)
        return sigma_complex.imag

    ydata_imag = sigma_exp.imag

    popt, pcov = curve_fit(
        model_imag,
        freq_thz,
        ydata_imag,
        p0=p0
    )

    sigma0, tau, c1 = popt
    
    # Optional Maintenance Log
    y_fit = model_imag(freq_thz, sigma0, tau, c1)
    rmse = np.sqrt(np.mean((ydata_imag - y_fit)**2))
    print(f"\n--- DRUDE-SMITH IMAG-ONLY RMSE: {rmse:.5f} S/m ---")
    
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
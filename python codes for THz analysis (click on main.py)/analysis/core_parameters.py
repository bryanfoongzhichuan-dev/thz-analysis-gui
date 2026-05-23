# -*- coding: utf-8 -*-
"""
Created on Fri Aug 29 21:45:38 2025

@author: bryan_foong
"""
import numpy as np

def fft(time, signal):
    if time.ndim == 1:
        y = np.fft.rfft(signal)
        freq = np.fft.rfftfreq(len(time), d=(time[-1] - time[0])/(len(time)-1))
        p1 = np.angle(y)
        p2 = np.unwrap(p1)
        y = np.atleast_2d(y)     # ensures 2D
        p2 = np.atleast_2d(p2)   # ensures 2D
        freq = np.atleast_2d(freq)
    else:
        y_list = []; p2_list = []; freq_list = []
        for t, s in zip(time, signal):
            y_row = np.fft.rfft(s)
            f_row = np.fft.rfftfreq(len(t), d=(t[-1]-t[0])/(len(t)-1))
            y_list.append(y_row); p2_list.append(np.unwrap(np.angle(y_row))); freq_list.append(f_row)
        y, p2, freq = np.array(y_list), np.array(p2_list), np.array(freq_list)
        
    return (y,freq, p2)

def n_f(freq, p_s, p_b, t):
    if freq.ndim == 1:
        c0_wd = c0_wd_f(freq, t)
        dp = np.abs(p_s - p_b)
        n = dp*c0_wd+1
        n = np.atleast_2d(n)
    else:
        n = np.array([n_f(f_row, p_s[i], p_b, t)[0] for i, f_row in enumerate(freq)])
    return n

def k_f(freq, m_s, m_b, n, t):
    # Ensure 2D inputs
    freq = np.atleast_2d(freq)
    m_s = np.atleast_2d(m_s)
    m_b = np.atleast_2d(m_b)
    n = np.atleast_2d(n)
    
    # Compute k for each row if 2D, else elementwise
    if freq.shape[0] == 1:
        c0_wd = c0_wd_f(freq, t)
        k = c0_wd * np.log(4 * n / ((m_s / m_b) * (n + 1)**2))
        k = np.atleast_2d(k)
    else:
        k = np.array([k_f(freq[i], m_s[i], m_b, n[i], t)[0] for i in range(freq.shape[0])])
    return k

def a_f(freq, k):
    freq = np.atleast_2d(freq)
    k = np.atleast_2d(k)
    
    if freq.shape[0] == 1:
        a = k * 4 * np.pi * freq * 1e12 / 3e8
        a = np.atleast_2d(a)
    else:
        a = np.array([a_f(freq[i], k[i])[0] for i in range(freq.shape[0])])
    return a

def dielec(freq, n, a):
    freq = np.atleast_2d(freq)
    n = np.atleast_2d(n)
    a = np.atleast_2d(a)
    
    if freq.shape[0] == 1:
        e_r = n**2 - (3e8 * a / (4 * np.pi * freq * 1e12))**2
        e_i = 3e8 * n * a / (2 * np.pi * freq * 1e12)
        e_r = np.atleast_2d(e_r)
        e_i = np.atleast_2d(e_i)
    else:
        e_r = np.array([dielec(freq[i], n[i], a[i])[0][0] for i in range(freq.shape[0])])
        e_i = np.array([dielec(freq[i], n[i], a[i])[1][0] for i in range(freq.shape[0])])
    return e_r, e_i

def c0_wd_f(freq, t):
    c0_wd = 3e8/(2*np.pi*freq*1e12*t*1e-3)
    return c0_wd


eps0 = 8.854e-12  # vacuum permittivity
def conductivity(freq, eps_r, eps_i):
    """
    Compute complex conductivity from dielectric function.

    freq: THz (your current system)
    eps_r, eps_i: dielectric function

    returns:
        sigma1, sigma2
    """

    freq = np.atleast_2d(freq)

    omega = 2 * np.pi * freq * 1e12  # THz → Hz

    eps = eps_r + 1j * eps_i

    sigma = 1j * eps0 * omega * (eps - 1)

    return np.real(sigma), np.imag(sigma)
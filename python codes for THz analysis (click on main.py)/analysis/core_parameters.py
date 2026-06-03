# -*- coding: utf-8 -*-
"""
Created on Fri Aug 29 21:45:38 2025

@author: bryan_foong
"""
import numpy as np
import math

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

def n_transmission(freq, p_s, p_b, t):
    if freq.ndim == 1:
        c0_wd = c0_wd_f(freq, t)
        dp = np.abs(p_s - p_b)
        n = dp*c0_wd+1
        n = np.atleast_2d(n)
    else:
        n = np.array([n_transmission(f_row, p_s[i], p_b, t)[0] for i, f_row in enumerate(freq)])
    return n

def k_transmission(freq, m_s, m_b, n, t):
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
        k = np.array([k_transmission(freq[i], m_s[i], m_b, n[i], t)[0] for i in range(freq.shape[0])])
    return k

def a_transmission(freq, k):
    freq = np.atleast_2d(freq)
    k = np.atleast_2d(k)
    
    if freq.shape[0] == 1:
        a = k * 4 * np.pi * freq * 1e12 / 3e8
        a = np.atleast_2d(a)
    else:
        a = np.array([a_transmission(freq[i], k[i])[0] for i in range(freq.shape[0])])
    return a

def dielec_transmission(freq, n, a):
    freq = np.atleast_2d(freq)
    n = np.atleast_2d(n)
    a = np.atleast_2d(a)
    
    if freq.shape[0] == 1:
        e_r = n**2 - (3e8 * a / (4 * np.pi * freq * 1e12))**2
        e_i = 3e8 * n * a / (2 * np.pi * freq * 1e12)
        e_r = np.atleast_2d(e_r)
        e_i = np.atleast_2d(e_i)
    else:
        e_r = np.array([dielec_transmission(freq[i], n[i], a[i])[0][0] for i in range(freq.shape[0])])
        e_i = np.array([dielec_transmission(freq[i], n[i], a[i])[1][0] for i in range(freq.shape[0])])
    return e_r, e_i

def c0_wd_f(freq, t):
    c0_wd = 3e8/(2*np.pi*freq*1e12*t*1e-3)
    return c0_wd

#reflection datas

def calculate_fresnel_phase(n, theta):
    """
    Phase-based reflection model (simplified scalar approximation).
    You can replace this with full complex Fresnel later.
    """
    sin0 = np.sqrt(1 - (np.sin(theta) / n) ** 2)
    rs = (np.cos(theta) - n * sin0) / (np.cos(theta) + n * sin0)
    rp = (sin0 - n * np.cos(theta)) / (sin0 + n * np.cos(theta))

    r = 0.5 * (rs + rp)
    return np.angle(r)


def n_reflection(freq, p_s, p_b, angle):
    """
    Invert phase difference to refractive index in reflection mode.
    """

    theta = math.radians(angle)

    # force numpy arrays
    p_s = np.array(p_s)
    p_b = np.array(p_b)

    # compute phase difference
    phase_diff = np.unwrap(p_s - p_b)

    # ensure 1D
    phase_diff = np.ravel(phase_diff)

    n_out = np.zeros_like(phase_diff, dtype=float)

    for i, dphi in enumerate(phase_diff):

        low, high = 1.0, 100.0
        guess_n = 0.5 * (low + high)

        target = float(dphi)   #  FORCE SCALAR

        for _ in range(100):
            model_phi = float(calculate_fresnel_phase(guess_n, theta))

            if model_phi > target:
                high = guess_n
            else:
                low = guess_n

            guess_n = 0.5 * (low + high)

        n_out[i] = guess_n

    return n_out

def fresnel_reflection_magnitude(n, k, theta):
    """
    Compute |r| for s/p averaged reflection (simplified scalar model).
    """

    nc = n + 1j * k
    cos_t = np.cos(theta)

    # approximate transmission angle
    sin_t = np.sin(theta)
    sin_t2 = sin_t / nc

    # avoid invalid sqrt
    sin_t2 = np.clip(np.real(sin_t2), -1, 1)
    cos_t2 = np.sqrt(1 - sin_t2**2)

    rs = (cos_t - nc * cos_t2) / (cos_t + nc * cos_t2)
    rp = (nc * cos_t - cos_t2) / (nc * cos_t + cos_t2)

    r = 0.5 * (rs + rp)
    return np.abs(r)


def k_reflection(freq, n, amp_s, amp_b, angle):
    theta = math.radians(angle)

    amp_s = np.ravel(np.array(amp_s))
    amp_b = np.ravel(np.array(amp_b))

    amp_diff = amp_s / (amp_b + 1e-12)   # avoid divide by zero

    k_out = np.zeros_like(amp_diff, dtype=float)

    for i, target_amp in enumerate(amp_diff):

        low, high = 0.0, 10.0
        guess_k = 0.5 * (low + high)

        target = float(target_amp)   # 🔥 FORCE SCALAR

        for _ in range(100):

            model = float(fresnel_reflection_magnitude(n[i], guess_k, theta))

            if model > target:
                high = guess_k
            else:
                low = guess_k

            guess_k = 0.5 * (low + high)

        k_out[i] = guess_k

    return k_out

def alpha_reflection(freq, k):
    """
    freq: THz
    k: extinction coefficient
    returns alpha in m^-1
    """
    c = 3e8
    omega = 2 * np.pi * freq * 1e12
    return (2 * omega * k) / c


def dielec_reflection(n, k):
    """
    Returns:
        eps_r, eps_i
    """

    eps_r = n**2 - k**2
    eps_i = 2 * n * k

    return eps_r, eps_i


#universal parameter
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
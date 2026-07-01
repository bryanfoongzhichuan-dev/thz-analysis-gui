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
    if t is None:
        raise ValueError("Thickness t is required (got None)")

    return 3e8/(2*np.pi*freq*1e12*t*1e-3)

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

    theta = math.radians(angle)

    freq = np.array(freq)
    p_s = np.array(p_s)
    p_b = np.array(p_b)

    # =========================
    # SINGLE TRACE
    # =========================
    if p_s.ndim == 1:

        return _solve_n(np.unwrap(p_s - p_b), theta)

    # =========================
    # MULTI TRACE
    # =========================
    n_traces = p_s.shape[0]

    results = []

    for i in range(n_traces):

        ps_i = p_s[i]

        # 🔥 FIX: safe broadcasting rule
        if p_b.ndim == 1:
            pb_i = p_b
        elif p_b.shape[0] == 1:
            pb_i = p_b[0]
        else:
            pb_i = p_b[i]

        phase_diff = np.unwrap(ps_i - pb_i)

        results.append(_solve_n(phase_diff, theta))

    return np.array(results)


def _solve_n(phase_diff, theta):

    n_out = np.zeros_like(phase_diff, dtype=float)

    for j, dphi in enumerate(phase_diff):

        target = float(dphi)

        # -------------------------
        # search space
        # -------------------------
        n_grid = np.linspace(1.0, 20.0, 400)

        best_n = 1.0
        best_err = np.inf

        for n in n_grid:

            model_phi = calculate_fresnel_phase(n, theta)

            err = (model_phi - target) ** 2

            if err < best_err:
                best_err = err
                best_n = n

        n_out[j] = best_n

    return n_out

def fresnel_reflection_magnitude(n, k, theta):

    nc = n + 1j * k
    cos_t = np.cos(theta)

    sin_t = np.sin(theta)
    sin_t2 = sin_t / nc

    sin_t2 = np.clip(np.abs(sin_t2), 0, 1)
    cos_t2 = np.sqrt(1 - sin_t2**2)

    rs = (cos_t - nc * cos_t2) / (cos_t + nc * cos_t2)
    rp = (nc * cos_t - cos_t2) / (nc * cos_t + cos_t2)

    r = 0.5 * (rs + rp)
    return np.abs(r)


def k_reflection_single(freq, n, amp_s, amp_b, angle):

    theta = math.radians(angle)

    amp_diff = amp_s / (amp_b + 1e-12)
    amp_diff = np.ravel(amp_diff)

    k_out = np.zeros_like(amp_diff, dtype=float)

    for i, target_amp in enumerate(amp_diff):

        low, high = 0.0, 10.0
        guess_k = 0.5 * (low + high)

        target = float(target_amp)

        n_i = n if np.ndim(n) == 0 else n[i]

        for _ in range(80):

            model = float(
                fresnel_reflection_magnitude(n_i, guess_k, theta)
            )

            if model > target:
                high = guess_k
            else:
                low = guess_k

            guess_k = 0.5 * (low + high)

        k_out[i] = guess_k

    return k_out

def k_reflection(freq, n, amp_s, amp_b, angle):

    freq = np.array(freq)
    n = np.array(n)
    amp_s = np.array(amp_s)
    amp_b = np.array(amp_b)

    theta = math.radians(angle)

    n_traces = freq.shape[0]

    results = []

    for i in range(n_traces):

        n_i = n if n.ndim == 1 else n[i]

        amp_s_i = amp_s[i]

        # 🔥 KEY FIX: broadcast safely
        if amp_b.ndim == 1:
            amp_b_i = amp_b
        elif amp_b.shape[0] == 1:
            amp_b_i = amp_b[0]
        else:
            amp_b_i = amp_b[i]

        k_i = k_reflection_single(
            freq[i],
            n_i,
            amp_s_i,
            amp_b_i,
            angle
        )

        results.append(k_i)

    return np.array(results)

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

    n = np.array(n)
    k = np.array(k)

    if n.shape != k.shape:
        raise ValueError(f"Shape mismatch: n{n.shape}, k{k.shape}")

    eps_r = n**2 - k**2
    eps_i = 2 * n * k

    return eps_r, eps_i

def ensure_batch(x):
    x = np.array(x)

    if x.ndim == 1:
        return x[np.newaxis, :]   # (1, M)

    return x

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
import numpy as np
import matplotlib.pyplot as plt
from windows import RealTimeCrossSectionViewer
from PyQt5.QtWidgets import QApplication
import sys


def original_far_field(U0, wavelength, z, dx):
    """
    Original far-field diffraction (ZL-TF-ZL method).
    
    Args:
        U0: Input complex field (2D numpy array).
        wavelength: Light wavelength (µm).
        z: Propagation distance (µm).
        dx: Input pixel size (µm).
        
    Returns:
        Intensity at distance z.
    """
    N = U0.shape[0]  # Assume square input
    k = 2 * np.pi / wavelength
    
    # Calculate output pixel size (pixout)
    z_limit = N * dx**2 / wavelength
    if abs(z) < z_limit:
        raise ValueError(f"Use near-field method for z < {z_limit:.2f} µm")
    pixout = wavelength * abs(z) / (N * dx)
    
    # --- Step 1: Pre-FFT quadratic phase (α_in) ---
    x = np.arange(-N//2, N//2) * dx  # Physical coordinates
    X, Y = np.meshgrid(x, x)
    alpha_in = np.pi * dx**2 / (wavelength * z)
    U1 = U0 * np.exp(1j * alpha_in * (X**2 + Y**2))
    
    # --- Step 2: Forward FFT ---
    U1_shifted = np.fft.ifftshift(U1)
    U1_fft = np.fft.fft2(U1_shifted)
    U1_fft = np.fft.fftshift(U1_fft)
    
    # --- Step 3: Post-FFT quadratic phase (α_out) ---
    fx = np.fft.fftfreq(N, d=dx)  # Frequency grid
    FX, FY = np.meshgrid(fx, fx)
    alpha_out = np.pi * pixout**2 / (wavelength * z)
    U2 = U1_fft * np.exp(1j * alpha_out * (FX**2 + FY**2))
    
    # Return intensity
    return np.abs(U2)**2


# --- Parameters for CLEAR near-field diffraction ---
N = 1024                # Grid size
wavelength = 0.528      # µm (He-Ne)
dx = 0.25               # µm (CRITICAL: Finer than λz/D)
z = 1e7                # µm (Extremely near-field)
D = 8.0                 # µm (Aperture size)


# Create a SQUARE aperture (instead of circular)
x = np.arange(-N//2, N//2) * dx
X, Y = np.meshgrid(x, x)
aperture = (np.abs(X) <= D/2) & (np.abs(Y) <= D/2)  # Square mask
U0 = aperture.astype(np.complex64)                  # Amplitude-only input

# Compute far-field pattern
I = original_far_field(U0, wavelength, z, dx)

I_3D = np.repeat(I[np.newaxis, :, :], 1, axis=0)


app = QApplication([])




viewer = RealTimeCrossSectionViewer(I_3D)

viewer.resize(1000, 800)
viewer.show()
sys.exit(app.exec())
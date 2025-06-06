import numpy as np
import matplotlib.pyplot as plt
from windows import RealTimeCrossSectionViewer
from PyQt5.QtWidgets import QApplication
import sys

def original_near_field(U0, wavelength, z, dx):
    """
    Original near-field Fresnel diffraction (ITF-TF-ZL method).
    
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
    
    # Frequency grid (FFT-shifted)
    fx = np.fft.fftshift(np.fft.fftfreq(N, d=dx))
    FX, FY = np.meshgrid(fx, fx)
    
    # Fresnel phase factor (α_short in original code)
    alpha = -np.pi * wavelength * z / (dx**2 * N**2)
    H = np.exp(1j * alpha * (FX**2 + FY**2))
    
    # Forward FFT (with pre-shifting)
    U0_shifted = np.fft.ifftshift(U0)
    U0_fft = np.fft.fft2(U0_shifted)
    
    # Multiply by Fresnel phase
    Uz_fft = U0_fft * H
    
    # Inverse FFT (with post-shifting)
    Uz = np.fft.ifft2(Uz_fft)
    Uz = np.fft.fftshift(Uz)
    
    # Return intensity
    return np.abs(Uz)**2

# --- Parameters for CLEAR near-field diffraction ---
N = 1024                # Grid size
wavelength = 0.528      # µm (He-Ne)
dx = 0.25               # µm (CRITICAL: Finer than λz/D)
z = 8e4                # µm (Extremely near-field)
D = 8.0                 # µm (Aperture size)


# Create a SQUARE aperture (instead of circular)
x = np.arange(-N//2, N//2) * dx
X, Y = np.meshgrid(x, x)
aperture = (np.abs(X) <= D/2) & (np.abs(Y) <= D/2)  # Square mask
U0 = aperture.astype(np.complex64)                  # Amplitude-only input

# Compute diffraction
I = original_near_field(U0, wavelength, z, dx)

I_3D = np.repeat(I[np.newaxis, :, :], 1, axis=0)


app = QApplication([])




viewer = RealTimeCrossSectionViewer(I_3D)

viewer.resize(1000, 800)
viewer.show()
sys.exit(app.exec())
import numpy as np
import matplotlib.pyplot as plt
from diffraction_propagation import far_field

def angular_spectrum(U0, wavelength, z, dx):
    """
    Angular Spectrum Method with correct shifting for near-field propagation.
    """
    N = max(U0.shape)  # Assume square input
    k = 2 * np.pi / wavelength

    fx = np.fft.fftfreq(N, d=dx)
    FX, FY = np.meshgrid(fx, fx)
    F2 = FX**2 + FY**2

    kz = 2 * np.pi * np.sqrt(np.maximum(0, 1 / wavelength**2 - F2))
    H = np.exp(1j * kz * z)

    # No shift before fft2
    U0_fft = np.fft.fft2(U0)

    # Use unshifted H (corresponds to unshifted fx grid)
    Uz_fft = U0_fft * H

    Uz = np.fft.ifft2(Uz_fft)
    Uz = np.abs(Uz)**2

    return Uz

# Parameters
wavelength = 0.633       # µm
dx = 1.0                 # µm
grid_size = 300          # µm (so N = 300 if dx = 1)
z = 795                 # µm
z_ = 800
N = int(grid_size / dx)
x = np.linspace(-grid_size/2, grid_size/2, N)
X, Y = np.meshgrid(x, x)
R = np.sqrt(X**2 + Y**2)

# Circular aperture: diameter = 150 µm ⇒ radius = 75 µm
radius = 75
U0 = np.zeros((N, N), dtype=np.complex128)
U0[R <= radius] = 1.0  # Uniform illumination inside the aperture

# Propagate
intensity = angular_spectrum(U0, wavelength, z, dx)
intensity_ = far_field(U0, wavelength, z_ , dx)

# Plot
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.title("Aperture Plane (z=0)")
plt.imshow(np.abs(U0), cmap='gray', extent=[-grid_size/2, grid_size/2]*2)
plt.xlabel("x (µm)")
plt.ylabel("y (µm)")

plt.subplot(1, 2, 2)
plt.title(f"Propagated Intensity (z={z} µm)")
plt.imshow(intensity, cmap='inferno', extent=[-grid_size/2, grid_size/2]*2)
plt.xlabel("x (µm)")
plt.ylabel("y (µm)")
plt.colorbar(label='Intensity')

plt.tight_layout()
plt.show()

# Plot
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.title("Aperture Plane (z=0)")
plt.imshow(np.abs(U0), cmap='gray', extent=[-grid_size/2, grid_size/2]*2)
plt.xlabel("x (µm)")
plt.ylabel("y (µm)")

plt.subplot(1, 2, 2)
plt.title(f"Propagated Intensity (z={z} µm)")
plt.imshow(intensity_, cmap='inferno', extent=[-grid_size/2, grid_size/2]*2)
plt.xlabel("x (µm)")
plt.ylabel("y (µm)")
plt.colorbar(label='Intensity')

plt.tight_layout()
plt.show()




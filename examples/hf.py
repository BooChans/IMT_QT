import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm


def hf_slow(wavelength = 633e-9, z = 1, N = 200, L = 10e-3):
    # Physical parameters
    k = 2 * np.pi / wavelength
    dx = L / N
    x = np.linspace(-L/2, L/2, N)
    X1, Y1 = np.meshgrid(x, x)

    # Aperture: Circular
    R = 0.3e-3
    U0 = np.where(X1**2 + Y1**2 <= R**2, 1.0, 0.0)

    # Observation grid (same as source plane here)
    X2, Y2 = X1.copy(), Y1.copy()
    U = np.zeros_like(U0, dtype=complex)

    # Compute the full Huygens-Fresnel integral
    for i in tqdm(range(N)):
        for j in range(N):
            x_obs = X2[i, j]
            y_obs = Y2[i, j]

            r = np.sqrt((x_obs - X1)**2 + (y_obs - Y1)**2 + z**2)
            H = np.exp(1j * k * r) / (r**2)
            U[i, j] = np.sum(U0 * H) * dx * dx * z / (1j * wavelength)

    # Intensity
    I = np.abs(U)**2
    return I

def hf_fresnel_approx(wavelength = 633e-9, z = 1, N = 200, L = 10e-3):
    # Physical parameters
    k = 2 * np.pi / wavelength
    dx = L / N
    x = np.linspace(-L/2, L/2, N)
    X1, Y1 = np.meshgrid(x, x)

    # Aperture: Circular
    R = 0.3e-3
    U0 = np.where(X1**2 + Y1**2 <= R**2, 1.0, 0.0)

    # Observation grid (same as source plane here)
    X2, Y2 = X1.copy(), Y1.copy()
    U = np.zeros_like(U0, dtype=complex)

    # Compute the full Huygens-Fresnel integral
    for i in tqdm(range(N)):
        for j in range(N):
            x_obs = X2[i, j]
            y_obs = Y2[i, j]

            delta_xy = (x_obs - X1)**2 + (y_obs - Y1)**2
            H = np.exp(1j * k * (z + 1/(2*z)*delta_xy)) 
            U[i, j] = np.sum(U0 * H) * dx * dx / (1j * wavelength * z)

    # Intensity
    I = np.abs(U)**2
    return I

if __name__ == "__main__":
    z = 20e-2
    L = 3e-3
    I = hf_fresnel_approx(z=z, L=L)
    # Plotting
    plt.figure(figsize=(6,5))
    plt.imshow(I, extent=[-L/2*1e3, L/2*1e3, -L/2*1e3, L/2*1e3], cmap='inferno')
    plt.title(f'Unified Diffraction Pattern (z = {z*1e3:.1f} mm)')
    plt.xlabel('x (mm)')
    plt.ylabel('y (mm)')
    plt.colorbar(label='Intensity')
    plt.tight_layout()
    plt.show()

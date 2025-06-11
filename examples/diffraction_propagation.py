import numpy as np 


def far_field(U0, wavelength, z, dx):
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
    U0 = np.complex128(U0)
    N = max(U0.shape)  # Assume square input
    k = 2 * np.pi / wavelength
    
    # Calculate output pixel size (pixout)
    z_limit = N * dx**2 / wavelength
    print(z_limit, N, dx, wavelength)
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

def near_field(U0, wavelength, z, dx):
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
    U0 = np.complex128(U0)
    N = max(U0.shape)  # Assume square input
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
import numpy as np 
from resizing_ import resample_and_crop_to_fixed_size, smart_resample_and_crop
 
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
    if abs(z) < z_limit:
        raise ValueError(f"Use near-field method for z < {z_limit:.2f} µm")
    pixout =  wavelength * abs(z) / (N * dx)
    #print(z_limit, N, dx, wavelength, pixout)

    
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
    
    # Return intensity (multiplied by a coefficient to obtain more consistent intensity values)
    return U2 * (dx / pixout)

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
    return Uz

def angular_spectrum(U0, wavelength, z, dx):
    """
    Angular Spectrum Method with correct shifting for near-field propagation.
    """
    U0 = np.complex128(U0)
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

    return Uz

def sweep(U0, wavelength, dx, z_start, z_end, step, callback = None):
    N = max(U0.shape)
    z_limit = N * dx**2 / wavelength
    Z = np.arange(z_start, z_end, step)

    h, w = U0.shape[1:3]
    l = len(Z)

    assert l < 101, "Step too small, please increase it"

    shape = (l,h,w)
    diffraction_patterns = np.zeros(shape, dtype=np.complex128)
    samplings = np.zeros((l))

    base_dx = 1.0 if Z[0] < z_limit else wavelength * abs(Z[0]) / (N * dx)
    for i in range(len(Z)): 
        z = Z[i]
        if abs(z) < z_limit:
            diffraction_patterns[i] = angular_spectrum(U0, wavelength, z, dx)
            samplings[i] = dx 
        else:
            diffraction_pattern = far_field(U0, wavelength, z, dx)
            samplings[i] = wavelength * abs(z) / (N * dx)
            diffraction_pattern = smart_resample_and_crop(diffraction_pattern, samplings[i], base_dx, (h,w))
            samplings[i] = base_dx
            diffraction_patterns[i] = diffraction_pattern
        if callback:
            callback((int(i+1)/l*100))

    return diffraction_patterns, samplings, Z

def sweep_w(U0, z, dx, w_start, w_end, step, callback = None):
    N = max(U0.shape)
    W = np.arange(w_start, w_end, step)

    h, w = U0.shape[1:3]
    l = len(W)

    shape = (l,h,w)
    diffraction_patterns = np.zeros(shape, dtype=np.complex128)
    samplings = np.zeros((l))


    base_dx = 1.0 if z < N * dx**2 / W[0] else W[0] * abs(z) / (N * dx)

    for i in range(len(W)):
        wavelength = W[i] 
        z_limit = N * dx**2 / wavelength
        if abs(z) < z_limit:
            diffraction_patterns[i] = angular_spectrum(U0, wavelength, z, dx)
            samplings[i] = dx 
        else:
            diffraction_pattern = far_field(U0, wavelength, z, dx)
            samplings[i] = wavelength * abs(z) / (N * dx)
            diffraction_pattern = smart_resample_and_crop(diffraction_pattern, samplings[i], base_dx, (h,w))
            samplings[i] = base_dx
            diffraction_patterns[i] = diffraction_pattern
        if callback:
            callback(int((i+1)/l*100))

    return diffraction_patterns, samplings, W

def fraunhofer(source):
    return np.fft.fftshift(np.fft.fft2(source))

def ft_1(source):
    return np.fft.fftshift(np.fft.fft2(source, norm="ortho"))

def ft_2(source):
    return np.abs(np.fft.ifft2(np.fft.ifftshift(source), norm="ortho"))

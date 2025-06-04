import numpy as np


def compute_fft2(aperture):
    """
    Compute the normalized 2D FFT intensity of a given aperture.

    Args:
        aperture (2D np.array): Binary image representing the aperture.

    Returns:
        2D np.array: Normalized intensity of the FFT (|FFT|^2), scaled between 0 and 1.
    """
    fft = np.fft.fftshift(np.fft.fft2(aperture))
    intensity = np.abs(fft) ** 2
    intensity /= intensity.max() 
    return intensity

def compute_fft2_log(aperture):
    """
    Compute the normalized log-scaled FFT magnitude of a given aperture.

    Args:
        aperture (2D np.array): Binary image representing the aperture.

    Returns:
        2D np.array: Normalized log-scaled magnitude of the FFT, scaled between 0 and 1.
    """
    fft = np.fft.fftshift(np.fft.fft2(aperture))
    magnitude = np.abs(fft)
    log_magnitude = np.log1p(magnitude)
    log_magnitude /= log_magnitude.max()  
    return log_magnitude
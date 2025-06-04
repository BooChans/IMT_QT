import numpy as np


def compute_fft2(aperture):
    fft = np.fft.fftshift(np.fft.fft2(aperture))
    intensity = np.abs(fft) ** 2
    intensity /= intensity.max() 
    return intensity

def compute_fft2_log(aperture):
    fft = np.fft.fftshift(np.fft.fft2(aperture))
    magnitude = np.abs(fft)
    log_magnitude = np.log1p(magnitude)
    log_magnitude /= log_magnitude.max()  
    return log_magnitude
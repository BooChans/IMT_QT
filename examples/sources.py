import numpy as np
import sys
from PyQt5.QtWidgets import QApplication
from windows import RealTimeCrossSectionViewer 

def plane_wave_rectangular(shape = (512,512), size = (100,100), dx = 1):
    """
    Create a centered rectangular aperture.

    Args:
        shape (tuple): Output image size (height, width).
        size (tuple): Rectangle size (height, width).

    Returns:
        2D np.array: Binary image with 1s inside the rectangle, 0s outside.
    """
    # Create a SQUARE aperture (instead of circular)
    h, w = shape
    hr, wr = size
    assert hr / dx < h, "Sampling value is too low"
    assert wr / dx < w, "Sampling value is too low"
    x = np.arange(-w//2, w//2) * dx
    y = np.arange(-h//2, h//2) * dx
    X, Y = np.meshgrid(x, y)
    aperture = ((np.abs(X) <= wr/2) & (np.abs(Y) <= hr/2)).astype(np.float64)  # Square mask
    return aperture.astype(np.float64)

def plane_wave_elliptical(shape = (512,512), size = (200,300), dx = 1):
    """
    Create a centered elliptical aperture.
    
    Args:
        shape (tuple): Output image size (height, width) in pixels.
        size (tuple): Ellipse diameters (big_diameter, small_diameter) in physical units (e.g., microns).
        dx (float): Sampling rate (physical size per pixel).
        
    Returns:
        2D np.array: Binary image with 1s inside the ellipse, 0s outside.
    """
    h, w = shape
    big_diameter, small_diameter = size
    
    # Create coordinate grids centered at zero, scaled by dx
    x = (np.arange(w) - w//2) * dx
    y = (np.arange(h) - h//2) * dx
    X, Y = np.meshgrid(x, y)
    
    # Ellipse semi-axes
    a = big_diameter / 2
    b = small_diameter / 2
    
    # Equation of ellipse: (X/a)^2 + (Y/b)^2 <= 1
    aperture = ((X / a)**2 + (Y / b)**2) <= 1
    
    return aperture.astype(np.float64)

def gaussian_beam(shape=(512, 512), w0=50, dx=1.0):
    """
    Generate a 2D Gaussian beam intensity profile.

    Args:
        shape (tuple): Output image size (height, width) in pixels.
        w0 (float): Beam waist radius in the same units as dx.
        dx (float): Sampling rate (size of each pixel).

    Returns:
        2D np.array: Gaussian intensity profile.
    """
    h, w = shape
    x = (np.arange(w) - w // 2) * dx
    y = (np.arange(h) - h // 2) * dx
    X, Y = np.meshgrid(x, y)

    r_squared = X**2 + Y**2
    intensity = np.exp(-2 * r_squared / w0**2)

    return intensity.astype(np.float64)

def converging_spherical_wave(shape=(512, 512), wavelength = 0.633, focal_length = 1e4, dx = 1.0):
    h, w = shape
    x = (np.arange(w) - w // 2) * dx
    y = (np.arange(h) - h // 2) * dx
    X,Y = np.meshgrid(x,y)

    source = np.exp( -1j * np.pi/(focal_length*wavelength)*(X**2 + Y**2))
    source /= np.abs(source) + 1e-12
    print(np.abs(source).min(), np.abs(source).max())
    return source

if __name__ == "__main__":

    app = QApplication([])

    # Parameters
    N = 2048               # increase grid size for larger window
    dx = 50e-6             # increase sampling interval (50 µm)
    wavelength = 633e-9
    z = 10                 # 10 meters propagation distance
    radius = 0.1e-3        # 0.1 mm aperture

    aperture = plane_wave_elliptical()

    num_slices = 1
    # Repeat the aperture and FFT along z axis
    aperture_3D = np.repeat(aperture[np.newaxis, :, :], num_slices, axis=0)


    viewer = RealTimeCrossSectionViewer(aperture_3D)

    viewer.resize(1000, 800)
    viewer.show()
    sys.exit(app.exec())
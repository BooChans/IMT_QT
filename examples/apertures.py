import numpy as np
import sys
from PyQt5.QtWidgets import QApplication
from DiffractionSection import RealTimeCrossSectionViewer 




def elliptical_aperture(shape=(512,512), size = (300,300), dx = 1.0):
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


def rectangular_aperture(shape=(512,512), size = (300,300), dx = 1.0):
    """
    Create a centered rectangular aperture.

    Args:
        shape (tuple): Output image size (height, width).
        size (tuple): Rectangle size (height, width).

    Returns:
        2D np.array: Binary image with 1s inside the rectangle, 0s outside.
    """
    # Create a SQUARE aperture (instead of circular)
    eps = 1e-9
    h, w = shape
    hr, wr = size
    print(hr, wr, dx, h, hr/dx)
    assert hr / dx <= h, "Sampling value is too low"
    assert wr / dx <= w, "Sampling value is too low"
    x = np.arange(-w//2, w//2) * dx
    y = np.arange(-h//2, h//2) * dx
    X, Y = np.meshgrid(x, y)
    aperture = ((np.abs(X) <= wr/2) & (np.abs(Y) <= hr/2)).astype(np.float64)  # Square mask
    print(np.max(aperture))
    return aperture


def slit_apeture(shape=(512,512), size = (200,100), W = 2, d = 10, dx = 1.0):
    """
    Create a vertical slit aperture with multiple slits, using physical units.

    Args:
        shape (tuple): Output image shape (pixels) (height, width).
        size (tuple): Total area (μm) to occupy with slits (height, width).
        W (float): Slit width in microns.
        d (float): Distance between slit centers in microns.
        dx (float): Sampling size (microns per pixel).

    Returns:
        2D np.array: Binary image with 1s for slits, 0s elsewhere.
    """

    assert W > 0 and d > 0, "W and d must be positive."
    assert W < d, f"Invalid config: slit width W={W} must be less than spacing d={d}"
    assert W / dx >= 1, f"Slit width W={W} too small for sampling dx={dx} (W/dx = {W/dx:.2f} < 1 px)"
    assert d / dx >= 1, f"Slit spacing d={d} too small for sampling dx={dx} (d/dx = {d/dx:.2f} < 1 px)"

    h, w = shape
    aperture = np.zeros((h, w), dtype=np.float64)

    # Convert dimensions from microns to pixels
    hs_px = int(size[0] / dx)
    ws_px = int(size[1] / dx)
    W_px = int(W / dx)
    d_px = int(d / dx)

    # Image center
    cy, cx = h // 2, w // 2
    y_start = cy - hs_px // 2
    y_end = cy + hs_px // 2

    # Number of slits
    num_slits = hs_px // d_px

    for i in range(num_slits):
        slit_cx = cx - (num_slits // 2) * d_px + i * d_px
        x_start = slit_cx - W_px // 2
        x_end = slit_cx + W_px // 2
        aperture[x_start:x_end, y_start:y_end] = 1.0

    return aperture


def square_aperture_array(shape=(512, 512), square_size=5, spacing=20, grid_size=(5, 5), dx=1.0):
    """
    Create a 2D image with a grid of square apertures.

    Args:
        shape (tuple): Size of the output image (height, width) in pixels.
        square_size (float): Size of each square aperture (in microns).
        spacing (float): Distance between square centers (in microns).
        grid_size (tuple): Number of squares (rows, columns).
        dx (float): Sampling rate (microns/pixel).

    Returns:
        2D np.array: Binary aperture image with 1 inside squares, 0 outside.
    """
    assert dx > 0, "Sampling dx must be positive."
    assert square_size > 0 and spacing > 0, "Square size and spacing must be positive."
    assert square_size < spacing, "square_size must be smaller than spacing to avoid overlap."
    assert grid_size[0] > 0 and grid_size[1] > 0, "Grid size must be positive."

    h, w = shape

    # Convert physical sizes (microns) to pixel units
    square_px = int(round(square_size / dx))
    spacing_px = int(round(spacing / dx))

    grid_h = spacing_px * (grid_size[0] - 1) + square_px
    grid_w = spacing_px * (grid_size[1] - 1) + square_px

    assert grid_h <= h and grid_w <= w, (
        f"Grid size ({grid_h}x{grid_w} px) exceeds image size ({h}x{w} px). "
        f"Try increasing image shape or reducing spacing/grid size."
    )

    aperture = np.zeros((h, w), dtype=np.float32)

    # Center the grid
    start_y = (h - grid_h) // 2
    start_x = (w - grid_w) // 2

    for i in range(grid_size[0]):  # rows
        for j in range(grid_size[1]):  # cols
            y = start_y + i * spacing_px
            x = start_x + j * spacing_px
            aperture[y:y + square_px, x:x + square_px] = 1.0

    return aperture


def elliptical_aperture_array(shape=(512, 512), big_diameter=10, small_diameter=5, spacing=25, grid_size=(5, 5), dx=1.0):
    """
    Create a 2D array with a grid of elliptical apertures.

    Args:
        shape (tuple): Output image shape (height, width) in pixels.
        big_diameter (float): Major axis diameter (microns).
        small_diameter (float): Minor axis diameter (microns).
        spacing (float): Center-to-center distance between ellipses (microns).
        grid_size (tuple): Number of ellipses (rows, cols).
        dx (float): Sampling resolution in microns/pixel.

    Returns:
        2D np.array: Binary aperture image with 1 inside ellipses, 0 outside.
    """
    assert dx > 0, "dx must be positive."
    assert big_diameter > 0 and small_diameter > 0 and spacing > 0, "Diameters and spacing must be positive."
    assert big_diameter < spacing and small_diameter < spacing, "Ellipses must not overlap."
    assert grid_size[0] > 0 and grid_size[1] > 0, "Grid dimensions must be positive."

    h, w = shape
    aperture = np.zeros((h, w), dtype=np.float32)

    # Convert from microns to pixels
    big_px = int(round(big_diameter / dx))
    small_px = int(round(small_diameter / dx))
    spacing_px = int(round(spacing / dx))

    a = big_px / 2.0  # Semi-major axis
    b = small_px / 2.0  # Semi-minor axis

    # Total grid size in pixels
    grid_h = spacing_px * (grid_size[0] - 1) + big_px
    grid_w = spacing_px * (grid_size[1] - 1) + big_px

    assert grid_h <= h and grid_w <= w, (
        f"Grid size ({grid_h}x{grid_w} px) exceeds image size ({h}x{w} px)."
    )

    # Start positions to center the array
    start_y = (h - grid_h) / 2.0
    start_x = (w - grid_w) / 2.0

    yy, xx = np.meshgrid(np.arange(h), np.arange(w), indexing='ij')

    for i in range(grid_size[0]):
        for j in range(grid_size[1]):
            center_y = start_y + i * spacing_px + a
            center_x = start_x + j * spacing_px + a

            # Ellipse equation
            mask = (((xx - center_x) / a) ** 2 + ((yy - center_y) / b) ** 2) <= 1
            aperture[mask] = 1.0

    return aperture

def zero_pad(U0, new_shape):
    """
    Pads a 2D array U0 with zeros to match new_shape.

    Args:
        U0 (2D np.array): Original input field.
        new_shape (tuple): Desired shape (rows, cols) after padding.

    Returns:
        2D np.array: Zero-padded array with U0 centered.
    """
    padded = np.zeros(new_shape, dtype=U0.dtype)
    old_shape = U0.shape

    start_y = (new_shape[0] - old_shape[0]) // 2
    start_x = (new_shape[1] - old_shape[1]) // 2

    padded[start_y:start_y + old_shape[0], start_x:start_x + old_shape[1]] = U0
    return padded


def estimate_aperture_extent(big_diameter, small_diameter, spacing, grid_size, dx=1.0):
    """
    Estimate the total physical size (in microns) of a grid of elliptical or square apertures.

    Args:
        big_diameter (float): Major diameter (μm) — use square size for square apertures.
        small_diameter (float): Minor diameter (μm) — ignored for size, included for symmetry.
        spacing (float): Center-to-center spacing between apertures (μm).
        grid_size (tuple): (rows, columns) — number of apertures.
        dx (float): Pixel size (μm/px), for reference.

    Returns:
        (height_um, width_um): Physical extent of the aperture grid (μm)
    """
    rows, cols = grid_size
    assert rows > 0 and cols > 0

    height_um = spacing * (rows - 1) + big_diameter
    width_um = spacing * (cols - 1) + small_diameter

    return height_um, width_um

if __name__ == "__main__":

    app = QApplication([])

    # Parameters
    N = 2048               # increase grid size for larger window
    dx = 50e-6             # increase sampling interval (50 µm)
    wavelength = 633e-9
    z = 10                 # 10 meters propagation distance
    radius = 0.1e-3        # 0.1 mm aperture

    aperture = elliptical_aperture()

    num_slices = 1
    # Repeat the aperture and FFT along z axis
    aperture_3D = np.repeat(aperture[np.newaxis, :, :], num_slices, axis=0)


    viewer = RealTimeCrossSectionViewer(aperture_3D)

    viewer.resize(1000, 800)
    viewer.show()
    sys.exit(app.exec())
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
    aperture = ((X / b)**2 + (Y / a)**2) <= 1
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


def slit_aperture(shape=(1024, 1024), size=(700, 1024), W=100, d=500, dx=1.0):
    """
    Create a horizontal multi-slit aperture pattern where the midpoint between
    the first and last slits lies on the center row of the image. All slits fit
    inside the specified aperture height.

    Args:
        shape (tuple): (image_height_px, image_width_px)
        size (tuple): (aperture_height_um, aperture_width_um)
        W (float): height of each slit (um)
        d (float): spacing between slit centers (um)
        dx (float): microns per pixel

    Returns:
        np.ndarray: binary aperture image (1s = slits)
    """
    assert W > 0 and d > 0
    assert W < d
    assert W / dx >= 1, "Slit height too small for resolution"
    assert d / dx >= 1, "Slit spacing too small for resolution"

    img_h, img_w = shape
    aperture = np.zeros((img_h, img_w), dtype=np.float64)

    # Convert physical units to pixels
    ap_h_px = int(size[0] / dx)
    ap_w_px = int(size[1] / dx)
    W_px = int(W / dx)
    d_px = int(d / dx)

    # Determine number of slits that can fit vertically in the aperture height
    num_slits = int((ap_h_px + d_px - 1) // d_px)  # max that fit with spacing
    if num_slits < 1:
        return aperture  # No slits can be drawn

    # Compute vertical center of image
    cy = img_h // 2
    cx = img_w // 2

    # Total vertical span of the slit centers
    slit_span = (num_slits - 1) * d_px

    # First slit center y-position so that midpoint of slit array is centered
    first_center_y = cy - slit_span // 2

    # Horizontal bounds (centered)
    x_start = cx - ap_w_px // 2
    x_end = cx + ap_w_px // 2

    # Draw each slit
    for i in range(num_slits):
        center_y = first_center_y + i * d_px
        y_start = center_y - W_px // 2
        y_end = center_y + W_px // 2

        if 0 <= y_start < img_h and y_end <= img_h:
            aperture[y_start:y_end, x_start:x_end] = 1.0

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

    aperture = slit_aperture(size=(30, 512))

    num_slices = 1
    # Repeat the aperture and FFT along z axis
    aperture_3D = np.repeat(aperture[np.newaxis, :, :], num_slices, axis=0)


    viewer = RealTimeCrossSectionViewer(aperture_3D)

    viewer.resize(1000, 800)
    viewer.show()
    sys.exit(app.exec())
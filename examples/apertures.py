import numpy as np
import sys
from PyQt5.QtWidgets import QApplication
from windows import RealTimeCrossSectionViewer 
from hf import hf_slow, hf_fresnel_approx




def circular_aperture(shape=(512,512), radius = 50):
    """
    Create a circular aperture in a binary 2D image.

    Args:
        shape (tuple): Size of the output image (height, width).
        radius (int): Radius of the circular aperture in pixels.

    Returns:
        2D np.array: Binary image with 1s inside the circle, 0s outside.
    """
    h, w = shape
    y, x = np.indices((h,w))
    cx, cy = w // 2, h // 2
    r = np.sqrt((x-cx)**2+(y-cy)**2)
    return (r <= radius).astype(float)

def rectangular_aperture(shape=(512,512), size = (50,50)):
    """
    Create a centered rectangular aperture.

    Args:
        shape (tuple): Output image size (height, width).
        size (tuple): Rectangle size (height, width).

    Returns:
        2D np.array: Binary image with 1s inside the rectangle, 0s outside.
    """
    h, w = shape
    hr, wr = size
    cx, cy = w // 2, h // 2
    half_h, half_w = hr // 2, wr // 2
    rectangle = np.zeros((h,w))
    rectangle[cx-half_h: cx+half_h, cy-half_w:cy+half_w] = 1.0
    return rectangle

def slit_apeture(shape=(512,512), size = (200,100), W = 2, d = 10):
    """
    Create a vertical slit aperture with multiple slits.

    Args:
        shape (tuple): Size of the output image (height, width).
        size (tuple): Area occupied by slits (height, width).
        W (int): Width of each slit in pixels.
        d (int): Distance between slit centers in pixels.

    Returns:
        2D np.array: Binary image with 1s for slits, 0s elsewhere.
    """
    h , w = shape
    cx, cy = w // 2, h // 2
    hs , ws = size
    half_h, half_w = hs // 2, ws // 2

    number_slit = hs // d 

    aperture = np.zeros((h,w))

    y_start = cy - half_h
    y_end = cy + half_h

    for i in range(number_slit):
                
        slit_center_x = cx - (number_slit // 2) * d + i * d

        x_start = slit_center_x - W // 2
        x_end = slit_center_x + W // 2


        aperture[x_start:x_end,y_start:y_end] = 1.0
    return aperture


def square_aperture_array(shape=(512,512), square_size=5, spacing=20, grid_size=(5,5)):
    """
    Create a 2D image with a grid of square apertures.
    
    Args:
        shape (tuple): Size of the output image (height, width).
        square_size (int): Size of each square aperture (pixels).
        spacing (int): Distance between squares (pixels), center-to-center.
        grid_size (tuple): Number of squares in (rows, cols).
        
    Returns:
        aperture (2D np.array): Binary aperture image with 1 inside squares, 0 outside.
    """
    h, w = shape
    aperture = np.zeros((h,w))
    
    # Calculate total grid size in pixels
    grid_h = spacing * (grid_size[0] - 1) + square_size
    grid_w = spacing * (grid_size[1] - 1) + square_size
    
    # Start coordinates to center the grid
    start_y = (h - grid_h) // 2
    start_x = (w - grid_w) // 2
    
    for i in range(grid_size[0]):  # rows
        for j in range(grid_size[1]):  # cols
            y = start_y + i * spacing
            x = start_x + j * spacing
            aperture[y:y+square_size, x:x+square_size] = 1.0
    
    return aperture

def elliptical_aperture_array(shape=(512,512), big_diameter=10, small_diameter=5, spacing=25, grid_size=(5,5)):
    h, w = shape
    aperture = np.zeros((h,w))

    grid_h = spacing * (grid_size[0] - 1) + big_diameter
    grid_w = spacing * (grid_size[1] - 1) + big_diameter

    start_y = (h - grid_h) / 2.0
    start_x = (w - grid_w) / 2.0

    # Use meshgrid with indexing='ij' to get correct y,x coordinates
    yy, xx = np.meshgrid(np.arange(h), np.arange(w), indexing='ij')

    a = big_diameter / 2.0
    b = small_diameter / 2.0

    for i in range(grid_size[0]):
        for j in range(grid_size[1]):
            center_y = start_y + i * spacing + a
            center_x = start_x + j * spacing + a

            # Equation of ellipse
            mask = (((xx - center_x) / a) ** 2 + ((yy - center_y) / b) ** 2) <= 1
            aperture[mask] = 1.0

    return aperture

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


if __name__ == "__main__":

    app = QApplication([])


    aperture = circular_aperture()
    aperture_fft = compute_fft2(aperture)

    num_slices = 1

    # Repeat the aperture and FFT along z axis
    #aperture_3D = np.repeat(aperture[np.newaxis, :, :], num_slices, axis=0)
    #fft_3d = np.repeat(aperture_fft[np.newaxis, :, :], num_slices, axis=0)

    z = 1
    L = 10e-2
    I = hf_fresnel_approx(z=z, L=L)

    #I = hf_slow(z=1e-4, L = 3e-3)
    I_3D = np.repeat(I[np.newaxis, :, :], num_slices, axis=0)
    print(I_3D.shape)
    viewer = RealTimeCrossSectionViewer(I_3D)

    viewer.resize(1000, 800)
    viewer.show()
    sys.exit(app.exec())
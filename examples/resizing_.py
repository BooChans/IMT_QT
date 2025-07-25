import numpy as np
from scipy.ndimage import zoom, center_of_mass

"""unused code, useful for scale preservation when doing a z sweep


def bounding_box(mask):
    coords = np.argwhere(mask)
    if coords.size == 0:
        return None  # no signal found
    y_min, x_min = coords.min(axis=0)
    y_max, x_max = coords.max(axis=0)
    return y_min, y_max, x_min, x_max

def crop_to_signal(volume_slice, pad=10):
    # volume_slice shape: (1, N, N)
    intensity = np.abs(volume_slice[0]) ** 2  # remove batch dim for masking
    threshold = 0.01 * intensity.max()
    mask = intensity > threshold
    bbox = bounding_box(mask)
    if bbox is None:
        return volume_slice  # fallback, no cropping
    
    y_min, y_max, x_min, x_max = bbox
    y_min = max(0, y_min - pad)
    y_max = min(volume_slice.shape[1], y_max + pad)  # shape[1] because shape = (1, H, W)
    x_min = max(0, x_min - pad)
    x_max = min(volume_slice.shape[2], x_max + pad)

    # crop including the batch dimension
    cropped = volume_slice[:, y_min:y_max, x_min:x_max]
    return cropped

"""

def format_if_large(value):
    if abs(value) >= 100:
        return f"{value:.2e}".replace("+0", "").replace("+", "")
    else:
        return str(round(value,2))
    



def resample_and_crop_to_fixed_size(U, current_dx, target_dx, output_shape=(512, 512)):
    """
    Resample a [1, N, N] field to a fixed resolution and output size [1, M, N],
    using scipy.ndimage.zoom for resizing.

    Args:
        U (np.ndarray): Input field of shape (1, N, N), complex or float.
        current_dx (float): Current pixel size (μm).
        target_dx (float): Target pixel size (μm).
        output_shape (tuple): Desired output shape (M, N).

    Returns:
        np.ndarray: Output field of shape (1, M, N).
    """
    if U.ndim != 3 or U.shape[0] != 1:
        raise ValueError("Input U must have shape (1, N, N)")

    U2d = U[0]  # Shape: (N, N)
    zoom_factor = current_dx / target_dx

    # Compute zoom factors for height and width (same since square pixels)
    zoom_factors = (zoom_factor, zoom_factor)

    # Zoom using scipy.ndimage.zoom (separately for real and imaginary if complex)
    if np.iscomplexobj(U2d):
        U_real = zoom(U2d.real, zoom_factors, order=1)  # order=1: linear interpolation
        U_imag = zoom(U2d.imag, zoom_factors, order=1)
        U_resampled = U_real + 1j * U_imag
    else:
        U_resampled = zoom(U2d, zoom_factors, order=1)

    # Center crop or pad to output_shape
    result = np.zeros(output_shape, dtype=U_resampled.dtype)
    resampled_shape = U_resampled.shape

    min_shape = np.minimum(resampled_shape, output_shape)
    start_src = [(s - m) // 2 for s, m in zip(resampled_shape, min_shape)]
    start_dst = [(d - m) // 2 for d, m in zip(output_shape, min_shape)]

    result[
        start_dst[0]:start_dst[0]+min_shape[0],
        start_dst[1]:start_dst[1]+min_shape[1]
    ] = U_resampled[
        start_src[0]:start_src[0]+min_shape[0],
        start_src[1]:start_src[1]+min_shape[1]
    ]

    return result[np.newaxis, ...]  # Shape: (1, M, N)

def smart_resample_and_crop(U, current_dx, target_dx, output_shape=(512, 512)):
    """
    Resample a [1, N, N] field to a fixed resolution and output size [1, M, N],
    but instead of zooming the whole image, crop around the center before zooming.

    Args:
        U (np.ndarray): Input field of shape (1, N, N), complex or float.
        current_dx (float): Current pixel size (μm).
        target_dx (float): Target pixel size (μm).
        output_shape (tuple): Desired output shape (M, N).

    Returns:
        np.ndarray: Output field of shape (1, M, N).
    """
    if U.ndim != 3 or U.shape[0] != 1:
        raise ValueError("Input U must have shape (1, N, N)")

    U2d = U[0]
    zoom_factor = current_dx / target_dx

    # Compute the crop size before zooming
    prezoom_shape = tuple([int(s / zoom_factor) for s in output_shape])
    center = [s // 2 for s in U2d.shape]

    # Crop around center
    start = [c - ps // 2 for c, ps in zip(center, prezoom_shape)]
    end = [s + ps for s, ps in zip(start, prezoom_shape)]

    # Clamp to image bounds
    start = [max(0, s) for s in start]
    end = [min(U2d.shape[i], start[i] + prezoom_shape[i]) for i in range(2)]

    cropped = U2d[start[0]:end[0], start[1]:end[1]]

    # Zoom
    zoom_factors = (zoom_factor, zoom_factor)
    if np.iscomplexobj(cropped):
        U_real = zoom(cropped.real, zoom_factors, order=3)
        U_imag = zoom(cropped.imag, zoom_factors, order=3)
        U_zoomed = U_real + 1j * U_imag
    else:
        U_zoomed = zoom(cropped, zoom_factors, order=1)

    # Final center crop or pad to output_shape
    result = np.zeros(output_shape, dtype=U_zoomed.dtype)
    min_shape = np.minimum(U_zoomed.shape, output_shape)
    start_src = [(s - m) // 2 for s, m in zip(U_zoomed.shape, min_shape)]
    start_dst = [(d - m) // 2 for d, m in zip(output_shape, min_shape)]

    result[
        start_dst[0]:start_dst[0]+min_shape[0],
        start_dst[1]:start_dst[1]+min_shape[1]
    ] = U_zoomed[
        start_src[0]:start_src[0]+min_shape[0],
        start_src[1]:start_src[1]+min_shape[1]
    ]

    return result[np.newaxis, ...]

def smart_resample_and_crop(U, current_dx, target_dx, output_shape=(512, 512)):
    """
    Resample a [1, N, N] field to a fixed resolution and output size [1, M, N],
    centering on the region with the highest signal (center of mass).

    Args:
        U (np.ndarray): Input field of shape (1, N, N), complex or float.
        current_dx (float): Current pixel size (μm).
        target_dx (float): Target pixel size (μm).
        output_shape (tuple): Desired output shape (M, N).

    Returns:
        np.ndarray: Output field of shape (1, M, N).
    """
    if U.ndim != 3 or U.shape[0] != 1:
        raise ValueError("Input U must have shape (1, N, N)")

    U2d = U[0]
    zoom_factor = current_dx / target_dx

    # Compute the crop size before zooming
    prezoom_shape = tuple([int(s / zoom_factor) for s in output_shape])

    # Compute center of mass of the magnitude
    magnitude = np.abs(U2d) if np.iscomplexobj(U2d) else U2d
    com = center_of_mass(magnitude)
    center = [int(round(c)) for c in com]

    # Crop around the center of mass
    start = [c - ps // 2 for c, ps in zip(center, prezoom_shape)]
    end = [s + ps for s, ps in zip(start, prezoom_shape)]

    # Clamp to image bounds
    start = [max(0, s) for s in start]
    end = [min(U2d.shape[i], start[i] + prezoom_shape[i]) for i in range(2)]

    # Ensure crop size matches prezoom_shape (adjust if clamped)
    for i in range(2):
        if end[i] - start[i] < prezoom_shape[i]:
            if start[i] == 0:
                end[i] = min(U2d.shape[i], start[i] + prezoom_shape[i])
            elif end[i] == U2d.shape[i]:
                start[i] = max(0, end[i] - prezoom_shape[i])

    cropped = U2d[start[0]:end[0], start[1]:end[1]]

    # Zoom
    zoom_factors = (zoom_factor, zoom_factor)
    if np.iscomplexobj(cropped):
        U_real = zoom(cropped.real, zoom_factors, order=1)
        U_imag = zoom(cropped.imag, zoom_factors, order=1)
        U_zoomed = U_real + 1j * U_imag
    else:
        U_zoomed = zoom(cropped, zoom_factors, order=1)

    # Final center crop or pad to output_shape
    result = np.zeros(output_shape, dtype=U_zoomed.dtype)
    min_shape = np.minimum(U_zoomed.shape, output_shape)
    start_src = [(s - m) // 2 for s, m in zip(U_zoomed.shape, min_shape)]
    start_dst = [(d - m) // 2 for d, m in zip(output_shape, min_shape)]

    result[
        start_dst[0]:start_dst[0]+min_shape[0],
        start_dst[1]:start_dst[1]+min_shape[1]
    ] = U_zoomed[
        start_src[0]:start_src[0]+min_shape[0],
        start_src[1]:start_src[1]+min_shape[1]
    ]

    return result[np.newaxis, ...]
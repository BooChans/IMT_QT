import numpy as np

import numpy as np

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
    threshold = 0.00001 * intensity.max()
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

def format_if_large(value):
    if abs(value) >= 100:
        return f"{value:.2e}".replace("+0", "").replace("+", "")
    else:
        return str(round(value,2))
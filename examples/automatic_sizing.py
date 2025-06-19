import numpy as np

def auto_sampling_N(source_size, apertures_size, shape = (512,512), filling_rate = 0.59):
    h_smax = max(source_size)
    h_amax = max(apertures_size)
    h, _ = shape
    if h_smax > h_amax:
        dx = h_smax/(h*filling_rate)
    else: 
        dx = h_amax/(h*filling_rate)
    return dx

def auto_shaping_dx(source_size, aperture_size, dx):
    h_smax = max(source_size) 
    h_amax = max(aperture_size)
    if h_smax > h_amax:
        N = int(2 ** (np.ceil(np.log2(h_smax/dx))))
    else: 
        N = int(2 ** (np.ceil(np.log2(h_amax/dx))))
    return N

def zero_pad(U0, new_shape):
    """
    Pads a 3D array U0 with zeros to match new_shape, preserving batch dimension.

    Args:
        U0 (3D np.array): Original input field with shape (1, H, W).
        new_shape (tuple): Desired spatial shape (new_H, new_W) after padding.

    Returns:
        3D np.array: Zero-padded array with U0[0] centered, shape (1, new_H, new_W).
    """
    assert U0.ndim == 3 and U0.shape[0] == 1, "Input must have shape (1, H, W)"
    
    old_h, old_w = U0.shape[1:]
    new_h, new_w = new_shape

    padded = np.zeros((1, new_h, new_w), dtype=U0.dtype)

    start_y = (new_h - old_h) // 2
    start_x = (new_w - old_w) // 2

    padded[0, start_y:start_y + old_h, start_x:start_x + old_w] = U0[0]
    return padded


def auto_sampling_N_2(source_size, shape = (512,512), filling_rate = 0.95):
    h_smax = max(source_size)
    h, _ = shape
    dx = h_smax/(h*filling_rate)

    return dx

def auto_sampling_dx_2(source_size, shape=(512,512), dx=1.0):
    h_smax = max(source_size) 
    N = int(2 ** (np.ceil(np.log2(h_smax/dx))))
    return N


import numpy as np


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



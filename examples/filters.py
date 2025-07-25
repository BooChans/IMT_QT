import numpy as np


def elliptic_filter(cutoff_freq_big_diameter, cutoff_freq_low_diameter, fx, fy):
    FX, FY = np.meshgrid(fx, fy)
    
    # Normalize FX and FY by their respective cutoff frequencies
    FX_norm = FX / cutoff_freq_low_diameter
    FY_norm = FY / cutoff_freq_big_diameter

    # Elliptic radius
    radius = np.sqrt(FX_norm**2 + FY_norm**2)
    
    # Apply elliptical low-pass filter mask
    mask = radius <= 1.0
    return np.array(mask.astype(float))


def rectangular_filter(cutoff_freq_width, cutoff_freq_height, fx, fy):
    FX, FY = np.meshgrid(fx, fy)

    # Create a rectangular mask
    mask = (np.abs(FY) <= cutoff_freq_width / 2) & (np.abs(FX) <= cutoff_freq_height / 2)

    return np.array(mask.astype(float))


def elliptic_filter_band(cutoff_freq_big_diameter, cutoff_freq_low_diameter, fx, fy, thickness):
    FX, FY = np.meshgrid(fx, fy)
    
    # Normalize FX and FY by their respective cutoff frequencies
    FX_norm_bc = FX / cutoff_freq_low_diameter
    FY_norm_bc = FY / cutoff_freq_big_diameter

    FX_norm_sc = FX / (cutoff_freq_low_diameter-thickness)
    FY_norm_sc = FY / (cutoff_freq_big_diameter-thickness)

    # Elliptic radius
    radius_bc = np.sqrt(FX_norm_bc**2 + FY_norm_bc**2)
    radius_sc = np.sqrt(FX_norm_sc**2 + FY_norm_sc**2)
    
    # Apply elliptical low-pass filter mask
    mask = np.logical_and(radius_sc >= 1.0, radius_bc <= 1.0)

    return np.array(mask.astype(float))

def rectangular_filter_band(cutoff_freq_width, cutoff_freq_height, fx, fy, thickness):
    FX, FY = np.meshgrid(fx, fy)

    # Outer rectangle bounds
    outer_mask = (np.abs(FY) <= cutoff_freq_width / 2) & (np.abs(FX) <= cutoff_freq_height / 2)

    # Inner rectangle bounds (subtract thickness)
    inner_mask = (np.abs(FY) <= (cutoff_freq_width - thickness) / 2) & \
                 (np.abs(FX) <= (cutoff_freq_height - thickness) / 2)

    # Band-pass mask: between outer and inner
    band_mask = outer_mask & ~inner_mask

    return np.array(band_mask.astype(float))
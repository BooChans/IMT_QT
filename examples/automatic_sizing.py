import numpy as np

def auto_sizing_sampling(z, wavelength, size_source, size_aperture):

    h_ap = max(size_aperture)
    h_src = max(size_source)

    print(h_ap, z, wavelength)
    dx_aperture = wavelength * z / (2 * h_ap)
    dx_source =  h_src/4
    print(dx_aperture, dx_source)
    dx = np.min([dx_aperture, dx_source])

    L = np.max([h_ap, h_src]) +  + (2 * wavelength * z / dx)

    N = int(2 ** np.ceil(np.log2(L / dx)))

    return dx, N


def auto_sizing_sampling_fresnel(z, wavelength, size_source, size_aperture, oversampling=2):
    # Max physical aperture and source sizes (microns or consistent units)
    h_ap = max(size_aperture)
    h_src = max(size_source)

    # Estimate maximum size needed to cover source and aperture
    L0 = max(h_ap, h_src)

    # Fresnel length scale for diffraction spread
    L_diff = np.sqrt(wavelength * z)

    # Base sampling interval must resolve the phase curvature:
    # dx <= sqrt(lambda * z / N)
    # We'll start by estimating dx from source and aperture resolution:
    dx_src = h_src / 4  # resolve source adequately
    dx_ap = wavelength * z / (2 * h_ap)  # Fresnel criterion

    # Choose the smaller dx and apply oversampling for safety
    dx = np.min([dx_src, dx_ap]) / oversampling

    # Determine simulation window size - pad to avoid wrap-around in FFT
    L = L0 + 4 * L_diff

    # Number of points, rounded up to next power of 2 for FFT
    N = int(2 ** np.ceil(np.log2(L / dx)))

    # Recalculate dx for integer N and window size
    dx = L / N

    print(f"Fresnel auto-sizing:\n  dx = {dx:.3e}\n  N = {N}\n  Window L = {L:.3e}")

    return dx, N
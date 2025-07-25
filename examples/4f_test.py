import numpy as np
from PIL import Image
from diffraction_propagation import angular_spectrum, far_field
import matplotlib.pyplot as plt
from automatic_sizing import zero_pad

import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft2, fftshift, ifft2, ifftshift
from PIL import Image
from diffraction_propagation import angular_spectrum
path = r"C:\Users\baoch\Downloads\AC7_YF-23_Flyby.png"



# --- Physical parameters ---
wavelength = 633e-9       # 633 nm (red HeNe laser)
focal_length = 0.1        # 10 cm focal length lenses
pixel_size = 10e-6        # 10 microns per pixel

# --- Load image from your path, grayscale, thumbnail and zero-pad ---
def zero_pad(img, target_shape):
    pad_y = target_shape[0] - img.shape[0]
    pad_x = target_shape[1] - img.shape[1]
    pad_before_y = pad_y // 2
    pad_after_y = pad_y - pad_before_y
    pad_before_x = pad_x // 2
    pad_after_x = pad_x - pad_before_x
    return np.pad(img, ((pad_before_y, pad_after_y), (pad_before_x, pad_after_x)), mode='constant')

def load_and_process_image(path, max_size=(512, 512), target_shape=(512, 512)):
    img = Image.open(path).convert("L")  # grayscale
    img.thumbnail(max_size,  Image.LANCZOS)
    img_np = np.array(img, dtype=np.float64) / 255.0  # normalize 0-1
    if img_np.shape != target_shape:
        img_np = zero_pad(img_np, target_shape)
    return img_np

# --- Compute spatial frequencies in Fourier plane ---
def spatial_freqs(N, dx):
    df = 1 / (N * dx)   # frequency resolution (cycles/m)
    if N % 2 == 0:
        f = np.linspace(-N/2, N/2-1, N) * df
    else:
        f = np.linspace(-(N-1)/2, (N-1)/2, N) * df
    return f

# --- Create a low-pass circular filter in spatial frequency domain ---
def circular_low_pass_filter(shape, cutoff_freq, fx, fy):
    FX, FY = np.meshgrid(fx, fy)
    radius = np.sqrt(FX**2 + FY**2)
    mask = radius <= cutoff_freq
    return mask.astype(float)

# --- 4f system simulation ---
def lens_phase(shape, wavelength, focal_length, dx):
    N = shape[0]
    x = (np.arange(N) - N // 2) * dx
    X, Y = np.meshgrid(x, x)
    k = 2 * np.pi / wavelength
    return np.exp(-1j * k * (X**2 + Y**2) / (2 * focal_length))

def fourier_4f_system_physical(input_img, wavelength, focal_length, pixel_size, filter_mask=None):
    # Apply lens 1 phase
    lens1 = lens_phase(input_img.shape, wavelength, focal_length, pixel_size)
    field = input_img * lens1

    # Propagate from input plane to Fourier plane
    field = angular_spectrum(field, wavelength, focal_length, pixel_size)

#    if filter_mask is not None:
#        field_filtered = field * filter_mask
#    else:
    field_filtered = field

    # Apply lens 2 phase
    lens2 = lens_phase(input_img.shape, wavelength, focal_length, pixel_size)
    field_filtered *= lens2

    # Propagate to image plane
    field_out = angular_spectrum(field_filtered, wavelength, focal_length, pixel_size)

    return (
        np.abs(field)**2,               # Fourier plane (before filter)
        np.abs(field_filtered)**2,     # Fourier plane (after filter)
        np.abs(field_out)**2           # Final image plane
    )

def fourier_4f_system_physical_no_lenses(input_img, wavelength, focal_length, pixel_size):
    field = angular_spectrum(input_img, wavelength, focal_length, pixel_size)
    field_out = angular_spectrum(field, wavelength, focal_length, pixel_size)
    return np.abs(input_img)**2, np.abs(field)**2, np.abs(field_out)**2  # Return both output and intermediate Fourier plane intensity

# --- Main ---
img_path = r"C:\Users\baoch\Downloads\AC7_YF-23_Flyby.png"

input_img = load_and_process_image(img_path)

N = input_img.shape[0]

fx = spatial_freqs(N, pixel_size)
fy = spatial_freqs(N, pixel_size)

# Example cutoff frequency for low-pass filter (cycles per meter)
cutoff_freq = 15e3

filter_mask = circular_low_pass_filter(input_img.shape, cutoff_freq, fx, fy)

ft_img, ft_filtered, output_img = fourier_4f_system_physical_no_lenses(input_img, wavelength, focal_length, pixel_size)

# --- Plotting ---
fig, ax = plt.subplots(1, 4, figsize=(18, 5))
ax[0].imshow(input_img, cmap='gray')
ax[0].set_title('Input Image')
ax[0].axis('off')

ax[1].imshow(np.log1p(np.abs(ft_img)), cmap='gray',
             extent=[fx.min(), fx.max(), fy.min(), fy.max()])
ax[1].set_title('Fourier Magnitude (cycles/m)')
ax[1].set_xlabel('fx (cycles/m)')
ax[1].set_ylabel('fy (cycles/m)')

ax[2].imshow(filter_mask, cmap='gray',
             extent=[fx.min(), fx.max(), fy.min(), fy.max()])
ax[2].set_title('Low-pass Filter Mask')
ax[2].set_xlabel('fx (cycles/m)')
ax[2].set_ylabel('fy (cycles/m)')

ax[3].imshow(output_img, cmap='gray')
ax[3].set_title('Output Image')
ax[3].axis('off')

plt.tight_layout()
plt.show()
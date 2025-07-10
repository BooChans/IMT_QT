import pyqtgraph as pg
import numpy as np
from pyqtgraph.Qt import QtWidgets

def wavelength_to_rgb(wavelength):
    """
    Convert a wavelength in nm (380 to 750) to an RGB color.
    Returns an array [R,G,B] with values 0-255.
    """
    gamma = 0.8
    intensity_max = 1

    if wavelength < 380 or wavelength > 750:
        return np.array([0, 0, 0], dtype=np.uint8)

    if 380 <= wavelength <= 440:
        attenuation = 0.3 + 0.7 * (wavelength - 380) / (440 - 380)
        R = ((-(wavelength - 440) / (440 - 380)) * attenuation) ** gamma
        G = 0.0
        B = (1.0 * attenuation) ** gamma
    elif 440 < wavelength <= 490:
        R = 0.0
        G = ((wavelength - 440) / (490 - 440)) ** gamma
        B = 1.0
    elif 490 < wavelength <= 510:
        R = 0.0
        G = 1.0
        B = (-(wavelength - 510) / (510 - 490)) ** gamma
    elif 510 < wavelength <= 580:
        R = ((wavelength - 510) / (580 - 510)) ** gamma
        G = 1.0
        B = 0.0
    elif 580 < wavelength <= 645:
        R = 1.0
        G = (-(wavelength - 645) / (645 - 580)) ** gamma
        B = 0.0
    else:  # 645 < wavelength <= 750
        attenuation = 0.3 + 0.7 * (750 - wavelength) / (750 - 645)
        R = (1.0 * attenuation) ** gamma
        G = 0.0
        B = 0.0

    R = int(max(0, min(1, R)) * 255)
    G = int(max(0, min(1, G)) * 255)
    B = int(max(0, min(1, B)) * 255)

    return np.array([R, G, B], dtype=np.uint8)

color = wavelength_to_rgb(480)

app = QtWidgets.QApplication([])

win = pg.ImageView()

# Your grayscale data
data = np.random.rand(256, 256)

# Define a red colormap (256 steps)

R, G, B = color

# Make LUT: grayscale 0 → black, 255 → full single_color
lut = np.zeros((256, 3), dtype=np.uint8)
lut[:, 0] = np.linspace(0, R, 256)  # ramp red channel
lut[:, 1] = np.linspace(0, G, 256)  # ramp green channel
lut[:, 2] = np.linspace(0, B, 256)  # ramp blue channel


# green and blue remain 0

# Apply image and LUT
win.setImage(data)
win.setColorMap(pg.ColorMap(pos=np.linspace(0,1,256), color=lut))

win.show()
app.exec()
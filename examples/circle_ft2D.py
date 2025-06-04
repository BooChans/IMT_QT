import numpy as np
import sys
import pyqtgraph as pg
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QSlider, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt
from pyqtgraph import LineROI
from scipy.ndimage import map_coordinates
from windows import RealTimeCrossSectionViewer 



def circular_aperture(shape=(512,512), radius = 50):
    h, w = shape
    y, x = np.indices((h,w))
    cx, cy = w // 2, h // 2
    r = np.sqrt((x-cx)**2+(y-cy)**2)
    return (r <= radius).astype(float)

def rectangular_aperture(shape=(512,512), size = (50,50)):
    h, w = shape
    hr, wr = size
    cx, cy = w // 2, h // 2
    half_h, half_w = hr // 2, wr // 2
    rectangle = np.zeros((h,w))
    rectangle[cx-half_h: cx+half_h, cy-half_w:cy+half_w] = 1.0
    return rectangle

def slit_apeture(shape=(512,512), height = 100, number_slit = 5, W = 2, d = 10):
    h , w = shape
    cx, cy = w // 2, h // 2
    hs , ws = height , number_slit * d
    half_h, half_w = hs // 2, ws // 2

    number_slit = int(hs/d)

    aperture = np.zeros((h,w))

    for i in range(number_slit):
        aperture[cx-half_w: cx+half_w, cy-half_w:cy+half_w] = 1.0
    None
    

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


    aperture = rectangular_aperture(size=(100,150))
    aperture_fft = compute_fft2(aperture)
    fft_3d = np.expand_dims(aperture_fft, axis=0) 

    print(fft_3d.shape)

    viewer = RealTimeCrossSectionViewer(fft_3d)

    viewer.resize(1000, 800)
    viewer.show()
    sys.exit(app.exec())
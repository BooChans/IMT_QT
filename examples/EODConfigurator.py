import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QCheckBox,
    QSplitter, QLabel, QSlider, QGridLayout,QGraphicsLineItem 
)
from PyQt5.QtCore import Qt
import pyqtgraph as pg
from SimulationSection import SimulationSection

class EODConfigurator(QWidget):
    def __init__(self):
        super().__init__()

    

import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QCheckBox,
    QSplitter, QLabel, QSlider, QGridLayout,QGraphicsLineItem , QPushButton
)
from PyQt5.QtCore import Qt
import pyqtgraph as pg
from EODSection import EODSection
from ImageSection import ImageSection
import sys

from ifmta.ifta import Ifta

class EODConfigurator(QMainWindow):
    def __init__(self):
        super().__init__()

        self.image_section = ImageSection()
        self.eod_section = EODSection()

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.image_section)
        splitter.addWidget(self.eod_section)

        self.central_widget = QWidget()
        self.central_widget_layout = QVBoxLayout(self.central_widget)

        self.central_widget_layout.addWidget(splitter)

        self.sim_button = QPushButton("Run EOD simulation")
        self.central_widget_layout.addWidget(self.sim_button)

        self.setCentralWidget(self.central_widget)
        self.setup_connections()
        
    def setup_connections(self):
        self.sim_button.clicked.connect(self.sim_EOD)
    
    def sim_EOD(self):
        image_params = self.image_section.get_inputs()

        eod_params = self.eod_section.get_inputs()

        if eod_params["npy_path"]:
            seed = np.load(eod_params["npy_path"])

        img_path = image_params["img_path"]
        image = image_params["image"]
        nlevels = eod_params["nlevels"]
        rfact = eod_params["rfact"]
        nbiter = eod_params["nbiter"]

        print(nlevels, rfact, nbiter, image_params["image_shape"])

        



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EODConfigurator()
    window.show()
    app.exec()

    

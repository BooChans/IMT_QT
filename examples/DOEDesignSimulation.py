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
from PIL import Image
from ifmta.ifta import Ifta
from automatic_sizing import zero_pad

class DOEDesignSimulation(QMainWindow):
    def __init__(self):
        super().__init__()

        self.image_section = ImageSection()
        self.eod_section = EODSection()

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.image_section)
        splitter.addWidget(self.eod_section)

        splitter.setSizes([200, 800])

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
        else: 
            seed = 0

        image_array_shape = tuple(map(int,image_params["image_array_shape"]))
        image = image_params["image"]
        nlevels = int(eod_params["nlevels"])
        rfact = float(eod_params["rfact"])
        nbiter = int(eod_params["nbiter"])
        compute_efficiency = eod_params["compute_efficiency"]
        compute_uniformity = eod_params["compute_uniformity"]

        

        print(nlevels, rfact, nbiter, image_params["image_shape"])

        phases = Ifta(image, image_size=image_array_shape, n_iter=nbiter, rfact=rfact, n_levels=nlevels, 
                      compute_efficiency= compute_efficiency, compute_uniformity = compute_uniformity, seed=seed)

        print(phases.shape, "computation done")
        self.eod_section.volume = phases
        self.eod_section.graph_view.update_data(phases)

                


        



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EODConfigurator()
    window.show()
    app.exec()

    

import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QCheckBox,
    QSplitter, QLabel, QSlider, QGridLayout,QGraphicsLineItem , QPushButton, QFileDialog, QHBoxLayout,QLineEdit, QToolButton, QStyle, QSizePolicy
)
from PyQt5.QtCore import Qt
import pyqtgraph as pg
from EODSection import EODSection
from ImageSection import ImageSection
from SimulationSection import SimulationSection
import sys
from PIL import Image
from ifmta.ifta import Ifta
from automatic_sizing import zero_pad

class DOEDesignSimulation(QMainWindow):
    def __init__(self):
        super().__init__()

        self.nbiter = "25"
        self.rfact = "1.2"
        self.seed = 0
        self.compute_efficiency = 0
        self.compute_uniformity = 0
        self.npy_path = None

        self.resize(2000, 1200)

        self.page = QWidget()
        self.page_layout = QVBoxLayout(self.page)
        self.image_section = ImageSection()
        self.eod_section = EODSection()
        self.simulation_section = SimulationSection()
        self.eod_section.graph_view.mode_selector.setCurrentText("Amplitude")

        self.image_section.graph_widget.slice_view.ui.histogram.hide()

        #no sampling
        self.simulation_section.sampling_selection_widget.hide()
        self.simulation_section.checkbox_widget.hide()

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.image_section)
        splitter.addWidget(self.eod_section)

        self.left = QWidget()
        self.left_layout = QVBoxLayout(self.left)
        


        splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


        self.ifta_params_widget = QWidget()
        self.ifta_params_widget_layout = QGridLayout(self.ifta_params_widget)

        self.sim_button = QPushButton("Run EOD simulation")
        self.sim_button.hide()


        splitter_ = QSplitter(Qt.Horizontal)
        
        self.setup_rfact()
        self.setup_nbiter()
        self.setup_npy_importer()
        self.setup_extras()
        self.setup_connections()

        self.left_layout.addWidget(splitter)
        self.left_layout.addWidget(self.ifta_params_widget)
        self.left_layout.addWidget(self.sim_button)
        splitter_.addWidget(self.left)
        splitter_.addWidget(self.simulation_section)

        self.left.setMinimumWidth(1100)  # or setMinimumSize(QSize(100, 0))
        splitter_.setSizes([1100, 2500])   # Big number to force right widget to take the rest

        self.page_layout.addWidget(splitter_)
        self.page.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setCentralWidget(self.page)
        self.setup_connections()


    def setup_rfact(self):

        self.rfact_widget = QWidget()
        self.rfact_widget_layout = QHBoxLayout(self.rfact_widget)

        rfact_label = QLabel("Reinforcement factor")

        self.rfact_line_edit = QLineEdit()
        self.rfact_line_edit.setFixedWidth(100)
        self.rfact_line_edit.setText(self.rfact)

        self.rfact_widget_layout.addWidget(rfact_label)
        #self.rfact_widget_layout.addStretch()
        self.rfact_widget_layout.addWidget(self.rfact_line_edit)
        #self.rfact_widget_layout.setStretch(0, 10)
        #self.rfact_widget_layout.setStretch(1, 3)
        self.ifta_params_widget_layout.addWidget(self.rfact_widget, 0, 0)


    def setup_nbiter(self):

        self.nbiter_widget = QWidget()
        self.nbiter_widget_layout = QHBoxLayout(self.nbiter_widget)

        nbiter_label = QLabel("Number of iterations")

        self.nbiter_line_edit = QLineEdit()
        self.nbiter_line_edit.setFixedWidth(100)
        self.nbiter_line_edit.setText(self.nbiter)

        self.nbiter_widget_layout.addWidget(nbiter_label)
        self.nbiter_widget_layout.addStretch()
        self.nbiter_widget_layout.addWidget(self.nbiter_line_edit)

        self.ifta_params_widget_layout.addWidget(self.nbiter_widget, 1, 0)


    def setup_extras(self):

        self.efficiency_checkbox = QCheckBox("Compute efficiency")
        self.efficiency_checkbox.setChecked(int(self.compute_efficiency))

        self.ifta_params_widget_layout.addWidget(self.efficiency_checkbox, 0,1)

        self.uniformity_checkbox = QCheckBox("Compute uniformity")
        self.uniformity_checkbox.setChecked(int(self.compute_uniformity))

        self.ifta_params_widget_layout.addWidget(self.uniformity_checkbox, 1,1)


    def setup_npy_importer(self):

        self.npy_import_widget = QWidget()
        self.npy_import_widget_layout = QHBoxLayout(self.npy_import_widget)

        file_label = QLabel("Select a seed file")

        self.npy_file_line_edit = QLineEdit()
        self.npy_file_button = QToolButton()

        icon = self.style().standardIcon(QStyle.SP_DirOpenIcon)
        self.npy_file_button.setIcon(icon)

        self.npy_import_widget_layout.addWidget(file_label)
        self.npy_import_widget_layout.addStretch()
        self.npy_import_widget_layout.addWidget(self.npy_file_line_edit)
        self.npy_import_widget_layout.addWidget(self.npy_file_button)
        self.ifta_params_widget_layout.addWidget(self.npy_import_widget)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", "All Files (*);;(*.npy)"
        )
        if file_path:
            self.npy_file_line_edit.setText(file_path)
            self.npy_path = file_path
        else: 
            self.npy_path = None
            self.seed = 0
            self.npy_file_line_edit.setText("")



    def setup_connections(self):
        self.sim_button.clicked.connect(self.sim_EOD)        
        self.npy_file_button.clicked.connect(self.browse_file)
        self.efficiency_checkbox.stateChanged.connect(self.sync_inputs)
        self.uniformity_checkbox.stateChanged.connect(self.sync_inputs)
        self.rfact_line_edit.textChanged.connect(self.sync_inputs)
        self.nbiter_line_edit.textChanged.connect(self.sync_inputs)

    
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

    def sync_inputs(self):
        self.rfact = self.rfact_line_edit.text()
        self.nbiter = self.nbiter_line_edit.text()
        
        self.compute_efficiency = 1 if self.efficiency_checkbox.isChecked() else 0
        self.compute_uniformity = 1 if self.uniformity_checkbox.isChecked() else 0
        print(self.get_inputs())

    
    def get_inputs(self):
        return {
            "rfact" : self.rfact,
            "nbiter" : self.nbiter,
            "compute_uniformity" : self.compute_uniformity,
            "compute_efficiency" : self.compute_efficiency,
            "npy_path" : self.npy_path, 
        }
                


        



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DOEDesignSimulation()
    window.show()
    app.exec()

    

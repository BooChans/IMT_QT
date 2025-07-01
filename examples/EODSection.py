import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QCheckBox,
    QSplitter, QLabel, QSlider, QGridLayout,QGraphicsLineItem, QComboBox, QLineEdit, QHBoxLayout, QFileDialog, QStyle, QToolButton, QPushButton
)
from PyQt5.QtCore import Qt
import pyqtgraph as pg
import sys
import matplotlib.pyplot as plt

from DiffractionSection import RealTimeCrossSectionViewer
from diffraction_propagation import far_field, angular_spectrum

class EODSection(QWidget):

    def __init__(self):
        super().__init__()

        self.EOD_shape = ("512", "512") 
        self.sampling = "1.0"
        self.nbiter = "25"
        self.rfact = "1.2"
        self.nlevels = "0"
        self.seed = 0
        self.compute_efficiency = 0
        self.compute_uniformity = 0

        self.distance_unit = "µm"
        self.simulation_distance = "1e6"
        self.wavelength = "0.633"
        self.sampling = "1.0"
        self.tile = "1"

        self.efficiency = None 
        self.uniformity = None 
        self.npy_path = None

        volume = np.ones((512, 512))
        self.volume = np.repeat(volume[np.newaxis, :, :], 1, axis=0)
        self.graph_view = RealTimeCrossSectionViewer(self.volume)

        self.setup_ui()

    def setup_ui(self):

        splitter = QSplitter(Qt.Horizontal)

        self.left = QWidget()
        self.page_layout = QVBoxLayout(self.left)

        self.setup_rfact()
        self.setup_nlevels()
        self.setup_nbiter()
        self.setup_npy_importer()
        self.setup_extras()
        self.setup_simulation()
        self.setup_eod_propagation_widget()
        self.setup_connections()

        splitter.addWidget(self.left)
        splitter.addWidget(self.graph_view)

        splitter.setSizes([200, 800])

        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(splitter)        

    def setup_rfact(self):

        self.rfact_widget = QWidget()
        self.rfact_widget_layout = QHBoxLayout(self.rfact_widget)

        rfact_label = QLabel("Reinforcement factor")

        self.rfact_line_edit = QLineEdit()
        self.rfact_line_edit.setFixedWidth(100)
        self.rfact_line_edit.setText(self.rfact)

        self.rfact_widget_layout.addWidget(rfact_label)
        self.rfact_widget_layout.addStretch()
        self.rfact_widget_layout.addWidget(self.rfact_line_edit)

        self.page_layout.addWidget(self.rfact_widget)

    def setup_nlevels(self):

        self.nlevels_widget = QWidget()
        self.nlevels_widget_layout = QHBoxLayout(self.nlevels_widget)

        nlevels_label = QLabel("Number of levels")

        self.nlevels_line_edit = QLineEdit()
        self.nlevels_line_edit.setFixedWidth(100)
        self.nlevels_line_edit.setText(self.nlevels)

        self.nlevels_widget_layout.addWidget(nlevels_label)
        self.nlevels_widget_layout.addStretch()
        self.nlevels_widget_layout.addWidget(self.nlevels_line_edit)

        self.page_layout.addWidget(self.nlevels_widget)

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

        self.page_layout.addWidget(self.nbiter_widget)


    def setup_extras(self):

        self.efficiency_checkbox = QCheckBox("Compute efficiency")
        self.efficiency_checkbox.setChecked(int(self.compute_efficiency))

        self.page_layout.addWidget(self.efficiency_checkbox)

        self.uniformity_checkbox = QCheckBox("Compute uniformity")
        self.uniformity_checkbox.setChecked(int(self.compute_uniformity))

        self.page_layout.addWidget(self.uniformity_checkbox)


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
        self.page_layout.addWidget(self.npy_import_widget)

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

    def setup_unit(self):

        self.unit_widget = QWidget()
        self.unit_widget_layout = QHBoxLayout(self.unit_widget)

        unit_label = QLabel("Select the distance unit")

        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["µm", "mm", "m"])
        self.unit_combo.setCurrentText(self.distance_unit)

        self.unit_widget_layout.addWidget(unit_label)
        self.unit_widget_layout.addStretch()
        self.unit_widget_layout.addWidget(self.unit_combo)

        self.sim_widget_layout.addWidget(self.unit_widget)

    def setup_wavelength(self):
               
        #Units definition
        self.wavelength_widget = QWidget()
        self.wavelength_widget_layout = QHBoxLayout(self.wavelength_widget)

        wavelength_label = QLabel("Select the wavelength")

        self.wavelength_line_edit = QLineEdit()
        self.wavelength_line_edit.setFixedWidth(100)
        self.wavelength_line_edit.setText(self.wavelength)

        self.wavelength_widget_layout.addWidget(wavelength_label)
        self.wavelength_widget_layout.addStretch()
        self.wavelength_widget_layout.addWidget(self.wavelength_line_edit)

        self.sim_widget_layout.addWidget(self.wavelength_widget)
    
    def setup_simulation_distance(self):
        #Units definition
        self.distance_simulation_widget = QWidget()
        self.distance_simulation_widget_layout = QHBoxLayout(self.distance_simulation_widget)

        dst_sim_label = QLabel("Select the simulation distance")

        self.dst_sim_line_edit = QLineEdit()
        self.dst_sim_line_edit.setFixedWidth(100)
        self.dst_sim_line_edit.setText(self.simulation_distance)

        self.distance_simulation_widget_layout.addWidget(dst_sim_label)
        self.distance_simulation_widget_layout.addStretch()
        self.distance_simulation_widget_layout.addWidget(self.dst_sim_line_edit)

        self.sim_widget_layout.addWidget(self.distance_simulation_widget)

    def setup_sampling(self):
        self.sampling_widget = QWidget()
        self.sampling_widget_layout = QHBoxLayout(self.sampling_widget)

        sampling_label = QLabel("Select the sampling")

        self.sampling_line_edit = QLineEdit()
        self.sampling_line_edit.setFixedWidth(100)
        self.sampling_line_edit.setText(self.sampling)

        self.sampling_widget_layout.addWidget(sampling_label)
        self.sampling_widget_layout.addStretch()
        self.sampling_widget_layout.addWidget(self.sampling_line_edit) 

        self.sim_widget_layout.addWidget(self.sampling_widget)      

    def setup_simulation(self):
        self.page_layout.addSpacing(10)
        self.page_layout.addWidget(QLabel("EOD Simulation"))
        self.sim_checkbox = QCheckBox("Allow simulation")
        self.page_layout.addWidget(self.sim_checkbox)


    def setup_eod_propagation_widget(self):


        self.sim_widget = QWidget()
        self.sim_widget_layout = QVBoxLayout(self.sim_widget)


        self.setup_unit()
        self.setup_simulation_distance()
        self.setup_wavelength()
        self.setup_sampling()
        self.setup_tile()

        self.launch_sim_button = QPushButton("Run propagation simulation with EOD")
        self.sim_widget_layout.addWidget(self.launch_sim_button)
        self.page_layout.addWidget(self.sim_widget)
        self.sim_widget.hide()

    def run_eod_propagation(self):
        try:
            print("in the try of the sim") 
            U0 = np.exp(-1j*self.volume[-1])
            tile = int(self.tile)
            tile_shape = (tile, tile)
            U0 = np.tile(U0, tile_shape)
            z = float(self.simulation_distance)
            dx = float(self.sampling)
            wavelength = float(self.wavelength)
            try:
                volume = far_field(U0, z, dx, wavelength)
                sampling = self.pixout(U0, wavelength, z, dx)
            except:
                volume = angular_spectrum(U0, z, dx, wavelength)
                sampling = dx
            self.graph_view.sampling = float(self.sampling)
            print(self.sampling, "sampling")
            print(volume.shape)
            if len(volume.shape) != 3:
                volume = np.repeat(volume[np.newaxis, :, :], 1, 0)
            init_volume = np.zeros_like(volume)
            self.result_window = RealTimeCrossSectionViewer(init_volume)
            self.result_window.sampling = sampling
            self.result_window.update_data(volume)
            self.result_window.setWindowTitle("EOD Propagation")
            self.result_window.show()
        except Exception as e:
            print(f"Error in the setup : {e}")

    
    def update_simulation_visibility(self, state):
        if state == Qt.Checked: 
            self.sim_widget.show()
        else: 
            self.sim_widget.hide()
        
    def sync_inputs(self):
        self.rfact = self.rfact_line_edit.text()
        self.nlevels = self.nlevels_line_edit.text()
        self.distance_unit = self.unit_combo.currentText()
        self.simulation_distance = self.dst_sim_line_edit.text()
        self.sampling = self.sampling_line_edit.text()
        self.graph_view.sampling = float(self.sampling)
        self.graph_view.update_data(self.volume)
        self.wavelength = self.wavelength_line_edit.text()
        self.nbiter = self.nbiter_line_edit.text()
        self.tile = self.tile_combo.currentText()
        
        self.compute_efficiency = 1 if self.efficiency_checkbox.isChecked() else 0
        self.compute_uniformity = 1 if self.uniformity_checkbox.isChecked() else 0


    
    def get_inputs(self):
        return {
            "EOD_shape" : self.EOD_shape, 
            "rfact" : self.rfact,
            "nlevels" : self.nlevels, 
            "nbiter" : self.nbiter,
            "distance_unit" : self.distance_unit,
            "wavelength" : self.wavelength,
            "simulation_distance" : self.simulation_distance,
            "sampling" : self.sampling,
            "compute_efficiency" : self.compute_efficiency, 
            "compute_uniformity" : self.compute_uniformity,
            "npy_path" : self.npy_path, 
            "volume" : self.volume,
            "tile" :  self.tile
        }

    def setup_tile(self):
        self.tile_widget = QWidget()
        self.tile_widget_layout = QHBoxLayout(self.tile_widget)

        tile_label = QLabel("Select tiling")

        self.tile_combo = QComboBox()
        self.tile_combo.addItems(["1", "2", "4", "8"])
        self.tile_combo.setCurrentText(self.tile)

        self.tile_widget_layout.addWidget(tile_label)
        self.tile_widget_layout.addStretch()
        self.tile_widget_layout.addWidget(self.tile_combo)

        self.sim_widget_layout.addWidget(self.tile_widget)

    def setup_connections(self):
        self.npy_file_button.clicked.connect(self.browse_file)
        self.sim_checkbox.stateChanged.connect(self.update_simulation_visibility)

        self.launch_sim_button.clicked.connect(self.run_eod_propagation)

        self.rfact_line_edit.textChanged.connect(self.sync_inputs)
        self.nlevels_line_edit.textChanged.connect(self.sync_inputs)
        self.dst_sim_line_edit.textChanged.connect(self.sync_inputs)
        self.sampling_line_edit.textChanged.connect(self.sync_inputs)
        self.efficiency_checkbox.stateChanged.connect(self.sync_inputs)
        self.uniformity_checkbox.stateChanged.connect(self.sync_inputs)
        self.wavelength_line_edit.textChanged.connect(self.sync_inputs)
        self.unit_combo.currentTextChanged.connect(self.sync_inputs)
        self.nbiter_line_edit.textChanged.connect(self.sync_inputs)
        self.tile_combo.currentTextChanged.connect(self.sync_inputs)


    def pixout(self, source, wavelength, z, dx):
        N = max(source.shape)
        pixout_ = wavelength * abs(z) / (N * dx)
        return pixout_
    


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = EODSection()
    window.show()

    app.exec()
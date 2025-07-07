import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QCheckBox,
    QSplitter, QLabel, QSlider, QGridLayout,QGraphicsLineItem, QComboBox, QLineEdit, QHBoxLayout, QFileDialog, QStyle, QToolButton, QPushButton, QRadioButton
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
        self.rfact = "1.2"
        self.nlevels = "0"
        self.seed = 0
        self.compute_efficiency = 0
        self.compute_uniformity = 0

        self.distance_unit = "µm"
        self.simulation_distance = "1e6"
        self.wavelength = "0.633"
        self.tile = "1"

        self.transmittance = "Phase"

        volume = np.ones((512, 512))
        self.volume = np.repeat(volume[np.newaxis, :, :], 1, axis=0)
        self.graph_view = RealTimeCrossSectionViewer(self.volume)
        self.setup_ui()

    def setup_ui(self):

        self.page_layout = QVBoxLayout(self)
        self.page_layout.addWidget(QLabel("DOE Transmittance"))
        self.page_layout.addWidget(self.graph_view)

        self.setup_unit()
        self.setup_nlevels()
        self.setup_simulation_distance()
        self.setup_wavelength()
        self.setup_sampling()
        self.setup_tile()
        self.setup_EOD_widget()
        self.setup_amp_pha()

        self.setup_grid()

        self.setup_connections()



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



    def setup_EOD_widget(self):
        
        self.EOD_widget = QWidget()
        self.EOD_widget_layout = QHBoxLayout(self.EOD_widget)

        eod_shape_label = QLabel("DOE period")
        EOD_shape = self.EOD_shape

        EOD_x_label = QLabel("x")


        self.eod_h_shape_line_edit = QLineEdit()
        self.eod_h_shape_line_edit.setFixedWidth(100)
        self.eod_h_shape_line_edit.setText(EOD_shape[0])

        self.eod_w_shape_line_edit = QLineEdit()
        self.eod_w_shape_line_edit.setFixedWidth(100)
        self.eod_w_shape_line_edit.setText(EOD_shape[1])

        self.EOD_widget_layout.addWidget(eod_shape_label)
        self.EOD_widget_layout.addStretch()
        self.EOD_widget_layout.addWidget(self.eod_h_shape_line_edit)
        self.EOD_widget_layout.addWidget(EOD_x_label)
        self.EOD_widget_layout.addWidget(self.eod_w_shape_line_edit)



    def setup_unit(self):

        self.unit_widget = QWidget()
        self.unit_widget_layout = QHBoxLayout(self.unit_widget)

        unit_label = QLabel("Distance unit")

        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["µm", "mm", "m"])
        self.unit_combo.setCurrentText(self.distance_unit)

        self.unit_widget_layout.addWidget(unit_label)
        self.unit_widget_layout.addStretch()
        self.unit_widget_layout.addWidget(self.unit_combo)


    def setup_wavelength(self):
               
        #Units definition
        self.wavelength_widget = QWidget()
        self.wavelength_widget_layout = QHBoxLayout(self.wavelength_widget)

        wavelength_label = QLabel("Wavelength")

        self.wavelength_line_edit = QLineEdit()
        self.wavelength_line_edit.setFixedWidth(100)
        self.wavelength_line_edit.setText(self.wavelength)

        self.wavelength_widget_layout.addWidget(wavelength_label)
        self.wavelength_widget_layout.addStretch()
        self.wavelength_widget_layout.addWidget(self.wavelength_line_edit)

    
    def setup_simulation_distance(self):
        #Units definition
        self.distance_simulation_widget = QWidget()
        self.distance_simulation_widget_layout = QHBoxLayout(self.distance_simulation_widget)

        dst_sim_label = QLabel("Simulation distance")

        self.dst_sim_line_edit = QLineEdit()
        self.dst_sim_line_edit.setFixedWidth(100)
        self.dst_sim_line_edit.setText(self.simulation_distance)

        self.distance_simulation_widget_layout.addWidget(dst_sim_label)
        self.distance_simulation_widget_layout.addStretch()
        self.distance_simulation_widget_layout.addWidget(self.dst_sim_line_edit)


    def setup_sampling(self):
        self.sampling_widget = QWidget()
        self.sampling_widget_layout = QHBoxLayout(self.sampling_widget)

        sampling_label = QLabel("Pixel size")

        self.sampling_line_edit = QLineEdit()
        self.sampling_line_edit.setFixedWidth(100)
        self.sampling_line_edit.setText(self.sampling)

        self.sampling_widget_layout.addWidget(sampling_label)
        self.sampling_widget_layout.addStretch()
        self.sampling_widget_layout.addWidget(self.sampling_line_edit) 



    def setup_amp_pha(self):
        self.amp_pha_widget = QWidget()
        self.amp_pha_widget_layout = QHBoxLayout(self.amp_pha_widget)

        transmittance_label = QLabel("Transmittance")

        self.transmittance_combo = QComboBox()
        self.transmittance_combo.addItems(["Phase", "Amplitude"])
        self.transmittance_combo.setCurrentText(self.transmittance)

        self.amp_pha_widget_layout.addWidget(transmittance_label)
        self.amp_pha_widget_layout.addStretch()
        self.amp_pha_widget_layout.addWidget(self.transmittance_combo)


    def setup_grid(self):
        self.params_widget = QWidget()
        self.params_widget_layout = QGridLayout(self.params_widget)

        self.params_widget_layout.addWidget(self.unit_widget, 0, 0)
        self.params_widget_layout.addWidget(self.sampling_widget, 1, 0)      
        self.params_widget_layout.addWidget(self.wavelength_widget, 2, 0)
        self.params_widget_layout.addWidget(self.distance_simulation_widget, 3, 0)

        self.params_widget_layout.addWidget(self.EOD_widget, 0, 1)
        self.params_widget_layout.addWidget(self.nlevels_widget, 1, 1)
        self.params_widget_layout.addWidget(self.amp_pha_widget, 2, 1)
        self.params_widget_layout.addWidget(self.tile_widget, 3, 1)

        self.page_layout.addWidget(self.params_widget)



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


        
    def sync_inputs(self):
        self.nlevels = self.nlevels_line_edit.text()
        self.distance_unit = self.unit_combo.currentText()
        self.simulation_distance = self.dst_sim_line_edit.text()
        self.sampling = self.sampling_line_edit.text()
        self.graph_view.sampling = float(self.sampling)
        self.graph_view.update_data(self.volume)
        self.wavelength = self.wavelength_line_edit.text()
        self.tile = self.tile_combo.currentText()

        eod_h = self.eod_h_shape_line_edit.text()
        eod_w = self.eod_w_shape_line_edit.text()
        self.EOD_shape = (eod_h, eod_w)

        self.transmittance = self.transmittance_combo.currentText()



    
    def get_inputs(self):
        return {
            "EOD_shape" : self.EOD_shape, 
            "nlevels" : self.nlevels, 
            "distance_unit" : self.distance_unit,
            "wavelength" : self.wavelength,
            "simulation_distance" : self.simulation_distance,
            "sampling" : self.sampling,
            "volume" : self.volume,
            "tile" :  self.tile,
            "transmittance" : self.transmittance
        }

    def setup_tile(self):
        self.tile_widget = QWidget()
        self.tile_widget_layout = QHBoxLayout(self.tile_widget)

        tile_label = QLabel("Tiling")

        self.tile_combo = QComboBox()
        self.tile_combo.addItems(["1", "2", "4", "8"])
        self.tile_combo.setCurrentText(self.tile)

        self.tile_widget_layout.addWidget(tile_label)
        self.tile_widget_layout.addStretch()
        self.tile_widget_layout.addWidget(self.tile_combo)


    def setup_connections(self):


        self.nlevels_line_edit.textChanged.connect(self.sync_inputs)
        self.dst_sim_line_edit.textChanged.connect(self.sync_inputs)
        self.sampling_line_edit.textChanged.connect(self.sync_inputs)
        self.wavelength_line_edit.textChanged.connect(self.sync_inputs)
        self.unit_combo.currentTextChanged.connect(self.sync_inputs)
        self.tile_combo.currentTextChanged.connect(self.sync_inputs)

        self.eod_h_shape_line_edit.textChanged.connect(self.sync_inputs)
        self.eod_w_shape_line_edit.textChanged.connect(self.sync_inputs)
        self.transmittance_combo.currentTextChanged.connect(self.sync_inputs)


    def pixout(self, source, wavelength, z, dx):
        N = max(source.shape)
        pixout_ = wavelength * abs(z) / (N * dx)
        return pixout_
    


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = EODSection()
    window.show()

    app.exec()
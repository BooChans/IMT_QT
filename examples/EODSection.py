import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QVBoxLayout, QWidget,
    QLabel, QGridLayout, QComboBox, QLineEdit, QHBoxLayout
)
import sys

from DiffractionSection import RealTimeCrossSectionViewer

class EODSection(QWidget):

    def __init__(self):
        super().__init__()

        self.EOD_shape = ("512", "512")
        self.sampling = "1.0"
        self.rfact = "1.2"
        self.nlevels = "4"
        self.seed = 0
        self.compute_efficiency = 0
        self.compute_uniformity = 0

        self.distance_unit = "µm"

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
        self.setup_sampling()
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
        self.nlevels_widget_layout.addSpacing(20)
        self.nlevels_widget_layout.addWidget(self.nlevels_line_edit)
        self.nlevels_widget_layout.addStretch()



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
        self.EOD_widget_layout.addSpacing(20)
        self.EOD_widget_layout.addWidget(self.eod_h_shape_line_edit)
        self.EOD_widget_layout.addWidget(EOD_x_label)
        self.EOD_widget_layout.addWidget(self.eod_w_shape_line_edit)
        self.EOD_widget_layout.addStretch()



    def setup_unit(self):

        self.unit_widget = QWidget()
        self.unit_widget_layout = QHBoxLayout(self.unit_widget)

        unit_label = QLabel("Distance unit")

        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["µm", "mm", "m"])
        self.unit_combo.setCurrentText(self.distance_unit)

        self.unit_widget_layout.addWidget(unit_label)
        self.unit_widget_layout.addSpacing(20)
        self.unit_widget_layout.addWidget(self.unit_combo)
        self.unit_widget_layout.addStretch()

    


    def setup_sampling(self):
        self.sampling_widget = QWidget()
        self.sampling_widget_layout = QHBoxLayout(self.sampling_widget)

        sampling_label = QLabel("Pixel size")

        self.sampling_line_edit = QLineEdit()
        self.sampling_line_edit.setFixedWidth(100)
        self.sampling_line_edit.setText(self.sampling)

        self.sampling_widget_layout.addWidget(sampling_label)
        self.sampling_widget_layout.addSpacing(20)
        self.sampling_widget_layout.addWidget(self.sampling_line_edit) 
        self.sampling_widget_layout.addStretch()



    def setup_amp_pha(self):
        self.amp_pha_widget = QWidget()
        self.amp_pha_widget_layout = QHBoxLayout(self.amp_pha_widget)

        transmittance_label = QLabel("Transmittance")

        self.transmittance_combo = QComboBox()
        self.transmittance_combo.addItems(["Phase", "Amplitude"])
        self.transmittance_combo.setCurrentText(self.transmittance)

        self.amp_pha_widget_layout.addWidget(transmittance_label)
        self.amp_pha_widget_layout.addSpacing(20)
        self.amp_pha_widget_layout.addWidget(self.transmittance_combo)
        self.amp_pha_widget_layout.addStretch()


    def setup_grid(self):
        self.params_widget = QWidget()
        self.params_widget_layout = QGridLayout(self.params_widget)

        self.params_widget_layout.addWidget(self.unit_widget, 0, 0)
        self.params_widget_layout.addWidget(self.sampling_widget, 1, 0)      

        self.params_widget_layout.addWidget(self.EOD_widget, 0, 1)
        self.params_widget_layout.addWidget(self.nlevels_widget, 1, 1)
        self.params_widget_layout.addWidget(self.amp_pha_widget, 2, 0)

        self.page_layout.addWidget(self.params_widget)


        
    def sync_inputs(self):
        self.nlevels = self.nlevels_line_edit.text()
        self.distance_unit = self.unit_combo.currentText()
        self.sampling = self.sampling_line_edit.text()
        self.graph_view.sampling = float(self.sampling)
        self.graph_view.update_data(self.graph_view.volume)

        eod_h = self.eod_h_shape_line_edit.text()
        eod_w = self.eod_w_shape_line_edit.text()
        self.EOD_shape = (eod_h, eod_w)

        self.transmittance = self.transmittance_combo.currentText()



    
    def get_inputs(self):
        return {
            "EOD_shape" : self.EOD_shape, 
            "nlevels" : self.nlevels, 
            "distance_unit" : self.distance_unit,
            "sampling" : self.sampling,
            "volume" : self.volume,
            "transmittance" : self.transmittance
        }


    def setup_connections(self):


        self.nlevels_line_edit.textChanged.connect(self.sync_inputs)
        self.sampling_line_edit.textChanged.connect(self.sync_inputs)
        self.unit_combo.currentTextChanged.connect(self.sync_inputs)

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
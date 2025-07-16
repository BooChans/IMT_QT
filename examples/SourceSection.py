import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QCheckBox,
    QSplitter, QLabel, QSlider, QGridLayout, QRadioButton, QComboBox, QLineEdit,QHBoxLayout,
)
from PyQt5.QtCore import Qt
import pyqtgraph as pg
from pyqtgraph import LineSegmentROI, InfiniteLine
from scipy.ndimage import map_coordinates
import sys

from DiffractionSection import RealTimeCrossSectionViewer
from sources import gaussian_beam, plane_wave_elliptical, plane_wave_rectangular, converging_spherical_wave
from automatic_sizing import auto_sampling_N

class SourceSection(QWidget):
    def __init__(self):
        super().__init__()
        self.source_type = "Plane Wave"
        self.wavelength = "0.633"
        self.beam_shape = "Rectangular"
        self.distance_unit = "µm"
        self.waist = "300"
        self.sampling = "1.0" #µm 
        self.array_shape = ("512","512")
        self.focal_length = "1e3"

        self.light_source = plane_wave_rectangular(shape=tuple(map(int,self.array_shape)))
        self.light_source = np.repeat(self.light_source[np.newaxis, :, :], 1, axis=0)
        self.graph_widget = RealTimeCrossSectionViewer(self.light_source)
        self.graph_widget.update_data(self.light_source)
        self.graph_widget.slice_view.setLevels(0,1)

        #hide histogram and roiPlot
        self.graph_widget.slice_view.ui.roiPlot.hide()
        self.graph_widget.slice_view.ui.histogram.hide()
        self.graph_widget.toggle_line_cb.hide()

        #hide display mode widget - display of the volume : intensity, amplitude, phase, log amplitude.
        self.graph_widget.display_widget.hide()


        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        
        self.page_layout = QVBoxLayout(self)
        self.page_layout.addWidget(QLabel("Illumination"))
        self.page_layout.addWidget(self.graph_widget)

        self.setup_unit_widget()
        self.setup_spec_widget()
        self.setup_beam_widget()
        self.setup_focal_length_widget()
        self.setup_beam_shape()



    def setup_unit_widget(self):
        #Units definition
        self.unit_widget = QWidget()
        self.unit_widget_layout = QHBoxLayout(self.unit_widget)

        label = QLabel("Select the distance unit")

        self.unit_combo = QComboBox()
        self.unit_combo.setFixedWidth(150) 
        self.unit_combo.addItems(["µm","mm","m"])
        self.unit_combo.setCurrentText(self.distance_unit)


        self.unit_widget_layout.addWidget(label)
        self.unit_widget_layout.addSpacing(20)
        self.unit_widget_layout.addWidget(self.unit_combo)
        self.unit_widget_layout.addStretch()

        self.page_layout.addWidget(self.unit_widget)
    def setup_spec_widget(self):
        #Spectral characteristics
        self.spec_widget = QWidget()
        self.spec_widget_layout = QHBoxLayout(self.spec_widget)

        wavelength_label = QLabel("Wavelength")
        self.wavelength_line_edit = QLineEdit()
        self.wavelength_line_edit.setText(self.wavelength)
        self.wavelength_line_edit.setFixedWidth(150)

        self.spec_widget_layout.addWidget(wavelength_label)
        self.spec_widget_layout.addSpacing(20)
        self.spec_widget_layout.addWidget(self.wavelength_line_edit)
        self.spec_widget_layout.addStretch()

        self.page_layout.addWidget(self.spec_widget)
    def setup_beam_widget(self):
        #Beam type
        self.beam_label_widget = QWidget()
        self.beam_label_widget_layout = QHBoxLayout(self.beam_label_widget)
        beam_label = QLabel("Beam shape")
        self.beam_label_widget_layout.addWidget(beam_label)

        self.option1 = QRadioButton("Plane wave")
        self.option2 = QRadioButton("Gaussian beam")
        self.option3 = QRadioButton("Converging spherical wave")

        self.option1.setChecked(True)  


        self.beam_label_widget_layout.addSpacing(20)
        self.beam_label_widget_layout.addWidget(self.option1)
        self.beam_label_widget_layout.addWidget(self.option2)
        self.beam_label_widget_layout.addWidget(self.option3)
        self.beam_label_widget_layout.addStretch()



        self.page_layout.addWidget(self.beam_label_widget)
    def setup_beam_shape(self):
        # Widgets for Gaussian Beam
        self.gaussian_widget = QWidget()
        self.gaussian_widget_layout = QHBoxLayout(self.gaussian_widget)
        self.gaussian_widget_layout.addWidget(QLabel("Beam waist"))
        self.gaussian_widget_layout.addSpacing(20)
        self.beam_waist_line_edit = QLineEdit()
        self.beam_waist_line_edit.setFixedWidth(100)
        self.beam_waist_line_edit.setText(self.waist)
        self.gaussian_widget_layout.addWidget(self.beam_waist_line_edit)
        self.gaussian_widget_layout.addStretch()
        self.page_layout.addWidget(self.gaussian_widget)

        self.page_layout.addWidget(self.gaussian_widget)
        self.update_beam_widgets()
    def setup_connections(self):
        self.option1.toggled.connect(self.update_beam_widgets)
        self.option2.toggled.connect(self.update_beam_widgets)
        self.option3.toggled.connect(self.update_beam_widgets)

        # Connect signals for live attribute updating
        self.option1.toggled.connect(self.update_attributes)
        self.option2.toggled.connect(self.update_attributes)
        self.option3.toggled.connect(self.update_attributes)
        self.unit_combo.currentIndexChanged.connect(self.update_attributes)
        self.wavelength_line_edit.textChanged.connect(self.update_attributes)
        self.beam_waist_line_edit.textChanged.connect(self.update_attributes)
        self.focal_length_line_edit.textChanged.connect(self.update_attributes)

        self.option1.toggled.connect(self.update_graph)
        self.option2.toggled.connect(self.update_graph)
        self.option3.toggled.connect(self.update_graph)
        self.unit_combo.currentIndexChanged.connect(self.update_graph)
        self.wavelength_line_edit.textChanged.connect(self.update_graph)

        self.beam_waist_line_edit.textChanged.connect(self.update_graph)
        self.focal_length_line_edit.textChanged.connect(self.update_graph)

        self.wavelength_line_edit.editingFinished.connect(self.update_color)
        self.update_color()

    def update_beam_widgets(self):
        if self.option1.isChecked():
            self.gaussian_widget.hide()
            self.focal_length_widget.hide()
        elif self.option2.isChecked():
            self.gaussian_widget.show()
            self.focal_length_widget.hide()
        else:
            self.gaussian_widget.hide()
            self.focal_length_widget.show()

    def update_attributes(self):
        # Update your widget's attributes here:
        if self.option1.isChecked():
            self.source_type = "Plane Wave"
        elif self.option2.isChecked():
            self.source_type = "Gaussian beam"
        else:
            self.source_type = "Converging spherical wave"
        self.distance_unit = self.unit_combo.currentText()
        self.wavelength = self.wavelength_line_edit.text()
        self.focal_length = self.focal_length_line_edit.text()
        if self.source_type == "Plane Wave":
            self.waist = None
        else:
            beam_waist = self.beam_waist_line_edit.text()
            self.waist = beam_waist


    def get_inputs(self):
        self.update_attributes()
        return {
            "source_type": self.source_type,
            "beam_shape": self.beam_shape,
            "unit": self.distance_unit,
            "wavelength": self.wavelength,
            "beam waist" : self.waist,
            "focal_length" : self.focal_length
        }
    def update_graph(self):
        inputs = self.get_inputs()
        self.graph_widget.sampling = float(self.sampling)
        dx = float(self.sampling)  # sampling step, adjust if you want to link to physical unit scaling
        if inputs["source_type"] == "Plane Wave":
            array_shape = tuple(map(int, self.array_shape))
            shape = array_shape  # Fixed pixel resolution for your grid — can be parameterized
            new_source = plane_wave_rectangular(shape=shape)

            # Add batch dimension for compatibility
            new_source = np.expand_dims(new_source, axis=0)

        elif inputs["source_type"] == "Gaussian beam":
            # Gaussian beam generation with waist
            try:
                waist = float(inputs["beam waist"])
            except Exception as e:
                print("Invalid beam waist:", e)
                return

            base_source = gaussian_beam(w0=waist)
            new_source = np.expand_dims(base_source, axis=0)

        else: 
            try:
                array_shape = tuple(map(int, self.array_shape))
                shape = array_shape
                focal_length = float(inputs['focal_length'])
                wavelength = float(inputs['wavelength'])
                base_source = converging_spherical_wave(shape=shape, wavelength=wavelength, focal_length=focal_length, dx = float(self.sampling))
                new_source = np.expand_dims(base_source, axis=0)
            except Exception as e:
                print("Invalid params for converging parameters :", e)
                return
    
        # Update graph widget with new source data
        self.light_source = new_source
        self.graph_widget.update_data(new_source)
        self.graph_widget.slice_view.setLevels(0,1)


    def setup_focal_length_widget(self):
        self.focal_length_widget = QWidget()
        self.focal_length_widget_layout = QHBoxLayout(self.focal_length_widget)

        self.focal_length_widget_layout.addWidget(QLabel("Focal length"))
        self.focal_length_widget_layout.addSpacing(20)
        self.focal_length_line_edit = QLineEdit()
        self.focal_length_line_edit.setText(self.focal_length)
        self.focal_length_widget_layout.addStretch()
        self.focal_length_line_edit.setFixedWidth(100)

        self.focal_length_widget_layout.addWidget(self.focal_length_line_edit)
        
        self.page_layout.addWidget(self.focal_length_widget)


    def wavelength_to_rgb(self,wavelength):
        """
        Convert a wavelength in nm (380 to 750) to an RGB color.
        Returns an array [R,G,B] with values 0-255.
        """
        if wavelength >= 380 and wavelength <= 750:
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
            color = np.array([R, G, B, 1], dtype=np.uint8)
        else:
            color = np.array([0, 0, 0, 0])
        return color
    
    def update_color(self):
        conversion = {"µm":1e3, "mm": 1e6, "m": 1e9}
        wavelength = float(self.wavelength) 
        wavelength = wavelength * conversion[self.distance_unit]
        color = self.wavelength_to_rgb(wavelength)

        R,G,B,V = color

        if V == 1:
            lut = np.zeros((256, 3), dtype=np.uint8)
            lut[:, 0] = np.linspace(0, R, 256)  
            lut[:, 1] = np.linspace(0, G, 256)  
            lut[:, 2] = np.linspace(0, B, 256)  

            self.graph_widget.slice_view.setColorMap(pg.ColorMap(pos=np.linspace(0,1,256), color=lut))
        else: 
            gray_lut = pg.ColorMap(pos=[0, 1], color=[[0, 0, 0], [255, 255, 255]])
            self.graph_widget.slice_view.setColorMap(gray_lut)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = SourceSection()
    widget.show()
    app.exec()
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
from sources import gaussian_beam, plane_wave_elliptical, plane_wave_rectangular
from automatic_sizing import auto_sizing_sampling

class SourceSection(QWidget):
    def __init__(self):
        super().__init__()
        self.source_type = "Plane Wave"
        self.wavelength = "0.633"
        self.beam_shape = "Elliptic"
        self.size = ("300","300")
        self.distance_unit = "µm"
        self.waist = "300"

        self.light_source = plane_wave_elliptical(size=tuple(map(int, self.size)))
        self.light_source = np.repeat(self.light_source[np.newaxis, :, :], 1, axis=0)
        self.graph_widget = RealTimeCrossSectionViewer(self.light_source)

        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        
        self.page_layout = QVBoxLayout(self)
        self.page_layout.addWidget(self.graph_widget)

        self.setup_unit_widget()
        self.setup_spec_widget()
        self.setup_beam_widget()
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
        self.unit_widget_layout.addWidget(self.unit_combo)


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
        self.spec_widget_layout.addWidget(self.wavelength_line_edit)

        self.page_layout.addWidget(self.spec_widget)
    def setup_beam_widget(self):
        #Beam type
        self.beam_label_widget = QWidget()
        self.beam_label_widget_layout = QHBoxLayout(self.beam_label_widget)
        beam_label = QLabel("Beam shape")
        self.beam_label_widget_layout.addWidget(beam_label)

        self.option1 = QRadioButton("Plane wave")
        self.option2 = QRadioButton("Gaussian beam")

        self.option1.setChecked(True)  


        self.beam_label_widget_layout.addStretch()
        self.beam_label_widget_layout.addWidget(self.option1)
        self.beam_label_widget_layout.addWidget(self.option2)


        self.page_layout.addWidget(self.beam_label_widget)
    def setup_beam_shape(self):
        # Widgets for Plane Wave
        self.plane_wave_widget = QWidget()
        self.plane_wave_layout = QVBoxLayout(self.plane_wave_widget)
        
        self.plane_wave_shape_widget = QWidget()
        self.plane_wave_shape_layout = QHBoxLayout(self.plane_wave_shape_widget)

        shape_label = QLabel("Shape")

        self.option_e = QRadioButton("Elliptic")
        self.option_r = QRadioButton("Rectangular")
        
        self.option_e.setChecked(True)  

        self.plane_wave_shape_layout.addWidget(shape_label)
        self.plane_wave_shape_layout.addStretch()
        self.plane_wave_shape_layout.addWidget(self.option_e)
        self.plane_wave_shape_layout.addWidget(self.option_r)
        
        self.plane_wave_size_widget = QWidget()
        self.plane_wave_size_layout = QHBoxLayout(self.plane_wave_size_widget)
        diameter_label = QLabel("Diameter")

        self.hdiameter_line_edit = QLineEdit()
        self.hdiameter_line_edit.setFixedWidth(100)
        self.hdiameter_line_edit.setText(self.size[0])
        x_label = QLabel("x")

        self.wdiameter_line_edit = QLineEdit()
        self.wdiameter_line_edit.setFixedWidth(100)     
        self.wdiameter_line_edit.setText(self.size[0])

        self.plane_wave_size_layout.addWidget(diameter_label)
        self.plane_wave_size_layout.addStretch()
        self.plane_wave_size_layout.addWidget(self.hdiameter_line_edit)
        self.plane_wave_size_layout.addWidget(x_label)
        self.plane_wave_size_layout.addWidget(self.wdiameter_line_edit)

        self.plane_wave_layout.addWidget(self.plane_wave_shape_widget)
        self.plane_wave_layout.addWidget(self.plane_wave_size_widget)
        self.page_layout.addWidget(self.plane_wave_widget)

        # Widgets for Gaussian Beam
        self.gaussian_widget = QWidget()
        self.gaussian_widget_layout = QHBoxLayout(self.gaussian_widget)
        self.gaussian_widget_layout.addWidget(QLabel("Beam waist"))
        self.gaussian_widget_layout.addStretch()
        self.beam_waist_line_edit = QLineEdit()
        self.beam_waist_line_edit.setFixedWidth(100)
        self.beam_waist_line_edit.setText(self.waist)
        self.gaussian_widget_layout.addWidget(self.beam_waist_line_edit)
        self.page_layout.addWidget(self.gaussian_widget)

        self.page_layout.addWidget(self.gaussian_widget)
        self.update_beam_widgets()
    def setup_connections(self):
        self.option1.toggled.connect(self.update_beam_widgets)
        self.option2.toggled.connect(self.update_beam_widgets)

        # Connect signals for live attribute updating
        self.option1.toggled.connect(self.update_attributes)
        self.option2.toggled.connect(self.update_attributes)
        self.option_e.toggled.connect(self.update_attributes)
        self.option_r.toggled.connect(self.update_attributes)
        self.unit_combo.currentIndexChanged.connect(self.update_attributes)
        self.wavelength_line_edit.textChanged.connect(self.update_attributes)
        self.hdiameter_line_edit.textChanged.connect(self.update_attributes)
        self.wdiameter_line_edit.textChanged.connect(self.update_attributes)
        self.beam_waist_line_edit.textChanged.connect(self.update_attributes)
        self.option1.toggled.connect(self.update_graph)
        self.option2.toggled.connect(self.update_graph)
        self.option_e.toggled.connect(self.update_graph)
        self.option_r.toggled.connect(self.update_graph)
        self.unit_combo.currentIndexChanged.connect(self.update_graph)
        self.wavelength_line_edit.textChanged.connect(self.update_graph)
        self.hdiameter_line_edit.textChanged.connect(self.update_graph)
        self.wdiameter_line_edit.textChanged.connect(self.update_graph)
        self.beam_waist_line_edit.textChanged.connect(self.update_graph)

    def update_beam_widgets(self):
        if self.option1.isChecked():
            self.plane_wave_widget.show()
            self.gaussian_widget.hide()
        elif self.option2.isChecked():
            self.plane_wave_widget.hide()
            self.gaussian_widget.show()
        else:
            self.plane_wave_widget.hide()
            self.gaussian_widget.hide()

    def update_attributes(self):
        inputs = self.get_inputs()
        # Update your widget's attributes here:
        self.source_type = inputs["source_type"]
        self.beam_shape = inputs["beam_shape"]
        self.distance_unit = inputs["unit"]
        self.wavelength = inputs["wavelength"]
        self.size = inputs["size"]
        self.waist = inputs["beam waist"]

    def get_inputs(self):
        self.source_type = "Plane Wave" if self.option1.isChecked() else "Gaussian Beam"
        self.beam_shape = "Elliptic" if self.option_e.isChecked() else "Rectangular"
        self.distance_unit = self.unit_combo.currentText()
        self.wavelength = self.wavelength_line_edit.text()
        if self.source_type == "Plane Wave":
            diameter_h = self.hdiameter_line_edit.text()
            diameter_w = self.wdiameter_line_edit.text()
            self.size = (diameter_h, diameter_w)
            self.waist = None
        else:
            beam_waist = self.beam_waist_line_edit.text()
            self.waist = beam_waist
            self.size = (beam_waist, beam_waist)


        return {
            "source_type": self.source_type,
            "beam_shape": self.beam_shape,
            "unit": self.distance_unit,
            "wavelength": self.wavelength,
            "size": self.size,
            "beam waist" : self.waist
        }
    def update_graph(self):
        inputs = self.get_inputs()
        try:
            dx = 1  # sampling step, adjust if you want to link to physical unit scaling
            
            if inputs["source_type"] == "Plane Wave":
                # Extract physical size from inputs
                # size = (height, width) in physical units for apertures
                try:
                    h_size = float(inputs["size"][0])
                    w_size = float(inputs["size"][1])
                except Exception as e:
                    print("Invalid size input:", e)
                    return

                shape = (512, 512)  # Fixed pixel resolution for your grid — can be parameterized

                if inputs["beam_shape"] == "Elliptic":
                    new_source = plane_wave_elliptical(shape=shape, size=(h_size, w_size), dx=dx)
                else:
                    new_source = plane_wave_rectangular(shape=shape, size=(h_size, w_size), dx=dx)

                # Add batch dimension for compatibility
                new_source = np.expand_dims(new_source, axis=0)

            else:
                # Gaussian beam generation with waist
                try:
                    waist = float(inputs["beam waist"])
                except Exception as e:
                    print("Invalid beam waist:", e)
                    return

                base_source = gaussian_beam(w0=waist)
                new_source = np.expand_dims(base_source, axis=0)

            # Update graph widget with new source data
            self.light_source = new_source
            self.graph_widget.update_data(new_source)

        except Exception as e:
            print("Error updating graph:", e)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = SourceSection()
    widget.show()
    app.exec()
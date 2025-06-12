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
from apertures import elliptical_aperture, rectangular_aperture, elliptical_aperture_array, square_aperture_array, slit_apeture, estimate_aperture_extent

class ApertureSection(QWidget):
    def __init__(self):
        super().__init__()
        #basic shape details
        self.aperture_shape = "Elliptic"
        self.array_shape = ("512", "512")
        self.aperture_size = ("150","150") 


        #slit shape details
        self.slit_width = "2"
        self.slit_distance = "10"


        #array aperture details
        self.array_matrix = ("5","5")
        self.array_spacing = "20"
        self.big_diameter = "10"
        self.small_diameter = "5" 
        self.square_size = "5"

        self.distance_unit = "µm"

        self.simulation_distance = "1e6" #µm
        self.sampling = "1.0" #µm


        self.aperture = elliptical_aperture(size = tuple(map(int, self.aperture_size)))
        self.aperture = np.repeat(self.aperture[np.newaxis, :, :], 1, axis=0)
        self.graph_widget = RealTimeCrossSectionViewer(self.aperture)
        self.setup_ui()

    def setup_ui(self):

        self.page_layout = QVBoxLayout(self)
        self.page_layout.addWidget(QLabel("Diffracting object"))
        self.page_layout.addWidget(self.graph_widget)

        self.setup_unit_widget()
        self.setup_simulation_distance()
        self.setup_aperture_shape()
        self.setup_aperture_details()

        self.setup_connections()

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


        self.page_layout.addWidget(self.distance_simulation_widget)    

    def setup_aperture_shape(self):

        shape_label = QLabel("Select the aperture shape")

        self.shape_widget = QWidget()
        self.shape_widget_layout = QHBoxLayout(self.shape_widget)
        self.shape_combo = QComboBox()
        self.shape_combo.addItems(["Elliptic", "Rectangular", "Slit", "Elliptic array", "Square array"])
        self.shape_combo.setCurrentText(self.aperture_shape)

        self.shape_widget_layout.addWidget(shape_label)
        self.shape_widget_layout.addStretch()
        self.shape_widget_layout.addWidget(self.shape_combo)
        self.page_layout.addWidget(self.shape_widget)
    def setup_aperture_details(self):
        #Widgets for Elliptical and Square (Simple aperture)
        self.simple_aperture_widget = QWidget() #for alignment
        self.simple_aperture_widget_layout = QHBoxLayout(self.simple_aperture_widget)
        self.simple_aperture_widget_ = QWidget()
        self.simple_aperture_widget_layout_ = QHBoxLayout(self.simple_aperture_widget_)

        simple_label = QLabel("Select the size of the aperture")

        self.simple_size_h_line_edit = QLineEdit()
        self.simple_size_h_line_edit.setText(self.aperture_size[0])
        self.simple_size_h_line_edit.setFixedWidth(100)
    
        self.simple_size_w_line_edit = QLineEdit()
        self.simple_size_w_line_edit.setText(self.aperture_size[1])
        self.simple_size_w_line_edit.setFixedWidth(100)
        simple_x_label = QLabel("x")


        self.simple_aperture_widget_layout_.addWidget(simple_label)
        self.simple_aperture_widget_layout_.addStretch()
        self.simple_aperture_widget_layout_.addWidget(self.simple_size_h_line_edit)
        self.simple_aperture_widget_layout_.addWidget(simple_x_label)
        self.simple_aperture_widget_layout_.addWidget(self.simple_size_w_line_edit)

        self.simple_aperture_widget_layout.addWidget(self.simple_aperture_widget_)
        self.page_layout.addWidget(self.simple_aperture_widget)

        #Widget for Slit

        self.slit_aperture_widget = QWidget()
        self.slit_aperture_widget_layout = QVBoxLayout(self.slit_aperture_widget)

        self.slit_size_widget = QWidget()
        self.slit_size_widget_layout = QHBoxLayout(self.slit_size_widget)
        slit_label = QLabel("Select the size of the aperture")

        self.slit_size_h_line_edit = QLineEdit()
        self.slit_size_h_line_edit.setText(self.aperture_size[0])
        self.slit_size_h_line_edit.setFixedWidth(100)

    
        self.slit_size_w_line_edit = QLineEdit()
        self.slit_size_w_line_edit.setText(self.aperture_size[1])
        self.slit_size_w_line_edit.setFixedWidth(100)
        slit_x_label = QLabel("x")


        self.slit_size_widget_layout.addWidget(slit_label)
        self.slit_size_widget_layout.addStretch()
        self.slit_size_widget_layout.addWidget(self.slit_size_h_line_edit)
        self.slit_size_widget_layout.addWidget(slit_x_label)
        self.slit_size_widget_layout.addWidget(self.slit_size_w_line_edit)

        self.slit_width_widget = QWidget()
        self.slit_width_widget_layout = QHBoxLayout(self.slit_width_widget)
        self.slit_distance_widget = QWidget()
        self.slit_distance_widget_layout = QHBoxLayout(self.slit_distance_widget)
        slit_width_label = QLabel("Select the width of one slit W")
        slit_distance_label = QLabel("Select the distance between two slits d")

        self.slit_width_line_edit = QLineEdit()
        self.slit_width_line_edit.setText(self.slit_width)
        self.slit_width_line_edit.setFixedWidth(100)
    
        self.slit_distance_line_edit = QLineEdit()
        self.slit_distance_line_edit.setText(self.slit_distance)
        self.slit_distance_line_edit.setFixedWidth(100)


        self.slit_width_widget_layout.addWidget(slit_width_label)
        self.slit_width_widget_layout.addStretch()
        self.slit_width_widget_layout.addWidget(self.slit_width_line_edit)

        self.slit_distance_widget_layout.addWidget(slit_distance_label)
        self.slit_distance_widget_layout.addStretch()
        self.slit_distance_widget_layout.addWidget(self.slit_distance_line_edit)

        self.slit_aperture_widget_layout.addWidget(self.slit_size_widget)
        self.slit_aperture_widget_layout.addWidget(self.slit_width_widget)
        self.slit_aperture_widget_layout.addWidget(self.slit_distance_widget)
        self.page_layout.addWidget(self.slit_aperture_widget)   

        #Widget for Arrays

        self.array_aperture_widget = QWidget()
        self.array_aperture_widget_layout = QVBoxLayout(self.array_aperture_widget)

        self.array_matrix_widget = QWidget()
        self.array_matrix_widget_layout = QHBoxLayout(self.array_matrix_widget)
        matrix_label = QLabel("Matrix array size")

        self.matrix_h_line_edit = QLineEdit()
        self.matrix_h_line_edit.setFixedWidth(100)
        self.matrix_h_line_edit.setText(self.array_matrix[0])

        self.matrix_w_line_edit = QLineEdit()
        self.matrix_w_line_edit.setFixedWidth(100)
        self.matrix_w_line_edit.setText(self.array_matrix[1])

        array_x_label = QLabel("x")

        self.array_matrix_widget_layout.addWidget(matrix_label)
        self.array_matrix_widget_layout.addStretch()
        self.array_matrix_widget_layout.addWidget(self.matrix_h_line_edit)
        self.array_matrix_widget_layout.addWidget(array_x_label)
        self.array_matrix_widget_layout.addWidget(self.matrix_w_line_edit)

        self.matrix_spacing_widget = QWidget()
        self.matrix_spacing_widget_layout = QHBoxLayout(self.matrix_spacing_widget)
        matrix_spacing = QLabel("Spacing")

        self.matrix_spacing_line_edit = QLineEdit()
        self.matrix_spacing_line_edit.setFixedWidth(100)
        self.matrix_spacing_line_edit.setText(self.array_spacing)


        self.matrix_spacing_widget_layout.addWidget(matrix_spacing)
        self.matrix_spacing_widget_layout.addStretch()
        self.matrix_spacing_widget_layout.addWidget(self.matrix_spacing_line_edit)


        self.array_aperture_widget_layout.addWidget(self.array_matrix_widget)
        self.array_aperture_widget_layout.addWidget(self.matrix_spacing_widget)
        self.page_layout.addWidget(self.array_aperture_widget)

        
        

        self.hel_bd_widget = QWidget()
        self.hel_bd_widget_layout = QHBoxLayout(self.hel_bd_widget)

        self.hel_sd_widget = QWidget()
        self.hel_sd_widget_layout = QHBoxLayout(self.hel_sd_widget)

        hel_array_big_diameter = QLabel("Big diameter")
        hel_array_small_diameter = QLabel("Small diameter")

        self.hel_bd_line_edit = QLineEdit()
        self.hel_bd_line_edit.setFixedWidth(100)
        self.hel_bd_line_edit.setText(self.big_diameter)

        self.hel_sd_line_edit = QLineEdit()
        self.hel_sd_line_edit.setFixedWidth(100)
        self.hel_sd_line_edit.setText(self.small_diameter)

        self.hel_bd_widget_layout.addWidget(hel_array_big_diameter)
        self.hel_bd_widget_layout.addStretch()
        self.hel_bd_widget_layout.addWidget(self.hel_bd_line_edit)

        self.hel_sd_widget_layout.addWidget(hel_array_small_diameter)
        self.hel_sd_widget_layout.addStretch()
        self.hel_sd_widget_layout.addWidget(self.hel_sd_line_edit)

        self.array_aperture_widget_layout.addWidget(self.hel_bd_widget)
        self.array_aperture_widget_layout.addWidget(self.hel_sd_widget)

        #Square details
        self.squ_array_widget = QWidget() #alignment
        self.squ_array_widget_layout = QHBoxLayout(self.squ_array_widget)


        squ_label = QLabel("Square size")

        self.squ_square_size_line_edit = QLineEdit()
        self.squ_square_size_line_edit.setFixedWidth(100)
        self.squ_square_size_line_edit.setText(self.square_size)

        self.squ_array_widget_layout.addWidget(squ_label)
        self.squ_array_widget_layout.addStretch()
        self.squ_array_widget_layout.addWidget(self.squ_square_size_line_edit)

        self.array_aperture_widget_layout.addWidget(self.squ_array_widget)


    def setup_connections(self):
        self.shape_combo.currentTextChanged.connect(self.update_aperture_shape_specifications)
        self.update_aperture_shape_specifications(self.aperture_shape)

        self.unit_combo.currentTextChanged.connect(self.update_aperture_graph)
        self.dst_sim_line_edit.textChanged.connect(self.update_aperture_graph)

        # Simple aperture
        self.simple_size_h_line_edit.textChanged.connect(self.update_aperture_graph)
        self.simple_size_w_line_edit.textChanged.connect(self.update_aperture_graph)

        # Slit aperture
        self.slit_size_h_line_edit.textChanged.connect(self.update_aperture_graph)
        self.slit_size_w_line_edit.textChanged.connect(self.update_aperture_graph)
        self.slit_width_line_edit.textChanged.connect(self.update_aperture_graph)
        self.slit_distance_line_edit.textChanged.connect(self.update_aperture_graph)

        # Array aperture
        self.matrix_h_line_edit.textChanged.connect(self.update_aperture_graph)
        self.matrix_w_line_edit.textChanged.connect(self.update_aperture_graph)
        self.matrix_spacing_line_edit.textChanged.connect(self.update_aperture_graph)

        self.hel_bd_line_edit.textChanged.connect(self.update_aperture_graph)
        self.hel_sd_line_edit.textChanged.connect(self.update_aperture_graph)
        self.squ_square_size_line_edit.textChanged.connect(self.update_aperture_graph)        

    def update_aperture_shape_specifications(self, text):
        
        # Hide all widgets first
        self.simple_aperture_widget.hide()
        self.slit_aperture_widget.hide()
        self.array_aperture_widget.hide()
        self.hel_bd_widget.hide()
        self.hel_sd_widget.hide()
        self.squ_array_widget.hide()
        
        # Show only the relevant widgets
        if text == "Elliptic" or text == "Rectangular":  # Fixed condition
            self.simple_aperture_widget.show()
        elif text == "Slit":
            self.slit_aperture_widget.show()
        elif text == "Elliptic array":
            self.array_aperture_widget.show()
            self.hel_bd_widget.show()
            self.hel_sd_widget.show()
        elif text == "Square array":
            self.array_aperture_widget.show()
            self.squ_array_widget.show()
        self.update_aperture_graph()

    def get_inputs(self):
        """Collect all aperture parameters based on current selection"""
        self.aperture_shape = self.shape_combo.currentText()
        self.distance_unit = self.unit_combo.currentText()
        self.simulation_distance = self.dst_sim_line_edit.text()
        # Common aperture size parameters
        self.aperture_size = (
            self.simple_size_h_line_edit.text() if self.aperture_shape in ["Elliptic", "Rectangular"] 
            else self.slit_size_h_line_edit.text(),
            self.simple_size_w_line_edit.text() if self.aperture_shape in ["Elliptic", "Rectangular"] 
            else self.slit_size_w_line_edit.text()
        )
        
        # Shape-specific parameters
        if self.aperture_shape == "Slit":
            self.slit_width = self.slit_width_line_edit.text()
            self.slit_distance = self.slit_distance_line_edit.text()
        elif self.aperture_shape == "Elliptic array":
            self.big_diameter = self.hel_bd_line_edit.text()
            self.small_diameter = self.hel_sd_line_edit.text()
        elif self.aperture_shape == "Square array":
            self.square_size = self.squ_square_size_line_edit.text()
        
        # Array parameters (common for both array types)
        if "array" in self.aperture_shape.lower():
            self.array_matrix = (
                self.matrix_h_line_edit.text(),
                self.matrix_w_line_edit.text()
            )
            self.array_spacing = self.matrix_spacing_line_edit.text()
            Mh = int(self.matrix_h_line_edit.text())
            Mw = int(self.matrix_w_line_edit.text())
            spacing = float(self.matrix_spacing_line_edit.text())

            if self.aperture_shape == "Square array":
                aperture_size = float(self.squ_square_size_line_edit.text())
            elif self.aperture_shape == "Elliptic array":
                aperture_size = float(self.hel_bd_line_edit.text())
            else:
                aperture_size = 0  # fallback if needed

            height = (Mh - 1) * spacing + aperture_size
            width  = (Mw - 1) * spacing + aperture_size

            self.aperture_size = (str(height), str(width))

        return {
            "aperture_shape": self.aperture_shape,
            "distance_unit": self.distance_unit,
            "simulation_distance" : self.simulation_distance,
            "aperture_size": self.aperture_size,
            "slit_width": self.slit_width,
            "slit_distance": self.slit_distance,
            "array_matrix": self.array_matrix,
            "array_spacing": self.array_spacing,
            "big_diameter": self.big_diameter,
            "small_diameter": self.small_diameter,
            "square_size": self.square_size
        }
    def generate_aperture(self):
        params = self.get_inputs()
        shape = params["aperture_shape"]
        array_shape = tuple(map(int,self.array_shape))
        dx = float(self.sampling)
        if shape == "Elliptic":
            size = tuple(map(int, params["aperture_size"]))
            assert max(size) < max((dx*array_shape[0], dx*array_shape[1]))
            return elliptical_aperture(shape=array_shape,size=size, dx = dx)

        elif shape == "Rectangular":
            size = tuple(map(int, params["aperture_size"]))
            assert max(size) < max((dx*array_shape[0], dx*array_shape[1]))
            return rectangular_aperture(shape=array_shape,size=size, dx=dx)

        elif shape == "Slit":
            size = tuple(map(int, self.aperture_size))
            width = int(params["slit_width"])
            distance = int(params["slit_distance"])
            assert max(size) < max((dx*array_shape[0], dx*array_shape[1]))
            return slit_apeture(shape=array_shape,size=size, d=distance, W=width, dx=dx)

        elif shape == "Elliptic array":
            matrix = tuple(map(int, params["array_matrix"]))
            spacing = int(params["array_spacing"])
            big_d = int(params["big_diameter"])
            small_d = int(params["small_diameter"])
            new_size = estimate_aperture_extent(big_diameter=big_d,small_diameter=small_d, spacing=spacing, grid_size=matrix)
            assert max(new_size) < max((dx*array_shape[0], dx*array_shape[1]))
            self.aperture_size = tuple(map(str,new_size))
            return elliptical_aperture_array(shape=array_shape,grid_size=matrix, spacing=spacing, big_diameter=big_d, small_diameter=small_d, dx=dx)

        elif shape == "Square array":
            matrix = tuple(map(int, params["array_matrix"]))
            spacing = int(params["array_spacing"])
            square_size = int(params["square_size"])
            new_size = estimate_aperture_extent(big_diameter=square_size,small_diameter=square_size, spacing=spacing, grid_size=matrix)
            assert max(new_size) < max((dx*array_shape[0], dx*array_shape[1]))
            self.aperture_size = tuple(map(str,new_size))
            return square_aperture_array(shape=array_shape,grid_size=matrix, spacing=spacing, square_size=square_size, dx=dx)
              
    def update_aperture_graph(self):
        self.sync_attributes_from_widgets()  # sync attributes from widgets before generating aperture
        aperture = self.generate_aperture()
        self.aperture = np.repeat(aperture[np.newaxis, :, :], 1, axis=0)
        self.graph_widget.update_data(self.aperture)

    def sync_attributes_from_widgets(self):
        self.aperture_shape = self.shape_combo.currentText()
        self.distance_unit = self.unit_combo.currentText()
        self.simulation_distance = self.dst_sim_line_edit.text()
        self.graph_widget.sampling = float(self.sampling)


        if self.aperture_shape in ["Elliptic", "Rectangular"]:
            self.aperture_size = (self.simple_size_h_line_edit.text(), self.simple_size_w_line_edit.text())
        elif self.aperture_shape == "Slit":
            self.aperture_size = (self.slit_size_h_line_edit.text(), self.slit_size_w_line_edit.text())
            self.slit_width = self.slit_width_line_edit.text()
            self.slit_distance = self.slit_distance_line_edit.text()
        elif self.aperture_shape == "Elliptic array":
            self.array_matrix = (self.matrix_h_line_edit.text(), self.matrix_w_line_edit.text())
            self.array_spacing = self.matrix_spacing_line_edit.text()
            self.big_diameter = self.hel_bd_line_edit.text()
            self.small_diameter = self.hel_sd_line_edit.text()
        elif self.aperture_shape == "Square array":
            self.array_matrix = (self.matrix_h_line_edit.text(), self.matrix_w_line_edit.text())
            self.array_spacing = self.matrix_spacing_line_edit.text()
            self.square_size = self.squ_square_size_line_edit.text()
        if "array" in self.aperture_shape.lower():
            self.array_matrix = (
                self.matrix_h_line_edit.text(),
                self.matrix_w_line_edit.text()
            )
            self.array_spacing = self.matrix_spacing_line_edit.text()
            Mh = int(self.matrix_h_line_edit.text())
            Mw = int(self.matrix_w_line_edit.text())
            spacing = float(self.matrix_spacing_line_edit.text())

            if self.aperture_shape == "Square array":
                aperture_size = float(self.squ_square_size_line_edit.text())
            elif self.aperture_shape == "Elliptic array":
                aperture_size = float(self.hel_bd_line_edit.text())
            else:
                aperture_size = 0  # fallback if needed

            height = (Mh - 1) * spacing + aperture_size
            width  = (Mw - 1) * spacing + aperture_size

            self.aperture_size = (str(height), str(width))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = ApertureSection()
    widget.show()
    app.exec()
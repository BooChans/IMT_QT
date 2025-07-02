import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QCheckBox,
    QSplitter, QLabel, QSlider, QGridLayout,QGraphicsLineItem, QComboBox, QLineEdit, QHBoxLayout, QFileDialog, QStyle, QToolButton
)
from PyQt5.QtCore import Qt
import pyqtgraph as pg
import sys
import matplotlib.pyplot as plt

from DiffractionSection import RealTimeCrossSectionViewer
from apertures import elliptical_aperture, rectangular_aperture
from automatic_sizing import auto_sampling_N_2, auto_sampling_dx_2, zero_pad
from PIL import Image

class ImageSection(QWidget):
    def __init__(self):
        super().__init__()
        #basic shape details, all units in µm

        self.image_shape = "Image"
        self.matrix_array_shape = ("512", "512")
        self.img_size_in_matrix = ("256", "256")


        #for circle and rectangle
        self.image_size = ("300", "300") 
        self.distance_unit = "µm"
        self.img_path = None

        self.offset_x = "0"
        self.offset_y = "0"

        self.sampling = "1.0"



        matrix_size = tuple(map(int, self.matrix_array_shape))
        image = np.zeros(matrix_size)
        self.image = np.repeat(image[np.newaxis, :, :], 1, axis=0)
        self.graph_widget = RealTimeCrossSectionViewer(self.image)
        self.graph_widget.display_widget.hide()

        self.setup_ui()

    def setup_ui(self):

        self.page_layout = QVBoxLayout(self)
        self.page_layout.addWidget(QLabel("Target image"))
        self.page_layout.addWidget(self.graph_widget)
        self.setup_image_importer()
        self.setup_unit()
        self.setup_matrix_shape()
        self.setup_img_shape()
        self.setup_offset()
        self.setup_shape() #unused - to remove
        self.setup_shape_dimensions()
        self.update_gui_combo(self.image_shape)
        self.setup_connections()

    
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

        self.page_layout.addWidget(self.unit_widget)
    

    def setup_shape(self):

        self.shape_widget = QWidget()
        self.shape_widget_layout = QHBoxLayout(self.shape_widget)

        self.combo = QComboBox()
        self.combo.addItems(["Elliptic", "Rectangular", "Image"])
        self.combo.setCurrentText(self.image_shape)

        setup_label = QLabel("Select an image shape")

        self.shape_widget_layout.addWidget(setup_label)
        self.shape_widget_layout.addStretch()
        self.shape_widget_layout.addWidget(self.combo)

        self.page_layout.addWidget(self.shape_widget)
        self.shape_widget.hide()

    
    def setup_matrix_shape(self):

        self.array_shape_widget = QWidget()
        self.array_shape_widget_layout = QHBoxLayout(self.array_shape_widget)

        array_shape_label = QLabel("Define the matrix shape")
        array_shape = self.matrix_array_shape

        shape_x_label = QLabel("x")


        self.h_shape_line_edit = QLineEdit()
        self.h_shape_line_edit.setFixedWidth(100)
        self.h_shape_line_edit.setText(array_shape[0])

        self.w_shape_line_edit = QLineEdit()
        self.w_shape_line_edit.setFixedWidth(100)
        self.w_shape_line_edit.setText(array_shape[1])

        self.array_shape_widget_layout.addWidget(array_shape_label)
        self.array_shape_widget_layout.addStretch()
        self.array_shape_widget_layout.addWidget(self.h_shape_line_edit)
        self.array_shape_widget_layout.addWidget(shape_x_label)
        self.array_shape_widget_layout.addWidget(self.w_shape_line_edit)

        self.page_layout.addWidget(self.array_shape_widget)
    

    def setup_img_shape(self):

        self.img_shape_widget = QWidget()
        self.img_shape_widget_layout = QHBoxLayout(self.img_shape_widget)

        image_shape_label = QLabel("Define the image shape")
        image_shape = self.img_size_in_matrix

        img_shape_x_label = QLabel("x")


        self.h_img_shape_line_edit = QLineEdit()
        self.h_img_shape_line_edit.setFixedWidth(100)
        self.h_img_shape_line_edit.setText(image_shape[0])

        self.w_img_shape_line_edit = QLineEdit()
        self.w_img_shape_line_edit.setFixedWidth(100)
        self.w_img_shape_line_edit.setText(image_shape[1])

        self.img_shape_widget_layout.addWidget(image_shape_label)
        self.img_shape_widget_layout.addStretch()
        self.img_shape_widget_layout.addWidget(self.h_img_shape_line_edit)
        self.img_shape_widget_layout.addWidget(img_shape_x_label)
        self.img_shape_widget_layout.addWidget(self.w_img_shape_line_edit)

        self.page_layout.addWidget(self.img_shape_widget)
    

    def setup_offset(self):

        self.offset_widget = QWidget()
        self.offset_widget_layout = QHBoxLayout(self.offset_widget)

        offset_label = QLabel("Offset x y")

        self.offset_x_line_edit = QLineEdit()
        self.offset_x_line_edit.setFixedWidth(100)
        self.offset_x_line_edit.setText(self.offset_x)

        self.offset_y_line_edit = QLineEdit()
        self.offset_y_line_edit.setFixedWidth(100)
        self.offset_y_line_edit.setText(self.offset_y)

        self.offset_widget_layout.addWidget(offset_label)
        self.offset_widget_layout.addStretch()
        self.offset_widget_layout.addWidget(self.offset_x_line_edit)
        self.offset_widget_layout.addWidget(self.offset_y_line_edit)

        self.page_layout.addWidget(self.offset_widget)
        

    def setup_shape_dimensions(self):

        self.shape_dimensions_widget = QWidget()
        self.shape_dimensions_widget_layout = QHBoxLayout(self.shape_dimensions_widget)

        dimensions_label = QLabel("Define the size of the object")

        shape_dimensions_x_label = QLabel("x")

        size = self.image_size

        self.h_size_line_edit = QLineEdit()
        self.h_size_line_edit.setFixedWidth(100)
        self.h_size_line_edit.setText(size[0])

        self.w_size_line_edit = QLineEdit()
        self.w_size_line_edit.setFixedWidth(100)
        self.w_size_line_edit.setText(size[1])

        self.shape_dimensions_widget_layout.addWidget(dimensions_label)
        self.shape_dimensions_widget_layout.addStretch()
        self.shape_dimensions_widget_layout.addWidget(self.h_size_line_edit)
        self.shape_dimensions_widget_layout.addWidget(shape_dimensions_x_label)
        self.shape_dimensions_widget_layout.addWidget(self.w_size_line_edit)

        self.page_layout.addWidget(self.shape_dimensions_widget)

    def setup_image_importer(self):

        self.img_import_widget = QWidget()
        self.img_import_widget_layout = QHBoxLayout(self.img_import_widget)

        file_label = QLabel("Select an image file")

        self.img_file_line_edit = QLineEdit()
        self.img_file_button = QToolButton()

        icon = self.style().standardIcon(QStyle.SP_DirOpenIcon)
        self.img_file_button.setIcon(icon)

        self.img_import_widget_layout.addWidget(file_label)
        self.img_import_widget_layout.addStretch()
        self.img_import_widget_layout.addWidget(self.img_file_line_edit)
        self.img_import_widget_layout.addWidget(self.img_file_button)
        self.img_import_widget.hide()
        self.page_layout.addWidget(self.img_import_widget)
    

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", "All Files (*);;(*.jpg);; (*.png);; (*.bmp);; (*.tiff)"
        )
        if file_path:
            self.img_file_line_edit.setText(file_path)
            self.img_path = file_path
            self.update_graph()
        else: 
            file_path = None
            self.img_file_line_edit.setText("")

    def setup_connections(self):
        self.img_file_button.clicked.connect(self.browse_file)

        self.combo.currentTextChanged.connect(self.update_graph)
        self.combo.currentTextChanged.connect(self.update_gui_combo)
        self.unit_combo.currentTextChanged.connect(self.update_graph)

        self.h_shape_line_edit.textChanged.connect(self.update_graph)
        self.w_shape_line_edit.textChanged.connect(self.update_graph)
        self.h_size_line_edit.textChanged.connect(self.update_graph)
        self.w_size_line_edit.textChanged.connect(self.update_graph)



    def get_inputs(self):
        self.image_shape = self.combo.currentText()
        self.matrix_array_shape = (self.h_shape_line_edit.text(), self.w_shape_line_edit.text())
        self.image_size = (self.h_size_line_edit.text(), self.w_size_line_edit.text())
        self.distance_unit = self.unit_combo.currentText()
        self.graph_widget.sampling = float(self.sampling)

        return {
            "image_shape" : self.image_shape,
            "matrix_array_shape" : self.matrix_array_shape,
            "image_shape_size" : self.image_size,
            "distance_unit" : self.distance_unit,
            "sampling" : self.sampling, 
            "img_path" : self.img_path,
            "image" : self.image
        }

    def generate_image(self):
        image_params = self.get_inputs()
        image_shape_size = tuple(map(int, image_params['image_shape_size']))
        matrix_array_shape = tuple(map(int, image_params['matrix_array_shape']))
        image_shape = image_params['image_shape']
        dx = float(self.sampling)
        if image_shape == "Elliptic":
            return elliptical_aperture(shape = matrix_array_shape, size = image_shape_size, dx=dx)
        if image_shape == "Rectangular":
            return rectangular_aperture(shape = matrix_array_shape, size= image_shape_size, dx = dx)
        if image_shape == "Image":
            return self.open_image()

    def update_graph(self):
        image = self.generate_image()
        self.image = np.repeat(image[np.newaxis, :, :], 1, axis=0)
        self.graph_widget.update_data(self.image)
    def open_image(self):
        img = Image.open(self.img_path).convert("L")
        matrix_array_shape = tuple(map(int, self.matrix_array_shape))
        img_size_in_array = tuple(map(int, self.img_size_in_matrix))
        img.thumbnail(img_size_in_array,Image.LANCZOS)
        img = np.array(img)
        img = img/img.max()
        img = zero_pad(np.array([img]), matrix_array_shape).squeeze()
        return img

    def update_gui_combo(self, text):
        self.img_import_widget.hide()
        self.shape_dimensions_widget.hide()
        
        if text == "Image":
            self.img_import_widget.show()
        else: 
            self.shape_dimensions_widget.show()

    def update_pixel_size(self):
        self.sampling = self.sampling_line_edit.text()
        self.graph_widget.sampling = float(self.sampling)
        self.graph_widget.update_data(self.graph_widget.volume)



        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    section = ImageSection()
    section.show()

    app.exec()

import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QCheckBox,
    QSplitter, QLabel, QSlider, QGridLayout,QGraphicsLineItem, QComboBox, QLineEdit, QHBoxLayout, QFileDialog, QStyle, QToolButton
)
from PyQt5.QtCore import Qt
import pyqtgraph as pg
import sys

from DiffractionSection import RealTimeCrossSectionViewer
from apertures import elliptical_aperture, rectangular_aperture
from automatic_sizing import auto_sampling_N_2, auto_sampling_dx_2

class ImageSection(QWidget):
    def __init__(self):
        super().__init__()
        #basic shape details, all units in µm

        self.image_shape = "Elliptic"
        self.image_array_shape = ("512", "512")
        self.image_size = ("512", "512") 
        self.distance_unit = "µm"
        self.img_path = None

        self.sampling = 1.0


        image_array_shape = tuple(map(int, self.image_array_shape))
        image_size = tuple(map(int, self.image_size))
        sampling = float(self.sampling)

        image = elliptical_aperture(shape = image_array_shape, size = image_size, dx = sampling)
        self.image = np.repeat(image[np.newaxis, :, :], 1, axis=0)
        self.graph_widget = RealTimeCrossSectionViewer(self.image)



        self.setup_ui()

    def setup_ui(self):

        self.page_layout = QVBoxLayout(self)
        self.page_layout.addWidget(self.graph_widget)
        self.setup_unit()
        self.setup_array_shape()
        self.setup_shape()
        self.setup_shape_dimensions()
        self.setup_image_importer()
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
    
    def setup_array_shape(self):

        self.array_shape_widget = QWidget()
        self.array_shape_widget_layout = QHBoxLayout(self.array_shape_widget)

        array_shape_label = QLabel("Define the array shape")
        array_shape = self.image_array_shape

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

        self.page_layout.addWidget(self.img_import_widget)
    

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", "All Files (*);;Text Files (*.txt)"
        )
        if file_path:
            self.img_file_line_edit.setText(file_path)

    def setup_connections(self):
        self.img_file_button.clicked.connect(self.browse_file)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    section = ImageSection()
    section.show()

    app.exec()

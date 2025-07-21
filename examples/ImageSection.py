import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QVBoxLayout, QWidget,
    QLabel, QComboBox, QLineEdit, QHBoxLayout, QFileDialog, QStyle, QToolButton
)

import sys

from DiffractionSection import RealTimeCrossSectionViewer
from apertures import elliptical_aperture, rectangular_aperture
from automatic_sizing import zero_pad
from PIL import Image
import os
import tifffile 

class ImageSection(QWidget):
    def __init__(self):
        super().__init__()
        #basic shape details, all units in µm

        self.image_shape = "Image"
        self.matrix_array_shape = ("512", "512")


        #for circle and rectangle
        self.image_size = ("300", "300") 
        self.distance_unit = "µm"
        self.img_path = None

        self.offset_x = "0"
        self.offset_y = "0"

        self.sampling = "1.0"



        matrix_size = tuple(map(int, self.matrix_array_shape))
        image = np.ones(matrix_size)
        self.image = np.repeat(image[np.newaxis, :, :], 1, axis=0)
        self.graph_widget = RealTimeCrossSectionViewer(self.image)
        self.graph_widget.display_widget.hide()
        self.graph_widget.toggle_line_cb.hide()


        self.setup_ui()

    def setup_ui(self):

        self.page_layout = QVBoxLayout(self)
        self.page_layout.addWidget(QLabel("Target image"))
        self.page_layout.addWidget(self.graph_widget)
        self.setup_image_importer()
        self.setup_unit()
        self.setup_matrix_shape()
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
        self.unit_widget_layout.addSpacing(20)
        self.unit_widget_layout.addWidget(self.unit_combo)
        self.unit_widget_layout.addStretch()

        self.page_layout.addWidget(self.unit_widget)
    

    def setup_shape(self):

        self.shape_widget = QWidget()
        self.shape_widget_layout = QHBoxLayout(self.shape_widget)

        self.combo = QComboBox()
        self.combo.addItems(["Elliptic", "Rectangular", "Image"])
        self.combo.setCurrentText(self.image_shape)

        setup_label = QLabel("Select an image shape")

        self.shape_widget_layout.addWidget(setup_label)
        self.shape_widget_layout.addSpacing(20)
        self.shape_widget_layout.addWidget(self.combo)
        self.shape_widget_layout.addStretch()

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
        self.array_shape_widget_layout.addSpacing(20)
        self.array_shape_widget_layout.addWidget(self.h_shape_line_edit)
        self.array_shape_widget_layout.addWidget(shape_x_label)
        self.array_shape_widget_layout.addWidget(self.w_shape_line_edit)
        self.array_shape_widget_layout.addStretch()

        self.page_layout.addWidget(self.array_shape_widget)
    

    

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
        self.offset_widget_layout.addSpacing(20)
        self.offset_widget_layout.addWidget(self.offset_x_line_edit)
        self.offset_widget_layout.addWidget(self.offset_y_line_edit)
        self.offset_widget_layout.addStretch()

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
        self.shape_dimensions_widget_layout.addSpacing(20)
        self.shape_dimensions_widget_layout.addWidget(self.h_size_line_edit)
        self.shape_dimensions_widget_layout.addWidget(shape_dimensions_x_label)
        self.shape_dimensions_widget_layout.addWidget(self.w_size_line_edit)
        self.shape_dimensions_widget_layout.addStretch()

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
        self.img_import_widget_layout.addSpacing(20)
        self.img_import_widget_layout.addWidget(self.img_file_line_edit)
        self.img_import_widget_layout.addWidget(self.img_file_button)
        self.img_import_widget_layout.addStretch()
        self.page_layout.addWidget(self.img_import_widget)
    

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", "Images (*.png *.jpg *.jpeg *.bmp *.tiff *.pgm);;All Files (*)"
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

        self.offset_x_line_edit.textChanged.connect(self.sync_offset)
        self.offset_y_line_edit.textChanged.connect(self.sync_offset)



    def get_inputs(self):
        self.image_shape = self.combo.currentText()
        self.matrix_array_shape = (self.h_shape_line_edit.text(), self.w_shape_line_edit.text())
        self.image_size = (self.h_size_line_edit.text(), self.w_size_line_edit.text())
        self.distance_unit = self.unit_combo.currentText()
        self.graph_widget.sampling = float(self.sampling)
        self.offset_x = self.offset_x_line_edit.text()
        self.offset_y = self.offset_y_line_edit.text()

        return {
            "image_shape" : self.image_shape, #size of elementary shapes : circle/rectangle
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
        ext = os.path.splitext(self.img_path)[1].lower()
        if ext == ".npy":
            img = np.load(self.img_path)
        elif ext ==".tiff":
            img = tifffile.imread(self.img_path)
        else:
            img = Image.open(self.img_path).convert("L")
            array_shape = tuple(map(int, self.matrix_array_shape))
            img = np.array(img)
            img = img/img.max()
            assert max(img.shape) <= max(array_shape)
            img = zero_pad(np.array([img]), array_shape).squeeze()
        return img.T

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

    def insert_with_offset(self,image, target_shape, offset):
        """
        Place `image` inside a zero-padded array of shape `target_shape` with the given `offset`.

        Parameters:
            image        : np.ndarray, the input image (2D)
            target_shape : tuple (H, W), the shape of the output array
            offset       : tuple (row_offset, col_offset), top-left position where image is inserted

        Returns:
            np.ndarray of shape target_shape with image placed at offset
        """
        new_image = np.zeros(target_shape, dtype=image.dtype)

        H, W = target_shape
        h, w = image.shape
        off_row, off_col = offset

        # Compute center positions
        center_row = (H - h) // 2 + off_row
        center_col = (W - w) // 2 + off_col

        # Compute valid insert ranges
        row_start = max(center_row, 0)
        col_start = max(center_col, 0)
        row_end = min(center_row + h, H)
        col_end = min(center_col + w, W)

        # Compute crop of input image if partially out of bounds
        img_row_start = max(0, -center_row)
        img_col_start = max(0, -center_col)
        img_row_end = img_row_start + (row_end - row_start)
        img_col_end = img_col_start + (col_end - col_start)

        # Insert
        new_image[row_start:row_end, col_start:col_end] = image[img_row_start:img_row_end, img_col_start:img_col_end]
        return new_image

    def update_with_offset(self):
        img = self.open_image()
        target_shape = tuple(map(int,self.matrix_array_shape))
        offset = tuple(map(int,(self.offset_x, self.offset_y)))
        new_img = self.insert_with_offset(img,target_shape, offset)
        return new_img


    def update_graph_with_offset(self):
        print(self.offset_x, self.offset_y)
        image = self.update_with_offset()
        self.image = np.repeat(image[np.newaxis, :, :], 1, axis=0)
        self.graph_widget.update_data(self.image)

    def sync_offset(self):
        self.offset_x = self.offset_x_line_edit.text()
        self.offset_y = self.offset_y_line_edit.text()
        self.update_graph_with_offset()
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    section = ImageSection()
    section.show()

    app.exec()

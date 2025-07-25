from PyQt5.QtWidgets import (
    QWidget, QLabel, QComboBox, QCheckBox, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QDialog, QDialogButtonBox, QApplication, QFileDialog, QRadioButton, QToolButton, QStyle
)
import sys
from DiffractionSection import RealTimeCrossSectionViewer
import numpy as np
import os 
import tifffile
from PIL import Image
from automatic_sizing import zero_pad

from filters import elliptic_filter, rectangular_filter, elliptic_filter_band, rectangular_filter_band

class SimSettingsDialog(QDialog):
    def __init__(self, current_values, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Parameters")
        self.resize(600, 800)  # Width x Height in pixels

        self.current_values = current_values


        self.graph_widget = RealTimeCrossSectionViewer(np.ones((1,512,512)))

        self.graph_widget.slice_view.setLevels(0,1)
        self.graph_widget.toggle_line_cb.hide()
        self.graph_widget.display_widget.hide()

        self.filter_type_widget = QWidget()
        self.filter_type_widget_layout = QHBoxLayout(self.filter_type_widget)

        self.filter_type_combo = QComboBox()
        self.filter_type_combo.addItems(["No filter","Elliptic", "Rectangular", "Elliptic Bandpass", "Rectangular Bandpass", "Image"])
        self.filter_type_combo.setCurrentText(self.current_values["filter_type"])
        
        self.filter_type_widget_layout.addWidget(QLabel("Filter"))
        self.filter_type_widget_layout.addSpacing(20)
        self.filter_type_widget_layout.addWidget(self.filter_type_combo)
        self.filter_type_widget_layout.addStretch()



        self.remove_outside_checkbox = QCheckBox("Remove outside")
        self.remove_outside_checkbox.setChecked(self.current_values["remove_outside"])

        self.cutoff_freq_widget = QWidget()
        self.cutoff_freq_widget_layout = QHBoxLayout(self.cutoff_freq_widget)

        self.x_cutoff_line_edit = QLineEdit(self.current_values["cutoff_freq"][0])
        self.y_cutoff_line_edit = QLineEdit(self.current_values["cutoff_freq"][1])
        self.x_cutoff_line_edit.setFixedWidth(100)
        self.y_cutoff_line_edit.setFixedWidth(100)

        self.cutoff_freq_widget_layout.addWidget(QLabel("Cutoff frequencies, x - y"))
        self.cutoff_freq_widget_layout.addSpacing(20)
        self.cutoff_freq_widget_layout.addWidget(self.x_cutoff_line_edit)
        self.cutoff_freq_widget_layout.addWidget(QLabel(" - "))
        self.cutoff_freq_widget_layout.addWidget(self.y_cutoff_line_edit)
        self.cutoff_freq_widget_layout.addStretch()

        self.thickness_widget = QWidget()
        self.thickness_widget_layout = QHBoxLayout(self.thickness_widget)

        self.thickness_line_edit = QLineEdit(self.current_values["thickness"])

        self.thickness_line_edit.setFixedWidth(100)

        band_cutoff_label = QLabel("Thickness")
        
        self.thickness_widget_layout.addWidget(band_cutoff_label)
        self.thickness_widget_layout.addSpacing(20)
        self.thickness_widget_layout.addWidget(self.thickness_line_edit)
        self.thickness_widget_layout.addStretch()

        self.offset_widget = QWidget()
        self.offset_widget_layout = QHBoxLayout(self.offset_widget)

        self.offset_x_line_edit = QLineEdit(self.current_values["offset_x"])
        self.offset_y_line_edit = QLineEdit(self.current_values["offset_y"])

        self.offset_x_line_edit.setFixedWidth(100)
        self.offset_y_line_edit.setFixedWidth(100)

        offset_label = QLabel("Offset x y")
        
        self.offset_widget_layout.addWidget(offset_label)
        self.offset_widget_layout.addSpacing(20)
        self.offset_widget_layout.addWidget(self.offset_x_line_edit)
        self.offset_widget_layout.addWidget(self.offset_y_line_edit)
        self.offset_widget_layout.addStretch()


        self.layout = QVBoxLayout()

        self.layout.addWidget(self.graph_widget)
        self.layout.addWidget(self.filter_type_widget)
        self.layout.addWidget(self.remove_outside_checkbox)
        self.layout.addWidget(self.cutoff_freq_widget)
        self.layout.addWidget(self.thickness_widget)

        self.setup_image_importer()

        self.layout.addWidget(self.offset_widget)



        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.layout.addWidget(buttons)


        self.setLayout(self.layout)

        self.setup_connections()
        self.setup_misc()

    def setup_image_importer(self):

        self.img_import_widget = QWidget()
        self.img_import_widget_layout = QHBoxLayout(self.img_import_widget)

        file_label = QLabel("Image file")

        self.img_file_line_edit = QLineEdit()
        self.img_file_button = QToolButton()

        icon = self.style().standardIcon(QStyle.SP_DirOpenIcon)
        self.img_file_button.setIcon(icon)

        self.img_import_widget_layout.addWidget(file_label)
        self.img_import_widget_layout.addSpacing(20)
        self.img_import_widget_layout.addWidget(self.img_file_line_edit)
        self.img_import_widget_layout.addWidget(self.img_file_button)
        self.img_import_widget_layout.addStretch()
        self.layout.addWidget(self.img_import_widget)





    def setup_connections(self):
        self.img_file_button.clicked.connect(self.browse_file)

        self.filter_type_combo.currentTextChanged.connect(self.update_combo_visibility)

        self.filter_type_combo.currentTextChanged.connect(self.update_filter)
        self.remove_outside_checkbox.stateChanged.connect(self.update_filter)
        self.x_cutoff_line_edit.textChanged.connect(self.update_filter)
        self.y_cutoff_line_edit.textChanged.connect(self.update_filter)
        self.thickness_line_edit.textChanged.connect(self.update_filter)
        self.offset_x_line_edit.textChanged.connect(self.update_filter)
        self.offset_y_line_edit.textChanged.connect(self.update_filter)


    def setup_misc(self):
        self.update_combo_visibility()
        self.update_filter()
    def browse_file(self):
        file_path, selected_filter = QFileDialog.getOpenFileName(
            self, "Select File", "", "Images (*.jpg *.jpeg *.png *.bmp *.tiff *.pgm);;NumPy (*.npy);;All Files (*)"
        )
        if file_path:
            self.img_file_line_edit.setText(file_path)
            self.update_filter()
        else: 
            self.img_file_line_edit.setText("")    

    def get_values(self):
        filter = self.generate_filter()
        filter = filter[np.newaxis,:]
        return {
            "filter_type": self.filter_type_combo.currentText(),
            "remove_outside": self.remove_outside_checkbox.isChecked(),
            "cutoff_freq": (self.x_cutoff_line_edit.text(),self.y_cutoff_line_edit.text()),
            "thickness" :  self.thickness_line_edit.text(),
            "img_path" : self.img_file_line_edit.text(),
            "filter" : filter,
            "offset_x" : self.offset_x_line_edit.text(),
            "offset_y" : self.offset_y_line_edit.text()
        }

    def update_combo_visibility(self):

        selected = self.filter_type_combo.currentText()

        self.img_import_widget.hide()
        self.cutoff_freq_widget.hide()
        self.thickness_widget.hide()
        self.offset_widget.hide()

        if selected in ["Elliptic", "Rectangular"]:
            self.cutoff_freq_widget.show()
            self.offset_widget.show()
        elif selected in ["Elliptic Bandpass", "Rectangular Bandpass"]:
            self.cutoff_freq_widget.show()
            self.thickness_widget.show()
            self.offset_widget.show()
        elif selected == "Image":
            self.img_import_widget.show()
            self.offset_widget.show()


    def generate_filter(self):
        shape = tuple(map(int, self.current_values["shape"]))
        filter_type =  self.filter_type_combo.currentText()
        remove_outside = self.remove_outside_checkbox.isChecked()
        cutoff_freq = (float(self.x_cutoff_line_edit.text()),float(self.y_cutoff_line_edit.text()))
        thickness =  float(self.thickness_line_edit.text())
        offset_x = int(self.offset_x_line_edit.text())
        offset_y = int(self.offset_y_line_edit.text())
        
        fx = self.current_values["fx"]
        fy = self.current_values["fy"]

        if filter_type == "Elliptic":
            filter = elliptic_filter(cutoff_freq[0], cutoff_freq[1], fx, fy)
        elif filter_type == "No filter":
            filter = np.ones(shape)
        elif filter_type == "Rectangular":
            filter = rectangular_filter(cutoff_freq[0], cutoff_freq[1], fx, fy)
        elif filter_type == "Elliptic Bandpass":
            filter = elliptic_filter_band(cutoff_freq[0], cutoff_freq[1], fx, fy, thickness)
        elif filter_type == "Rectangular Bandpass":
            filter = rectangular_filter_band(cutoff_freq[0], cutoff_freq[1], fx, fy, thickness)
        elif filter_type == "Image":
            filter = self.open_image()
        
        print(filter.shape)
        if filter_type != "No filter":
            filter = self.insert_with_offset(filter, shape, (offset_x, offset_y))
        if remove_outside:
            filter = filter.max()-filter
        return filter



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


    def open_image(self):
        img_path = self.img_file_line_edit.text()
        ext = os.path.splitext(img_path)[1].lower()
        array_shape = tuple(map(int,self.current_values["shape"]))

        if ext == ".npy":
            img = np.load(img_path)

        elif ext == ".tiff":
            img = tifffile.imread(img_path)
            img = img.T

        else:
            img = Image.open(img_path).convert("L")
            img = np.array(img)
            img = img / img.max()
            img = zero_pad(np.array([img]), array_shape).squeeze()
            img = img.T
        return img
    
    def update_filter(self):
        filter = self.generate_filter()
        filter = filter[np.newaxis,:]
        print(filter.max())
        self.graph_widget.update_data(filter)
        self.graph_widget.sampling = self.current_values["df"]
        self.graph_widget.slice_view.setLevels(0,1)

        

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Define some example current values to pass in
    current_values = {
        "shape" : ("512", "512"),
        "filter_type": "No filter",
        "remove_outside": False,
        "cutoff_freq": ("150000", "150000"),
        "thickness" : "50000",
        "offset_x" : "0",
        "offset_y" : "0",
        "fx" :  np.linspace(-512/2, 512/2-1, 512) * 1/(512*1e-6),
        "fy" : np.linspace(-512/2, 512/2-1, 512) * 1/(512*1e-6),
        "df" : 1.0/(512*1e-6)
    }

    dialog = SimSettingsDialog(current_values)
    
    if dialog.exec_() == QDialog.Accepted:
        result = dialog.get_values()
        print("User clicked OK")
        print("Updated values:", result)
    else:
        print("User cancelled the dialog")

    sys.exit()
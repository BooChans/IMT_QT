import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QCheckBox,
    QSplitter, QLabel, QSlider, QGridLayout,QGraphicsLineItem , QPushButton, QFileDialog, QHBoxLayout,QLineEdit, QToolButton, QStyle, QSizePolicy
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
import pyqtgraph as pg
from EODSection import EODSection
from ImageSection import ImageSection
from SimulationSection import SimulationSection
import sys
from PIL import Image
from ifmta.ifta import Ifta
from automatic_sizing import zero_pad
from ressource_path import resource_path
import tifffile

class DOEDesignSimulation(QMainWindow):
    def __init__(self):
        super().__init__()

        self.nbiter_ph1 = "25"
        self.nbiter_ph2 = "25"
        self.rfact = "1.2"
        self.seed = 0
        self.compute_efficiency = 0
        self.compute_uniformity = 0
        self.npy_path = None

        self.phases = None
        self.resize(2000, 1200)

        self.page = QWidget()
        self.page_layout = QVBoxLayout(self.page)
        self.image_section = ImageSection()
        self.eod_section = EODSection()
        self.simulation_section = SimulationSection()
        self.eod_section.graph_view.mode_selector.setCurrentText("Amplitude")

        self.image_section.graph_widget.slice_view.ui.histogram.hide()

        #no sampling
        self.simulation_section.sampling_selection_widget.hide()
        self.simulation_section.checkbox_widget.hide()

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.image_section)
        splitter.addWidget(self.eod_section)

        self.left = QWidget()
        self.left_layout = QVBoxLayout(self.left)
        


        splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


        self.ifta_params_widget = QWidget()
        self.ifta_params_widget_layout = QGridLayout(self.ifta_params_widget)



        splitter_ = QSplitter(Qt.Horizontal)
        
        self.setup_rfact()
        self.setup_nbiter_amp()
        self.setup_nbiter_pha()
        self.setup_npy_importer()
        self.setup_extras() #for efficiency and uniformity, if needed

        self.left_layout.addWidget(splitter)
        self.left_layout.addWidget(self.ifta_params_widget)
        splitter_.addWidget(self.left)
        splitter_.addWidget(self.simulation_section)

        self.left.setMinimumWidth(1100)  # or setMinimumSize(QSize(100, 0))
        splitter_.setSizes([1100, 2500])   # Big number to force right widget to take the rest

        self.page_layout.addWidget(splitter_)
        self.page.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setup_buttons()
        self.setCentralWidget(self.page)
        self.setup_connections()


    def setup_rfact(self):

        self.rfact_widget = QWidget()
        self.rfact_widget_layout = QHBoxLayout(self.rfact_widget)

        rfact_label = QLabel("Reinforcement factor")

        self.rfact_line_edit = QLineEdit()
        self.rfact_line_edit.setFixedWidth(100)
        self.rfact_line_edit.setText(self.rfact)

        self.rfact_widget_layout.addWidget(rfact_label)
        #self.rfact_widget_layout.addStretch()
        self.rfact_widget_layout.addWidget(self.rfact_line_edit)
        #self.rfact_widget_layout.setStretch(0, 10)
        #self.rfact_widget_layout.setStretch(1, 3)
        self.ifta_params_widget_layout.addWidget(self.rfact_widget, 0, 0)


    def setup_nbiter_amp(self):

        self.nbiter_widget = QWidget()
        self.nbiter_widget_layout = QHBoxLayout(self.nbiter_widget)

        nbiter_label = QLabel("Iterations phase 1")

        self.nbiter_line_edit = QLineEdit()
        self.nbiter_line_edit.setFixedWidth(100)
        self.nbiter_line_edit.setText(self.nbiter_ph1)

        self.nbiter_widget_layout.addWidget(nbiter_label)
        self.nbiter_widget_layout.addStretch()
        self.nbiter_widget_layout.addWidget(self.nbiter_line_edit)

        self.ifta_params_widget_layout.addWidget(self.nbiter_widget, 1, 0)

    def setup_nbiter_pha(self):

        self.nbiter_pha_widget = QWidget()
        self.nbiter_pha_widget_layout = QHBoxLayout(self.nbiter_pha_widget)

        nbiter_pha_label = QLabel("Iterations phase 2")

        self.nbiter_pha_line_edit = QLineEdit()
        self.nbiter_pha_line_edit.setFixedWidth(100)
        self.nbiter_pha_line_edit.setText(self.nbiter_ph2)

        self.nbiter_pha_widget_layout.addWidget(nbiter_pha_label)
        self.nbiter_pha_widget_layout.addStretch()
        self.nbiter_pha_widget_layout.addWidget(self.nbiter_pha_line_edit)

        self.ifta_params_widget_layout.addWidget(self.nbiter_pha_widget, 1, 1)


    def setup_extras(self):

        self.efficiency_checkbox = QCheckBox("Compute efficiency")
        self.efficiency_checkbox.setChecked(int(self.compute_efficiency))


        self.uniformity_checkbox = QCheckBox("Compute uniformity")
        self.uniformity_checkbox.setChecked(int(self.compute_uniformity))



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
        self.ifta_params_widget_layout.addWidget(self.npy_import_widget, 0, 1)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", "NumPy files (*.npy);;All Files (*)"
        )
        if file_path:
            self.npy_file_line_edit.setText(file_path)
            self.npy_path = file_path
        else: 
            self.npy_path = None
            self.seed = 0
            self.npy_file_line_edit.setText("")

    def save_file(self):
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Save File",
            "output.npy",
            "NumPy files (*.npy);;TIFF files (*.tiff);;All Files (*)"
        )        
        if file_path:
            if selected_filter.startswith("NumPy"):
                if not file_path.endswith(".npy"):
                    file_path += ".npy"
                if self.phases is not None:
                    np.save(file_path, self.phases[-1])
            elif selected_filter.startswith("TIFF"):
                if not file_path.endswith(".tiff"):
                    file_path += ".tiff"
                if self.phases is not None:
                    tifffile.imwrite(file_path, self.phases[-1])
            else:
                if not file_path.endswith(".npy") and not file_path.endswith(".tiff"):
                    raise Exception("Error, please provide the extension of your output file")
                else:
                    if file_path.endswith(".npy"):
                        if self.phases is not None:
                            np.save(file_path, self.phases[-1])  
                    if file_path.endswith(".tiff"):                      
                        if self.phases is not None:
                            tifffile.imwrite(file_path, self.phases[-1])
            print(f"Saving to {file_path}, data shape: {self.phases[-1].shape if (self.phases is not None and len(self.phases) > 0) else 'None'}")




    def setup_buttons(self):
        self.buttons_widget = QWidget()
        self.buttons_widget_layout = QHBoxLayout(self.buttons_widget)

        self.sim_button = QPushButton("Run DOE simulation")
        self.sim_button.setIcon(QIcon(resource_path("icons/arrows.png")))
        self.sim_button.setIconSize(QSize(24, 24))

        button_style = """
            QPushButton {{
                font-size: 16px;
                padding: 10px 20px;
                border: 2px solid {color};
                border-radius: 8px;
                color: black;
            }}
            QPushButton:hover {{
                background-color: {hover};
            }}
        """

        self.sim_button.setStyleSheet(button_style.format(color="green", hover="#eaffea"))
        self.sim_button.setFixedWidth(220)
        self.buttons_widget_layout.addWidget(self.sim_button)

        self.save_button = QPushButton("Save DOE")
        self.save_button.setIcon(QIcon(resource_path("icons/floppy-disk.png")))
        self.save_button.setIconSize(QSize(24, 24))
        self.save_button.setStyleSheet(button_style.format(color="blue", hover="#d2f1ff"))
        self.save_button.setFixedWidth(220)
        self.buttons_widget_layout.addWidget(self.save_button)
        self.buttons_widget_layout.addStretch()

        self.left_layout.addWidget(self.buttons_widget)


    def setup_connections(self):
        self.sim_button.clicked.connect(self.sim_EOD)        
        self.npy_file_button.clicked.connect(self.browse_file)
        self.save_button.clicked.connect(self.save_file)
        self.efficiency_checkbox.stateChanged.connect(self.sync_inputs)
        self.uniformity_checkbox.stateChanged.connect(self.sync_inputs)
        self.rfact_line_edit.textChanged.connect(self.sync_inputs)
        self.nbiter_line_edit.textChanged.connect(self.sync_inputs)
        self.nbiter_pha_line_edit.textChanged.connect(self.sync_inputs)

    
    def sim_EOD(self):
        image_params = self.image_section.get_inputs()

        eod_params = self.eod_section.get_inputs()

        if self.npy_path:
            seed = np.load(self.npy_path)
        else: 
            seed = 0

        eod_shape = tuple(map(int,eod_params["EOD_shape"]))
        image = image_params["image"]
        nlevels = int(eod_params["nlevels"])
        rfact = float(self.rfact)
        nbiter_ph1 = int(self.nbiter_ph1)
        nbiter_ph2 = int(self.nbiter_ph2)
        compute_efficiency = self.compute_efficiency
        compute_uniformity = self.compute_uniformity

        

        print(nlevels, rfact, nbiter_ph1, nbiter_ph2, image_params["image_shape"])

        phases = Ifta(image, image_size=eod_shape, n_iter_ph1= nbiter_ph1, n_iter_ph2= nbiter_ph2, rfact=rfact, n_levels=nlevels, 
                      compute_efficiency= compute_efficiency, compute_uniformity = compute_uniformity, seed=seed)

        print(phases.shape, "computation done")
        self.eod_section.volume = phases
        self.phases = phases
        self.eod_section.graph_view.samplings = float(self.eod_section.sampling) * np.ones((len(phases),))
        self.eod_section.graph_view.update_data(phases)


    def sync_inputs(self):
        self.rfact = self.rfact_line_edit.text()
        self.nbiter_ph1 = self.nbiter_line_edit.text()
        self.nbiter_ph2 = self.nbiter_pha_line_edit.text()
        
        self.compute_efficiency = 1 if self.efficiency_checkbox.isChecked() else 0
        self.compute_uniformity = 1 if self.uniformity_checkbox.isChecked() else 0

    
    def get_inputs(self):
        return {
            "rfact" : self.rfact,
            "nbiter_ph1" : self.nbiter_ph1,
            "nbiter_ph2" : self.nbiter_ph2,
            "compute_uniformity" : self.compute_uniformity,
            "compute_efficiency" : self.compute_efficiency,
            "npy_path" : self.npy_path, 
        }
                
        


        



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DOEDesignSimulation()
    window.show()
    app.exec()

    

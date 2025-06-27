import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QCheckBox,
    QSplitter, QLabel, QSlider, QGridLayout, QPushButton, QAction, QMessageBox, QComboBox, QHBoxLayout, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QIcon
import pyqtgraph as pg
from pyqtgraph import LineSegmentROI, InfiniteLine
from scipy.ndimage import map_coordinates
import sys
import traceback

from automatic_sizing import auto_sampling_N, auto_shaping_dx, zero_pad
import matplotlib.pyplot as plt

from SourceSection import SourceSection
from ApertureSection import ApertureSection
from SimulationSection import SimulationSection

from SplashScreen import SplashScreen

class OpticalDiffractionSimulator(QMainWindow):
    def __init__(self):
        super().__init__()

        self.expert_mode = False
        self.window_size = "512"
        self.sampling = "1.0"

        #menu_bar = self.menuBar()
        #mode_menu = menu_bar.addMenu("Mode")

        #self.expert_mode_toggle = QAction("Expert Mode", self, checkable=True)
        #self.expert_mode_toggle.setChecked(False) 
        #self.expert_mode_toggle.triggered.connect(self.expert_mode_enable)
        #mode_menu.addAction(self.expert_mode_toggle)

        # Instantiate all 3 sections
        self.source_section = SourceSection()
        self.aperture_section = ApertureSection()
        self.simulation_section = SimulationSection()
        
        #disable widgets related to expert mode 
        self.simulation_section.sampling_selection_widget.hide()
        self.simulation_section.checkbox_widget.hide()


        self.graph_window_size = (300,300)
        # Layout with splitter
        self.left_widget = QWidget()
        self.left_widget_layout = QVBoxLayout(self.left_widget)

        splitter_ = QSplitter(Qt.Horizontal)
        splitter_.addWidget(self.source_section)
        splitter_.addWidget(self.aperture_section)

        self.global_params_widget = QWidget()
        self.global_params_widget_layout = QHBoxLayout(self.global_params_widget)

        window_size_label = QLabel("Window Size :")
        self.window_size_combo = QComboBox()
        self.window_size_combo.addItems(["512", "1024"])
        self.window_size_combo.setCurrentText(self.window_size)

        sampling_label = QLabel("Sampling :")
        self.sampling_combo = QComboBox()
        self.sampling_combo.addItems(["0.8","1.0", "2.0"])
        self.sampling_combo.setCurrentText(self.sampling)

        self.global_params_widget_layout.addWidget(window_size_label)
        self.global_params_widget_layout.addStretch()
        self.global_params_widget_layout.addWidget(self.window_size_combo)
        self.global_params_widget_layout.addSpacing(30)
        self.global_params_widget_layout.addWidget(sampling_label)
        self.global_params_widget_layout.addStretch()
        self.global_params_widget_layout.addWidget(self.sampling_combo)

        label = QLabel("Global parameters")
        label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)  # Only grow horizontally
        label.setMaximumHeight(20)  # You can tweak this (e.g., 16 or 18)

        self.global_params_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.global_params_widget.setMaximumHeight(50)  # Try 30, or tweak lower if needed
        self.left_widget_layout.addWidget(splitter_)
        self.left_widget_layout.addWidget(label)
        self.left_widget_layout.addWidget(self.global_params_widget)


        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.left_widget)
        splitter.addWidget(self.simulation_section)

        self.source_section.setMinimumWidth(350)
        self.aperture_section.setMinimumWidth(450)

        # After adding all widgets, set sizes explicitly
        splitter.setSizes([650, 900])

        # Create a wrapper central widget with a layout
        central_widget = QWidget()
        central_layout = QVBoxLayout()
        central_widget.setLayout(central_layout)

        # Add splitter and button to the layout
        central_layout.addWidget(splitter)

        # Go Button
        self.go_button = self.simulation_section.go_button
        self.sweep_button = self.simulation_section.sweep_button




        self.setCentralWidget(central_widget)

        #hide histograms & RoIPlot
        self.source_section.graph_widget.slice_view.ui.histogram.hide()
        self.aperture_section.graph_widget.slice_view.ui.histogram.hide()
        self.source_section.graph_widget.slice_view.ui.roiPlot.hide()
        self.aperture_section.graph_widget.slice_view.ui.roiPlot.hide()
        


        self.setup_connections()
        #hide histograms & RoIPl
        # Optional: initial run
        # self.run_simulation()


    def setup_connections(self): 
        self.go_button.clicked.connect(self.run_simulation)
        self.sweep_button.clicked.connect(self.run_sweep)

        #start : unnecessary connections
        self.source_section.hdiameter_line_edit.editingFinished.connect(self.update_sampling)
        self.source_section.wdiameter_line_edit.editingFinished.connect(self.update_sampling)
        self.source_section.beam_waist_line_edit.editingFinished.connect(self.update_sampling)

        self.aperture_section.shape_combo.currentTextChanged.connect(self.update_sampling)
        self.aperture_section.unit_combo.currentTextChanged.connect(self.update_sampling)

        # Line edits for simulation distance
        self.aperture_section.dst_sim_line_edit.editingFinished.connect(self.update_sampling)

        # Simple aperture size line edits
        self.aperture_section.simple_size_h_line_edit.editingFinished.connect(self.update_sampling)
        self.aperture_section.simple_size_w_line_edit.editingFinished.connect(self.update_sampling)

        # Slit aperture line edits
        self.aperture_section.slit_size_h_line_edit.editingFinished.connect(self.update_sampling)
        self.aperture_section.slit_size_w_line_edit.editingFinished.connect(self.update_sampling)
        self.aperture_section.slit_width_line_edit.editingFinished.connect(self.update_sampling)
        self.aperture_section.slit_distance_line_edit.editingFinished.connect(self.update_sampling)

        # Array aperture line edits
        self.aperture_section.matrix_h_line_edit.editingFinished.connect(self.update_sampling)
        self.aperture_section.matrix_w_line_edit.editingFinished.connect(self.update_sampling)
        self.aperture_section.matrix_spacing_line_edit.editingFinished.connect(self.update_sampling)
        
        self.aperture_section.hel_bd_line_edit.editingFinished.connect(self.update_sampling)
        self.aperture_section.hel_sd_line_edit.editingFinished.connect(self.update_sampling)
        
        self.aperture_section.squ_square_size_line_edit.editingFinished.connect(self.update_sampling)

        self.source_section.hdiameter_line_edit.editingFinished.connect(self.update_samlping_input)
        self.source_section.wdiameter_line_edit.editingFinished.connect(self.update_samlping_input)
        self.source_section.beam_waist_line_edit.editingFinished.connect(self.update_samlping_input)

        self.aperture_section.shape_combo.currentTextChanged.connect(self.update_samlping_input)
        self.aperture_section.unit_combo.currentTextChanged.connect(self.update_samlping_input)

        # Line edits for simulation distance
        self.aperture_section.dst_sim_line_edit.editingFinished.connect(self.update_samlping_input)

        # Simple aperture size line edits
        self.aperture_section.simple_size_h_line_edit.editingFinished.connect(self.update_samlping_input)
        self.aperture_section.simple_size_w_line_edit.editingFinished.connect(self.update_samlping_input)

        # Slit aperture line edits
        self.aperture_section.slit_size_h_line_edit.editingFinished.connect(self.update_samlping_input)
        self.aperture_section.slit_size_w_line_edit.editingFinished.connect(self.update_samlping_input)
        self.aperture_section.slit_width_line_edit.editingFinished.connect(self.update_samlping_input)
        self.aperture_section.slit_distance_line_edit.editingFinished.connect(self.update_samlping_input)

        # Array aperture line edits
        self.aperture_section.matrix_h_line_edit.editingFinished.connect(self.update_samlping_input)
        self.aperture_section.matrix_w_line_edit.editingFinished.connect(self.update_samlping_input)
        self.aperture_section.matrix_spacing_line_edit.editingFinished.connect(self.update_samlping_input)
        
        self.aperture_section.hel_bd_line_edit.editingFinished.connect(self.update_samlping_input)
        self.aperture_section.hel_sd_line_edit.editingFinished.connect(self.update_samlping_input)
        
        self.aperture_section.squ_square_size_line_edit.editingFinished.connect(self.update_samlping_input)
        #

        self.simulation_section.sampling_line_edit.editingFinished.connect(self.update_window)
        self.simulation_section.checkbox.stateChanged.connect(self.restore_auto_sampling)

        self.window_size_combo.currentTextChanged.connect(self.update_window_size)
        self.sampling_combo.currentTextChanged.connect(self.update_sampling_simple)

    def run_simulation(self):
        try:
            # 1. Get the aperture mask
            aperture_params = self.aperture_section.get_inputs()
            aperture = self.aperture_section.aperture

            # 2. Get the source distribution
            source_params = self.source_section.get_inputs()
            source = self.source_section.light_source

            # 3. Get wavelength, distance, pixel size
            wavelength = float(source_params['wavelength'])
            z = float(aperture_params["simulation_distance"])
            assert self.source_section.sampling == self.aperture_section.sampling
            dx = float(self.source_section.sampling)   
            assert max(aperture.shape) == max(source.shape)
            N_win =  max(aperture.shape)
            N_target = int(self.simulation_section.resolution_multiplier) * N_win
            if N_win < N_target :
                new_shape = (N_target, N_target)
                source = zero_pad(source, new_shape)
                aperture = zero_pad(aperture, new_shape)
            # 4. Update simulation
            self.simulation_section.update_diffraction(source, aperture, wavelength, z, dx)
        except Exception as e:
            print(f"Exception in run_simulation: {e}")
    
    def run_sweep(self):
    # 1. Get the aperture mask
        aperture_params = self.aperture_section.get_inputs()
        aperture = self.aperture_section.aperture

        # 2. Get the source distribution
        source_params = self.source_section.get_inputs()
        source = self.source_section.light_source

        # 3. Get wavelength, distance, pixel size
        wavelength = float(source_params['wavelength'])
        z = float(aperture_params["simulation_distance"])
        assert self.source_section.sampling == self.aperture_section.sampling
        dx = float(self.source_section.sampling)   
        assert max(aperture.shape) == max(source.shape)
        N_win =  max(aperture.shape)
        N_target = int(self.simulation_section.resolution_multiplier) * N_win
        if N_win < N_target :
            new_shape = (N_target, N_target)
            source = zero_pad(source, new_shape)
            aperture = zero_pad(aperture, new_shape)
        # 4. Update simulation
        self.simulation_section.update_sweep(source, aperture, wavelength, z, dx)


    def update_sampling(self):
        if self.expert_mode:

            aperture_params = self.aperture_section.get_inputs()


            # 2. Get the source distribution
            source_params = self.source_section.get_inputs()

            # 3. Get wavelength, distance, pixel size
            source_size = tuple(map(float,source_params['size']))
            aperture_size = tuple(map(float,aperture_params['aperture_size']))

            light_source_array_shape = tuple(map(int,self.source_section.array_shape))
            aperture_array_shape = tuple(map(int,self.aperture_section.array_shape))
            assert self.source_section.sampling == self.aperture_section.sampling
            dx = float(self.source_section.sampling)

            if max(source_size) > max((dx*light_source_array_shape[0], dx*light_source_array_shape[1])) or \
            max(aperture_size) > max((dx*aperture_array_shape[0], dx*aperture_array_shape[1])):
                dx = auto_sampling_N(source_size=source_size, apertures_size=aperture_size, shape=light_source_array_shape)
                dx_str = str(dx)
                self.source_section.sampling = dx_str
                self.aperture_section.sampling = dx_str
                self.simulation_section.sampling = dx_str
                self.aperture_section.update_aperture_graph()
                self.source_section.update_graph()

            if max(source_size) < 0.58 * max((dx*light_source_array_shape[0], dx*light_source_array_shape[1])) or \
            0.58 * max(aperture_size) < max((dx*aperture_array_shape[0], dx*aperture_array_shape[1])):
                dx = auto_sampling_N(source_size=source_size, apertures_size=aperture_size, shape=light_source_array_shape)
                dx_str = str(dx)
                self.source_section.sampling = dx_str
                self.aperture_section.sampling = dx_str
                self.simulation_section.sampling = dx_str
                self.aperture_section.update_aperture_graph()
                self.source_section.update_graph()




    def update_window(self):
        if not self.expert_mode:
            aperture_params = self.aperture_section.get_inputs()


            # 2. Get the source distribution
            source_params = self.source_section.get_inputs()

            # 3. Get sampling params

            sampling_params = self.simulation_section.get_inputs()

            dx_str = sampling_params['sampling']
            dx = float(dx_str)

            # 3. Get wavelength, distance, pixel size
            source_size = tuple(map(int,source_params['size']))
            aperture_size = tuple(map(int,aperture_params['aperture_size']))

            N = auto_shaping_dx(source_size=source_size, aperture_size=aperture_size, dx = dx)
            assert N < 2049, "Sampling is too low"
            self.source_section.sampling = dx_str
            self.aperture_section.sampling = dx_str
            self.simulation_section.sampling = dx_str
            if N > 512 and N < 2049:
                array_shape = (str(N), str(N))
                self.source_section.array_shape = array_shape
                self.aperture_section.array_shape = array_shape
            elif N < 512: 
                array_shape = (512, 512)
                self.source_section.array_shape = array_shape
                self.aperture_section.array_shape = array_shape
            self.source_section.update_attributes()
            self.source_section.update_graph()
            self.aperture_section.sync_attributes_from_widgets()
            self.aperture_section.update_aperture_graph()
            self.simulation_section.update_sampling_line()


    def update_samlping_input(self):
        self.simulation_section.update_sampling_line()

    def restore_auto_sampling(self, state):
        if self.expert_mode:
            if state == Qt.Unchecked: 
                array_shape = (512, 512)
                self.source_section.array_shape = array_shape
                self.aperture_section.array_shape = array_shape
                self.update_sampling()
                self.source_section.update_attributes()
                self.source_section.update_graph()
                self.aperture_section.sync_attributes_from_widgets()
                self.aperture_section.update_aperture_graph()
                self.simulation_section.update_sampling_line()

    def expert_mode_enable(self, checked):
        self.expert_mode = checked
        print("hey bro")
        if checked:
            self.simulation_section.sampling_selection_widget.show()
            self.simulation_section.checkbox_widget.show()
        else:
            self.simulation_section.sampling_selection_widget.hide()
            self.simulation_section.checkbox_widget.show()
            self.default_mode()

    def default_mode(self):
        #self.source_section.default()
        #self.aperture_section.default()
        None

    def update_window_size(self):
        self.window_size = self.window_size_combo.currentText()

        window_size_tuple = (self.window_size, self.window_size)

        self.source_section.array_shape = window_size_tuple
        self.aperture_section.array_shape = window_size_tuple



        self.source_section.update_graph()
        self.aperture_section.update_aperture_graph()

    def update_sampling_simple(self):
        self.sampling = self.sampling_combo.currentText()

        self.source_section.sampling = self.sampling
        self.aperture_section.sampling = self.sampling

        self.source_section.update_graph()
        self.aperture_section.update_aperture_graph()

if __name__ == "__main__":


    app = QApplication(sys.argv)
    window = SplashScreen(OpticalDiffractionSimulator, "splashscreen_assets/ops_ss.png")
    window.show()
    app.exec()


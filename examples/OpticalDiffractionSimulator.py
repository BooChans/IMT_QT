import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QCheckBox,
    QSplitter, QLabel, QSlider, QGridLayout, QPushButton, QAction, QMessageBox, QComboBox, QHBoxLayout, QSizePolicy
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
import pyqtgraph as pg
from pyqtgraph import LineSegmentROI, InfiniteLine
from scipy.ndimage import map_coordinates
import sys
import os


from automatic_sizing import auto_sampling_N, auto_shaping_dx, zero_pad
import matplotlib.pyplot as plt
from ressource_path import resource_path

from SourceSection import SourceSection
from ApertureSection import ApertureSection
from SimulationSection import SimulationSection

from SplashScreen import SplashScreen

class OpticalDiffractionSimulator(QMainWindow):
    def __init__(self):
        super().__init__()

        self.expert_mode = False
        self.matrix_size = "512"
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
        
        #disabling widgets of the simulation section
        self.simulation_section.wavelength_widget.hide()
        self.simulation_section.tile_widget.hide()

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

        window_size_label = QLabel("Matrix Size :")
        self.window_size_combo = QComboBox()
        self.window_size_combo.addItems(["512", "1024"])
        self.window_size_combo.setCurrentText(self.matrix_size)

        sampling_label = QLabel("Sampling :")
        self.sampling_combo = QComboBox()
        self.sampling_combo.addItems(["0.8","1.0", "2.0"])
        self.sampling_combo.setCurrentText(self.sampling)

        self.global_params_widget_layout.addWidget(window_size_label)
        self.global_params_widget_layout.addSpacing(20)
        self.global_params_widget_layout.addWidget(self.window_size_combo)
        self.global_params_widget_layout.addStretch()
        self.global_params_widget_layout.addWidget(sampling_label)
        self.global_params_widget_layout.addSpacing(20)
        self.global_params_widget_layout.addWidget(self.sampling_combo)
        self.global_params_widget_layout.addStretch()

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
        self.sweep_button_w = self.simulation_section.sweep_button_w




        self.setCentralWidget(central_widget)

        #hide histograms & RoIPlot
        self.source_section.graph_widget.slice_view.ui.histogram.hide()
        self.aperture_section.graph_widget.slice_view.ui.histogram.hide()
        self.source_section.graph_widget.slice_view.ui.roiPlot.hide()
        self.aperture_section.graph_widget.slice_view.ui.roiPlot.hide()
        


        self.setup_connections()
        self.update_illumination_of_aperture()
        #hide histograms & RoIPl
        # Optional: initial run
        # self.run_simulation()


    def setup_connections(self): 
        self.go_button.clicked.connect(self.run_simulation)
        self.sweep_button.clicked.connect(self.run_sweep)
        self.sweep_button_w.clicked.connect(self.run_sweep_w)

        #start : unnecessary connections
        self.source_section.beam_waist_line_edit.editingFinished.connect(self.update_sampling)

        self.aperture_section.shape_combo.currentTextChanged.connect(self.update_sampling)
        self.aperture_section.unit_combo.currentTextChanged.connect(self.update_sampling)

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

        self.source_section.beam_waist_line_edit.editingFinished.connect(self.update_samlping_input)

        self.aperture_section.shape_combo.currentTextChanged.connect(self.update_samlping_input)
        self.aperture_section.unit_combo.currentTextChanged.connect(self.update_samlping_input)

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
        
        self.source_section.beam_waist_line_edit.editingFinished.connect(self.update_illumination_of_aperture)

        self.aperture_section.shape_combo.currentTextChanged.connect(self.update_illumination_of_aperture)
        self.aperture_section.unit_combo.currentTextChanged.connect(self.update_illumination_of_aperture)

        # Simple aperture size line edits
        self.aperture_section.simple_size_h_line_edit.editingFinished.connect(self.update_illumination_of_aperture)
        self.aperture_section.simple_size_w_line_edit.editingFinished.connect(self.update_illumination_of_aperture)

        # Slit aperture line edits
        self.aperture_section.slit_size_h_line_edit.editingFinished.connect(self.update_illumination_of_aperture)
        self.aperture_section.slit_size_w_line_edit.editingFinished.connect(self.update_illumination_of_aperture)
        self.aperture_section.slit_width_line_edit.editingFinished.connect(self.update_illumination_of_aperture)
        self.aperture_section.slit_distance_line_edit.editingFinished.connect(self.update_illumination_of_aperture)

        # Array aperture line edits
        self.aperture_section.matrix_h_line_edit.editingFinished.connect(self.update_illumination_of_aperture)
        self.aperture_section.matrix_w_line_edit.editingFinished.connect(self.update_illumination_of_aperture)
        self.aperture_section.matrix_spacing_line_edit.editingFinished.connect(self.update_illumination_of_aperture)
        
        self.aperture_section.hel_bd_line_edit.editingFinished.connect(self.update_illumination_of_aperture)
        self.aperture_section.hel_sd_line_edit.editingFinished.connect(self.update_illumination_of_aperture)
        
        self.aperture_section.squ_square_size_line_edit.editingFinished.connect(self.update_illumination_of_aperture)

        self.source_section.option1.toggled.connect(self.update_illumination_of_aperture)
        self.source_section.option2.toggled.connect(self.update_illumination_of_aperture)
        self.source_section.option3.toggled.connect(self.update_illumination_of_aperture)

        self.aperture_section.img_file_button.clicked.connect(self.update_illumination_of_aperture)
        self.aperture_section.eod_mode_checkbox.stateChanged.connect(self.update_illumination_of_aperture)

        self.aperture_section.img_amp.toggled.connect(self.update_illumination_of_aperture)
        self.aperture_section.img_pha.toggled.connect(self.update_illumination_of_aperture)


        self.simulation_section.sampling_line_edit.editingFinished.connect(self.update_window)
        self.simulation_section.checkbox.stateChanged.connect(self.restore_auto_sampling)

        self.window_size_combo.currentTextChanged.connect(self.update_window_size)
        self.sampling_combo.currentTextChanged.connect(self.update_sampling_simple)

        self.source_section.wavelength_line_edit.editingFinished.connect(self.update_color)
        self.update_color()

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
            z = float(self.simulation_section.simulation_distance)
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
            self.simulation_section.start_diffraction(source, aperture, wavelength, z, dx)
            self.update_color()
        except Exception as e:
            print(f"Exception in run_simulation: {e}")
    
    def run_sweep(self):
        try:
        # 1. Get the aperture mask
            aperture_params = self.aperture_section.get_inputs()
            aperture = self.aperture_section.aperture

            # 2. Get the source distribution
            source_params = self.source_section.get_inputs()
            source = self.source_section.light_source

            # 3. Get wavelength, distance, pixel size
            wavelength = float(source_params['wavelength'])
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
            self.simulation_section.start_update_sweep(source, aperture, wavelength, dx)
            self.update_color()
        except Exception as e:
            print(f"Sweep error : {e}")

    def run_sweep_w(self):
        try:
        # 1. Get the aperture mask
            aperture_params = self.aperture_section.get_inputs()
            aperture = self.aperture_section.aperture

            # 2. Get the source distribution
            source_params = self.source_section.get_inputs()
            source = self.source_section.light_source

            # 3. Get wavelength, distance, pixel size
            z = float(self.simulation_section.simulation_distance)
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
            self.simulation_section.start_update_sweep_w(source, aperture, z, dx)
        except Exception as e:
            print(f"Sweep error : {e}")


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
        self.matrix_size = self.window_size_combo.currentText()

        window_size_tuple = (self.matrix_size, self.matrix_size)

        self.source_section.array_shape = window_size_tuple
        self.aperture_section.array_shape = window_size_tuple



        self.source_section.update_graph()
        self.aperture_section.update_aperture_graph()
        self.update_illumination_of_aperture()

    def update_sampling_simple(self):
        self.sampling = self.sampling_combo.currentText()

        self.source_section.sampling = self.sampling
        self.aperture_section.sampling = self.sampling

        self.source_section.update_graph()
        self.aperture_section.update_aperture_graph()
        self.update_illumination_of_aperture()

    def update_illumination_of_aperture(self):
        aperture = self.aperture_section.aperture
        source = self.source_section.light_source

        if self.source_section.source_type != "Gaussian beam":
            U0 = np.abs(aperture) + 0.5*np.abs(source)
            self.aperture_section.illuminated_aperture = U0
            self.aperture_section.graph_widget.update_data_ap(U0)
            self.aperture_section.graph_widget.slice_view.setLevels(0,1.5)
        else:
            U0 = np.abs(aperture) + 0.7*(1-aperture)*np.abs(source)
            self.aperture_section.illuminated_aperture = U0
            self.aperture_section.graph_widget.update_data_ap(U0)
            self.aperture_section.graph_widget.slice_view.setLevels(0,1)

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
        wavelength = float(self.source_section.wavelength) 
        wavelength = wavelength * conversion[self.source_section.distance_unit]
        color = self.wavelength_to_rgb(wavelength)

        R,G,B,V = color

        if V == 1:
            lut = np.zeros((256, 3), dtype=np.uint8)
            lut[:, 0] = np.linspace(0, R, 256)  
            lut[:, 1] = np.linspace(0, G, 256)  
            lut[:, 2] = np.linspace(0, B, 256)  

            self.source_section.graph_widget.slice_view.setColorMap(pg.ColorMap(pos=np.linspace(0,1,256), color=lut))
            self.aperture_section.graph_widget.slice_view.setColorMap(pg.ColorMap(pos=np.linspace(0,1,256), color=lut))
            self.simulation_section.graph_widget.slice_view.setColorMap(pg.ColorMap(pos=np.linspace(0,1,256), color=lut))
        else: 
            gray_lut = pg.ColorMap(pos=[0, 1], color=[[0, 0, 0], [255, 255, 255]])
            self.source_section.graph_widget.slice_view.setColorMap(gray_lut)
            self.aperture_section.graph_widget.slice_view.setColorMap(gray_lut)
            self.simulation_section.graph_widget.slice_view.setColorMap(gray_lut)

if __name__ == "__main__":


    app = QApplication(sys.argv)
    splash_path = resource_path("splashscreen_assets/ops_ss.png")
    window = SplashScreen(OpticalDiffractionSimulator, splash_path)
    window.show()
    app.exec()


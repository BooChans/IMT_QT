import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QCheckBox,
    QSplitter, QLabel, QGridLayout , QPushButton, QFileDialog, QHBoxLayout,QLineEdit, QSizePolicy, QProgressBar
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
import pyqtgraph as pg
from EODSection import EODSection
from ImageSection import ImageSection
from SimulationSection import SimulationSection
from GenericThread import GenericThread
import sys
from PIL import Image
from ifmta.ifta import IftaImproved
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
        self.doe = None
        self.ifta_tread = None

        self.resize(2000, 1200)

        self.page = QWidget()
        self.page_layout = QVBoxLayout(self.page)
        self.image_section = ImageSection()
        self.eod_section = EODSection()
        self.simulation_section = SimulationSection()
        
        self.simulation_section.intermediate_graph_widget.hide()
        self.simulation_section.intermediate_settings_button.hide()
        self.simulation_section.go_filtering_button.hide()
        # Simulation distance preset

        self.simulation_section.simulation_distance = "1e8"
        self.simulation_section.dst_sim_line_edit.setText(self.simulation_section.simulation_distance)

        self.eod_section.graph_view.mode_selector.setCurrentText("Phase")

        self.image_section.graph_widget.slice_view.ui.histogram.hide()


        # hide line profile for target image

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.image_section)
        splitter.addWidget(self.eod_section)

        self.left = QWidget()
        self.left_layout = QVBoxLayout(self.left)
        


        splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


        self.ifta_params_widget = QWidget()
        self.ifta_params_widget_layout = QGridLayout(self.ifta_params_widget)

        self.sim_doe = self.simulation_section.go_button
        self.sim_doe_sweep = self.simulation_section.sweep_button
        self.sim_doe_sweep_w = self.simulation_section.sweep_button_w

        splitter_ = QSplitter(Qt.Horizontal)
        
        self.setup_rfact()
        self.setup_nbiter_amp()
        self.setup_nbiter_pha()
        self.setup_extras() #for efficiency and uniformity, if needed

        self.left_layout.addWidget(splitter)
        self.left_layout.addWidget(self.ifta_params_widget)
        splitter_.addWidget(self.left)
        splitter_.addWidget(self.simulation_section)

        self.left.setMinimumWidth(1100)  # or setMinimumSize(QSize(100, 0))
        splitter_.setSizes([1100, 2500])   # Big number to force right widget to take the rest

        self.page_layout.addWidget(splitter_)
        self.simulation_section.hide()
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
        self.rfact_widget_layout.addSpacing(20)
        self.rfact_widget_layout.addWidget(self.rfact_line_edit)
        self.rfact_widget_layout.addStretch()
        self.ifta_params_widget_layout.addWidget(self.rfact_widget, 0, 0)


    def setup_nbiter_amp(self):

        self.nbiter_widget = QWidget()
        self.nbiter_widget_layout = QHBoxLayout(self.nbiter_widget)

        nbiter_label = QLabel("Iterations phase 1")

        self.nbiter_line_edit = QLineEdit()
        self.nbiter_line_edit.setFixedWidth(100)
        self.nbiter_line_edit.setText(self.nbiter_ph1)

        self.nbiter_widget_layout.addWidget(nbiter_label)
        self.nbiter_widget_layout.addSpacing(20)
        self.nbiter_widget_layout.addWidget(self.nbiter_line_edit)
        self.nbiter_widget_layout.addStretch()

        self.ifta_params_widget_layout.addWidget(self.nbiter_widget, 0, 1)

    def setup_nbiter_pha(self):

        self.nbiter_pha_widget = QWidget()
        self.nbiter_pha_widget_layout = QHBoxLayout(self.nbiter_pha_widget)

        nbiter_pha_label = QLabel("Iterations phase 2")

        self.nbiter_pha_line_edit = QLineEdit()
        self.nbiter_pha_line_edit.setFixedWidth(100)
        self.nbiter_pha_line_edit.setText(self.nbiter_ph2)

        self.nbiter_pha_widget_layout.addWidget(nbiter_pha_label)
        self.nbiter_pha_widget_layout.addSpacing(20)
        self.nbiter_pha_widget_layout.addWidget(self.nbiter_pha_line_edit)
        self.nbiter_pha_widget_layout.addStretch()

        self.ifta_params_widget_layout.addWidget(self.nbiter_pha_widget, 0, 2)


    def setup_extras(self):

        self.efficiency_checkbox = QCheckBox("Compute efficiency")
        self.efficiency_checkbox.setChecked(int(self.compute_efficiency))


        self.uniformity_checkbox = QCheckBox("Compute uniformity")
        self.uniformity_checkbox.setChecked(int(self.compute_uniformity))



    def save_file(self):
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Save File",
            "doe_output",
            "PNG files (*.png);;TIFF files (*.tiff);;NumPy files (*.npy);;All Files (*)"
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
            elif selected_filter.startswith("PNG"):
                if not file_path.endswith(".png"):
                    file_path += ".png"
                if self.phases is not None:
                    doe = self.phases[-1]
                    doe = np.mod(doe, 2*np.pi)
                    doe = np.round(255/(2*np.pi)*doe) 
                    doe = doe.astype(np.uint8) 
                    doe = Image.fromarray(doe)
                    doe.save(file_path)
            else:
                if not file_path.endswith(".npy") and not file_path.endswith(".tiff") and not file_path.endswith(".png"):
                    raise Exception("Error, please provide the extension of your output file")
                else:
                    if file_path.endswith(".npy"):
                        if self.phases is not None:
                            np.save(file_path, self.phases[-1])  
                    if file_path.endswith(".tiff"):                      
                        if self.phases is not None:
                            tifffile.imwrite(file_path, self.phases[-1])
                    if file_path.endswith(".png"):                      
                        if self.phases is not None:
                            doe = self.phases[-1]
                            doe = np.mod(doe, 2*np.pi)
                            doe = np.round(255/(2*np.pi)*doe) 
                            doe = Image.fromarray(doe)
                            doe.save(file_path)
            print(f"Saving to {file_path}, data shape: {self.phases[-1].shape if (self.phases is not None and len(self.phases) > 0) else 'None'}")




    def setup_buttons(self):
        self.buttons_widget = QWidget()
        self.buttons_widget_layout = QHBoxLayout(self.buttons_widget)

        self.sim_button = QPushButton("Run DOE design")
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


        self.save_button = QPushButton("Save DOE")
        self.save_button.setIcon(QIcon(resource_path("icons/floppy-disk.png")))
        self.save_button.setIconSize(QSize(24, 24))
        self.save_button.setStyleSheet(button_style.format(color="blue", hover="#d2f1ff"))

        self.sim_checkbox = QCheckBox("Show Simulation Window")
        self.sim_checkbox.setChecked(False)

        self.save_button.setFixedWidth(220)

        self.progress = QProgressBar()
        self.progress.setMinimum = 0
        self.progress.setMaximum = 100
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #CCC;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #00CC66;
                width: 1px;
            }
        """)

        #adding every buttons/widgets on the local widget layout
        self.buttons_widget_layout.addStretch()
        self.buttons_widget_layout.addWidget(self.sim_button)
        self.buttons_widget_layout.addSpacing(10)  # optional spacing
        self.buttons_widget_layout.addWidget(self.progress)  # optional spacing
        self.progress.hide()
        self.buttons_widget_layout.addSpacing(10)
        self.buttons_widget_layout.addWidget(self.save_button)
        self.buttons_widget_layout.addSpacing(20)  # optional spacing
        self.buttons_widget_layout.addStretch()
        self.buttons_widget_layout.addWidget(self.sim_checkbox)

        self.left_layout.addWidget(self.buttons_widget)


    def setup_connections(self):
        self.sim_button.clicked.connect(self.start_sim_EOD)        
        
        self.save_button.clicked.connect(self.save_file)
        self.efficiency_checkbox.stateChanged.connect(self.sync_inputs)
        self.uniformity_checkbox.stateChanged.connect(self.sync_inputs)
        self.rfact_line_edit.textChanged.connect(self.sync_inputs)
        self.nbiter_line_edit.textChanged.connect(self.sync_inputs)
        self.nbiter_pha_line_edit.textChanged.connect(self.sync_inputs)

        self.sim_doe.clicked.connect(self.run_simulation)
        self.sim_doe_sweep.clicked.connect(self.run_sweep)
        self.sim_doe_sweep_w.clicked.connect(self.run_sweep_w)

        self.sim_checkbox.stateChanged.connect(self.show_simulation_window)
        self.simulation_section.wavelength_line_edit.editingFinished.connect(self.update_color)
        self.update_color()

    
    def start_sim_EOD(self):
        image_params = self.image_section.get_inputs()

        eod_params = self.eod_section.get_inputs()


        eod_shape = tuple(map(int,eod_params["EOD_shape"]))
        image = image_params["image"]
        nlevels = int(eod_params["nlevels"])
        rfact = float(self.rfact)
        nbiter_ph1 = int(self.nbiter_ph1)
        nbiter_ph2 = int(self.nbiter_ph2)
        compute_efficiency = self.compute_efficiency
        compute_uniformity = self.compute_uniformity
        seed = self.seed

        print(nlevels, rfact, nbiter_ph1, nbiter_ph2, image_params["image_shape"])

        self.ifta_thread = GenericThread(self.sim_EOD,
                                        image,
                                        eod_shape,
                                        nbiter_ph1,
                                        nbiter_ph2,
                                        rfact,
                                        nlevels,
                                        compute_efficiency,
                                        compute_uniformity, 
                                        seed)
        self.ifta_thread.progress_changed.connect(self.progress.setValue)
        self.ifta_thread.finished_with_result.connect(self.on_ifta_done)

        self.progress.show()
        self.progress.setValue(0)

        # Start thread
        self.ifta_thread.start()


    
    def sim_EOD(self, image, image_size, n_iter_ph1, n_iter_ph2, rfact, n_levels, 
                      compute_efficiency, compute_uniformity, seed, callback=None):


        phases = IftaImproved(image, image_size=image_size, n_iter_ph1=n_iter_ph1, n_iter_ph2=n_iter_ph2, rfact=rfact, n_levels=n_levels, 
                      compute_efficiency=compute_efficiency, compute_uniformity=compute_uniformity, seed=seed, callback=callback)

        return phases

    def on_ifta_done(self, phases):
        print(phases.shape, "computation done")
        self.eod_section.volume = phases
        self.phases = phases
        does = np.exp(1j * phases)
        self.eod_section.graph_view.samplings = float(self.eod_section.sampling) * np.ones((len(phases),))
        self.doe = phases[-1]
        self.doe = self.doe[np.newaxis, :, :]
        self.eod_section.graph_view.update_data(np.exp(1j * self.doe))
        self.progress.hide()



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
                
    def run_simulation(self):
        try:
        # 1. Get the aperture mask
            eod_params = self.eod_section.get_inputs()
            doe_phase = self.doe
            doe = np.exp(1j*doe_phase)
            tile = int(self.simulation_section.tile)
            print(tile)
            tile_shape = (tile, tile)
            doe = np.tile(doe, tile_shape)

            source = np.ones_like(doe)

            # 3. Get wavelength, distance, pixel size
            wavelength = float(self.simulation_section.wavelength)
            z = float(self.simulation_section.simulation_distance)
            dx = float(eod_params["sampling"])   
            N_win =  max(doe.shape)
            N_target = int(self.simulation_section.resolution_multiplier) * N_win
            if N_win < N_target :
                new_shape = (N_target, N_target)
                source = zero_pad(source, new_shape)
                doe = zero_pad(doe, new_shape)
            # 4. Update simulation
            self.simulation_section.start_diffraction(source, doe, wavelength, z, dx, eod = True)
        except Exception as e:
            print(f"Exception in run_simulation: {e}")
    
    def run_sweep(self):
        try:
        # 1. Get the aperture mask
            eod_params = self.eod_section.get_inputs()
            doe_phase = self.doe
            doe = np.exp(1j*doe_phase)
            tile = int(self.simulation_section.tile)
            tile_shape = (tile, tile)
            doe = np.tile(doe, tile_shape)


            source = np.ones_like(doe)

            # 3. Get wavelength, distance, pixel size
            wavelength = float(self.simulation_section.wavelength)
            dx = float(eod_params["sampling"])   
            N_win =  max(doe.shape)
            N_target = int(self.simulation_section.resolution_multiplier) * N_win
            if N_win < N_target :
                new_shape = (N_target, N_target)
                source = zero_pad(source, new_shape)
                doe = zero_pad(doe, new_shape)
            # 4. Update simulation
            self.simulation_section.start_update_sweep(source, doe, wavelength, dx)
        except Exception as e:
            print(f"Update sweep error : {e}")

    def run_sweep_w(self):
        try:
        # 1. Get the aperture mask
            eod_params = self.eod_section.get_inputs()
            doe_phase = self.doe
            doe = np.exp(1j*doe_phase)
            doe[np.newaxis, :, :]
            tile = int(self.simulation_section.tile)
            tile_shape = (tile, tile)
            doe = np.tile(doe, tile_shape)


            source = np.ones_like(doe)

            # 3. Get wavelength, distance, pixel size
            z = float(self.simulation_section.simulation_distance)
            dx = float(eod_params["sampling"])   
            N_win =  max(doe.shape)
            N_target = int(self.simulation_section.resolution_multiplier) * N_win
            if N_win < N_target :
                new_shape = (N_target, N_target)
                source = zero_pad(source, new_shape)
                doe = zero_pad(doe, new_shape)
            # 4. Update simulation
            self.simulation_section.start_update_sweep_w(source, doe, z, dx)
        except Exception as e:
            print(f"Update sweep error : {e}")

    def show_simulation_window(self):
        if self.sim_checkbox.isChecked():
            self.simulation_section.show()
        else:
            self.simulation_section.hide()
        
    def wavelength_to_rgb(self,wavelength):
        """
        Convert a wavelength in nm (380 to 750) to an RGB color.
        Returns an array [R,G,B] with values 0-255.
        """
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

        return np.array([R, G, B], dtype=np.uint8)
    
    def update_color(self):
        conversion = {"µm":1e3, "mm": 1e6, "m": 1e9}
        wavelength = float(self.simulation_section.wavelength) 
        wavelength = wavelength * conversion[self.eod_section.distance_unit]
        print(wavelength)
        color = self.wavelength_to_rgb(wavelength)

        R,G,B = color

        lut = np.zeros((256, 3), dtype=np.uint8)
        lut[:, 0] = np.linspace(0, R, 256)  
        lut[:, 1] = np.linspace(0, G, 256)  
        lut[:, 2] = np.linspace(0, B, 256)  

        self.simulation_section.graph_widget.slice_view.setColorMap(pg.ColorMap(pos=np.linspace(0,1,256), color=lut))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DOEDesignSimulation()
    window.show()
    app.exec()

    

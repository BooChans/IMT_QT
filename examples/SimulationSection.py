import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QVBoxLayout, QWidget, QCheckBox,
    QLabel, QComboBox, QLineEdit,QHBoxLayout, QPushButton, QProgressBar, QDialog
)
from PyQt5.QtCore import QSize, pyqtSignal
from PyQt5.QtGui import QIcon
from scipy.ndimage import map_coordinates
import sys

from ressource_path import resource_path
from DiffractionSection import RealTimeCrossSectionViewer
from diffraction_propagation import far_field, angular_spectrum, sweep, sweep_w, fraunhofer, ft_1, ft_2
from GenericThread import GenericThread
from MessageWorker import MessageWorker

from SimSettingsDialog import SimSettingsDialog


class SimulationSection(QWidget):
    intermediate_updated = pyqtSignal(object) 
    def __init__(self):
        super().__init__()
        self.unit_distance = "µm"
        self.sampling = "1.0" #user defined sampling for the aperture and the source
        self.volume = np.zeros((1, 512,512))
        self.resolution_multiplier = "1"
        self.start_sweep = "1e2"
        self.end_sweep = "1e4"
        self.step_sweep = "100"

        self.start_sweep_w = "0.380"
        self.end_sweep_w = "0.750"
        self.step_sweep_w = "0.01"

        self.simulation_distance = "1e6" #µm
        self.wavelength = "0.633" #µm
        self.tile = "1"

        self.fourier_mode = False

        self.graph_widget = RealTimeCrossSectionViewer(self.volume)

        self.filter = np.ones((1,512,512))
        self.intermediate_volume = np.zeros((1,512,512))


        # 4f filtering parameters
        self.intermediate_graph_widget = RealTimeCrossSectionViewer(self.volume)
        self.intermediate_graph_widget.toggle_line_cb.hide()
        self.intermediate_graph_widget.display_widget.hide()
        self.intermediate_graph_widget.window_info_widget.hide()


        self.filter_type = "No filter"
        self.remove_outside = False

        self.filter = np.ones((1,512,512))
        self.filter_shape = ("512","512")
        self.cutoff_freq = ("1.5e5", "1.5e5")
        self.thickness = "5e4"
        self.offset_x = "0"
        self.offset_y = "0"
        self.df = 1/(512*1e-6)
        h,w = tuple(map(int, self.filter_shape))
        self.fx = np.linspace(-h/2, h/2-1, h) * self.df
        self.fy = np.linspace(-w/2, w/2-1, w) * self.df


        self.sim_thread = None

        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        self.widget_layout = QVBoxLayout(self)
        self.widget_layout.addWidget(QLabel("Diffraction pattern"))
        self.widget_layout.addWidget(self.intermediate_graph_widget)
        
        self.intermediate_settings_button = QPushButton("Filter settings")
        self.intermediate_settings_button.setFixedWidth(150)
        self.widget_layout.addWidget(self.intermediate_settings_button)


        self.widget_layout.addWidget(self.graph_widget)

        self.resolution_widget = QWidget()
        self.resolution_widget_layout = QHBoxLayout(self.resolution_widget)

        # Simulation distance definition
        self.distance_simulation_widget = QWidget()
        self.distance_simulation_widget_layout = QHBoxLayout(self.distance_simulation_widget)

               
        #Units definition
        self.wavelength_widget = QWidget()
        self.wavelength_widget_layout = QHBoxLayout(self.wavelength_widget)

        wavelength_label = QLabel("Wavelength")

        self.wavelength_line_edit = QLineEdit()
        self.wavelength_line_edit.setFixedWidth(100)
        self.wavelength_line_edit.setText(self.wavelength)

        self.wavelength_widget_layout.addWidget(wavelength_label)
        self.wavelength_widget_layout.addSpacing(20)
        self.wavelength_widget_layout.addWidget(self.wavelength_line_edit)
        self.wavelength_widget_layout.addStretch()


        self.widget_layout.addWidget(self.wavelength_widget)

        dst_sim_label = QLabel("Simulation distance")

        self.dst_sim_line_edit = QLineEdit()
        self.dst_sim_line_edit.setFixedWidth(100)
        self.dst_sim_line_edit.setText(self.simulation_distance)

        self.distance_simulation_widget_layout.addWidget(dst_sim_label)
        self.distance_simulation_widget_layout.addSpacing(20)
        self.distance_simulation_widget_layout.addWidget(self.dst_sim_line_edit)
        self.distance_simulation_widget_layout.addStretch()


        self.widget_layout.addWidget(self.distance_simulation_widget)  
        
        self.tile_widget = QWidget()
        self.tile_widget_layout = QHBoxLayout(self.tile_widget)

        tile_label = QLabel("Tiling")

        self.tile_combo = QComboBox()
        self.tile_combo.addItems(["1", "2", "4", "8"])
        self.tile_combo.setCurrentText(self.tile)

        
        self.tile_widget_layout.addWidget(tile_label)
        self.tile_widget_layout.addSpacing(20)
        self.tile_widget_layout.addWidget(self.tile_combo)
        self.tile_widget_layout.addStretch()

        self.widget_layout.addWidget(self.tile_widget)


        resolution_label = QLabel("Over-sample output plane")
        self.combo_res = QComboBox()
        self.combo_res.addItems(["1","2", "4"])      
        self.combo_res.setCurrentText(self.resolution_multiplier)  

        self.resolution_widget_layout.addWidget(resolution_label)
        self.resolution_widget_layout.addSpacing(20)
        self.resolution_widget_layout.addWidget(self.combo_res)
        self.resolution_widget_layout.addStretch()

        self.widget_layout.addWidget(self.resolution_widget)


        self.algo_label = QLabel("")
        self.widget_layout.addWidget(self.algo_label)

        self.checkbox_sweep = QCheckBox("Z Sweep")
        self.widget_layout.addWidget(self.checkbox_sweep)

        self.sweep_widget = QWidget()
        self.sweep_widget_layout = QHBoxLayout(self.sweep_widget)

        self.sweep_widget_layout.addWidget(QLabel("start : end : step"))
        self.sweep_widget_layout.addSpacing(20)

        self.start_sweep_line_edit = QLineEdit()
        self.start_sweep_line_edit.setText(self.start_sweep)
        self.start_sweep_line_edit.setFixedWidth(100)

        self.end_sweep_line_edit = QLineEdit()
        self.end_sweep_line_edit.setText(self.end_sweep)
        self.end_sweep_line_edit.setFixedWidth(100)

        
        self.step_sweep_line_edit = QLineEdit()
        self.step_sweep_line_edit.setText(self.step_sweep)
        self.step_sweep_line_edit.setFixedWidth(100)


        self.sweep_widget_layout.addWidget(self.start_sweep_line_edit)
        self.sweep_widget_layout.addWidget(self.end_sweep_line_edit)
        self.sweep_widget_layout.addWidget(self.step_sweep_line_edit)
        self.sweep_widget_layout.addStretch()
        

        self.widget_layout.addWidget(self.sweep_widget)
        self.sweep_widget.hide()

        self.checkbox_sweep_w = QCheckBox("Wavelength Sweep")
        self.widget_layout.addWidget(self.checkbox_sweep_w)

        self.sweep_widget_w = QWidget()
        self.sweep_widget_w_layout = QHBoxLayout(self.sweep_widget_w)

        self.sweep_widget_w_layout.addWidget(QLabel("start : end : step"))
        self.sweep_widget_w_layout.addSpacing(20)

        self.start_sweep_w_line_edit = QLineEdit()
        self.start_sweep_w_line_edit.setText(self.start_sweep_w)
        self.start_sweep_w_line_edit.setFixedWidth(100)


        self.end_sweep_w_line_edit = QLineEdit()
        self.end_sweep_w_line_edit.setText(self.end_sweep_w)
        self.end_sweep_w_line_edit.setFixedWidth(100)

        self.step_sweep_w_line_edit = QLineEdit()
        self.step_sweep_w_line_edit.setText(self.step_sweep_w)
        self.step_sweep_w_line_edit.setFixedWidth(100)


        self.sweep_widget_w_layout.addWidget(self.start_sweep_w_line_edit)
        self.sweep_widget_w_layout.addWidget(self.end_sweep_w_line_edit)
        self.sweep_widget_w_layout.addWidget(self.step_sweep_w_line_edit)
        self.sweep_widget_w_layout.addStretch()
        

        self.widget_layout.addWidget(self.sweep_widget_w)
        self.sweep_widget_w.hide()
        #self.sweep_w_widget.hide()

        # Create progress bar
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
        self.progress.hide()

        # Create button
        self.go_button = QPushButton("Run Simulation")
        self.go_button.setIcon(QIcon(resource_path("icons/arrows.png")))
        self.go_button.setIconSize(QSize(24, 24))

        self.sweep_button = QPushButton("Z Sweep")
        self.sweep_button.setIcon(QIcon(resource_path("icons/game.png")))  # Change icon if needed
        self.sweep_button.setIconSize(QSize(24, 24))

        self.sweep_button_w = QPushButton("Wavelength Sweep")
        self.sweep_button_w.setIcon(QIcon(resource_path("icons/blue_arrow.png")))  # Change icon if needed
        self.sweep_button_w.setIconSize(QSize(24, 24))

        self.go_filtering_button = QPushButton("Run 4f Simulation")
        self.go_filtering_button.setIcon(QIcon(resource_path("icons/arrows.png")))
        self.go_filtering_button.setIconSize(QSize(24, 24))

        # Style it
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

        self.go_button.setStyleSheet(button_style.format(color="green", hover="#eaffea"))
        self.sweep_button.setStyleSheet(button_style.format(color="red", hover="#ffeaea"))
        self.sweep_button_w.setStyleSheet(button_style.format(color="blue", hover="#b9dbfe"))
        self.go_filtering_button.setStyleSheet(button_style.format(color="green", hover="#eaffea"))

        self.sweep_button.hide()
        self.sweep_button_w.hide()
        # Fix the button size (optional)
        self.go_button.setFixedWidth(200)  # or whatever width looks good
        self.sweep_button.setFixedWidth(200)  # or whatever width looks good
        self.sweep_button_w.setFixedWidth(200)
        self.go_filtering_button.setFixedWidth(200)
        # Right-align the button using a layout
        right_layout = QHBoxLayout()
        right_layout.addWidget(self.go_button)
        right_layout.addWidget(self.sweep_button)  
        right_layout.addWidget(self.sweep_button_w)
        right_layout.addWidget(self.go_filtering_button)
        right_layout.addWidget(self.progress)
        right_layout.addStretch() # pushes the button to the left
        # Add this layout to your main layout
        self.widget_layout.addLayout(right_layout)

        self.log_label = QLabel()
        self.widget_layout.addWidget(self.log_label)


    def setup_connections(self):
        self.combo_res.currentTextChanged.connect(self.update_resolution)
        self.checkbox_sweep.stateChanged.connect(self.update_sweep_visibility)
        self.checkbox_sweep_w.stateChanged.connect(self.update_sweep_w_visibility)


        self.start_sweep_line_edit.editingFinished.connect(self.update_sweep_params)
        self.step_sweep_line_edit.editingFinished.connect(self.update_sweep_params)
        self.end_sweep_line_edit.editingFinished.connect(self.update_sweep_params)

        self.start_sweep_w_line_edit.editingFinished.connect(self.update_sweep_w_params)
        self.step_sweep_w_line_edit.editingFinished.connect(self.update_sweep_w_params)
        self.end_sweep_w_line_edit.editingFinished.connect(self.update_sweep_w_params)

        self.dst_sim_line_edit.textChanged.connect(self.update_sim_params)
        self.wavelength_line_edit.textChanged.connect(self.update_sim_params)
        self.tile_combo.currentTextChanged.connect(self.update_sim_params)

        self.intermediate_settings_button.clicked.connect(self.open_dialog)


    def start_diffraction(self, source, aperture, wavelength, z, dx, eod=False):
        self.diffraction_thread = MessageWorker(
            self.update_diffraction, source, aperture, wavelength, z, dx, eod
        )
        self.diffraction_thread.finished_with_result.connect(lambda res: self.on_diffraction_done(res, eod))
        self.diffraction_thread.start()
        c = max(source.shape)
        if c > 2048:
            self.log_label.setText(f"Matrix size : {c} x {c} is big, computation may be slow, please wait")


    def update_diffraction(self, source, aperture, wavelength, z, dx, eod = False, message_callback = None):

        assert source.shape == aperture.shape, f"Unmatched array shape. Source {source.shape}, Aperture {aperture.shape}."
        U0 = source * aperture
        N = max(U0.shape)
        z_limit = N * dx**2 / wavelength
        fraunhofer_limit = (N * dx)**2 / wavelength

        if message_callback:
            message_callback(f"Fraunhofer limit: {fraunhofer_limit:.2f} μm")

        if z < fraunhofer_limit:
            try:
                result = far_field(U0, wavelength, z, dx)
                sampling = wavelength * abs(z) / (N * dx)
                algo = f"Fresnel algorithm for z > zlimit, z limit = {z_limit:.2f}"
            except Exception:
                result = angular_spectrum(U0, wavelength, z, dx)
                sampling = dx
                algo = f"Near field algorithm for z <= zlimit , z limit = {z_limit:.2f}"
        else:
            result = fraunhofer(U0)
            sampling = wavelength * abs(z) / (N * dx)
            algo = f"Fraunhofer algorithm, z limit = {z_limit:.2f}"

        return result, sampling, algo
    
    def on_diffraction_done(self, result, eod):
        volume, sampling, algo_label_text = result
        self.volume = volume
        self.graph_widget.sampling = sampling
        self.algo_label.setText(algo_label_text)
        self.log_label.setText("")
        
        try:
            self.graph_widget.update_data(self.volume, eod=eod)
            self.graph_widget.update_cross_section()
            self.graph_widget.update_cursor_labels()
        except Exception as e:
            print(f"Error updating graph: {e}")


    def start_update_sweep(self, source, aperture, wavelength, dx):
        assert source.shape == aperture.shape, f"Unmatched array shape. Source {source.shape}, Aperture {aperture.shape}."
        U0 = source * aperture
        z_start = float(self.start_sweep)
        z_step = float(self.step_sweep)
        z_end = float(self.end_sweep)

        self.sim_thread = GenericThread(
            self.update_sweep,
            U0,
            wavelength,
            dx,
            z_start,
            z_end,
            z_step
        )

        self.sim_thread.progress_changed.connect(self.progress.setValue)
        self.sim_thread.finished_with_result.connect(self.on_sweep_done)

        self.progress.show()
        self.progress.setValue(0)

        # Start thread
        self.sim_thread.start()

    def update_sweep(self, U0, wavelength, dx, z_start, z_end, z_step, callback = None):
        try:
            volume, samplings, distances = sweep(U0, wavelength, dx, z_start,z_end, z_step, callback)
        except Exception as e:
            print(f"Update sweep error : {e}")
        return volume, samplings, distances, "distance"



    def on_sweep_done(self, result):
        if result is None:
            return 
        if result[3] == "distance":
            self.volume, self.graph_widget.samplings, self.graph_widget.distances, _ = result
            self.graph_widget.wavelengths = None
        else:
            self.volume, self.graph_widget.samplings, self.graph_widget.wavelengths, _ = result
            self.graph_widget.distances = None
        self.graph_widget.update_data(self.volume)
        self.graph_widget.update_cross_section()
        self.graph_widget.update_cursor_labels()
        self.graph_widget.on_time_changed()
        self.progress.hide()

    def start_update_sweep_w(self, source, aperture, z, dx):
        assert source.shape == aperture.shape, f"Unmatched array shape. Source {source.shape}, Aperture {aperture.shape}."
        U0 = source * aperture
        w_start = float(self.start_sweep_w)
        w_step = float(self.step_sweep_w)
        w_end = float(self.end_sweep_w)

        self.sim_thread = GenericThread(
            self.update_sweep_w,
            U0,
            z,
            dx,
            w_start,
            w_end,
            w_step
        )

        self.sim_thread.progress_changed.connect(self.progress.setValue)
        self.sim_thread.finished_with_result.connect(self.on_sweep_done)

        self.progress.show()
        self.progress.setValue(0)

        # Start thread
        self.sim_thread.start()

    def update_sweep_w(self, U0, z, dx, w_start, w_end, w_step, callback = None):
        try:
            volume, samplings, wavelengths = sweep_w(U0, z, dx, w_start, w_end, w_step, callback)
        except Exception as e:
            print(f"Update sweep error : {e}")
        return volume, samplings, wavelengths, "wavelengths"

    
    def pixout(self, source, wavelength, z, dx):
        N = max(source.shape)
        pixout_ = wavelength * abs(z) / (N * dx)
        return pixout_


    def update_resolution(self, text):
        self.resolution_multiplier = text

    def update_sweep_visibility(self, checked):
        self.sweep_widget.setVisible(checked)
        self.sweep_button.setVisible(checked)

    def update_sweep_w_visibility(self, checked):
        self.sweep_widget_w.setVisible(checked)
        self.sweep_button_w.setVisible(checked)

    def update_sweep_params(self):
        self.start_sweep = self.start_sweep_line_edit.text()
        self.end_sweep = self.end_sweep_line_edit.text()
        self.step_sweep = self.step_sweep_line_edit.text()

    def update_sweep_w_params(self):
        self.start_sweep_w = self.start_sweep_w_line_edit.text()
        self.end_sweep_w = self.end_sweep_w_line_edit.text()
        self.step_sweep_w = self.step_sweep_w_line_edit.text()
    
    def update_sim_params(self):
        self.simulation_distance = self.dst_sim_line_edit.text()
        self.wavelength = self.wavelength_line_edit.text()
        self.tile = self.tile_combo.currentText()


    def open_dialog(self):
        shape = self.filter_shape
        filter_type = self.filter_type
        remove_outside = self.remove_outside
        cutoff_freq = self.cutoff_freq
        thickness = self.thickness
        offset_x = self.offset_x
        offset_y = self.offset_y
        fx = self.fx
        fy = self.fy
        df = self.df
        current_values = {
            "shape" : shape,
            "filter_type": filter_type,
            "remove_outside": remove_outside,
            "cutoff_freq": cutoff_freq,
            "thickness" : thickness,
            "offset_x" : offset_x,
            "offset_y" : offset_y,
            "fx" :  fx,
            "fy" : fy,
            "df" : df
        }

        dialog = SimSettingsDialog(current_values)
        
        if dialog.exec_() == QDialog.Accepted:
            result = dialog.get_values()
            print("User clicked OK")
            self.filter_type = result["filter_type"]
            self.remove_outside = result["remove_outside"]
            self.cutoff_freq = result["cutoff_freq"]
            self.thickness = result["thickness"]
            self.filter = result["filter"]
            self.intermediate_updated.emit(result)
        else:
            print("User cancelled the dialog")

    def fourier_option(self, checked):
        if checked:
            self.intermediate_graph_widget.show()
            self.intermediate_settings_button.show()
            self.go_filtering_button.show()
            self.go_button.hide()
            self.checkbox_sweep.hide()
            self.checkbox_sweep_w.hide()
            self.distance_simulation_widget.hide()
            self.update_sweep_visibility(False)
            self.update_sweep_w_visibility(False)
            self.resolution_widget.hide()
        else:
            self.intermediate_graph_widget.hide()
            self.intermediate_settings_button.hide()
            self.go_filtering_button.hide()
            self.go_button.show()
            self.checkbox_sweep.show()
            self.checkbox_sweep_w.show()
            self.distance_simulation_widget.show()
            self.update_sweep_visibility(self.checkbox_sweep.isChecked())
            self.update_sweep_w_visibility(self.checkbox_sweep_w.isChecked())
            self.resolution_widget.show()


    def update_intermediate_graph(self, source, aperture):
        self.intermediate_volume = ft_1(source*aperture)
        
    def update_fourier_filtering_graph(self):
        intermediate_volume = self.intermediate_volume
        filter = self.filter
        U0 = intermediate_volume * filter
        self.volume = ft_2(U0)
        self.graph_widget.update_data(self.volume)

        
        



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimulationSection()
    window.show()
    app.exec()
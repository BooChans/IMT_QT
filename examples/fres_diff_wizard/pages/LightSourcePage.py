import sys
from PyQt5.QtWidgets import (
    QApplication, QWizard, QWizardPage, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QWidget, QComboBox, QRadioButton
)

class LightSourcePage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Light source parameters")
        self.setSubTitle("Define the light source parameters")
        self.source_type = "Plane Wave"
        self.wavelength = "0.633"
        self.beam_shape = "Elliptic"
        self.size = ("300","300")
        self.distance_unit = "µm"
        self.waist = "300"

        self.setup_ui()
        self.setup_connections()


    def setup_ui(self):
        
        self.page_layout = QVBoxLayout(self)

        self.setup_unit_widget()
        self.setup_spec_widget()
        self.setup_beam_widget()
        self.setup_beam_shape()



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
    def setup_spec_widget(self):
        #Spectral characteristics
        self.spec_widget = QWidget()
        self.spec_widget_layout = QHBoxLayout(self.spec_widget)

        wavelength_label = QLabel("Wavelength")
        self.wavelength_line_edit = QLineEdit()
        self.wavelength_line_edit.setText(self.wavelength)
        self.wavelength_line_edit.setFixedWidth(150)

        self.spec_widget_layout.addWidget(wavelength_label)
        self.spec_widget_layout.addWidget(self.wavelength_line_edit)

        self.page_layout.addWidget(self.spec_widget)
    def setup_beam_widget(self):
        #Beam type
        self.beam_label_widget = QWidget()
        self.beam_label_widget_layout = QHBoxLayout(self.beam_label_widget)
        beam_label = QLabel("Beam shape")
        self.beam_label_widget_layout.addWidget(beam_label)

        self.option1 = QRadioButton("Plane wave")
        self.option2 = QRadioButton("Gaussian beam")

        self.option1.setChecked(True)  


        self.beam_label_widget_layout.addStretch()
        self.beam_label_widget_layout.addWidget(self.option1)
        self.beam_label_widget_layout.addWidget(self.option2)


        self.page_layout.addWidget(self.beam_label_widget)
    def setup_beam_shape(self):
        # Widgets for Plane Wave
        self.plane_wave_widget = QWidget()
        self.plane_wave_layout = QVBoxLayout(self.plane_wave_widget)
        
        self.plane_wave_shape_widget = QWidget()
        self.plane_wave_shape_layout = QHBoxLayout(self.plane_wave_shape_widget)

        shape_label = QLabel("Shape")

        self.option_e = QRadioButton("Elliptic")
        self.option_r = QRadioButton("Rectangular")
        
        self.option_e.setChecked(True)  

        self.plane_wave_shape_layout.addWidget(shape_label)
        self.plane_wave_shape_layout.addStretch()
        self.plane_wave_shape_layout.addWidget(self.option_e)
        self.plane_wave_shape_layout.addWidget(self.option_r)
        
        self.plane_wave_size_widget = QWidget()
        self.plane_wave_size_layout = QHBoxLayout(self.plane_wave_size_widget)
        diameter_label = QLabel("Diameter")

        self.hdiameter_line_edit = QLineEdit()
        self.hdiameter_line_edit.setFixedWidth(100)
        self.hdiameter_line_edit.setText(self.size[0])
        x_label = QLabel("x")

        self.wdiameter_line_edit = QLineEdit()
        self.wdiameter_line_edit.setFixedWidth(100)     
        self.wdiameter_line_edit.setText(self.size[0])

        self.plane_wave_size_layout.addWidget(diameter_label)
        self.plane_wave_size_layout.addStretch()
        self.plane_wave_size_layout.addWidget(self.hdiameter_line_edit)
        self.plane_wave_size_layout.addWidget(x_label)
        self.plane_wave_size_layout.addWidget(self.wdiameter_line_edit)

        self.plane_wave_layout.addWidget(self.plane_wave_shape_widget)
        self.plane_wave_layout.addWidget(self.plane_wave_size_widget)
        self.page_layout.addWidget(self.plane_wave_widget)

        # Widgets for Gaussian Beam
        self.gaussian_widget = QWidget()
        self.gaussian_widget_layout = QHBoxLayout(self.gaussian_widget)
        self.gaussian_widget_layout.addWidget(QLabel("Beam waist"))
        self.gaussian_widget_layout.addStretch()
        self.beam_waist_line_edit = QLineEdit()
        self.beam_waist_line_edit.setFixedWidth(100)
        self.beam_waist_line_edit.setText(self.waist)
        self.gaussian_widget_layout.addWidget(self.beam_waist_line_edit)
        self.page_layout.addWidget(self.gaussian_widget)

        self.page_layout.addWidget(self.gaussian_widget)
        self.update_beam_widgets()
    def setup_connections(self):
        self.option1.toggled.connect(self.update_beam_widgets)
        self.option2.toggled.connect(self.update_beam_widgets)
    def update_beam_widgets(self):
        if self.option1.isChecked():
            self.plane_wave_widget.show()
            self.gaussian_widget.hide()
        elif self.option2.isChecked():
            self.plane_wave_widget.hide()
            self.gaussian_widget.show()
        else:
            self.plane_wave_widget.hide()
            self.gaussian_widget.hide()
    def get_inputs(self):
        self.source_type = "Plane Wave" if self.option1.isChecked() else "Gaussian Beam"
        self.beam_shape = "Elliptic" if self.option_e.isChecked() else "Rectangular"
        self.distance_unit = self.unit_combo.currentText()
        self.wavelength = self.wavelength_line_edit.text()
        if self.source_type == "Plane Wave":
            diameter_h = self.hdiameter_line_edit.text()
            diameter_w = self.wdiameter_line_edit.text()
            self.size = (diameter_h, diameter_w)
            self.waist = None
        else:
            self.size = None
            beam_waist = self.beam_waist_line_edit.text()
            self.waist = beam_waist

        return {
            "source_type": self.source_type,
            "beam_shape": self.beam_shape,
            "unit": self.distance_unit,
            "wavelength": self.wavelength,
            "size": self.size,
            "beam waist" : self.waist
        }

if __name__ == "__main__":

    app = QApplication(sys.argv)
    wizard = QWizard()

    wizard.setMinimumSize(1000, 800)

    page = LightSourcePage()
    wizard.addPage(page)
    wizard.finished.connect(lambda: print(page.get_inputs()))
    wizard.show()
    app.exec()
import sys
from PyQt5.QtWidgets import (
    QApplication, QWizard, QWizardPage, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QWidget, QComboBox, QRadioButton, QScrollArea
)

class SummaryPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Simulation Summary")
        self.setSubTitle("Review your parameters before proceeding")
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Create scroll area for potentially long summaries
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.content = QWidget()
        self.scroll_layout = QVBoxLayout(self.content)
        self.scroll.setWidget(self.content)
        self.layout.addWidget(self.scroll)
        
        # Will be populated when initialized
        self.summary_label = QLabel()
        self.summary_label.setWordWrap(True)
        self.scroll_layout.addWidget(self.summary_label)

    def initializePage(self):
        """Called when the page is displayed"""
        # Get parameters from previous pages
        source_params = self.wizard().page(0).get_inputs()  # Assuming source is page 0
        aperture_params = self.wizard().page(1).get_inputs()  # Assuming aperture is page 1
        
        # Format the summary text
        summary_text = self._format_summary(source_params, aperture_params)
        self.summary_label.setText(summary_text)

    def _format_summary(self, source_params, aperture_params):
        """Create a nicely formatted summary string"""
        text = "<h3>Source Parameters:</h3>"
        text += f"<b>Type:</b> {source_params['source_type']}<br>"
        text += f"<b>Shape:</b> {source_params['beam_shape']}<br>"
        text += f"<b>Wavelength:</b> {source_params['wavelength']} {source_params['unit']}<br>"
        if source_params['size']:
            text += f"<b>Size:</b> {source_params['size'][0]} × {source_params['size'][1]} {source_params['unit']}<br>"
        else: 
            text += f"<b>Beam Waist:</b> {source_params['beam waist']} {source_params['unit']}<br>"
        
        text += "<h3>Aperture Parameters:</h3>"
        text += f"<b>Shape:</b> {aperture_params['aperture_shape']}<br>"
        
        if aperture_params['aperture_size']:
            text += f"<b>Aperture Size:</b> {aperture_params['aperture_size'][0]} × {aperture_params['aperture_size'][1]} {aperture_params['distance_unit']}<br>"
        
        if aperture_params['slit_width']:
            text += f"<b>Slit Width:</b> {aperture_params['slit_width']} {aperture_params['distance_unit']}<br>"
            text += f"<b>Slit Distance:</b> {aperture_params['slit_distance']} {aperture_params['distance_unit']}<br>"
        
        if aperture_params['array_matrix']:
            text += f"<b>Array Matrix:</b> {aperture_params['array_matrix'][0]} × {aperture_params['array_matrix'][1]}<br>"
            text += f"<b>Array Spacing:</b> {aperture_params['array_spacing']} {aperture_params['distance_unit']}<br>"
        
        if aperture_params['big_diameter']:
            text += f"<b>Big Diameter:</b> {aperture_params['big_diameter']} {aperture_params['distance_unit']}<br>"
            text += f"<b>Small Diameter:</b> {aperture_params['small_diameter']} {aperture_params['distance_unit']}<br>"
        
        if aperture_params['square_size']:
            text += f"<b>Square Size:</b> {aperture_params['square_size']} {aperture_params['distance_unit']}<br>"
        
        text += "<h3>Simulation Parameters:</h3>"
        text += f"<b>Simulation distance z:</b> {aperture_params['simulation_distance']} {aperture_params['distance_unit']}<br>"
         



        return text
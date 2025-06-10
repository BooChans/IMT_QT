import sys
from PyQt5.QtWidgets import (
    QWizard,QApplication
)
from fres_diff_wizard.pages.LightSourcePage import LightSourcePage
from fres_diff_wizard.pages.AperturePage import AperturePage
from fres_diff_wizard.pages.SummaryPage import SummaryPage


class MyWizard(QWizard):
    def __init__(self):
        super().__init__()
        
        # Add your pages
        self.addPage(LightSourcePage())  # Page 0
        self.addPage(AperturePage())  # Page 1
        self.addPage(SummaryPage())  # Page 2
        
        self.setWindowTitle("Optics Simulation Wizard")

if __name__ == "__main__":

    app = QApplication(sys.argv)

    wizard = MyWizard()
    wizard.show()

    app.exec()
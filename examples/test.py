import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QSplitter
from PyQt5.QtCore import Qt
import pyqtgraph as pg

# Replace with your refactored RealTimeCrossSectionViewer (as QWidget)
from DiffractionSection import RealTimeCrossSectionViewer  

class TripleViewer(QWidget):
    def __init__(self, volume_data_list, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)

        # Add three independent viewers
        for vol in volume_data_list:
            viewer = RealTimeCrossSectionViewer(vol)
            splitter.addWidget(viewer)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    z_dim, y_dim, x_dim = 100, 256, 256
    x = np.arange(x_dim)
    y = np.arange(y_dim)
    xx, yy = np.meshgrid(x, y)
    chessboard_2d = ((xx // 32 + yy // 32) % 2).astype(float)
    base_volume = np.stack([chessboard_2d for _ in range(z_dim)], axis=0)

    # Create three slightly different volumes for demo
    volumes = [base_volume, base_volume * 0.5, base_volume * 0.2]

    window = TripleViewer(volumes)
    window.resize(1500, 800)
    window.show()

    sys.exit(app.exec_())
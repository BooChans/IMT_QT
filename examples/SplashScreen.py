import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QCheckBox,
    QSplitter, QLabel, QSlider, QGridLayout, QPushButton, QAction, QMessageBox, QComboBox, QHBoxLayout, QSizePolicy
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap
import sys


class SplashScreen(QWidget):
    def __init__(self, WindowClass, img_path):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setFixedSize(1200, 700)
        self.windowclass = WindowClass
        self.img_path = img_path

        layout = QVBoxLayout()
        label = QLabel()
        pixmap = QPixmap(img_path)

        available_width = self.width()
        available_height = self.height() - 50  # reserve 50px for button

        scaled_pixmap = pixmap.scaled(
            available_width,
            available_height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        label.setPixmap(scaled_pixmap)

        label.setAlignment(Qt.AlignCenter)

        button = QPushButton("Enter Application")
        button.clicked.connect(self.proceed)

        layout.addWidget(label)
        layout.addWidget(button)
        self.setLayout(layout)

    def proceed(self):
        self.close()
        self.main_window = self.windowclass()
        self.main_window.show()

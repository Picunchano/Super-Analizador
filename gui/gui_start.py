# gui/gui_start.py

import sys
import os
import glob 

from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QMessageBox
from PyQt6.QtGui import QFont, QColor, QPalette, QPixmap
from PyQt6.QtCore import Qt

# Asumimos que los otros archivos están en las carpetas correctas
from .gui_game_explorer import GameExplorer
from app_analyzer.info_data import DataManager

class Inicio(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bienvenida 💖")
        self.setGeometry(200, 200, 650, 700)

        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#ffe6f0"))
        self.setPalette(palette)

        # Logo principal
        self.logo_principal = QLabel(self)
        self.logo_principal.setPixmap(QPixmap(os.path.join(os.path.dirname(__file__), "pictures", "Pink Y2K K-Pop Merch Store Logo (1).png")))
        self.logo_principal.setScaledContents(True)
        self.logo_principal.setFixedSize(600, 400)
        self.logo_principal.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Imagen secundaria
        self.imagen_secundaria = QLabel(self)
        pixmap_secundaria = QPixmap(os.path.join(os.path.dirname(__file__), "pictures", "2432632.png"))
        if pixmap_secundaria.isNull():
            print("Error: No se pudo cargar la imagen 2432632.png")
            self.imagen_secundaria.setText("Imagen no encontrada")
        else:
            self.imagen_secundaria.setPixmap(pixmap_secundaria)
        self.imagen_secundaria.setScaledContents(True)
        self.imagen_secundaria.setFixedSize(220, 220)
        self.imagen_secundaria.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.imagen_secundaria.setStyleSheet("border: none;")

        # Botón de inicio
        self.boton_iniciar = QPushButton("Iniciar aplicación 🎮", self)
        self.boton_iniciar.setStyleSheet(
            "background-color: #ff66b2; color: white; padding: 8px; border-radius: 5px;"
        )
        self.boton_iniciar.setFont(QFont("Arial", 14))
        self.boton_iniciar.clicked.connect(self.abrir_game_explorer)

        # Layout principal
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.addStretch(1)
        layout.addWidget(self.logo_principal, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.imagen_secundaria, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addStretch(2)
        layout.addWidget(self.boton_iniciar, 0, Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(30, 0, 30, 30)
        self.setLayout(layout)

        self.check_data_files()

    def check_data_files(self):
        data_dir = "data_base_game"
        if not os.path.isdir(data_dir):
            self.show_error(f"El directorio '{data_dir}' no existe.")
            return

        expected_files = 4
        files_found = glob.glob(os.path.join(data_dir, 'all_games_*.csv'))

        if len(files_found) < expected_files:
            self.show_error(f"Faltan archivos de datos. Se encontraron {len(files_found)} de {expected_files}.")

    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)
        self.boton_iniciar.setEnabled(False)
        self.boton_iniciar.setStyleSheet("background-color: #cccccc; color: #666666;")

    def abrir_game_explorer(self):
        self.manager = DataManager()
        self.ventana_secundaria = GameExplorer(self.manager)
        self.ventana_secundaria.show()
        self.close()
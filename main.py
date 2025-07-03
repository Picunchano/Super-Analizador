import sys
## Primero instala las dependencias necesarias:
## pip install PyQt6
## pip install pandas
## pip install matplotlib

from PyQt6.QtWidgets import QApplication
from gui.gui_start import Inicio

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana_de_bienvenida = Inicio()
    ventana_de_bienvenida.show()
    sys.exit(app.exec())
import sys
from cx_Freeze import setup, Executable

# Lista de carpetas y archivos que necesitas incluir
include_files = [
    ('data_base_game', 'data_base_game'),
    ('gui/pictures', 'gui/pictures')
]

# Opciones para la construcción del .exe
# Asegúrate de que todas las librerías que usas estén aquí
build_exe_options = {
    "packages": ["os", "pandas", "matplotlib", "PyQt6.QtWidgets"],
    "include_files": include_files
}

# Base para ocultar la consola de fondo en Windows
base = None
if sys.platform == "win32":
    base = "Win32GUI"

# Configuración final
setup(
    name="Super Analizador",
    version="1.0",
    description="Analizador de catálogos de videojuegos",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base)]
)
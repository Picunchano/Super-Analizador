# gui/gui_game_explorer.py

import sys
import pandas as pd
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QComboBox,
    QTabWidget, QListWidget, QTextEdit, QSlider, QHBoxLayout,
    QTableWidgetItem, QStatusBar, QListWidgetItem
)
from PyQt6.QtGui import QIcon, QColor
# Se añade QTimer para la búsqueda optimizada
from PyQt6.QtCore import Qt, QTimer
from app_analyzer.my_favorite_game import FavoritesManager

class GameExplorer(QMainWindow):
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.favorites_manager = FavoritesManager()

        self.analysis_data = None
        self.analysis_platform = None

        self.setWindowTitle("GameExplorer - Tu biblioteca de videojuegos")
        self.setGeometry(100, 100, 900, 600)

        self.initUI()
        self.apply_styles()
        
        # --- NUEVO: Configuración del temporizador para la búsqueda ---
        self.search_timer = QTimer(self)
        self.search_timer.setSingleShot(True)  # Se ejecuta solo una vez por pausa
        self.search_timer.setInterval(300)     # Espera 300ms después de la última letra
        self.search_timer.timeout.connect(self.search_games)

        # Carga inicial
        self.platform_selector.setCurrentIndex(0)
        self.platform_changed(self.platform_selector.currentText())
        self.populate_favorites_list()

    def initUI(self):
        # ... (código sin cambios)
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.tabs.addTab(self.tab_catalogo(), "Catálogo")
        self.tabs.addTab(self.tab_favoritos(), "Mis Juegos")
        self.tabs.addTab(self.tab_analisis(), "Análisis")
        self.tabs.addTab(self.tab_acerca(), "Acerca de")
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)


    def tab_catalogo(self):
        tab = QWidget()
        layout = QVBoxLayout()
        platform_layout = QHBoxLayout()
        platform_label = QLabel("Seleccionar Plataforma:")
        self.platform_selector = QComboBox()
        self.platform_selector.addItems(["PlayStation", "XBOX", "Nintendo", "PC"])
        self.platform_selector.currentTextChanged.connect(self.platform_changed)
        platform_layout.addWidget(platform_label)
        platform_layout.addWidget(self.platform_selector)
        platform_layout.addStretch()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por nombre del juego...")
        
        # --- MODIFICADO: La señal ahora activa el temporizador ---
        self.search_input.textChanged.connect(self.on_search_text_changed)
        
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Nombre", "Género", "Puntuación"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

        add_button = QPushButton("Agregar a Favoritos")
        add_button.clicked.connect(self.add_selected_to_favorites)

        layout.addLayout(platform_layout)
        layout.addWidget(self.search_input)
        layout.addWidget(self.table)
        layout.addWidget(add_button)
        tab.setLayout(layout)
        return tab

    # --- MÉTODO NUEVO: Inicia el temporizador cada vez que escribes ---
    def on_search_text_changed(self):
        """Reinicia el temporizador cada vez que el texto cambia."""
        self.search_timer.start()

    def search_games(self):
        """
        Esta función ahora es llamada por el temporizador, no directamente.
        """
        search_text = self.search_input.text()
        results_df = self.data_manager.search_game_name(search_text)
        self.populate_table(results_df)

    # ... (El resto de la clase, como tab_favoritos, tab_analisis, etc., se mantiene sin cambios)
    def tab_favoritos(self):
        tab = QWidget()
        layout = QVBoxLayout()
        self.fav_list = QListWidget()
        self.fav_list.currentItemChanged.connect(self.display_favorite_details)
        self.notes_area = QTextEdit()
        self.rating_slider = QSlider(Qt.Orientation.Horizontal)
        self.rating_slider.setRange(0, 10)
        self.rating_slider.setTickInterval(1)
        self.rating_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        fav_buttons_layout = QHBoxLayout()
        save_details_button = QPushButton("Guardar Cambios")
        save_details_button.clicked.connect(self.save_favorite_details)
        delete_button = QPushButton("Eliminar de Favoritos")
        delete_button.clicked.connect(self.remove_selected_favorite)
        fav_buttons_layout.addWidget(save_details_button)
        fav_buttons_layout.addWidget(delete_button)
        layout.addWidget(QLabel("Juegos Guardados:"))
        layout.addWidget(self.fav_list)
        layout.addWidget(QLabel("Notas Personales:"))
        layout.addWidget(self.notes_area)
        layout.addWidget(QLabel("Calificación Personal:"))
        layout.addWidget(self.rating_slider)
        layout.addLayout(fav_buttons_layout)
        tab.setLayout(layout)
        return tab

    def tab_analisis(self):
        tab = QWidget()
        layout = QVBoxLayout()
        platform_layout = QHBoxLayout()
        platform_label = QLabel("1. Selecciona la Consola:")
        self.analysis_platform_selector = QComboBox()
        self.analysis_platform_selector.addItems(["PlayStation", "XBOX", "Nintendo", "PC"])
        platform_layout.addWidget(platform_label)
        platform_layout.addWidget(self.analysis_platform_selector)
        genres_label = QLabel("2. Selecciona los Géneros:")
        self.analysis_genre_list = QListWidget()
        self.analysis_genre_list.setStyleSheet("QListWidget::item:hover { background-color: #fce4ec; }")
        self.analysis_genre_list.itemChanged.connect(self.update_genre_item_style)
        if self.data_manager.genre_map:
            for genre_name in sorted(self.data_manager.genre_map.values()):
                item = QListWidgetItem(genre_name)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Unchecked)
                self.analysis_genre_list.addItem(item)
        buttons_layout = QHBoxLayout()
        self.analyze_button = QPushButton("Contar Videojuegos")
        self.analyze_button.clicked.connect(self.perform_analysis)
        self.generate_chart_button = QPushButton("📊 Generar Gráfico")
        self.generate_chart_button.clicked.connect(self.generate_comparison_chart)
        self.generate_chart_button.setEnabled(False)
        buttons_layout.addWidget(self.analyze_button)
        buttons_layout.addWidget(self.generate_chart_button)
        self.analysis_results_label = QLabel("Resultados del análisis aparecerán aquí.")
        self.analysis_results_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.analysis_results_label.setStyleSheet("font-weight: normal; margin-top: 10px;")
        layout.addLayout(platform_layout)
        layout.addWidget(genres_label)
        layout.addWidget(self.analysis_genre_list)
        layout.addLayout(buttons_layout)
        layout.addWidget(self.analysis_results_label)
        tab.setLayout(layout)
        return tab

    def tab_acerca(self):
        tab = QWidget()
        layout = QVBoxLayout()
        info = QLabel(
            """
            <h2>GameExplorer</h2>
            <p>Aplicación creada para gestionar tu biblioteca de videojuegos.</p>
            <p><b>Autor:</b> Tu nombre aquí</p>
            <p><b>Versión:</b> 1.0</p>
            <p>Desarrollado en Python + PyQt6</p>
            """
        )
        info.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(info)
        tab.setLayout(layout)
        return tab

    def add_selected_to_favorites(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            self.status_bar.showMessage("Por favor, selecciona un juego del catálogo primero.", 4000)
            return
        row_index = selected_rows[0].row()
        game_data = {
            'name': self.table.item(row_index, 0).text(),
            'genres': self.table.item(row_index, 1).text(),
            'rating': self.table.item(row_index, 2).text()
        }
        if self.favorites_manager.add_favorite(game_data):
            self.status_bar.showMessage(f"'{game_data['name']}' añadido a favoritos.", 4000)
            self.populate_favorites_list()
        else:
            self.status_bar.showMessage(f"'{game_data['name']}' ya estaba en favoritos.", 4000)

    def remove_selected_favorite(self):
        selected_item = self.fav_list.currentItem()
        if not selected_item:
            self.status_bar.showMessage("Por favor, selecciona un juego de tu lista de favoritos.", 4000)
            return
        game_name = selected_item.text()
        self.favorites_manager.remove_favorite(game_name)
        self.status_bar.showMessage(f"'{game_name}' eliminado de favoritos.", 4000)
        self.populate_favorites_list()
        self.notes_area.clear()
        self.rating_slider.setValue(0)

    def populate_favorites_list(self):
        self.fav_list.clear()
        favorites = self.favorites_manager.get_all_favorites()
        if favorites is not None and not favorites.empty:
            for game_name in favorites['name']:
                self.fav_list.addItem(QListWidgetItem(game_name))

    def display_favorite_details(self, current_item, previous_item):
        if not current_item:
            self.notes_area.clear()
            self.rating_slider.setValue(0)
            return
        game_name = current_item.text()
        details = self.favorites_manager.get_favorite_details(game_name)
        if details is not None:
            self.notes_area.setText(str(details.get('personal_notes', '')))
            self.rating_slider.setValue(int(details.get('personal_rating', 0)))

    def save_favorite_details(self):
        selected_item = self.fav_list.currentItem()
        if not selected_item:
            self.status_bar.showMessage("Selecciona un juego para guardar los cambios.", 4000)
            return
        game_name = selected_item.text()
        notes = self.notes_area.toPlainText()
        rating = self.rating_slider.value()
        if self.favorites_manager.update_favorite_details(game_name, notes, rating):
            self.status_bar.showMessage(f"Cambios para '{game_name}' guardados.", 4000)
        else:
            self.status_bar.showMessage("Error al guardar los cambios.", 4000)

    def platform_changed(self, platform_name):
        success = self.data_manager.load_new_data(platform_name)
        if success:
            self.search_games()
            self.status_bar.showMessage(f"Mostrando juegos de {platform_name}", 5000)
        else:
            self.table.setRowCount(0)
            self.status_bar.showMessage(f"Error al cargar datos de {platform_name}", 5000)
    
    def populate_table(self, dataframe):
        if dataframe is None or dataframe.empty:
            self.table.setRowCount(0)
            return
        self.table.blockSignals(True)
        self.table.setRowCount(len(dataframe))
        column_map = {'name': 0, 'genres': 1, 'rating': 2}
        for row_idx, row_data in dataframe.iterrows():
            for col_name, col_idx in column_map.items():
                if col_name in row_data and pd.notna(row_data[col_name]):
                    item = QTableWidgetItem(str(row_data[col_name]))
                    self.table.setItem(row_idx, col_idx, item)
        self.table.blockSignals(False)
        self.table.resizeColumnsToContents()

    def perform_analysis(self):
        platform = self.analysis_platform_selector.currentText()
        self.data_manager.load_new_data(platform)
        self.status_bar.showMessage(f"Analizando base de datos de {platform}...", 3000)
        selected_genres = []
        for i in range(self.analysis_genre_list.count()):
            item = self.analysis_genre_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected_genres.append(item.text())
        if not selected_genres:
            self.analysis_results_label.setText("Por favor, selecciona al menos un género.")
            self.generate_chart_button.setEnabled(False)
            return
        counts = self.data_manager.count_games_by_genre(selected_genres)
        self.analysis_data = counts
        self.analysis_platform = platform
        results_text = f"<b>Conteo de juegos en {platform}:</b><br><br>"
        for genre, count in counts.items():
            results_text += f"• {genre}: <b>{count}</b> juegos<br>"
        self.analysis_results_label.setText(results_text)
        self.generate_chart_button.setEnabled(True)

    def update_genre_item_style(self, item):
        if item.checkState() == Qt.CheckState.Checked:
            item.setBackground(QColor("#f8bbd0"))
        else:
            item.setBackground(QColor("transparent"))
            
    def generate_comparison_chart(self):
        if not self.analysis_data:
            return
        genres = list(self.analysis_data.keys())
        counts = list(self.analysis_data.values())
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(genres, counts, color='#f06292')
        ax.set_ylabel('Cantidad de Juegos')
        ax.set_title(f'Comparativa de Géneros en {self.analysis_platform}')
        ax.tick_params(axis='x', rotation=45)
        fig.tight_layout()
        plt.show()

    def apply_styles(self):
        self.setStyleSheet(
            """
            QMainWindow { background-color: #fff0f5; }
            QTabWidget::pane { border: 1px solid #e91e63; }
            QTabBar::tab {
                background: #f8bbd0; border: 1px solid #e91e63; padding: 8px;
                border-top-left-radius: 8px; border-top-right-radius: 8px; margin-right: 2px;
            }
            QTabBar::tab:selected { background: #f06292; color: white; }
            QLabel { color: #880e4f; font-weight: bold; }
            QLineEdit, QComboBox, QTextEdit, QSlider {
                background-color: white; border: 1px solid #e91e63;
                border-radius: 4px; padding: 6px;
            }
            QPushButton {
                background-color: #e91e63; color: white; padding: 8px;
                border-radius: 6px; font-weight: bold;
            }
            QPushButton:hover { background-color: #d81b60; }
            QTableWidget { background-color: white; border: 1px solid #e91e63; }
            QListWidget { background-color: white; border: 1px solid #e91e63; }
            QStatusBar { background-color: #fce4ec; color: #880e4f; }
            """
        )
# app_analyzer/info_data.py

import pandas as pd
import os
import ast

class DataManager:
    """
    Gestiona la carga y búsqueda de datos desde los archivos CSV de videojuegos.
    """
    def __init__(self):
        self.df = pd.DataFrame()
        self.base_path = "data_base_game"
        self.genre_map = {}
        self.load_genres()
        print("DataManager listo. Mapeo de géneros cargado.")

    def load_genres(self):
        try:
            genres_csv_path = os.path.join(self.base_path, "genres.csv")
            genres_df = pd.read_csv(genres_csv_path)

            if len(genres_df.columns) >= 2:
                id_col = genres_df.columns[0]
                name_col = genres_df.columns[1]
                self.genre_map = pd.Series(genres_df[name_col].values, index=genres_df[id_col]).to_dict()
            else:
                print("ADVERTENCIA: 'genres.csv' no tiene las dos columnas esperadas.")
                self.genre_map = {}
        except FileNotFoundError:
            print("ADVERTENCIA: No se encontró 'genres.csv'. Se mostrarán los IDs.")
            self.genre_map = {}

    def _map_genre_ids_to_names(self, genre_ids_str):
        if not self.genre_map or pd.isna(genre_ids_str):
            return "Sin género"
        try:
            genre_ids = ast.literal_eval(genre_ids_str)
            genre_names = [self.genre_map.get(gid, "Desconocido") for gid in genre_ids]
            return ', '.join(genre_names)
        except (ValueError, SyntaxError):
            return "Género inválido"

    def load_new_data(self, platform):
        route_csv = os.path.join(self.base_path, f"all_games_{platform}.csv")
        try:
            self.df = pd.read_csv(route_csv)
            print(f"CSV de {platform} cargado exitosamente.")
            if self.genre_map and 'genres' in self.df.columns:
                print("Traduciendo IDs de género a nombres...")
                self.df['genres'] = self.df['genres'].apply(self._map_genre_ids_to_names)
                print("Traducción completada.")
            return True
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo CSV en la ruta: {route_csv}")
            self.df = pd.DataFrame()
            return False

    def get_full_catalog(self):
        return self.df

    def search_game_name(self, text_search):
        """
        Busca juegos por nombre. Si el texto está vacío, devuelve el catálogo completo.
        """
        if self.df.empty:
            return pd.DataFrame()
        
        if not text_search:
            return self.get_full_catalog()

        # Esta es la línea clave que filtra por nombre
        if 'name' in self.df.columns:
            result = self.df[self.df['name'].str.contains(text_search, case=False, na=False)]
            return result
            
        return pd.DataFrame()

    def count_games_by_genre(self, genres_to_count):
        if self.df.empty or 'genres' not in self.df.columns:
            return {}
        genre_counts = {}
        for genre in genres_to_count:
            count = self.df['genres'].str.contains(genre, na=False).sum()
            genre_counts[genre] = int(count)
        return genre_counts
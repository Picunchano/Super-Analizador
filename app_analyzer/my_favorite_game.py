# app_analyzer/my_favorite_game.py

import pandas as pd
import os

class FavoritesManager:
    """
    La función de esta clase es almacenar los juegos favoritos que añade el usuario.
    """

    def __init__(self, filepath='data_base_game/favorites.csv'):
        self.filepath = filepath
        self.columns = ['name', 'genres', 'rating', 'personal_notes', 'personal_rating']
        self.favorites_df = pd.DataFrame(columns=self.columns)
        self.load_favorites()

    def load_favorites(self):
        """Carga los juegos favoritos desde el archivo CSV."""
        if os.path.exists(self.filepath):
            try:
                self.favorites_df = pd.read_csv(self.filepath)
                print("Juegos Favoritos cargados.")
            except pd.errors.EmptyDataError:
                print("Archivo de favoritos está vacío. Se continúa con una lista nueva.")
                self.favorites_df = pd.DataFrame(columns=self.columns)
        else:
            print("No se encontró archivo de favoritos. Se creará uno nuevo.")
            self.save_favorites()

    # --- MÉTODO CORREGIDO ---
    # El nombre ahora es plural para ser consistente.
    def save_favorites(self):
        """Guarda la lista actual de favoritos en el archivo CSV."""
        self.favorites_df.to_csv(self.filepath, index=False)
        print("Los juegos favoritos han sido guardados.")

    def add_favorite(self, game_data):
        if game_data['name'] in self.favorites_df['name'].values:
            print(f"El juego '{game_data['name']}' ya está en favoritos.")
            return False
        
        game_data['personal_notes'] = ''
        game_data['personal_rating'] = 0

        new_favorite = pd.DataFrame([game_data])
        self.favorites_df = pd.concat([self.favorites_df, new_favorite], ignore_index=True)
        self.save_favorites() # La llamada ahora coincide
        return True

    def remove_favorite(self, game_name):
        self.favorites_df = self.favorites_df[self.favorites_df['name'] != game_name].reset_index(drop=True)
        self.save_favorites() # La llamada ahora coincide

    def get_all_favorites(self):
        return self.favorites_df

    def get_favorite_details(self, game_name):
        details = self.favorites_df[self.favorites_df['name'] == game_name]
        if not details.empty:
            return details.iloc[0]
        return None

    def update_favorite_details(self, game_name, notes, rating):
        """Actualiza las notas y la calificación de un juego favorito."""
        idx = self.favorites_df.index[self.favorites_df['name'] == game_name].tolist()
        if idx:
            self.favorites_df.loc[idx[0], 'personal_notes'] = notes
            self.favorites_df.loc[idx[0], 'personal_rating'] = rating
            self.save_favorites() # La llamada ahora coincide
            return True
        return False
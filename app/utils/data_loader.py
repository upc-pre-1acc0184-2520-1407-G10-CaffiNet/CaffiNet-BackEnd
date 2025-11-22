# app/utils/data_loader.py (FINAL Y CORREGIDO)

import pandas as pd
from pathlib import Path
from typing import Dict, Any, Union

DATA_DIR = Path(__file__).parent.parent / "data"

def load_csv(file_name: str, delimiter: str = ";") -> pd.DataFrame:
    """Carga un archivo CSV desde la carpeta 'data'."""
    path = DATA_DIR / file_name
    try:
        df = pd.read_csv(path, delimiter=delimiter, encoding="latin1")
        # Limpieza simple: convertir nombres de columnas a minúsculas y sin tildes
        df.columns = [
            col.lower()
            .replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
            .replace(' ', '_')
            for col in df.columns
        ]
        return df
    except FileNotFoundError:
        print(f"Error: Archivo no encontrado en {path}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error al cargar {file_name}: {e}")
        return pd.DataFrame()

class DataLoader:
    """
    Clase Singleton para cargar todos los datasets una sola vez y hacerlos
    accesibles como atributos.
    """
    _instance: Union['DataLoader', None] = None
    
    # --- Atributos para Almacenar Datos (Definiciones requeridas) ---
    
    # Mapeados por ID para acceso rápido O(1)
    cafeterias_data: Dict[int, Any] = {}
    tags_data: Dict[int, Any] = {}
    cafe_data: Dict[int, Any] = {}
    
    # DataFrames completos (ACCEDIDOS POR EL ROUTER)
    df_cafeterias: pd.DataFrame = pd.DataFrame()
    df_tags: pd.DataFrame = pd.DataFrame()
    df_cafes: pd.DataFrame = pd.DataFrame()
    
    df_bebidas: pd.DataFrame = pd.DataFrame()
    df_productos: pd.DataFrame = pd.DataFrame()
    df_horarios: pd.DataFrame = pd.DataFrame()
    cafes_bebidas_data: pd.DataFrame = pd.DataFrame()
    cafeterias_productos_data: pd.DataFrame = pd.DataFrame()
    
    # --- Singleton Pattern ---
    def __new__(cls) -> 'DataLoader':
        if cls._instance is None:
            cls._instance = super(DataLoader, cls).__new__(cls)
            cls._instance._load_data() # Carga los datos solo la primera vez
        return cls._instance

    # --- Lógica de Carga de Datos ---
    def _to_id_dict(self, df: pd.DataFrame, id_col: str) -> Dict[int, Any]:
        """Convierte un DataFrame a un diccionario usando una columna ID como clave."""
        if df.empty or id_col not in df.columns:
            return {}
        return df.set_index(id_col).to_dict('index')

    def _load_data(self):
        print("Iniciando carga de datasets (TODOS)...")
        
        # 1. Carga de DataFrames en variables locales
        df_tags_raw = load_csv("dataset_caracteristicas_cafeterias.csv")
        df_cafeterias_raw = load_csv("dataset_cafeterias_peru_colombia.csv")
        df_cafes_raw = load_csv("dataset_cafes.csv")
        
        # 2. ASIGNACIÓN A LOS ATRIBUTOS DE LA INSTANCIA (self.)
        self.df_tags = df_tags_raw
        self.df_cafeterias = df_cafeterias_raw
        self.df_cafes = df_cafes_raw
        
        self.df_bebidas = load_csv("dataset_cafe_datos.csv")
        self.df_productos = load_csv("dataset_producto.csv")
        self.cafes_bebidas_data = load_csv("dataset_relacion_cafeteria_bebidas.csv")
        self.cafeterias_productos_data = load_csv("dataset_relacion_cafeteria_productos.csv")
        self.df_horarios = load_csv("dataset_cafeterias_horarios.csv") 

        # 3. Mapeo a diccionarios
        self.cafeterias_data = self._to_id_dict(self.df_cafeterias, id_col='cafeteria_id')
        self.tags_data = self._to_id_dict(self.df_tags, id_col='cafeteria_id')
        self.cafe_data = self._to_id_dict(df_cafes_raw, id_col='id_cafes')
        
        print("Carga de datasets finalizada. Todos los datos están disponibles.")
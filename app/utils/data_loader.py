import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

def load_csv(file_name: str, delimiter: str = ";"):
    path = DATA_DIR / file_name
    df = pd.read_csv(path, delimiter=delimiter, encoding="latin1")
    return df

# Cargar todos los datasets
df_tags = load_csv("dataset_caracteristicas_cafeterias.csv")
df_cafeterias = load_csv("dataset_cafeterias_peru_colombia.csv")
df_cafes = load_csv("dataset_cafes.csv")
df_bebidas = load_csv("dataset_cafe_datos.csv")
df_productos = load_csv("dataset_producto.csv")
df_cafes_bebidas = load_csv("dataset_relacion_cafeteria_bebidas.csv")
df_cafeterias_productos = load_csv("dataset_relacion_cafeteria_productos.csv")
df_horarios = load_csv("dataset_cafeterias_horarios.csv")

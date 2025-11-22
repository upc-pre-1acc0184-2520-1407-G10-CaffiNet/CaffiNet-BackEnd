# app/routers/cafeterias.py (FINAL Y CORREGIDO)

from fastapi import APIRouter, Query
from app.utils.data_loader import DataLoader # Importamos la clase
import pandas as pd
from typing import Optional

router = APIRouter(prefix="/cafeterias", tags=["Cafeterias"])

# 1. Instancia Singleton para acceder a los datos
data_loader = DataLoader() 

# 2. Acceso a los DataFrames con los nombres CORRECTOS
# Ahora son data_loader.df_cafeterias y data_loader.df_tags
DF_CAFETERIAS = data_loader.df_cafeterias 
DF_TAGS = data_loader.df_tags 

# --- Función Auxiliar para Limpieza de Tags ---
def _clean_tags(df_t: pd.DataFrame) -> pd.DataFrame:
    """Normaliza las columnas booleanas de tags."""
    if df_t.empty:
        return df_t
        
    df_clean = df_t.copy()
    boolean_cols = ["pet_friendly", "enchufes", "wifi", "terraza"]
    
    for col in boolean_cols:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].astype(str).str.strip().str.lower().isin(["sí", "si"])
            
    return df_clean

# -------------------------------------------------------------
# ENDPOINT: GET /cafeterias
# -------------------------------------------------------------
@router.get("/")
def get_cafeterias(
    pet_friendly: Optional[bool] = Query(None),
    tipo_musica: Optional[str] = Query(None),
    iluminacion: Optional[str] = Query(None),
    enchufes: Optional[bool] = Query(None),
    wifi: Optional[bool] = Query(None),
    terraza: Optional[bool] = Query(None),
    estilo_decorativo: Optional[str] = Query(None)
):
    """
    Devuelve todas las cafeterías, filtrando opcionalmente por cualquier tag.
    """
    df = DF_CAFETERIAS.copy()
    df_t = _clean_tags(DF_TAGS)

    # Merge tags
    df = df.merge(df_t, on="cafeteria_id", how="left")

    # Filtrado dinámico
    if pet_friendly is not None:
        df = df[df["pet_friendly"] == pet_friendly]
    if tipo_musica:
        df = df[df["tipo_musica"].astype(str).str.lower() == tipo_musica.lower()]
    if iluminacion:
        df = df[df["iluminacion"].astype(str).str.lower() == iluminacion.lower()]
    if enchufes is not None:
        df = df[df["enchufes"] == enchufes]
    if wifi is not None:
        df = df[df["wifi"] == wifi]
    if terraza is not None:
        df = df[df["terraza"] == terraza]
    if estilo_decorativo:
        df = df[df["estilo_decorativo"].astype(str).str.lower() == estilo_decorativo.lower()]
        
    if df.empty:
        return []

    return df.to_dict(orient="records")


# -------------------------------------------------------------
# ENDPOINT: GET /cafeterias/{cafeteria_id}
# -------------------------------------------------------------
@router.get("/{cafeteria_id}")
def get_cafeteria_detail(cafeteria_id: int):
    """
    Devuelve información de una cafetería específica.
    """
    df_cafeteria = DF_CAFETERIAS[DF_CAFETERIAS["cafeteria_id"] == cafeteria_id].copy()
    
    if df_cafeteria.empty:
        return {"message": "Cafetería no encontrada"}
    
    # Merge con tags
    df_t = _clean_tags(DF_TAGS)
    
    df_cafeteria = df_cafeteria.merge(df_t[df_t['cafeteria_id'] == cafeteria_id], on="cafeteria_id", how="left")
    
    if not df_cafeteria.empty:
        return df_cafeteria.iloc[0].to_dict()
        
    return {"message": "Detalle de cafetería no encontrado después del merge"}
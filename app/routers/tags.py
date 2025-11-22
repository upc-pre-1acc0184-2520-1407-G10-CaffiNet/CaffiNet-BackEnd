from fastapi import APIRouter, Query
from app.utils.data_loader import DataLoader # 🛑 CORRECCIÓN: Importamos la clase DataLoader
import pandas as pd
from typing import List, Dict, Any, Optional

router = APIRouter(prefix="/tags", tags=["Tags"])

# 1. Obtener la instancia Singleton y cargar los datos
data_loader = DataLoader() 

# 2. Acceder al DataFrame como atributo de la instancia
DF_TAGS = data_loader.df_tags 

# --- Función Auxiliar para Limpieza de Tags ---
def _clean_tags(df: pd.DataFrame) -> pd.DataFrame:
    """Normaliza las columnas booleanas de tags de 'sí/no' a True/False."""
    if df.empty:
        return df.copy()
    
    df_clean = df.copy()
    boolean_cols = ["pet_friendly", "enchufes", "wifi", "terraza"]
    
    for col in [c for c in boolean_cols if c in df_clean.columns]:
        # Convierte 'sí/si' a True, cualquier otra cosa a False (incluida NaN)
        df_clean[col] = df_clean[col].apply(
            lambda x: True if str(x).strip().lower() in ["sí", "si"] else False
        )
            
    return df_clean

# -------------------------------------------------------------
# ENDPOINT: GET /tags/
# Usa un solo endpoint para /tags/ y /tags/?cafeteria_id=X
# -------------------------------------------------------------
@router.get("/")
def get_tags(cafeteria_id: Optional[int] = Query(None)) -> List[Dict[str, Any]] | Dict[str, Any]:
    """
    Devuelve los tags de todas las cafeterías o de una específica, 
    convirtiendo los valores 'sí/no' a True/False.
    """
    if DF_TAGS.empty:
        return []

    # Aplicamos la limpieza de booleanos al DataFrame original
    df = _clean_tags(DF_TAGS)
    
    if cafeteria_id is not None:
        # Filtrado por ID si se proporciona
        df_filtered = df[df["cafeteria_id"] == cafeteria_id]
        
        if df_filtered.empty:
            return {"message": "Cafetería no encontrada"}
            
        row = df_filtered.iloc[0].to_dict()
        
        # Retorno del detalle (formato solicitado)
        return {
            "cafeteria_id": row["cafeteria_id"], 
            "tags": {k: row[k] for k in df.columns if k != "cafeteria_id"}
        }
    
    # Retorno de todos los registros (formato solicitado)
    result = []
    for _, row in df.iterrows():
        result.append({
            "cafeteria_id": row["cafeteria_id"],
            "tags": {k: row[k] for k in df.columns if k != "cafeteria_id"}
        })
    return result
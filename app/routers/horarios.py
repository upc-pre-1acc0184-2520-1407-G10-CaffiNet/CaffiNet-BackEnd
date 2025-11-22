from fastapi import APIRouter, HTTPException
from app.utils.data_loader import DataLoader # 🛑 CORRECCIÓN: Importamos la clase DataLoader
from typing import Dict, Any

router = APIRouter(prefix="/horarios", tags=["Horarios"]) # Agregamos prefix y tags

# 1. Obtener la instancia Singleton
data_loader = DataLoader() 

# 2. Acceder al DataFrame como atributo de la instancia
DF_HORARIOS = data_loader.df_horarios 

@router.get("/{cafeteria_id}")
def get_horario(cafeteria_id: int) -> Dict[str, Any]:
    """
    Devuelve el horario de una cafetería específica por ID.
    """
    if DF_HORARIOS.empty:
        raise HTTPException(status_code=500, detail="Datos de horarios no cargados.")

    df = DF_HORARIOS[DF_HORARIOS["cafeteria_id"] == cafeteria_id]
    
    if df.empty:
        raise HTTPException(status_code=404, detail="No se encontró horario para esta cafetería")
        
    return df.iloc[0].to_dict()
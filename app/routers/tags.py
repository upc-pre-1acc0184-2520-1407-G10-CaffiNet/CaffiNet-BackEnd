from fastapi import APIRouter, Query
from app.utils.data_loader import df_tags

router = APIRouter()

@router.get("/")
def get_tags(cafeteria_id: int = None):
    """
    Devuelve los tags de todas las cafeterías o de una específica.
    Convierte 'sí/no' a True/False
    """
    df = df_tags.copy()
    
    # Convertir booleanos
    boolean_cols = ["pet_friendly", "enchufes", "wifi", "terraza"]
    for col in boolean_cols:
        df[col] = df[col].apply(lambda x: True if str(x).strip().lower() in ["sí", "si"] else False)
    
    if cafeteria_id:
        df = df[df["cafeteria_id"] == cafeteria_id]
        if df.empty:
            return {"message": "Cafetería no encontrada"}
        row = df.iloc[0].to_dict()
        return {"cafeteria_id": row["cafeteria_id"], "tags": {k: row[k] for k in df.columns if k != "cafeteria_id"}}
    
    # Todos
    result = []
    for _, row in df.iterrows():
        result.append({
            "cafeteria_id": row["cafeteria_id"],
            "tags": {k: row[k] for k in df.columns if k != "cafeteria_id"}
        })
    return result

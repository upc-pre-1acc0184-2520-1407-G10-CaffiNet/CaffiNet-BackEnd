from fastapi import APIRouter, Query
from app.utils.data_loader import df_cafeterias_productos, df_productos

router = APIRouter()

@router.get("/{cafeteria_id}")
def get_cafeteria_productos(
    cafeteria_id: int,
    tipo: str = None,
    vegano: bool = None
):
    df = df_cafeterias_productos[df_cafeterias_productos["cafeteria_id"] == cafeteria_id]
    if df.empty:
        return {"message": "No hay productos para esta cafetería"}
    
    # Join con productos
    df = df.merge(df_productos, left_on="producto_id", right_on="id_productos", how="left")
    
    # Filtros opcionales
    if tipo:
        df = df[df["tipo"].str.lower() == tipo.lower()]
    if vegano is not None:
        df = df[df["vegano"].str.lower() == ("sí" if vegano else "no")]

    return df.to_dict(orient="records")

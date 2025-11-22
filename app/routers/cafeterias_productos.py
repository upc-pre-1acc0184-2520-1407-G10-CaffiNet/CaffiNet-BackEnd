from fastapi import APIRouter, Query
from app.utils.data_loader import DataLoader

router = APIRouter()

# Obtener la instancia Singleton
data_loader = DataLoader()
DF_CAFETERIAS_PRODUCTOS = data_loader.cafeterias_productos_data
DF_PRODUCTOS = data_loader.df_productos

@router.get("/{cafeteria_id}")
def get_cafeteria_productos(
    cafeteria_id: int,
    tipo: str = None,
    vegano: bool = None
):
    df = DF_CAFETERIAS_PRODUCTOS[DF_CAFETERIAS_PRODUCTOS["cafeteria_id"] == cafeteria_id]
    if df.empty:
        return {"message": "No hay productos para esta cafetería"}
    
    # Join con productos
    df = df.merge(DF_PRODUCTOS, left_on="producto_id", right_on="id_productos", how="left")
    
    # Filtros opcionales
    if tipo:
        df = df[df["tipo"].str.lower() == tipo.lower()]
    if vegano is not None:
        df = df[df["vegano"].str.lower() == ("sí" if vegano else "no")]

    return df.to_dict(orient="records")

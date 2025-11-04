from fastapi import APIRouter, Query
from app.utils.data_loader import df_productos, df_cafeterias_productos

router = APIRouter()

@router.get("/")
def get_productos(
    tipo: str = None,
    vegano: bool = None,
    precio_min: float = None,
    precio_max: float = None
):
    df = df_productos.copy()

    if tipo:
        df = df[df["tipo"].str.lower() == tipo.lower()]
    if vegano is not None:
        df = df[df["vegano"].str.lower() == ("sí" if vegano else "no")]
    if precio_min is not None:
        df = df[df["precio"] >= precio_min]
    if precio_max is not None:
        df = df[df["precio"] <= precio_max]

    return df.to_dict(orient="records")

@router.get("/{producto_id}")
def get_producto(producto_id: int):
    df = df_productos[df_productos["id_productos"] == producto_id]
    if df.empty:
        return {"message": "Producto no encontrado"}
    return df.iloc[0].to_dict()

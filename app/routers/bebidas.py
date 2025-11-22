from fastapi import APIRouter, Query
from app.utils.data_loader import DataLoader

router = APIRouter()

# Obtener la instancia Singleton
data_loader = DataLoader()
DF_BEBIDAS = data_loader.df_bebidas

@router.get("/")
def get_bebidas(
    categoria: str = None,
    bebida: str = None,
    tamano: str = None,
    leche: str = None
):
    """
    Devuelve todas las bebidas con filtros opcionales.
    """
    df = DF_BEBIDAS.copy()

    if categoria:
        df = df[df["Categoría"].str.lower() == categoria.lower()]
    if bebida:
        df = df[df["Bebida"].str.lower() == bebida.lower()]
    if tamano:
        df = df[df["Tamaño"].str.lower() == tamano.lower()]
    if leche:
        df = df[df["Leche"].str.lower() == leche.lower()]

    return df.to_dict(orient="records")

@router.get("/{bebida_id}")
def get_bebida(bebida_id: int):
    df = DF_BEBIDAS[DF_BEBIDAS["id_tipo_bebida"] == bebida_id]
    if df.empty:
        return {"message": "Bebida no encontrada"}
    return df.iloc[0].to_dict()

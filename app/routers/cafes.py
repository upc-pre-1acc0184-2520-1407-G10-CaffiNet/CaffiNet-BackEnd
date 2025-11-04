from fastapi import APIRouter, Query
from app.utils.data_loader import df_cafes

router = APIRouter()

@router.get("/")
def get_cafes(pais: str = None, variedad: str = None):
    df = df_cafes.copy()
    if pais:
        df = df[df["pais"].str.lower() == pais.lower()]
    if variedad:
        df = df[df["variedad"].str.lower() == variedad.lower()]
    return df.to_dict(orient="records")

@router.get("/{cafe_id}")
def get_cafe(cafe_id: int):
    df = df_cafes[df_cafes["id_cafes"] == cafe_id]
    if df.empty:
        return {"message": "Café no encontrado"}
    return df.iloc[0].to_dict()

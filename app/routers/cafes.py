from fastapi import APIRouter, Query
from app.utils.data_loader import DataLoader

router = APIRouter()

# Obtener la instancia Singleton
data_loader = DataLoader()
DF_CAFES = data_loader.df_cafes

@router.get("/")
def get_cafes(pais: str = None, variedad: str = None):
    df = DF_CAFES.copy()
    if pais:
        df = df[df["pais"].str.lower() == pais.lower()]
    if variedad:
        df = df[df["variedad"].str.lower() == variedad.lower()]
    return df.to_dict(orient="records")

@router.get("/{cafe_id}")
def get_cafe(cafe_id: int):
    df = DF_CAFES[DF_CAFES["id_cafes"] == cafe_id]
    if df.empty:
        return {"message": "Café no encontrado"}
    return df.iloc[0].to_dict()

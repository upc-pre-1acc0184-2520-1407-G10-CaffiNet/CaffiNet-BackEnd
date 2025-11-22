from fastapi import APIRouter, Query
from app.utils.data_loader import DataLoader

router = APIRouter()

# Obtener la instancia Singleton
data_loader = DataLoader()
DF_CAFES_BEBIDAS = data_loader.cafes_bebidas_data
DF_BEBIDAS = data_loader.df_bebidas

@router.get("/{cafeteria_id}")
def get_cafeteria_bebidas(
    cafeteria_id: int,
    categoria: str = None,
    bebida: str = None
):
    df = DF_CAFES_BEBIDAS[DF_CAFES_BEBIDAS["cafeteria_id"] == cafeteria_id]
    if df.empty:
        return {"message": "No hay bebidas para esta cafetería"}
    
    # Join con bebidas
    df = df.merge(DF_BEBIDAS, left_on="bebida_id", right_on="id_tipo_bebida", how="left")
    
    # Filtros opcionales
    if categoria:
        df = df[df["categoria"].str.lower() == categoria.lower()]
    if bebida:
        df = df[df["Bebida"].str.lower() == bebida.lower()]

    return df.to_dict(orient="records")

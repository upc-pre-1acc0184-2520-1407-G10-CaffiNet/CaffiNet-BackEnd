from fastapi import APIRouter, Query
from app.utils.data_loader import df_cafeterias, df_tags

router = APIRouter(prefix="/cafeterias", tags=["Cafeterias"])

@router.get("/")
def get_cafeterias(
    pet_friendly: bool = None,
    tipo_musica: str = None,
    iluminacion: str = None,
    enchufes: bool = None,
    wifi: bool = None,
    terraza: bool = None,
    estilo_decorativo: str = None
):
    """
    Devuelve todas las cafeterías, filtrando opcionalmente por cualquier tag.
    """
    df = df_cafeterias.copy()
    df_t = df_tags.copy()

    # Convertir booleanos
    boolean_cols = ["pet_friendly", "enchufes", "wifi", "terraza"]
    for col in boolean_cols:
        df_t[col] = df_t[col].apply(lambda x: True if str(x).strip().lower() in ["sí", "si"] else False)

    # Merge tags
    df = df.merge(df_t, on="cafeteria_id", how="left")

    # Filtrado dinámico
    if pet_friendly is not None:
        df = df[df["pet_friendly"] == pet_friendly]
    if tipo_musica:
        df = df[df["tipo_musica"].str.lower() == tipo_musica.lower()]
    if iluminacion:
        df = df[df["iluminacion"].str.lower() == iluminacion.lower()]
    if enchufes is not None:
        df = df[df["enchufes"] == enchufes]
    if wifi is not None:
        df = df[df["wifi"] == wifi]
    if terraza is not None:
        df = df[df["terraza"] == terraza]
    if estilo_decorativo:
        df = df[df["estilo_decorativo"].str.lower() == estilo_decorativo.lower()]

    return df.to_dict(orient="records")


@router.get("/{cafeteria_id}")
def get_cafeteria_detail(cafeteria_id: int):
    """
    Devuelve información de una cafetería específica.
    """
    df = df_cafeterias[df_cafeterias["cafeteria_id"] == cafeteria_id]
    if df.empty:
        return {"message": "Cafetería no encontrada"}
    
    # Merge con tags
    df_t = df_tags.copy()
    boolean_cols = ["pet_friendly", "enchufes", "wifi", "terraza"]
    for col in boolean_cols:
        df_t[col] = df_t[col].apply(lambda x: True if str(x).strip().lower() in ["sí", "si"] else False)
    
    df = df.merge(df_t, on="cafeteria_id", how="left")
    return df.iloc[0].to_dict()

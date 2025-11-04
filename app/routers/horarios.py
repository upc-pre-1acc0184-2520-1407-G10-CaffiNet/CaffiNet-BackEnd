from fastapi import APIRouter
from app.utils.data_loader import df_horarios

router = APIRouter()

@router.get("/{cafeteria_id}")
def get_horario(cafeteria_id: int):
    df = df_horarios[df_horarios["cafeteria_id"] == cafeteria_id]
    if df.empty:
        return {"message": "No se encontró horario para esta cafetería"}
    return df.iloc[0].to_dict()

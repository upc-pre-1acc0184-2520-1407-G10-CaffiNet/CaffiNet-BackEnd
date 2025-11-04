# routers/historial.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import HistorialBusqueda
from datetime import datetime

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def add_historial(usuario_id: int, termino: str, db: Session = Depends(get_db)):
    hist = HistorialBusqueda(usuario_id=usuario_id, termino=termino, fecha_hora=datetime.utcnow())
    db.add(hist)
    db.commit()
    db.refresh(hist)
    return hist

@router.get("/{usuario_id}")
def get_historial(usuario_id: int, db: Session = Depends(get_db)):
    return db.query(HistorialBusqueda).filter(HistorialBusqueda.usuario_id==usuario_id).all()

# routers/calificaciones.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Calificacion

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def add_calificacion(usuario_id: int, cafeteria_id: int, rating: int, db: Session = Depends(get_db)):
    cal = Calificacion(usuario_id=usuario_id, cafeteria_id=cafeteria_id, rating=rating)
    db.add(cal)
    db.commit()
    db.refresh(cal)
    return cal

@router.get("/{cafeteria_id}")
def get_calificaciones(cafeteria_id: int, db: Session = Depends(get_db)):
    return db.query(Calificacion).filter(Calificacion.cafeteria_id==cafeteria_id).all()

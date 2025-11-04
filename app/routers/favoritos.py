# routers/favoritos.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Favorito

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def add_favorito(usuario_id: int, cafeteria_id: int, db: Session = Depends(get_db)):
    existing = db.query(Favorito).filter(
        Favorito.usuario_id==usuario_id, Favorito.cafeteria_id==cafeteria_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Favorito ya existe")
    fav = Favorito(usuario_id=usuario_id, cafeteria_id=cafeteria_id)
    db.add(fav)
    db.commit()
    db.refresh(fav)
    return fav

@router.get("/{usuario_id}")
def get_favoritos(usuario_id: int, db: Session = Depends(get_db)):
    return db.query(Favorito).filter(Favorito.usuario_id==usuario_id).all()

@router.delete("/")
def remove_favorito(usuario_id: int, cafeteria_id: int, db: Session = Depends(get_db)):
    fav = db.query(Favorito).filter(
        Favorito.usuario_id==usuario_id, Favorito.cafeteria_id==cafeteria_id
    ).first()
    if not fav:
        raise HTTPException(status_code=404, detail="Favorito no encontrado")
    db.delete(fav)
    db.commit()
    return {"detail": "Favorito eliminado"}

# routers/usuarios.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Usuario
from pydantic import BaseModel
from passlib.context import CryptContext

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Schemas de Pydantic
class UsuarioResponse(BaseModel):
    id: int
    nombre: str
    email: str

    class Config:
        orm_mode = True

class UsuarioUpdate(BaseModel):
    nombre: str = None
    email: str = None
    password: str = None

# Dependency para obtener sesión DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Obtener un usuario por ID
@router.get("/{user_id}", response_model=UsuarioResponse)
def get_usuario(user_id: int, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

# Actualizar usuario
@router.put("/{user_id}", response_model=UsuarioResponse)
def update_usuario(user_id: int, usuario: UsuarioUpdate, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if usuario.nombre:
        user.nombre = usuario.nombre
    if usuario.email:
        user.email = usuario.email
    if usuario.password:
        user.password = pwd_context.hash(usuario.password)

    db.commit()
    db.refresh(user)
    return user

# app/models.py
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Enum, TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base
from pydantic import BaseModel
from typing import Dict, Any, List

# --------------------------
# Historial de búsquedas
# --------------------------
class HistorialBusqueda(Base):
    __tablename__ = "historial_busqueda"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    termino = Column(String(255), nullable=False)
    fecha_hora = Column(DateTime, default=datetime.utcnow)

    usuario = relationship("Usuario", back_populates="historial")


# --------------------------
# Usuario
# --------------------------
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50))
    email = Column(String(50), unique=True, index=True)
    password = Column(String(100))

    historial = relationship("HistorialBusqueda", back_populates="usuario")
    calificaciones = relationship("Calificacion", back_populates="usuario")
    favoritos = relationship("Favorito", back_populates="usuario")


# --------------------------
# Cafetería
# --------------------------
class Cafeteria(Base):
    __tablename__ = "cafeterias"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100))
    country = Column(String(50))
    latitude = Column(Integer)
    longitude = Column(Integer)

    tags = relationship("Tag", back_populates="cafeteria")
    calificaciones = relationship("Calificacion", back_populates="cafeteria")
    niveles = relationship("NivelCafeteria", back_populates="cafeteria")
    favoritos = relationship("Favorito", back_populates="cafeteria")


# --------------------------
# Tags de cafetería
# --------------------------
class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    cafeteria_id = Column(Integer, ForeignKey("cafeterias.id"))
    pet_friendly = Column(Boolean)
    tipo_musica = Column(String(50))
    iluminacion = Column(String(50))
    enchufes = Column(Boolean)
    wifi = Column(Boolean)
    terraza = Column(Boolean)
    estilo_decorativo = Column(String(50))

    cafeteria = relationship("Cafeteria", back_populates="tags")


# --------------------------
# Calificaciones
# --------------------------
class Calificacion(Base):
    __tablename__ = "calificaciones"

    id = Column(Integer, primary_key=True, index=True)
    cafeteria_id = Column(Integer, ForeignKey("cafeterias.id"))
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    rating = Column(Integer)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    cafeteria = relationship("Cafeteria", back_populates="calificaciones")
    usuario = relationship("Usuario", back_populates="calificaciones")


# --------------------------
# Niveles de cafetería
# --------------------------
class NivelEnum(enum.Enum):
    Bronze = "Bronze"
    Silver = "Silver"
    Gold = "Gold"

class NivelCafeteria(Base):
    __tablename__ = "niveles_cafeteria"

    cafeteria_id = Column(Integer, ForeignKey("cafeterias.id"), primary_key=True)
    nivel = Column(Enum(NivelEnum))

    cafeteria = relationship("Cafeteria", back_populates="niveles")


# --------------------------
# Favoritos
# --------------------------
class Favorito(Base):
    __tablename__ = "favoritos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    cafeteria_id = Column(Integer, ForeignKey("cafeterias.id"))

    usuario = relationship("Usuario", back_populates="favoritos")
    cafeteria = relationship("Cafeteria", back_populates="favoritos")

# --- Entradas (Input) ---

class UserLocation(BaseModel):
    latitude: float
    longitude: float

class OptimalRouteRequest(BaseModel):
    algorithm: str # Dijkstra, Floyd-Warshall, Bellman-Ford
    user_location: UserLocation
    filters: Dict[str, Any] # Tags, precios, etc.

# --- Salidas (Output) ---

class CafeRouteItemSchema(BaseModel):
    cafeteria_id: int
    name: str
    latitude: float
    longitude: float
    optimal_cost: float
    distance_km: float

class OptimalRouteResultSchema(BaseModel):
    ordered_cafeterias: List[CafeRouteItemSchema]
    selected_algorithm: str
    big_o_notation: str
    processing_time_ms: int
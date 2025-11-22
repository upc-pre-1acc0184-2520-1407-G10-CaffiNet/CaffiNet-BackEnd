# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.utils import discover

app = FastAPI(title="Caffinet Backend")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializa la base de datos y crea tablas si no existen
init_db()

# Routers
from app.routers import (
    cafeterias,
    tags,
    bebidas,
    productos,
    cafes,
    cafeterias_bebidas,
    cafeterias_productos,
    horarios,
    auth,
    usuarios,
    favoritos,
    calificaciones,
    historial_busquedas,
)

# Routers de datasets
app.include_router(tags.router, prefix="/tags", tags=["Tags"])
app.include_router(cafeterias.router, prefix="/cafeterias", tags=["Cafeterias"])
app.include_router(bebidas.router, prefix="/bebidas", tags=["Bebidas"])
app.include_router(productos.router, prefix="/productos", tags=["Productos"])
app.include_router(cafes.router, prefix="/cafes", tags=["Cafés"])
app.include_router(
    cafeterias_bebidas.router,
    prefix="/cafeterias-bebidas",
    tags=["Cafeterias-Bebidas"],
)
app.include_router(
    cafeterias_productos.router,
    prefix="/cafeterias-productos",
    tags=["Cafeterias-Productos"],
)
app.include_router(horarios.router, prefix="/horarios", tags=["Horarios"])

# Routers de usuarios y app
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(usuarios.router, prefix="/usuarios", tags=["Usuarios"])
app.include_router(favoritos.router, prefix="/favoritos", tags=["Favoritos"])
app.include_router(
    calificaciones.router, prefix="/calificaciones", tags=["Calificaciones"]
)
app.include_router(historial_busquedas.router, prefix="/historial", tags=["Historial"])
app.include_router(discover.router)

@app.get("/")
def root():
    return {"message": "Backend Caffinet funcionando correctamente"}

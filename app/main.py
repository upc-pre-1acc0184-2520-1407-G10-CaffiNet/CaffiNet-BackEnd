# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db, SessionLocal
from app.utils import discover

# importamos Cafeteria y DataLoader para el seeding
from app.models import Cafeteria
from app.utils.data_loader import DataLoader

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

# ==========================
# Seeding automático de cafeterias
# ==========================
def seed_cafeterias_if_empty():
    """
    Si la tabla `cafeterias` está vacía, la llena usando el mismo dataset
    que usa el router de cafeterías (DataLoader.df_cafeterias).
    """
    db = SessionLocal()
    try:
        count = db.query(Cafeteria).count()
        if count > 0:
            print(f"[seed] Tabla cafeterias ya tiene {count} filas. No se hace seeding.")
            return

        print("[seed] Tabla cafeterias vacía. Cargando dataset y seedéandola...")

        loader = DataLoader()
        df = loader.df_cafeterias.copy()

        insertados = 0

        for _, row in df.iterrows():

            caf_id = int(row["cafeteria_id"])

            # Por si acaso, aunque la tabla esté vacía
            existing = db.query(Cafeteria).filter(Cafeteria.id == caf_id).first()
            if existing:
                continue

            # Solo necesitamos el id para que las FKs de favoritos/calificaciones funcionen
            cafeteria = Cafeteria(id=caf_id)
            db.add(cafeteria)
            insertados += 1

        db.commit()
        print(f"[seed] Cafeterías insertadas: {insertados}")
        print("[seed] Seeding de cafeterias completado ✅")

    finally:
        db.close()


@app.on_event("startup")
def on_startup():
    # Se ejecuta automáticamente al levantar el backend
    seed_cafeterias_if_empty()


@app.get("/")
def root():
    return {"message": "Backend Caffinet funcionando correctamente"}

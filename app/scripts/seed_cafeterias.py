# app/scripts/seed_cafeterias.py

from app.utils.data_loader import DataLoader
from app.database import SessionLocal
from app.models import Cafeteria


def main():
    # 1. Crear sesión con la BD
    db = SessionLocal()

    # 2. Cargar el mismo DataFrame que usa el router de cafeterías
    loader = DataLoader()
    df = loader.df_cafeterias.copy()

    print("Columnas del DataFrame de cafeterías:")
    print(df.columns)

    insertados = 0
    ya_existian = 0

    for _, row in df.iterrows():
        # En tu router usas la columna 'cafeteria_id' para hacer el merge
        caf_id = int(row["cafeteria_id"])

        # 3. Ver si ya existe en la tabla (para poder ejecutar el script varias veces)
        existing = db.query(Cafeteria).filter(Cafeteria.id == caf_id).first()
        if existing:
            ya_existian += 1
            continue

        # 4. Crear la fila de Cafeteria
        # OJO: solo seteamos el id, los demás campos pueden quedar NULL.
        cafeteria = Cafeteria(
            id=caf_id
            # Si más adelante quieres, puedes mapear también:
            # nombre=row.get("nombre"),
            # country=row.get("country"),
            # latitude=row.get("latitude"),
            # longitude=row.get("longitude"),
        )

        db.add(cafeteria)
        insertados += 1

    # 5. Guardar cambios
    db.commit()
    db.close()

    print("===================================")
    print(f"Cafeterías insertadas: {insertados}")
    print(f"Cafeterías que ya existían: {ya_existian}")
    print("Seeding terminado ✅")


if __name__ == "__main__":
    main()


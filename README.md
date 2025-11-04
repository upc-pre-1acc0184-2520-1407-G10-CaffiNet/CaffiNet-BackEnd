# Caffinet Backend

Backend para la aplicación Caffinet, desarrollado con **FastAPI**, **SQLAlchemy** y **MySQL**.

---

## Requisitos

- Python 3.10+
- MySQL Server
- Git

---

## Clonar el repositorio

```bash
git clone https://github.com/upc-pre-1acc0184-2520-1407-G10-CaffiNet/CaffiNet-BackEnd.git
cd Caffinet-Backend
```


## Crear y activar entorno virtual

Primero, asegúrate de instalar `venv` si no lo tienes (normalmente viene con Python 3.10+).

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

## Instalar dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt

```
> **Nota:** `requirements.txt` incluye todas las librerías necesarias, como FastAPI, SQLAlchemy, pymysql, pandas, etc.



## Configuración del archivo `.env`

Crea un archivo `.env` en la raíz del proyecto con tus credenciales de base de datos:

```bash
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña
DB_HOST=localhost
DB_PORT=3306
DB_NAME=caffinet_db
```
> **Nota:** Importante: No subas `.env` al repositorio. Puedes crear un env.example como plantilla.


## Crear la base de datos

En MySQL:

```bash
CREATE DATABASE caffinet_db;
```

> **Nota:** Asegúrate que el nombre coincida con el que pusiste en `.env`.

## Ejecutar el backend

Desde la raíz del proyecto, con el entorno virtual activado:

```bash
uvicorn app.main:app --reload
```


```bash
http://127.0.0.1:8000/docs#/
```

## Rutas Principales

- `/` → Mensaje de bienvenida
- `/tags` → Gestión de tags
- `/cafeterias` → Gestión de cafeterías
- `/bebidas` → Gestión de bebidas
- `/productos` → Gestión de productos
- `/auth` → Autenticación
- `/usuarios` → Gestión de usuarios
- `/favoritos` → Favoritos de usuarios
- `/calificaciones` → Calificaciones de cafeterías
- `/historial` → Historial de búsquedas

> **Nota:** Las demás rutas están documentadas en los routers correspondientes.


## Notas

- Asegúrate de tener los datasets en la carpeta `app/data` si los usas.
- No subir al repositorio: venv/, __pycache__/, archivos .pyc, .env.
- Cada vez que modifiques código, con `--reload `Uvicorn recargará automáticamente.
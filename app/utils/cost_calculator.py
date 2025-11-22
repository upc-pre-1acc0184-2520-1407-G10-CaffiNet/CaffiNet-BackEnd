# app/utils/cost_calculator.py
from typing import Dict, List, Any, Tuple
from math import radians, sin, cos, sqrt, atan2
from datetime import datetime
from app.utils.data_loader import DataLoader # Asumo que tienes un DataLoader
import requests
import polyline

# Carga la Data (deberías tener una instancia Singleton de tu DataLoader)
data_loader = DataLoader()
COFFEE_DATA = data_loader.cafe_data
CAFETERIA_DATA = data_loader.cafeterias_data
TAGS_DATA = data_loader.tags_data
# DataFrames útiles para filtros
DF_HORARIOS = data_loader.df_horarios
DF_PRODUCTOS = data_loader.df_productos
CAFETERIAS_PRODUCTOS_DF = data_loader.cafeterias_productos_data
CAFES_BEBIDAS_DF = data_loader.cafes_bebidas_data
DF_BEBIDAS = data_loader.df_bebidas
# Añade aquí más data: BEBIDAS_DATA, PRODUCTOS_DATA, etc.

# --- Constante de Distancia (Radio de la Tierra en km) ---
R = 6371.0

# --- OSRM para obtener polylines ---
OSRM_URL = "http://router.project-osrm.org/route/v1/driving" 

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calcula la distancia Haversine entre dos puntos en kilómetros."""
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance


def _tag_true(value: Any) -> bool:
    """Normaliza valores de tags y devuelve True si la respuesta indica 'sí'."""
    if value is None:
        return False
    s = str(value).strip().lower()
    return s.startswith('s') or s in ('si', 'sí', 'true', '1', 'y', 'yes')


def _weekday_name_spanish(dt: datetime) -> str:
    # Map Python weekday (0=Lunes) to Spanish names used in dataset
    mapping = {
        0: 'lunes', 1: 'martes', 2: 'miercoles', 3: 'jueves', 4: 'viernes', 5: 'sabado', 6: 'domingo'
    }
    return mapping[dt.weekday()]


def is_open_now(cafeteria_id: int, now: datetime = None) -> bool:
    """Determina si una cafetería está abierta ahora usando `DF_HORARIOS`.

    La columna `dias_abre` suele contener rangos como 'Lunes-Sabado' o listados;
    esta función hace una comprobación conservadora: si alguna fila para la cafetería
    incluye el día actual y las horas contienen valores válidos, intentamos evaluar.
    """
    if DF_HORARIOS is None or DF_HORARIOS.empty:
        return True
    if now is None:
        now = datetime.now()

    try:
        df = DF_HORARIOS
        rows = df[df['cafeteria_id'] == cafeteria_id]
        if rows.empty:
            return True

        weekday = _weekday_name_spanish(now)
        current_minutes = now.hour * 60 + now.minute

        for _, r in rows.iterrows():
            dias = str(r.get('dias_abre', '')).lower()
            if weekday not in dias and '-' not in dias and weekday not in dias.split(','):
                # si no menciona el día explícitamente, ignoramos esta fila
                continue

            try:
                apertura = str(r.get('hora_apertura', '')).strip()
                cierre = str(r.get('hora_cierre', '')).strip()
                if not apertura or not cierre:
                    continue
                # Formato esperado HH:MM
                ah, am = map(int, apertura.split(':'))
                ch, cm = map(int, cierre.split(':'))
                apertura_min = ah * 60 + am
                cierre_min = ch * 60 + cm

                # si cierre < apertura asumimos horario pasado la medianoche
                if cierre_min < apertura_min:
                    # abierto si ahora >= apertura o ahora <= cierre
                    if current_minutes >= apertura_min or current_minutes <= cierre_min:
                        return True
                else:
                    if apertura_min <= current_minutes <= cierre_min:
                        return True
            except Exception:
                # Si falla parseo, consideramos esa fila no válida y seguimos
                continue

        # Si ninguna fila indica abierto ahora, devolvemos False
        return False
    except Exception:
        return True


def has_vegan_option(cafeteria_id: int) -> bool:
    """Comprueba de forma básica si la cafetería ofrece productos catalogados como veganos."""
    try:
        if CAFETERIAS_PRODUCTOS_DF is None or CAFETERIAS_PRODUCTOS_DF.empty or DF_PRODUCTOS is None or DF_PRODUCTOS.empty:
            return False

        rel = CAFETERIAS_PRODUCTOS_DF
        prod_ids = rel[rel['cafeteria_id'] == cafeteria_id]['producto_id'].unique()
        if len(prod_ids) == 0:
            return False

        prods = DF_PRODUCTOS[DF_PRODUCTOS['producto_id'].isin(prod_ids)]
        if prods.empty:
            return False

        # Buscamos en columnas descriptivas palabras 'vegano' o 'vegan'
        for col in prods.columns:
            try:
                if prods[col].astype(str).str.lower().str.contains('vegano|vegan').any():
                    return True
            except Exception:
                continue

        return False
    except Exception:
        return False

# --- Lógica de Ponderación de Preferencias ---

def calculate_preference_cost(cafeteria_id: int, filters: Dict[str, Any]) -> float:
    """
    Calcula el coste adicional (penalización) o beneficio (coste negativo)
    basado en las preferencias del usuario.
    
    Mayor coste = Menos deseable.
    Menor coste = Más deseable.
    """
    coste = 0.0

    tag_data = TAGS_DATA.get(cafeteria_id, {}) or {}

    # Hard/soft tag-based preferences
    # Si el usuario pide pet_friendly y la cafetería no lo es -> excluir (handled in prefilter)
    if filters.get('pet_friendly', False) and not _tag_true(tag_data.get('pet_friendly')):
        coste += 5.0

    # Soft preferences: si coincide tipo_musica, iluminacion o estilo, reducimos coste
    preferred_music = filters.get('tipo_musica')
    if preferred_music and preferred_music == tag_data.get('tipo_musica'):
        coste -= 1.0

    preferred_iluminacion = filters.get('iluminacion')
    if preferred_iluminacion and preferred_iluminacion == tag_data.get('iluminacion'):
        coste -= 0.8

    preferred_estilo = filters.get('estilo_decorativo')
    if preferred_estilo and preferred_estilo == tag_data.get('estilo_decorativo'):
        coste -= 0.8

    # Vegano: comprobar relaciones reales, si tiene opciones veganas reducimos coste, si no, penalizamos
    if filters.get('vegano', False):
        if has_vegan_option(cafeteria_id):
            coste -= 1.5
        else:
            coste += 5.0

    # Variedad de cafe (ejemplo de beneficio)
    if filters.get('variedad_cafe') and filters.get('variedad_cafe') == COFFEE_DATA.get(cafeteria_id, {}).get('variedad'):
        coste -= 2.0

    return coste

# --- Constructor del Grafo ---

def build_preference_graph(
    user_lat: float, 
    user_lon: float, 
    filters: Dict[str, Any]
) -> Tuple[Dict[int, Dict[int, float]], List[int], int]:
    """
    Construye el grafo de cafeterías con el usuario como nodo central.
    El peso de la arista es (Distancia + Coste de Preferencia).
    """
    
    # 1. Filtra las cafeterías según las preferencias iniciales (hard-filters)
    candidate_cafeterias = {}

    max_distance_km = filters.get('distancia_max_km')
    abierto_req = filters.get('abierto_ahora', False)

    for cafeteria_id, cafe_data in CAFETERIA_DATA.items():
        # Ignorar si faltan coordenadas
        if 'latitude' not in cafe_data or 'longitude' not in cafe_data:
            continue

        # Tag checks (hard filters)
        tag_data = TAGS_DATA.get(cafeteria_id, {}) or {}
        if filters.get('wifi') and not _tag_true(tag_data.get('wifi')):
            continue
        if filters.get('terraza') and not _tag_true(tag_data.get('terraza')):
            continue
        if filters.get('enchufes') and not _tag_true(tag_data.get('enchufes')):
            continue
        if filters.get('pet_friendly') and not _tag_true(tag_data.get('pet_friendly')):
            continue

        # Distance filter (hard)
        cafe_lat = cafe_data['latitude'] / 10**7
        cafe_lon = cafe_data['longitude'] / 10**7
        distance = haversine_distance(user_lat, user_lon, cafe_lat, cafe_lon)
        if max_distance_km is not None:
            try:
                if float(distance) > float(max_distance_km):
                    continue
            except Exception:
                pass

        # Horarios: abierto_ahora
        if abierto_req:
            if not is_open_now(cafeteria_id):
                continue

        # --- Filtros sobre precio / bebidas / productos (hard filters) ---
        # Precio: 'precio' puede ser una cadena o lista con valores 'barato','medio','caro'
        precio_filter = filters.get('precio')
        if precio_filter:
            wanted = precio_filter if isinstance(precio_filter, (list, tuple)) else [precio_filter]
            wanted = [str(w).strip().lower() for w in wanted]
            has_category = False
            try:
                # Revisar bebidas
                if CAFES_BEBIDAS_DF is not None and not CAFES_BEBIDAS_DF.empty:
                    rel = CAFES_BEBIDAS_DF
                    rows = rel[rel['cafeteria_id'] == cafeteria_id]
                    if not rows.empty and 'categoria' in rows.columns:
                        categorias = rows['categoria'].astype(str).str.lower().unique()
                        if any(w in categorias for w in wanted):
                            has_category = True
                # Revisar productos si no encontrado en bebidas
                if not has_category and CAFETERIAS_PRODUCTOS_DF is not None and not CAFETERIAS_PRODUCTOS_DF.empty:
                    relp = CAFETERIAS_PRODUCTOS_DF
                    rows_p = relp[relp['cafeteria_id'] == cafeteria_id]
                    if not rows_p.empty and 'categoria' in rows_p.columns:
                        categorias_p = rows_p['categoria'].astype(str).str.lower().unique()
                        if any(w in categorias_p for w in wanted):
                            has_category = True
            except Exception:
                has_category = False

            if not has_category:
                continue

        # Categoria de bebida: filtra por la columna 'categoria' en df_bebidas (p.ej. 'Caf�', 'Bebidas Espresso Cl�sicas')
        bebida_categoria = filters.get('categoria_bebida')
        if bebida_categoria:
            wanted_b = bebida_categoria if isinstance(bebida_categoria, (list, tuple)) else [bebida_categoria]
            wanted_b = [str(w).strip().lower() for w in wanted_b]
            has_b_cat = False
            try:
                if CAFES_BEBIDAS_DF is not None and not CAFES_BEBIDAS_DF.empty and DF_BEBIDAS is not None and not DF_BEBIDAS.empty:
                    rel = CAFES_BEBIDAS_DF
                    bebida_ids = rel[rel['cafeteria_id'] == cafeteria_id]['bebida_id'].unique()
                    if len(bebida_ids) > 0:
                        # columna de id en DF_BEBIDAS: intentar detectar nombre (id_tipo_bebida o id)
                        id_cols = [c for c in DF_BEBIDAS.columns if 'id' in c]
                        if id_cols:
                            id_col = id_cols[0]
                            matches = DF_BEBIDAS[DF_BEBIDAS[id_col].isin(bebida_ids)]
                            if not matches.empty and 'categoria' in matches.columns:
                                cats = matches['categoria'].astype(str).str.lower().unique()
                                if any(w in cats for w in wanted_b):
                                    has_b_cat = True
            except Exception:
                has_b_cat = False

            if not has_b_cat:
                continue

        # Tipos de producto: filtra por DF_PRODUCTOS['tipo'] (ej. 'postre','comida','bebida')
        tipos_producto = filters.get('tipos_producto')
        if tipos_producto:
            wanted_t = tipos_producto if isinstance(tipos_producto, (list, tuple)) else [tipos_producto]
            wanted_t = [str(w).strip().lower() for w in wanted_t]
            has_tipo = False
            try:
                if CAFETERIAS_PRODUCTOS_DF is not None and not CAFETERIAS_PRODUCTOS_DF.empty and DF_PRODUCTOS is not None and not DF_PRODUCTOS.empty:
                    relp = CAFETERIAS_PRODUCTOS_DF
                    producto_ids = relp[relp['cafeteria_id'] == cafeteria_id]['producto_id'].unique()
                    if len(producto_ids) > 0:
                        # columna id en DF_PRODUCTOS: buscar 'id_productos' o similar
                        id_cols_p = [c for c in DF_PRODUCTOS.columns if 'id' in c]
                        if id_cols_p:
                            id_col_p = id_cols_p[0]
                            matches_p = DF_PRODUCTOS[DF_PRODUCTOS[id_col_p].isin(producto_ids)]
                            if not matches_p.empty and 'tipo' in matches_p.columns:
                                tipos = matches_p['tipo'].astype(str).str.lower().unique()
                                if any(w in tipos for w in wanted_t):
                                    has_tipo = True
            except Exception:
                has_tipo = False

            if not has_tipo:
                continue

        candidate_cafeterias[cafeteria_id] = cafe_data
    
    # ID especial para el nodo de origen del usuario
    USER_NODE_ID = 0 
    
    # Inicializa el grafo
    graph: Dict[int, Dict[int, float]] = {USER_NODE_ID: {}}
    nodes = [USER_NODE_ID]

    for cafeteria_id, cafe_data in candidate_cafeterias.items():
        nodes.append(cafeteria_id)

        cafe_lat = cafe_data['latitude'] / 10**7 # Denormalizar Lat/Lon (datos estan en 10^7)
        cafe_lon = cafe_data['longitude'] / 10**7

        # 1. Distancia física
        distance = haversine_distance(user_lat, user_lon, cafe_lat, cafe_lon)

        # 2. Coste de preferencias
        preference_cost = calculate_preference_cost(cafeteria_id, filters)

        # 3. Peso Total de la Arista (Coste = Distancia + Penalización/Beneficio)
        total_weight = distance + preference_cost

        # Añadir la arista del usuario a la cafetería (solo rutas unidireccionales desde el usuario)
        graph[USER_NODE_ID][cafeteria_id] = total_weight
        
        # Opcional: Para Floyd-Warshall y Bellman-Ford,
        # necesitarías también añadir aristas entre cafeterías si quieres rutas múltiples.
        # Por ahora, solo rutas desde el usuario.
        
    return graph, nodes, USER_NODE_ID


def get_route_polyline(
    start_lat: float, 
    start_lon: float, 
    end_lat: float, 
    end_lon: float
) -> List[Tuple[float, float]]:
    """
    Obtiene el polyline (lista de puntos lat/lon) desde el servicio OSRM.
    Retorna una lista de tuplas (lat, lon) que representa la ruta geométrica.
    Si OSRM no responde o hay error, retorna una línea recta (solo puntos inicio/fin).
    """
    try:
        # Formato OSRM: lng,lat (nota el orden invertido)
        coordinates = f"{start_lon},{start_lat};{end_lon},{end_lat}"
        url = f"{OSRM_URL}/{coordinates}"
        params = {
            "steps": "false",
            "geometries": "polyline",  # Retorna polyline6 (comprimido)
            "overview": "full",  # Incluye la ruta completa
        }
        
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        if data.get("code") == "Ok" and data.get("routes"):
            route = data["routes"][0]
            geometry_str = route.get("geometry", "")
            if geometry_str:
                # Decodificar polyline6 (formato comprimido de Google)
                points = polyline.decode(geometry_str, precision=6)
                # polyline.decode devuelve [(lat, lon), ...], que es lo que queremos
                return points
        
        return [(start_lat, start_lon), (end_lat, end_lon)]
    except Exception as e:
        # Si hay error, retorna línea recta como fallback
        print(f"Error al obtener polyline de OSRM: {e}")
        return [(start_lat, start_lon), (end_lat, end_lon)]
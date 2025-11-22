# app/utils/cost_calculator.py
from typing import Dict, List, Any, Tuple
from math import radians, sin, cos, sqrt, atan2
from app.utils.data_loader import DataLoader # Asumo que tienes un DataLoader

# Carga la Data (deberías tener una instancia Singleton de tu DataLoader)
data_loader = DataLoader() 
COFFEE_DATA = data_loader.cafe_data 
CAFETERIA_DATA = data_loader.cafeterias_data
TAGS_DATA = data_loader.tags_data
# Añade aquí más data: BEBIDAS_DATA, PRODUCTOS_DATA, etc.

# --- Constante de Distancia (Radio de la Tierra en km) ---
R = 6371.0 

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calcula la distancia Haversine entre dos puntos en kilómetros."""
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance

# --- Lógica de Ponderación de Preferencias ---

def calculate_preference_cost(cafeteria_id: int, filters: Dict[str, Any]) -> float:
    """
    Calcula el coste adicional (penalización) o beneficio (coste negativo)
    basado en las preferencias del usuario.
    
    Mayor coste = Menos deseable.
    Menor coste = Más deseable.
    """
    coste = 0.0
    
    # 1. Ponderación por Tags (ej: Pet Friendly)
    tag_data = TAGS_DATA.get(cafeteria_id, {})
    if tag_data:
        # Penalización si el usuario quiere pet_friendly y la cafetería no lo es
        if filters.get('pet_friendly', False) and not tag_data.get('pet_friendly'):
            coste += 5.0
        
        # Penalización/Beneficio por Música
        preferred_music = filters.get('tipo_musica')
        if preferred_music and tag_data.get('tipo_musica') != preferred_music:
            coste += 2.0
            
    # 2. Ponderación por Menú (ej: Vegano)
    # **ESTO REQUIERE LLAMAR A LAS TABLAS DE RELACIÓN (cafeterias-productos/bebidas)**
    # Por ahora, es un placeholder:
    if filters.get('vegano', False):
         # Asumimos que si no hay productos veganos, penalizamos.
         # Aquí iría la lógica real de consulta a los datos de productos.
         coste += 5.0 # Penalización ficticia
         
    # 3. Ponderación por Algoritmo y Peso de Preferencia (Ejemplo)
    # Podemos asignar beneficios (pesos negativos) para priorizar más que solo la distancia.
    if filters.get('variedad_cafe') == COFFEE_DATA.get(cafeteria_id, {}).get('variedad'):
        coste -= 2.0 # Si coincide la variedad, la ruta es 2.0 "km" más corta (beneficio)
        
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
    
    # 1. Filtra las cafeterías según las preferencias iniciales (Ej: solo en el rango)
    # Por simplicidad, tomaremos todas las cafeterías como candidatas
    candidate_cafeterias = CAFETERIA_DATA 
    
    # ID especial para el nodo de origen del usuario
    USER_NODE_ID = 0 
    
    # Inicializa el grafo
    graph: Dict[int, Dict[int, float]] = {USER_NODE_ID: {}}
    nodes = [USER_NODE_ID]

    for cafeteria_id, cafe_data in candidate_cafeterias.items():
        
        # Ignorar si faltan coordenadas (simulación)
        if 'latitude' not in cafe_data or 'longitude' not in cafe_data:
            continue
            
        nodes.append(cafeteria_id)
        
        cafe_lat = cafe_data['latitude'] / 10**9 # Desnormalizar Lat/Lon si es necesario
        cafe_lon = cafe_data['longitude'] / 10**9

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
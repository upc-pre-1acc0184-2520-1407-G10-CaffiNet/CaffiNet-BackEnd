# app/routers/discover.py
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from app.models import OptimalRouteRequest, OptimalRouteResultSchema, CafeRouteItemSchema
from app.utils.cost_calculator import build_preference_graph, haversine_distance
from app.utils.graph_algorithms import dijkstra_algorithm, floyd_warshall_algorithm, bellman_ford_algorithm

router = APIRouter(
    prefix="/discover",
    tags=["Discover (Graph Algorithms)"],
)

@router.post("/optimal_route/", response_model=OptimalRouteResultSchema)
def calculate_optimal_route(request: OptimalRouteRequest):
    """
    Calcula la ruta óptima desde la ubicación del usuario a las cafeterías
    usando el algoritmo de grafo seleccionado y las preferencias ponderadas.
    """
    
    user_lat = request.user_location.latitude
    user_lon = request.user_location.longitude
    algorithm_name = request.algorithm
    filters = request.filters
    
    # 1. Construir el grafo (Nodos y Aristas ponderadas)
    graph, all_nodes, user_node_id = build_preference_graph(
        user_lat=user_lat, 
        user_lon=user_lon, 
        filters=filters
    )
    
    if user_node_id not in graph:
        raise HTTPException(status_code=400, detail="No se pudo inicializar el nodo de usuario.")

    # 2. Ejecutar el algoritmo seleccionado
    distances: Dict[Any, float] = {}
    processing_time: float = 0.0
    big_o: str = ""
    
    if algorithm_name == "Dijkstra":
        distances, processing_time, big_o = dijkstra_algorithm(graph, user_node_id)
    elif algorithm_name == "Floyd-Warshall":
        # Nota: Floyd-Warshall requiere aristas entre todos los nodos para ser útil.
        # Aquí lo simularemos extrayendo solo las distancias desde el nodo de usuario.
        all_dist, processing_time, big_o = floyd_warshall_algorithm(graph, all_nodes)
        distances = {node: all_dist.get((user_node_id, node), float('inf')) for node in all_nodes}
    elif algorithm_name == "Bellman-Ford":
        distances, processing_time, big_o = bellman_ford_algorithm(graph, user_node_id, all_nodes)
        if big_o == "Ciclo Negativo Detectado":
             raise HTTPException(status_code=500, detail="El grafo contiene un ciclo negativo. Use pesos positivos.")
    else:
        raise HTTPException(status_code=400, detail=f"Algoritmo '{algorithm_name}' no soportado.")

    # 3. Formatear y Ordenar Resultados
    results_list: List[CafeRouteItemSchema] = []
    
    from app.utils.data_loader import DataLoader # Re-importar si es necesario
    data_loader = DataLoader()
    CAFETERIA_DATA = data_loader.cafeterias_data
    
    for cafe_id, optimal_cost in distances.items():
        if cafe_id == user_node_id or optimal_cost == float('inf'):
            continue
            
        cafe_data = CAFETERIA_DATA.get(cafe_id)
        if not cafe_data:
            continue
            
        cafe_lat = cafe_data['latitude'] / 10**9 # Desnormalizar
        cafe_lon = cafe_data['longitude'] / 10**9

        # Calcular la distancia física real para mostrarla
        distance_km = haversine_distance(user_lat, user_lon, cafe_lat, cafe_lon)
        
        results_list.append(CafeRouteItemSchema(
            cafeteria_id=cafe_id,
            name=cafe_data['name'],
            latitude=cafe_lat,
            longitude=cafe_lon,
            optimal_cost=optimal_cost,
            distance_km=distance_km,
        ))

    # Ordenar por el Coste Óptimo (menor coste = mejor ruta)
    results_list.sort(key=lambda x: x.optimal_cost)
    
    # 4. Devolver la Respuesta
    return OptimalRouteResultSchema(
        ordered_cafeterias=results_list,
        selected_algorithm=algorithm_name,
        big_o_notation=big_o,
        processing_time_ms=int(processing_time * 1000),
    )
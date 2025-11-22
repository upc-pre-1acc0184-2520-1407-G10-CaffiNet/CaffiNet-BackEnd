# app/utils/graph_algorithms.py
import heapq
import time
from typing import Dict, List, Tuple

# La estructura del grafo será un diccionario: 
# {nodo_origen: {nodo_destino: peso}}

def dijkstra_algorithm(graph: Dict[int, Dict[int, float]], start_node: int) -> Tuple[Dict[int, float], float, str]:
    """Calcula la ruta más corta desde un nodo de inicio usando Dijkstra."""
    start_time = time.time()
    
    # Construir el conjunto completo de nodos: claves del grafo y todos los vecinos
    nodes = set(graph.keys())
    for neighbours in graph.values():
        nodes.update(neighbours.keys())

    # {nodo: distancia_minima} inicializado con infinito
    distances: Dict[int, float] = {node: float('inf') for node in nodes}
    # Asegurarse de inicializar la distancia del nodo inicial aunque no esté en las claves
    distances[start_node] = 0
    
    # Cola de prioridad: [(distancia, nodo)]
    priority_queue = [(0, start_node)]
    
    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)
        
        # Ignorar si ya encontramos una ruta más corta
        if current_distance > distances[current_node]:
            continue
            
        for neighbor, weight in graph.get(current_node, {}).items():
            distance = current_distance + weight
            
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(priority_queue, (distance, neighbor))
                
    processing_time = time.time() - start_time
    
    # La complejidad O(E + V log V) asume el uso de un heap binario.
    return distances, processing_time, "O(E + V log V)"


def floyd_warshall_algorithm(graph: Dict[int, Dict[int, float]], nodes: List[int]) -> Tuple[Dict[Tuple[int, int], float], float, str]:
    """Calcula las rutas más cortas entre todos los pares de nodos."""
    start_time = time.time()
    num_nodes = len(nodes)
    
    # Inicializa las distancias: { (origen, destino): distancia }
    dist: Dict[Tuple[int, int], float] = {}
    
    for i in nodes:
        for j in nodes:
            if i == j:
                dist[(i, j)] = 0.0
            elif j in graph.get(i, {}):
                dist[(i, j)] = graph[i][j]
            else:
                dist[(i, j)] = float('inf')
                
    # Algoritmo de Floyd-Warshall
    for k in nodes:
        for i in nodes:
            for j in nodes:
                current_dist = dist.get((i, j), float('inf'))
                through_k = dist.get((i, k), float('inf')) + dist.get((k, j), float('inf'))
                if through_k < current_dist:
                    dist[(i, j)] = through_k
                    
    processing_time = time.time() - start_time
    
    # La complejidad es O(V^3)
    return dist, processing_time, "O(V^3)"


def bellman_ford_algorithm(graph: Dict[int, Dict[int, float]], start_node: int, nodes: List[int]) -> Tuple[Dict[int, float], float, str]:
    """
    Calcula la ruta más corta desde un nodo de inicio, manejando pesos negativos.
    También detecta ciclos de peso negativo.
    """
    start_time = time.time()
    
    # {nodo: distancia_minima}
    distances: Dict[int, float] = {node: float('inf') for node in nodes}
    distances[start_node] = 0
    
    # Recolectar todas las aristas (edges)
    edges: List[Tuple[int, int, float]] = []
    for u, neighbors in graph.items():
        for v, weight in neighbors.items():
            edges.append((u, v, weight))
            
    num_nodes = len(nodes)
    
    # Paso 1: Relajación de aristas |V| - 1 veces
    for _ in range(num_nodes - 1):
        for u, v, weight in edges:
            if distances[u] != float('inf') and distances[u] + weight < distances[v]:
                distances[v] = distances[u] + weight
                
    # Paso 2: Detección de ciclos de peso negativo
    for u, v, weight in edges:
        if distances[u] != float('inf') and distances[u] + weight < distances[v]:
            # Este es un ciclo negativo. En un caso real, deberías lanzar un error.
            # Aquí, simplemente retornamos un indicador.
            return {}, 0.0, "Ciclo Negativo Detectado"
            
    processing_time = time.time() - start_time
    
    # La complejidad es O(V * E)
    return distances, processing_time, "O(V * E)"
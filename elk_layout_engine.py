"""
Motor de layout ortogonal usando algoritmo propio (inspirado en ELK)
Para diagramas P&ID con constraints de puertos y prioridades
"""
import math
from typing import Dict, List, Tuple, Optional
from elk_layout_pipeline import Graph, Node, Edge, Port, EdgePriority

class OrthogonalLayoutEngine:
    """Motor de layout ortogonal para diagramas P&ID"""
    
    def __init__(self, graph: Graph):
        self.graph = graph
        self.grid_size = 50  # Tamaño de grid para alineación
        self.min_distance = 100  # Distancia mínima entre nodos
        self.port_offset = 10  # Offset de puertos desde el borde
    
    def calculate_layout(self) -> Dict:
        """
        Calcula el layout ortogonal optimizado
        Retorna: dict con posiciones de nodos y waypoints de edges
        """
        print("🔧 Calculando layout ortogonal...")
        
        # 1. Posicionar nodos respetando constraints
        node_positions = self._calculate_node_positions()
        
        # 2. Calcular waypoints ortogonales para edges
        edge_waypoints = self._calculate_edge_waypoints(node_positions)
        
        print(f"   ✅ Layout calculado para {len(node_positions)} nodos")
        print(f"   ✅ Waypoints calculados para {len(edge_waypoints)} edges")
        
        return {
            'nodes': node_positions,
            'edges': edge_waypoints
        }
    
    def _calculate_node_positions(self) -> Dict[str, Dict]:
        """Calcula posiciones optimizadas de nodos"""
        positions = {}
        
        # Mantener posiciones fijas
        for node_id, node in self.graph.nodes.items():
            if node.fixed_position:
                positions[node_id] = {
                    'x': node.x,
                    'y': node.y,
                    'width': node.width,
                    'height': node.height
                }
        
        # Ordenar nodos por prioridad (mayor primero)
        sorted_nodes = sorted(
            self.graph.nodes.items(),
            key=lambda x: (x[1].priority, x[1].x),  # Por prioridad y luego por x
            reverse=True
        )
        
        # Posicionar nodos no fijos usando algoritmo de fuerza dirigida simplificado
        for node_id, node in sorted_nodes:
            if node.fixed_position:
                continue
            
            # Calcular posición basada en conexiones
            new_pos = self._calculate_node_position_from_connections(node, positions)
            positions[node_id] = {
                'x': new_pos[0],
                'y': new_pos[1],
                'width': node.width,
                'height': node.height
            }
        
        return positions
    
    def _calculate_node_position_from_connections(self, node: Node, existing_positions: Dict) -> Tuple[float, float]:
        """Calcula posición de nodo basada en sus conexiones, evitando solapamientos"""
        connected_positions = []
        
        # Encontrar nodos conectados
        for edge in self.graph.edges.values():
            if edge.source_id == node.id:
                target_pos = existing_positions.get(edge.target_id)
                if target_pos:
                    # Posicionar a la izquierda del target
                    x = target_pos['x'] - node.width - self.min_distance
                    y = target_pos['y']
                    connected_positions.append((x, y))
            elif edge.target_id == node.id:
                source_pos = existing_positions.get(edge.source_id)
                if source_pos:
                    # Posicionar a la derecha del source
                    x = source_pos['x'] + source_pos['width'] + self.min_distance
                    y = source_pos['y']
                    connected_positions.append((x, y))
        
        if connected_positions:
            # Promedio de posiciones sugeridas
            avg_x = sum(p[0] for p in connected_positions) / len(connected_positions)
            avg_y = sum(p[1] for p in connected_positions) / len(connected_positions)
            
            # Alinear a grid
            avg_x = round(avg_x / self.grid_size) * self.grid_size
            avg_y = round(avg_y / self.grid_size) * self.grid_size
            
            # Verificar y evitar solapamientos
            new_pos = self._avoid_overlaps(avg_x, avg_y, node, existing_positions)
            
            return new_pos
        
        # Mantener posición original si no hay conexiones, pero verificar solapamientos
        new_pos = self._avoid_overlaps(node.x, node.y, node, existing_positions)
        return new_pos
    
    def _avoid_overlaps(self, x: float, y: float, node: Node, existing_positions: Dict) -> Tuple[float, float]:
        """Ajusta posición para evitar solapamientos"""
        max_iterations = 10
        current_x, current_y = x, y
        
        for _ in range(max_iterations):
            overlaps = False
            
            # Verificar solapamiento con todos los nodos existentes
            for other_id, other_pos in existing_positions.items():
                if self._boxes_overlap(
                    current_x, current_y, node.width, node.height,
                    other_pos['x'], other_pos['y'], other_pos['width'], other_pos['height']
                ):
                    overlaps = True
                    # Mover hacia abajo y a la derecha
                    current_y += self.min_distance
                    current_x += self.grid_size
                    break
            
            if not overlaps:
                break
        
        # Asegurar posición no negativa
        current_x = max(0, current_x)
        current_y = max(0, current_y)
        
        # Alinear a grid
        current_x = round(current_x / self.grid_size) * self.grid_size
        current_y = round(current_y / self.grid_size) * self.grid_size
        
        return (current_x, current_y)
    
    def _boxes_overlap(self, x1: float, y1: float, w1: float, h1: float,
                      x2: float, y2: float, w2: float, h2: float) -> bool:
        """Verifica si dos cajas se solapan"""
        # Agregar margen mínimo
        margin = 10
        return not (x1 + w1 + margin < x2 or x2 + w2 + margin < x1 or 
                   y1 + h1 + margin < y2 or y2 + h2 + margin < y1)
    
    def _calculate_edge_waypoints(self, node_positions: Dict[str, Dict]) -> Dict[str, List[Tuple[float, float]]]:
        """Calcula waypoints ortogonales para todos los edges"""
        edge_waypoints = {}
        
        # Ordenar edges por prioridad
        sorted_edges = sorted(
            self.graph.edges.items(),
            key=lambda x: x[1].priority.value
        )
        
        for edge_id, edge in sorted_edges:
            source_pos = node_positions.get(edge.source_id)
            target_pos = node_positions.get(edge.target_id)
            
            if not source_pos or not target_pos:
                continue
            
            # Calcular waypoints ortogonales
            waypoints = self._calculate_orthogonal_route(
                edge, source_pos, target_pos
            )
            
            edge_waypoints[edge_id] = waypoints
        
        return edge_waypoints
    
    def _calculate_orthogonal_route(
        self,
        edge: Edge,
        source_pos: Dict,
        target_pos: Dict
    ) -> List[Tuple[float, float]]:
        """Calcula ruta ortogonal entre source y target"""
        waypoints = []
        
        # Obtener puertos
        source_port = edge.source_port
        target_port = edge.target_port
        
        # Calcular puntos de conexión
        if source_port and source_port in self.graph.ports:
            port = self.graph.ports[source_port]
            source_x = source_pos['x'] + port.x * source_pos['width']
            source_y = source_pos['y'] + port.y * source_pos['height']
        else:
            # Centro del nodo
            source_x = source_pos['x'] + source_pos['width'] / 2
            source_y = source_pos['y'] + source_pos['height'] / 2
        
        if target_port and target_port in self.graph.ports:
            port = self.graph.ports[target_port]
            target_x = target_pos['x'] + port.x * target_pos['width']
            target_y = target_pos['y'] + port.y * target_pos['height']
        else:
            # Centro del nodo
            target_x = target_pos['x'] + target_pos['width'] / 2
            target_y = target_pos['y'] + target_pos['height'] / 2
        
        # Algoritmo de ruteo ortogonal (L-shaped o U-shaped)
        dx = target_x - source_x
        dy = target_y - source_y
        
        # Determinar mejor ruta ortogonal
        if abs(dx) > abs(dy):
            # Ruta horizontal primero
            mid_x = (source_x + target_x) / 2
            waypoints.append((mid_x, source_y))
            waypoints.append((mid_x, target_y))
        else:
            # Ruta vertical primero
            mid_y = (source_y + target_y) / 2
            waypoints.append((source_x, mid_y))
            waypoints.append((target_x, mid_y))
        
        # Alinear waypoints a grid
        aligned_waypoints = []
        for wx, wy in waypoints:
            aligned_x = round(wx / self.grid_size) * self.grid_size
            aligned_y = round(wy / self.grid_size) * self.grid_size
            aligned_waypoints.append((aligned_x, aligned_y))
        
        return aligned_waypoints


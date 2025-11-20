"""
Motor de layout ortogonal mejorado para diagramas P&ID
Algoritmo optimizado con fuerza dirigida, detección de cruces y ruteo inteligente
"""
import math
from typing import Dict, List, Tuple, Optional, Set
from elk_layout_pipeline import Graph, Node, Edge, Port, EdgePriority

class ImprovedOrthogonalLayoutEngine:
    """Motor de layout ortogonal mejorado para diagramas P&ID"""
    
    def __init__(self, graph: Graph):
        self.graph = graph
        self.grid_size = 50
        self.min_distance = 100
        self.port_offset = 10
        self.iterations = 50  # Iteraciones para fuerza dirigida
        self.cooling_factor = 0.95  # Factor de enfriamiento para simulación
        
    def calculate_layout(self) -> Dict:
        """
        Calcula el layout ortogonal optimizado usando algoritmo mejorado
        Retorna: dict con posiciones de nodos y waypoints de edges
        """
        print("🔧 Calculando layout ortogonal mejorado...")
        
        # 1. Fase 1: Posicionamiento inicial respetando constraints
        node_positions = self._initial_positioning()
        
        # 2. Fase 2: Optimización iterativa con fuerza dirigida
        node_positions = self._force_directed_optimization(node_positions)
        
        # 3. Fase 3: Resolución final de solapamientos
        node_positions = self._final_overlap_resolution(node_positions)
        
        # 4. Calcular waypoints ortogonales optimizados
        edge_waypoints = self._calculate_optimized_waypoints(node_positions)
        
        print(f"   ✅ Layout calculado para {len(node_positions)} nodos")
        print(f"   ✅ Waypoints calculados para {len(edge_waypoints)} edges")
        
        return {
            'nodes': node_positions,
            'edges': edge_waypoints
        }
    
    def _initial_positioning(self) -> Dict[str, Dict]:
        """Posicionamiento inicial respetando constraints"""
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
        
        # Ordenar nodos por prioridad y dependencias
        sorted_nodes = self._topological_sort()
        
        # Posicionar nodos en orden topológico
        for node_id, node in sorted_nodes:
            if node.fixed_position:
                continue
            
            # Calcular posición basada en conexiones y flujo
            new_pos = self._calculate_initial_position(node, positions)
            positions[node_id] = {
                'x': new_pos[0],
                'y': new_pos[1],
                'width': node.width,
                'height': node.height
            }
        
        return positions
    
    def _topological_sort(self) -> List[Tuple[str, Node]]:
        """Ordena nodos topológicamente basado en el flujo de edges"""
        # Construir grafo de dependencias
        in_degree = {node_id: 0 for node_id in self.graph.nodes.keys()}
        dependencies = {node_id: [] for node_id in self.graph.nodes.keys()}
        
        for edge in self.graph.edges.values():
            if edge.edge_type == 'gas' and edge.priority == EdgePriority.MAIN_PIPE:
                # Para pipes principales, el target depende del source
                if edge.source_id in in_degree and edge.target_id in in_degree:
                    in_degree[edge.target_id] += 1
                    dependencies[edge.source_id].append(edge.target_id)
        
        # Ordenar por prioridad primero, luego topológicamente
        sorted_nodes = []
        remaining = set(self.graph.nodes.items())
        
        # Primero agregar nodos fijos
        for node_id, node in list(remaining):
            if node.fixed_position:
                sorted_nodes.append((node_id, node))
                remaining.remove((node_id, node))
        
        # Luego ordenar por prioridad
        remaining_sorted = sorted(
            remaining,
            key=lambda x: (x[1].priority, in_degree.get(x[0], 0)),
            reverse=True
        )
        
        sorted_nodes.extend(remaining_sorted)
        
        return sorted_nodes
    
    def _calculate_initial_position(self, node: Node, existing_positions: Dict) -> Tuple[float, float]:
        """Calcula posición inicial basada en conexiones y flujo"""
        # Encontrar nodos conectados y sus posiciones
        connected_sources = []
        connected_targets = []
        
        for edge in self.graph.edges.values():
            if edge.source_id == node.id:
                target_pos = existing_positions.get(edge.target_id)
                if target_pos:
                    connected_targets.append((target_pos, edge))
            elif edge.target_id == node.id:
                source_pos = existing_positions.get(edge.source_id)
                if source_pos:
                    connected_sources.append((source_pos, edge))
        
        # Calcular posición basada en el tipo de conexiones
        if connected_sources:
            # Si tiene sources, posicionar después de ellos
            avg_x = sum(pos['x'] + pos['width'] for pos, _ in connected_sources) / len(connected_sources)
            avg_y = sum(pos['y'] for pos, _ in connected_sources) / len(connected_sources)
            
            # Posicionar a la derecha del último source
            x = avg_x + self.min_distance
            y = avg_y
        elif connected_targets:
            # Si solo tiene targets, posicionar antes de ellos
            avg_x = sum(pos['x'] for pos, _ in connected_targets) / len(connected_targets)
            avg_y = sum(pos['y'] for pos, _ in connected_targets) / len(connected_targets)
            
            # Posicionar a la izquierda del primer target
            x = avg_x - node.width - self.min_distance
            y = avg_y
        else:
            # Mantener posición original
            x, y = node.x, node.y
        
        # Asegurar no negativa y alineada a grid
        x = max(0, round(x / self.grid_size) * self.grid_size)
        y = max(0, round(y / self.grid_size) * self.grid_size)
        
        # Evitar solapamientos iniciales
        return self._avoid_overlaps(x, y, node, existing_positions)
    
    def _force_directed_optimization(self, positions: Dict[str, Dict]) -> Dict[str, Dict]:
        """Optimización iterativa usando fuerza dirigida"""
        print("   🔄 Optimizando con fuerza dirigida...")
        
        temperature = 100.0  # Temperatura inicial
        
        for iteration in range(self.iterations):
            new_positions = positions.copy()
            total_displacement = 0
            
            for node_id, node in self.graph.nodes.items():
                if node.fixed_position:
                    continue
                
                current_pos = positions[node_id]
                fx, fy = 0.0, 0.0  # Fuerzas
                
                # Fuerza de repulsión con otros nodos
                for other_id, other_node in self.graph.nodes.items():
                    if other_id == node_id or other_node.fixed_position:
                        continue
                    
                    other_pos = positions[other_id]
                    dx = current_pos['x'] - other_pos['x']
                    dy = current_pos['y'] - other_pos['y']
                    distance = math.sqrt(dx*dx + dy*dy + 1)  # +1 para evitar división por cero
                    
                    if distance < self.min_distance * 2:
                        # Fuerza de repulsión
                        force = (self.min_distance * 2 - distance) / distance
                        fx += dx * force * 0.1
                        fy += dy * force * 0.1
                
                # Fuerza de atracción con nodos conectados
                for edge in self.graph.edges.values():
                    if edge.source_id == node_id:
                        target_pos = positions.get(edge.target_id)
                        if target_pos:
                            dx = target_pos['x'] - current_pos['x']
                            dy = target_pos['y'] - current_pos['y']
                            distance = math.sqrt(dx*dx + dy*dy + 1)
                            
                            # Fuerza de atracción (más débil)
                            force = distance / (self.min_distance * 3)
                            fx += dx * force * 0.05
                            fy += dy * force * 0.05
                    elif edge.target_id == node_id:
                        source_pos = positions.get(edge.source_id)
                        if source_pos:
                            dx = source_pos['x'] - current_pos['x']
                            dy = source_pos['y'] - current_pos['y']
                            distance = math.sqrt(dx*dx + dy*dy + 1)
                            
                            force = distance / (self.min_distance * 3)
                            fx += dx * force * 0.05
                            fy += dy * force * 0.05
                
                # Aplicar fuerzas con temperatura (simulated annealing)
                new_x = current_pos['x'] + fx * temperature
                new_y = current_pos['y'] + fy * temperature
                
                # Alinear a grid
                new_x = round(new_x / self.grid_size) * self.grid_size
                new_y = round(new_y / self.grid_size) * self.grid_size
                
                # Asegurar no negativa
                new_x = max(0, new_x)
                new_y = max(0, new_y)
                
                # Actualizar posición
                new_positions[node_id] = {
                    'x': new_x,
                    'y': new_y,
                    'width': current_pos['width'],
                    'height': current_pos['height']
                }
                
                total_displacement += abs(fx) + abs(fy)
            
            positions = new_positions
            temperature *= self.cooling_factor  # Enfriar gradualmente
            
            if total_displacement < 1.0:  # Convergencia
                break
        
        return positions
    
    def _final_overlap_resolution(self, positions: Dict[str, Dict]) -> Dict[str, Dict]:
        """Resolución final de solapamientos"""
        print("   🔧 Resolviendo solapamientos finales...")
        
        max_iterations = 20
        for iteration in range(max_iterations):
            overlaps_found = False
            
            for node_id, node in self.graph.nodes.items():
                if node.fixed_position:
                    continue
                
                current_pos = positions[node_id]
                
                # Verificar solapamientos
                for other_id, other_pos in positions.items():
                    if other_id == node_id:
                        continue
                    
                    if self._boxes_overlap(
                        current_pos['x'], current_pos['y'],
                        current_pos['width'], current_pos['height'],
                        other_pos['x'], other_pos['y'],
                        other_pos['width'], other_pos['height']
                    ):
                        overlaps_found = True
                        
                        # Calcular dirección de separación
                        dx = current_pos['x'] - other_pos['x']
                        dy = current_pos['y'] - other_pos['y']
                        
                        # Mover en dirección opuesta
                        if abs(dx) > abs(dy):
                            new_x = other_pos['x'] + other_pos['width'] + self.min_distance
                            new_y = current_pos['y']
                        else:
                            new_x = current_pos['x']
                            new_y = other_pos['y'] + other_pos['height'] + self.min_distance
                        
                        new_x = max(0, round(new_x / self.grid_size) * self.grid_size)
                        new_y = max(0, round(new_y / self.grid_size) * self.grid_size)
                        
                        positions[node_id] = {
                            'x': new_x,
                            'y': new_y,
                            'width': current_pos['width'],
                            'height': current_pos['height']
                        }
                        break
            
            if not overlaps_found:
                break
        
        return positions
    
    def _calculate_optimized_waypoints(self, node_positions: Dict[str, Dict]) -> Dict[str, List[Tuple[float, float]]]:
        """Calcula waypoints ortogonales optimizados evitando cruces"""
        edge_waypoints = {}
        
        # Ordenar edges por prioridad
        sorted_edges = sorted(
            self.graph.edges.items(),
            key=lambda x: (x[1].priority.value, x[0])
        )
        
        # Rastrear rutas existentes para evitar cruces
        existing_routes = []
        
        for edge_id, edge in sorted_edges:
            source_pos = node_positions.get(edge.source_id)
            target_pos = node_positions.get(edge.target_id)
            
            if not source_pos or not target_pos:
                continue
            
            # Calcular ruta ortogonal optimizada
            waypoints = self._calculate_smart_orthogonal_route(
                edge, source_pos, target_pos, existing_routes
            )
            
            edge_waypoints[edge_id] = waypoints
            existing_routes.append((edge_id, waypoints))
        
        return edge_waypoints
    
    def _calculate_smart_orthogonal_route(
        self,
        edge: Edge,
        source_pos: Dict,
        target_pos: Dict,
        existing_routes: List[Tuple[str, List[Tuple[float, float]]]]
    ) -> List[Tuple[float, float]]:
        """Calcula ruta ortogonal inteligente evitando cruces"""
        # Obtener puntos de conexión
        source_x, source_y = self._get_connection_point(edge, edge.source_id, source_pos, 'source')
        target_x, target_y = self._get_connection_point(edge, edge.target_id, target_pos, 'target')
        
        dx = target_x - source_x
        dy = target_y - source_y
        
        # Probar diferentes rutas y elegir la mejor
        routes = []
        
        # Ruta 1: Horizontal primero (L-shaped)
        if abs(dx) > 0:
            mid_x = (source_x + target_x) / 2
            route1 = [
                (round(mid_x / self.grid_size) * self.grid_size, source_y),
                (round(mid_x / self.grid_size) * self.grid_size, target_y)
            ]
            routes.append(route1)
        
        # Ruta 2: Vertical primero (L-shaped)
        if abs(dy) > 0:
            mid_y = (source_y + target_y) / 2
            route2 = [
                (source_x, round(mid_y / self.grid_size) * self.grid_size),
                (target_x, round(mid_y / self.grid_size) * self.grid_size)
            ]
            routes.append(route2)
        
        # Ruta 3: U-shaped (si es necesario)
        if abs(dx) > self.min_distance and abs(dy) > self.min_distance:
            route3 = [
                (source_x, source_y + self.min_distance),
                (source_x, (source_y + target_y) / 2),
                (target_x, (source_y + target_y) / 2),
                (target_x, target_y - self.min_distance)
            ]
            routes.append(route3)
        
        # Elegir ruta con menos cruces
        best_route = routes[0] if routes else []
        min_crossings = self._count_route_crossings(routes[0], existing_routes) if routes else float('inf')
        
        for route in routes[1:]:
            crossings = self._count_route_crossings(route, existing_routes)
            if crossings < min_crossings:
                min_crossings = crossings
                best_route = route
        
        return best_route
    
    def _get_connection_point(
        self,
        edge: Edge,
        node_id: str,
        node_pos: Dict,
        role: str
    ) -> Tuple[float, float]:
        """Obtiene punto de conexión considerando puertos"""
        if role == 'source' and edge.source_port:
            port = self.graph.ports.get(edge.source_port)
            if port:
                return (
                    node_pos['x'] + port.x * node_pos['width'],
                    node_pos['y'] + port.y * node_pos['height']
                )
        elif role == 'target' and edge.target_port:
            port = self.graph.ports.get(edge.target_port)
            if port:
                return (
                    node_pos['x'] + port.x * node_pos['width'],
                    node_pos['y'] + port.y * node_pos['height']
                )
        
        # Por defecto, usar centro del lado apropiado
        if role == 'source':
            return (node_pos['x'] + node_pos['width'], node_pos['y'] + node_pos['height'] / 2)
        else:
            return (node_pos['x'], node_pos['y'] + node_pos['height'] / 2)
    
    def _count_route_crossings(
        self,
        route: List[Tuple[float, float]],
        existing_routes: List[Tuple[str, List[Tuple[float, float]]]]
    ) -> int:
        """Cuenta cruces con rutas existentes"""
        crossings = 0
        
        for i in range(len(route) - 1):
            seg_start = route[i]
            seg_end = route[i + 1]
            
            for other_id, other_route in existing_routes:
                for j in range(len(other_route) - 1):
                    other_start = other_route[j]
                    other_end = other_route[j + 1]
                    
                    if self._segments_intersect(seg_start, seg_end, other_start, other_end):
                        crossings += 1
        
        return crossings
    
    def _segments_intersect(
        self,
        p1: Tuple[float, float],
        p2: Tuple[float, float],
        p3: Tuple[float, float],
        p4: Tuple[float, float]
    ) -> bool:
        """Verifica si dos segmentos de línea se intersectan"""
        def ccw(A, B, C):
            return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])
        
        return ccw(p1, p3, p4) != ccw(p2, p3, p4) and ccw(p1, p2, p3) != ccw(p1, p2, p4)
    
    def _avoid_overlaps(self, x: float, y: float, node: Node, existing_positions: Dict) -> Tuple[float, float]:
        """Ajusta posición para evitar solapamientos"""
        max_iterations = 10
        current_x, current_y = x, y
        
        for _ in range(max_iterations):
            overlaps = False
            
            for other_id, other_pos in existing_positions.items():
                if self._boxes_overlap(
                    current_x, current_y, node.width, node.height,
                    other_pos['x'], other_pos['y'], other_pos['width'], other_pos['height']
                ):
                    overlaps = True
                    current_y += self.min_distance
                    current_x += self.grid_size
                    break
            
            if not overlaps:
                break
        
        current_x = max(0, round(current_x / self.grid_size) * self.grid_size)
        current_y = max(0, round(current_y / self.grid_size) * self.grid_size)
        
        return (current_x, current_y)
    
    def _boxes_overlap(
        self,
        x1: float, y1: float, w1: float, h1: float,
        x2: float, y2: float, w2: float, h2: float
    ) -> bool:
        """Verifica si dos cajas se solapan"""
        margin = 10
        return not (x1 + w1 + margin < x2 or x2 + w2 + margin < x1 or
                   y1 + h1 + margin < y2 or y2 + h2 + margin < y1)


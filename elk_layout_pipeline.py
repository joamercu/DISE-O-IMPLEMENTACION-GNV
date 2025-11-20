"""
Pipeline híbrido automatizado para layout ortogonal de diagramas P&ID
Opción A - Solución robusta con ELK (Eclipse Layout Kernel)

Estructura:
1. Extraer grafo (nodos, puertos, edges) del .drawio XML
2. Definir constraints: puertos obligatorios, prioridades, bounding boxes
3. Ejecutar ELK para calcular posiciones y waypoints ortogonales
4. Aplicar resultados al XML
5. Validación automática
"""
import xml.etree.ElementTree as ET
import json
import math
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum

class EdgePriority(Enum):
    """Prioridad de edges para routing"""
    MAIN_PIPE = 1      # Tubería principal de gas
    CONTROL_SIGNAL = 2 # Señales de control
    DATA_SIGNAL = 3    # Señales de datos
    VENT = 4           # Venteos

@dataclass
class Port:
    """Representa un puerto de conexión en un nodo"""
    id: str
    node_id: str
    x: float  # Posición relativa (0.0-1.0)
    y: float  # Posición relativa (0.0-1.0)
    side: str = "auto"  # "north", "south", "east", "west", "auto"
    required: bool = True

@dataclass
class Node:
    """Representa un nodo (componente) en el diagrama"""
    id: str
    label: str
    x: float
    y: float
    width: float
    height: float
    node_type: str  # "tank", "valve", "regulator", "sensor", "ecu", etc.
    ports: List[Port] = field(default_factory=list)
    fixed_position: bool = False  # Si True, no se mueve en el layout
    priority: int = 0  # Prioridad para posicionamiento (mayor = más importante)

@dataclass
class Edge:
    """Representa una conexión (edge) en el diagrama"""
    id: str
    source_id: str
    target_id: str
    label: str
    edge_type: str  # "gas", "control", "data", "vent"
    priority: EdgePriority = EdgePriority.MAIN_PIPE
    waypoints: List[Tuple[float, float]] = field(default_factory=list)
    source_port: Optional[str] = None
    target_port: Optional[str] = None

@dataclass
class Graph:
    """Grafo completo del diagrama"""
    nodes: Dict[str, Node] = field(default_factory=dict)
    edges: Dict[str, Edge] = field(default_factory=dict)
    ports: Dict[str, Port] = field(default_factory=dict)

class DrawIOGraphExtractor:
    """Extrae el grafo (nodos, puertos, edges) del XML draw.io"""
    
    # Mapeo de estilos a tipos de nodo
    STYLE_TO_TYPE = {
        'cylinder3': 'tank',
        'valve': 'valve',
        'hexagon': 'regulator',
        'parallelogram': 'manifold',
        'ellipse': 'sensor',
        'rect': 'ecu',
        'cylinder': 'filter',
    }
    
    # Mapeo de labels a tipos de edge
    LABEL_TO_EDGE_TYPE = {
        'Gas CNG': 'gas',
        'Gas Regulado': 'gas',
        'Gas a': 'gas',
        'Control': 'control',
        'Datos': 'data',
        'Detección': 'data',
        'Diagnóstico': 'data',
        'Venteo': 'vent',
    }
    
    def __init__(self, xml_file: str):
        self.xml_file = xml_file
        self.tree = ET.parse(xml_file)
        self.root = self.tree.getroot()
        self.graph = Graph()
    
    def extract(self) -> Graph:
        """Extrae el grafo completo del XML"""
        print("📊 Extrayendo grafo del diagrama...")
        
        # Extraer nodos
        self._extract_nodes()
        
        # Extraer edges
        self._extract_edges()
        
        # Inferir puertos basados en conexiones
        self._infer_ports()
        
        print(f"   ✅ Nodos extraídos: {len(self.graph.nodes)}")
        print(f"   ✅ Edges extraídos: {len(self.graph.edges)}")
        print(f"   ✅ Puertos inferidos: {len(self.graph.ports)}")
        
        return self.graph
    
    def _extract_nodes(self):
        """Extrae todos los nodos (vértices) del XML"""
        for cell in self.root.findall('.//mxCell[@vertex="1"]'):
            cell_id = cell.get('id', '')
            if not cell_id or cell_id in ['0', '1']:
                continue
            
            value = cell.get('value', '')
            style = cell.get('style', '')
            geo = cell.find('mxGeometry')
            
            if geo is None:
                continue
            
            x = float(geo.get('x', 0))
            y = float(geo.get('y', 0))
            w = float(geo.get('width', 80))
            h = float(geo.get('height', 60))
            
            # Determinar tipo de nodo
            node_type = self._determine_node_type(style, value)
            
            # Determinar si posición es fija (componentes críticos)
            fixed = self._is_fixed_position(cell_id, value)
            
            # Determinar prioridad
            priority = self._determine_priority(cell_id, value, node_type)
            
            node = Node(
                id=cell_id,
                label=value.replace('&#xa;', '\n'),
                x=x,
                y=y,
                width=w,
                height=h,
                node_type=node_type,
                fixed_position=fixed,
                priority=priority
            )
            
            self.graph.nodes[cell_id] = node
    
    def _extract_edges(self):
        """Extrae todos los edges (conexiones) del XML"""
        for cell in self.root.findall('.//mxCell[@edge="1"]'):
            edge_id = cell.get('id', '')
            source_id = cell.get('source', '')
            target_id = cell.get('target', '')
            
            if not source_id or not target_id:
                continue
            
            value = cell.get('value', '')
            style = cell.get('style', '')
            
            # Determinar tipo de edge
            edge_type = self._determine_edge_type(value)
            
            # Determinar prioridad
            priority = self._determine_edge_priority(value, edge_type)
            
            # Extraer waypoints existentes
            waypoints = self._extract_waypoints(cell)
            
            edge = Edge(
                id=edge_id,
                source_id=source_id,
                target_id=target_id,
                label=value.replace('&#xa;', '\n'),
                edge_type=edge_type,
                priority=priority,
                waypoints=waypoints
            )
            
            self.graph.edges[edge_id] = edge
    
    def _infer_ports(self):
        """Infiere puertos basados en las conexiones existentes"""
        for edge_id, edge in self.graph.edges.items():
            source_node = self.graph.nodes.get(edge.source_id)
            target_node = self.graph.nodes.get(edge.target_id)
            
            if not source_node or not target_node:
                continue
            
            # Calcular posición relativa de puertos basado en geometría
            source_port = self._calculate_port_position(source_node, target_node, 'source')
            target_port = self._calculate_port_position(target_node, source_node, 'target')
            
            if source_port:
                port_id = f"{edge.source_id}_port_{len(source_node.ports)}"
                port = Port(
                    id=port_id,
                    node_id=edge.source_id,
                    x=source_port[0],
                    y=source_port[1],
                    side=source_port[2]
                )
                self.graph.ports[port_id] = port
                source_node.ports.append(port)
                edge.source_port = port_id
            
            if target_port:
                port_id = f"{edge.target_id}_port_{len(target_node.ports)}"
                port = Port(
                    id=port_id,
                    node_id=edge.target_id,
                    x=target_port[0],
                    y=target_port[1],
                    side=target_port[2]
                )
                self.graph.ports[port_id] = port
                target_node.ports.append(port)
                edge.target_port = port_id
    
    def _calculate_port_position(self, node: Node, other_node: Node, role: str) -> Optional[Tuple[float, float, str]]:
        """Calcula la posición del puerto basado en la posición relativa de los nodos"""
        # Centro del nodo
        node_center_x = node.x + node.width / 2
        node_center_y = node.y + node.height / 2
        
        # Centro del otro nodo
        other_center_x = other_node.x + other_node.width / 2
        other_center_y = other_node.y + other_node.height / 2
        
        # Vector de dirección
        dx = other_center_x - node_center_x
        dy = other_center_y - node_center_y
        
        # Determinar lado del puerto
        if abs(dx) > abs(dy):
            # Horizontal
            if dx > 0:
                side = 'east'
                x, y = 1.0, 0.5
            else:
                side = 'west'
                x, y = 0.0, 0.5
        else:
            # Vertical
            if dy > 0:
                side = 'south'
                x, y = 0.5, 1.0
            else:
                side = 'north'
                x, y = 0.5, 0.0
        
        return (x, y, side)
    
    def _determine_node_type(self, style: str, value: str) -> str:
        """Determina el tipo de nodo basado en el estilo"""
        for shape_key, node_type in self.STYLE_TO_TYPE.items():
            if shape_key in style:
                return node_type
        
        # Fallback basado en el valor
        value_lower = value.lower()
        if 'tanque' in value_lower:
            return 'tank'
        elif 'válvula' in value_lower or 'valve' in value_lower:
            return 'valve'
        elif 'regulador' in value_lower:
            return 'regulator'
        elif 'filtro' in value_lower:
            return 'filter'
        elif 'sensor' in value_lower or 'pt-' in value_lower.lower() or 'tt-' in value_lower.lower():
            return 'sensor'
        elif 'ecu' in value_lower or 'control' in value_lower:
            return 'ecu'
        elif 'motor' in value_lower:
            return 'motor'
        elif 'manifold' in value_lower:
            return 'manifold'
        
        return 'unknown'
    
    def _determine_edge_type(self, value: str) -> str:
        """Determina el tipo de edge basado en el label"""
        value_lower = value.lower()
        for label_key, edge_type in self.LABEL_TO_EDGE_TYPE.items():
            if label_key.lower() in value_lower:
                return edge_type
        
        # Verificar estilo para señales
        if 'dashed=1' in value or 'dashed=true' in value:
            if 'control' in value_lower:
                return 'control'
            return 'data'
        
        return 'gas'
    
    def _determine_edge_priority(self, value: str, edge_type: str) -> EdgePriority:
        """Determina la prioridad del edge"""
        if edge_type == 'gas':
            return EdgePriority.MAIN_PIPE
        elif edge_type == 'control':
            return EdgePriority.CONTROL_SIGNAL
        elif edge_type == 'data':
            return EdgePriority.DATA_SIGNAL
        elif edge_type == 'vent':
            return EdgePriority.VENT
        return EdgePriority.MAIN_PIPE
    
    def _determine_priority(self, node_id: str, value: str, node_type: str) -> int:
        """Determina la prioridad del nodo para posicionamiento"""
        # Componentes críticos del flujo principal tienen mayor prioridad
        if node_type in ['tank', 'manifold', 'regulator']:
            return 10
        elif node_type in ['valve', 'filter']:
            return 8
        elif node_type == 'ecu':
            return 6
        elif node_type == 'sensor':
            return 4
        return 2
    
    def _is_fixed_position(self, node_id: str, value: str) -> bool:
        """Determina si el nodo debe mantener su posición"""
        # Componentes críticos mantienen posición aproximada
        value_lower = value.lower()
        if 'tanque' in value_lower or 'tank' in value_lower:
            return True  # Tanques en posición fija
        if 'motor' in value_lower:
            return True  # Motor en posición fija
        return False
    
    def _extract_waypoints(self, cell) -> List[Tuple[float, float]]:
        """Extrae waypoints existentes de un edge"""
        waypoints = []
        geo = cell.find('mxGeometry')
        if geo is not None:
            array = geo.find('Array')
            if array is not None:
                for point in array.findall('mxPoint'):
                    x = float(point.get('x', 0))
                    y = float(point.get('y', 0))
                    waypoints.append((x, y))
        return waypoints


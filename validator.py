"""
Validador automático del diagrama usando XPaths
Verifica integridad, conexiones y constraints
"""
import xml.etree.ElementTree as ET
from typing import List, Dict, Tuple

class DiagramValidator:
    """Validador automático del diagrama P&ID"""
    
    def __init__(self, xml_file: str):
        self.xml_file = xml_file
        self.tree = ET.parse(xml_file)
        self.root = self.tree.getroot()
        self.errors = []
        self.warnings = []
    
    def validate_all(self) -> Tuple[bool, List[str], List[str]]:
        """
        Ejecuta todas las validaciones
        Retorna: (is_valid, errors, warnings)
        """
        print("🔍 Validando diagrama...")
        
        # Validaciones
        self._validate_xml_structure()
        self._validate_node_geometries()
        self._validate_edge_connections()
        self._validate_waypoints()
        self._validate_overlaps()
        
        is_valid = len(self.errors) == 0
        
        print(f"   {'✅' if is_valid else '❌'} Validación completada")
        if self.errors:
            print(f"   ⚠️ {len(self.errors)} errores encontrados")
        if self.warnings:
            print(f"   ⚠️ {len(self.warnings)} advertencias encontradas")
        
        return is_valid, self.errors, self.warnings
    
    def _validate_xml_structure(self):
        """Valida estructura básica del XML"""
        # Verificar elementos principales
        if self.root.find('.//diagram') is None:
            self.errors.append("Falta elemento <diagram>")
        
        if self.root.find('.//mxGraphModel') is None:
            self.errors.append("Falta elemento <mxGraphModel>")
        
        if self.root.find('.//root') is None:
            self.errors.append("Falta elemento <root>")
    
    def _validate_node_geometries(self):
        """Valida geometrías de nodos"""
        for cell in self.root.findall('.//mxCell[@vertex="1"]'):
            cell_id = cell.get('id', '')
            if cell_id in ['0', '1']:
                continue
            
            geo = cell.find('mxGeometry')
            if geo is None:
                self.errors.append(f"Nodo {cell_id} sin geometría")
                continue
            
            x = float(geo.get('x', 0))
            y = float(geo.get('y', 0))
            w = float(geo.get('width', 0))
            h = float(geo.get('height', 0))
            
            if w <= 0 or h <= 0:
                self.errors.append(f"Nodo {cell_id} tiene dimensiones inválidas: {w}x{h}")
            
            if x < 0 or y < 0:
                self.warnings.append(f"Nodo {cell_id} tiene posición negativa: ({x}, {y})")
    
    def _validate_edge_connections(self):
        """Valida que todos los edges tengan source y target válidos"""
        all_node_ids = set()
        for cell in self.root.findall('.//mxCell[@vertex="1"]'):
            all_node_ids.add(cell.get('id', ''))
        
        for cell in self.root.findall('.//mxCell[@edge="1"]'):
            edge_id = cell.get('id', '')
            source_id = cell.get('source', '')
            target_id = cell.get('target', '')
            
            if not source_id:
                self.errors.append(f"Edge {edge_id} sin source")
            
            if not target_id:
                self.errors.append(f"Edge {edge_id} sin target")
            
            if source_id and source_id not in all_node_ids:
                self.errors.append(f"Edge {edge_id} tiene source inválido: {source_id}")
            
            if target_id and target_id not in all_node_ids:
                self.errors.append(f"Edge {edge_id} tiene target inválido: {target_id}")
    
    def _validate_waypoints(self):
        """Valida waypoints de edges"""
        for cell in self.root.findall('.//mxCell[@edge="1"]'):
            edge_id = cell.get('id', '')
            geo = cell.find('mxGeometry')
            
            if geo is None:
                continue
            
            array = geo.find('Array')
            if array is not None:
                points = array.findall('mxPoint')
                for i, point in enumerate(points):
                    x = point.get('x', '')
                    y = point.get('y', '')
                    
                    if not x or not y:
                        self.warnings.append(f"Edge {edge_id} tiene waypoint {i} sin coordenadas")
                    else:
                        try:
                            float(x)
                            float(y)
                        except ValueError:
                            self.errors.append(f"Edge {edge_id} tiene waypoint {i} con coordenadas inválidas")
    
    def _validate_overlaps(self):
        """Valida solapamientos de nodos"""
        node_boxes = []
        
        for cell in self.root.findall('.//mxCell[@vertex="1"]'):
            cell_id = cell.get('id', '')
            if cell_id in ['0', '1']:
                continue
            
            geo = cell.find('mxGeometry')
            if geo is None:
                continue
            
            x = float(geo.get('x', 0))
            y = float(geo.get('y', 0))
            w = float(geo.get('width', 0))
            h = float(geo.get('height', 0))
            
            node_boxes.append((cell_id, x, y, w, h))
        
        # Verificar solapamientos
        for i, (id1, x1, y1, w1, h1) in enumerate(node_boxes):
            for j, (id2, x2, y2, w2, h2) in enumerate(node_boxes[i+1:], i+1):
                if self._boxes_overlap(x1, y1, w1, h1, x2, y2, w2, h2):
                    self.warnings.append(f"Nodos {id1} y {id2} se solapan")
    
    def _boxes_overlap(self, x1, y1, w1, h1, x2, y2, w2, h2) -> bool:
        """Verifica si dos cajas se solapan"""
        return not (x1 + w1 < x2 or x2 + w2 < x1 or y1 + h1 < y2 or y2 + h2 < y1)
    
    def print_report(self):
        """Imprime reporte de validación"""
        print("\n" + "="*60)
        print("REPORTE DE VALIDACIÓN")
        print("="*60)
        
        if not self.errors and not self.warnings:
            print("✅ Diagrama válido - Sin errores ni advertencias")
            return
        
        if self.errors:
            print(f"\n❌ ERRORES ({len(self.errors)}):")
            for i, error in enumerate(self.errors, 1):
                print(f"   {i}. {error}")
        
        if self.warnings:
            print(f"\n⚠️ ADVERTENCIAS ({len(self.warnings)}):")
            for i, warning in enumerate(self.warnings, 1):
                print(f"   {i}. {warning}")
        
        print("="*60)


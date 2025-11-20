"""
Aplicador de resultados del layout al XML draw.io
Actualiza geometrías de nodos y waypoints de edges
"""
import xml.etree.ElementTree as ET
from typing import Dict, List, Tuple

class XMLApplicator:
    """Aplica resultados del layout al XML draw.io"""
    
    def __init__(self, xml_file: str):
        self.xml_file = xml_file
        self.tree = ET.parse(xml_file)
        self.root = self.tree.getroot()
    
    def apply_layout(self, layout_results: Dict):
        """
        Aplica los resultados del layout al XML
        
        Args:
            layout_results: dict con 'nodes' y 'edges' del layout engine
        """
        print("📝 Aplicando layout al XML...")
        
        # Aplicar posiciones de nodos
        nodes_updated = self._apply_node_positions(layout_results.get('nodes', {}))
        
        # Aplicar waypoints de edges
        edges_updated = self._apply_edge_waypoints(layout_results.get('edges', {}))
        
        print(f"   ✅ {nodes_updated} nodos actualizados")
        print(f"   ✅ {edges_updated} edges actualizados")
    
    def _apply_node_positions(self, node_positions: Dict) -> int:
        """Aplica nuevas posiciones a los nodos"""
        updated = 0
        
        for node_id, position in node_positions.items():
            cell = self.root.find(f'.//mxCell[@id="{node_id}"]')
            if cell is None:
                continue
            
            geo = cell.find('mxGeometry')
            if geo is None:
                continue
            
            # Actualizar posición
            geo.set('x', str(position['x']))
            geo.set('y', str(position['y']))
            
            # Actualizar tamaño si es necesario
            if 'width' in position:
                geo.set('width', str(position['width']))
            if 'height' in position:
                geo.set('height', str(position['height']))
            
            updated += 1
        
        return updated
    
    def _apply_edge_waypoints(self, edge_waypoints: Dict) -> int:
        """Aplica waypoints a los edges"""
        updated = 0
        
        for edge_id, waypoints in edge_waypoints.items():
            cell = self.root.find(f'.//mxCell[@id="{edge_id}"]')
            if cell is None:
                continue
            
            geo = cell.find('mxGeometry')
            if geo is None:
                geo = ET.SubElement(cell, 'mxGeometry')
                geo.set('width', '50')
                geo.set('height', '50')
                geo.set('relative', '1')
                geo.set('as', 'geometry')
            
            # Buscar o crear Array de waypoints
            array = geo.find('Array')
            if array is None:
                array = ET.SubElement(geo, 'Array')
                array.set('as', 'points')
            else:
                # Limpiar waypoints existentes
                for point in array.findall('mxPoint'):
                    array.remove(point)
            
            # Agregar nuevos waypoints
            for wx, wy in waypoints:
                point = ET.SubElement(array, 'mxPoint')
                point.set('x', str(wx))
                point.set('y', str(wy))
            
            updated += 1
        
        return updated
    
    def save(self, output_file: str = None):
        """Guarda el XML actualizado"""
        if output_file is None:
            output_file = self.xml_file
        
        self.tree.write(output_file, encoding='utf-8', xml_declaration=True)
        print(f"💾 XML guardado en: {output_file}")


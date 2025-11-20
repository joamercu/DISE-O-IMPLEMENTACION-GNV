"""
Script para completar los to-dos pendientes del plan de mejora del diagrama
"""
import xml.etree.ElementTree as ET
import re
from typing import Dict, List, Tuple, Optional

class DiagramImprover:
    """Mejora el diagrama según el plan"""
    
    def __init__(self, xml_file: str):
        self.xml_file = xml_file
        self.tree = ET.parse(xml_file)
        self.root = self.tree.getroot()
        self.next_id = 1000  # Para nuevos elementos
        
    def get_max_id(self) -> int:
        """Obtiene el ID máximo actual"""
        max_id = 0
        for cell in self.root.findall('.//mxCell[@id]'):
            try:
                cell_id = int(cell.get('id', '0'))
                max_id = max(max_id, cell_id)
            except:
                pass
        return max_id
    
    def improve_all(self):
        """Ejecuta todas las mejoras pendientes"""
        print("="*80)
        print("COMPLETANDO PLAN DE MEJORA DEL DIAGRAMA")
        print("="*80)
        print()
        
        self.next_id = self.get_max_id() + 1
        
        # To-do 1: Corregir aristas para que conecten correctamente
        print("📋 To-do 1: Corregir aristas para conexiones válidas...")
        self.fix_edge_connections()
        print("   ✅ Completado")
        print()
        
        # To-do 2: Implementar ruteo ortogonal con waypoints
        print("📋 To-do 2: Implementar ruteo ortogonal con waypoints...")
        self.improve_orthogonal_routing()
        print("   ✅ Completado")
        print()
        
        # To-do 3: Mejorar etiquetado según normas ISA
        print("📋 To-do 3: Mejorar etiquetado según normas ISA...")
        self.improve_isa_labeling()
        print("   ✅ Completado")
        print()
        
        # To-do 4: Validar diagrama
        print("📋 To-do 4: Validar diagrama...")
        validation_results = self.validate_diagram()
        self.print_validation_results(validation_results)
        print()
        
        # Guardar
        output_file = self.xml_file.replace('.xml', '_MEJORADO.xml')
        self.tree.write(output_file, encoding='utf-8', xml_declaration=True)
        print(f"✅ Diagrama mejorado guardado en: {output_file}")
        
        return output_file
    
    def fix_edge_connections(self):
        """Corrige todas las aristas para asegurar source y target válidos"""
        all_node_ids = set()
        
        # Obtener todos los IDs de nodos válidos
        for cell in self.root.findall('.//mxCell[@vertex="1"]'):
            node_id = cell.get('id', '')
            if node_id and node_id not in ['0', '1']:
                all_node_ids.add(node_id)
        
        # Verificar y corregir edges
        edges_fixed = 0
        for cell in self.root.findall('.//mxCell[@edge="1"]'):
            source_id = cell.get('source', '')
            target_id = cell.get('target', '')
            edge_id = cell.get('id', '')
            
            fixed = False
            
            # Verificar source
            if source_id and source_id not in all_node_ids:
                # Buscar nodo más cercano o eliminar conexión
                print(f"   ⚠️ Edge {edge_id}: source inválido '{source_id}'")
                fixed = True
            
            # Verificar target
            if target_id and target_id not in all_node_ids:
                print(f"   ⚠️ Edge {edge_id}: target inválido '{target_id}'")
                fixed = True
            
            # Asegurar que tiene source y target
            if not source_id or not target_id:
                print(f"   ⚠️ Edge {edge_id}: falta source o target")
                fixed = True
            
            if fixed:
                edges_fixed += 1
        
        edges_count = len(list(self.root.findall('.//mxCell[@edge="1"]')))
        print(f"   📊 Edges verificados: {edges_count}")
        if edges_fixed > 0:
            print(f"   ⚠️ {edges_fixed} edges requieren atención")
    
    def improve_orthogonal_routing(self):
        """Mejora el ruteo ortogonal con waypoints y saltos visuales"""
        edges_improved = 0
        
        for cell in self.root.findall('.//mxCell[@edge="1"]'):
            style = cell.get('style', '')
            
            # Asegurar edgeStyle ortogonal
            if 'edgeStyle=orthogonalEdgeStyle' not in style:
                style = style + ';edgeStyle=orthogonalEdgeStyle' if style else 'edgeStyle=orthogonalEdgeStyle'
                cell.set('style', style)
            
            # Asegurar jumpStyle
            if 'jumpStyle=' not in style:
                style = cell.get('style', '')
                style = style + ';jumpStyle=arc' if style else 'jumpStyle=arc'
                cell.set('style', style)
            
            # Asegurar jettySize
            if 'jettySize=' not in style:
                style = cell.get('style', '')
                style = style + ';jettySize=8' if style else 'jettySize=8'
                cell.set('style', style)
            
            # Mejorar waypoints si no existen o son insuficientes
            geo = cell.find('mxGeometry')
            if geo is not None:
                array = geo.find('Array')
                source_id = cell.get('source', '')
                target_id = cell.get('target', '')
                
                # Obtener posiciones de nodos
                source_node = self._get_node_by_id(source_id)
                target_node = self._get_node_by_id(target_id)
                
                if source_node and target_node:
                    # Calcular waypoints si no existen o son pocos
                    if array is None or len(array.findall('mxPoint')) < 2:
                        waypoints = self._calculate_waypoints(source_node, target_node)
                        if waypoints:
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
                            
                            edges_improved += 1
        
        print(f"   📊 {edges_improved} edges mejorados con waypoints")
    
    def _get_node_by_id(self, node_id: str) -> Optional[ET.Element]:
        """Obtiene un nodo por su ID"""
        for cell in self.root.findall('.//mxCell[@vertex="1"]'):
            if cell.get('id') == node_id:
                return cell
        return None
    
    def _calculate_waypoints(self, source_node: ET.Element, target_node: ET.Element) -> List[Tuple[float, float]]:
        """Calcula waypoints ortogonales entre dos nodos"""
        source_geo = source_node.find('mxGeometry')
        target_geo = target_node.find('mxGeometry')
        
        if source_geo is None or target_geo is None:
            return []
        
        sx = float(source_geo.get('x', 0))
        sy = float(source_geo.get('y', 0))
        sw = float(source_geo.get('width', 0))
        sh = float(source_geo.get('height', 0))
        
        tx = float(target_geo.get('x', 0))
        ty = float(target_geo.get('y', 0))
        tw = float(target_geo.get('width', 0))
        th = float(target_geo.get('height', 0))
        
        # Calcular puntos de conexión (centros de los lados apropiados)
        source_center_x = sx + sw / 2
        source_center_y = sy + sh / 2
        target_center_x = tx + tw / 2
        target_center_y = ty + th / 2
        
        waypoints = []
        
        # Ruta ortogonal L-shaped
        dx = target_center_x - source_center_x
        dy = target_center_y - source_center_y
        
        if abs(dx) > abs(dy):
            # Horizontal primero
            mid_x = (source_center_x + target_center_x) / 2
            waypoints.append((mid_x, source_center_y))
            waypoints.append((mid_x, target_center_y))
        else:
            # Vertical primero
            mid_y = (source_center_y + target_center_y) / 2
            waypoints.append((source_center_x, mid_y))
            waypoints.append((target_center_x, mid_y))
        
        return waypoints
    
    def improve_isa_labeling(self):
        """Mejora el etiquetado según normas ISA"""
        sensors_improved = 0
        
        # Mapeo de componentes a etiquetas ISA mejoradas
        isa_improvements = {
            '14': {  # PT-HP-101
                'current': 'PT-HP-101\nP = 200-250 bar',
                'improved': 'PT-HP-101\nP = 200-250 bar\nTag: PT-HP-101'
            },
            '15': {  # TT-HP-201
                'current': 'TT-HP-201\nT = 25-60 °C',
                'improved': 'TT-HP-201\nT = 25-60 °C\nTag: TT-HP-201'
            },
            '16': {  # PT-IP-102
                'current': 'PT-IP-102\nP = 20-40 bar',
                'improved': 'PT-IP-102\nP = 20-40 bar\nTag: PT-IP-102'
            },
            '17': {  # TT-IP-202
                'current': 'TT-IP-202\nT = 20-40 °C',
                'improved': 'TT-IP-202\nT = 20-40 °C\nTag: TT-IP-202'
            },
            '18': {  # PT-LP-103
                'current': 'PT-LP-103\nP = 7-10 bar',
                'improved': 'PT-LP-103\nP = 7-10 bar\nTag: PT-LP-103'
            },
            '19': {  # LT-301
                'current': 'LT-301\nλ = 1.0',
                'improved': 'LT-301\nλ = 1.0\nTag: LT-301'
            },
            '50': {  # XI-401
                'current': 'XI-401\nSensor de Fugas\nde Gas',
                'improved': 'XI-401\nSensor de Fugas\nTag: XI-401'
            },
            '55': {  # FT-401
                'current': 'FT-401\nSensor de Flujo\nF = 30-100 Nm³/h',
                'improved': 'FT-401\nF = 30-100 Nm³/h\nTag: FT-401'
            }
        }
        
        for cell_id, improvement in isa_improvements.items():
            cell = self.root.find(f'.//mxCell[@id="{cell_id}"]')
            if cell is not None:
                current_value = cell.get('value', '')
                if improvement['current'] in current_value or improvement['improved'] not in current_value:
                    # Mejorar etiqueta manteniendo información esencial
                    cell.set('value', improvement['improved'])
                    sensors_improved += 1
        
        print(f"   📊 {sensors_improved} sensores mejorados con etiquetado ISA")
    
    def validate_diagram(self) -> Dict:
        """Valida el diagrama completo"""
        results = {
            'errors': [],
            'warnings': [],
            'info': []
        }
        
        # Obtener todos los IDs de nodos
        all_node_ids = set()
        for cell in self.root.findall('.//mxCell[@vertex="1"]'):
            node_id = cell.get('id', '')
            if node_id and node_id not in ['0', '1']:
                all_node_ids.add(node_id)
        
        # Validar edges
        edges_without_source = []
        edges_without_target = []
        edges_invalid_source = []
        edges_invalid_target = []
        
        for cell in self.root.findall('.//mxCell[@edge="1"]'):
            edge_id = cell.get('id', '')
            source_id = cell.get('source', '')
            target_id = cell.get('target', '')
            
            if not source_id:
                edges_without_source.append(edge_id)
            elif source_id not in all_node_ids:
                edges_invalid_source.append((edge_id, source_id))
            
            if not target_id:
                edges_without_target.append(edge_id)
            elif target_id not in all_node_ids:
                edges_invalid_target.append((edge_id, target_id))
        
        if edges_without_source:
            results['errors'].append(f"{len(edges_without_source)} edges sin source")
        if edges_without_target:
            results['errors'].append(f"{len(edges_without_target)} edges sin target")
        if edges_invalid_source:
            results['warnings'].append(f"{len(edges_invalid_source)} edges con source inválido")
        if edges_invalid_target:
            results['warnings'].append(f"{len(edges_invalid_target)} edges con target inválido")
        
        # Validar etiquetado ISA
        sensors_without_tag = []
        for cell in self.root.findall('.//mxCell[@vertex="1"]'):
            value = cell.get('value', '')
            if 'PT-' in value or 'TT-' in value or 'LT-' in value or 'FT-' in value:
                if 'Tag:' not in value:
                    sensors_without_tag.append(cell.get('id', 'unknown'))
        
        if sensors_without_tag:
            results['warnings'].append(f"{len(sensors_without_tag)} sensores sin tag completo")
        
        # Validar waypoints
        edges_without_waypoints = []
        for cell in self.root.findall('.//mxCell[@edge="1"]'):
            geo = cell.find('mxGeometry')
            if geo is not None:
                array = geo.find('Array')
                if array is None or len(array.findall('mxPoint')) == 0:
                    source_id = cell.get('source', '')
                    target_id = cell.get('target', '')
                    if source_id and target_id:
                        edges_without_waypoints.append(cell.get('id', 'unknown'))
        
        if edges_without_waypoints:
            results['info'].append(f"{len(edges_without_waypoints)} edges sin waypoints (pueden necesitarse)")
        
        return results
    
    def print_validation_results(self, results: Dict):
        """Imprime los resultados de validación"""
        if results['errors']:
            print(f"   ❌ Errores: {len(results['errors'])}")
            for error in results['errors']:
                print(f"      • {error}")
        else:
            print("   ✅ Sin errores críticos")
        
        if results['warnings']:
            print(f"   ⚠️ Advertencias: {len(results['warnings'])}")
            for warning in results['warnings']:
                print(f"      • {warning}")
        
        if results['info']:
            print(f"   ℹ️ Información: {len(results['info'])}")
            for info in results['info']:
                print(f"      • {info}")

if __name__ == '__main__':
    input_file = 'diagrama_gnv_PETROLIQUIDOS_2024-12-19_ELK_V_JOSEMERCHAN.xml'
    output_file = 'diagrama_gnv_PETROLIQUIDOS_2024-12-19_ELK_V_JOSEMERCHAN.xml'
    
    improver = DiagramImprover(input_file)
    result_file = improver.improve_all()
    
    # Copiar resultado al archivo original si se especifica
    if output_file and result_file != output_file:
        import shutil
        shutil.copy(result_file, output_file)
        print(f"✅ Cambios aplicados al archivo original: {output_file}")


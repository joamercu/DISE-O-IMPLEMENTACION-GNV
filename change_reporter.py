"""
Generador de reportes de cambios y aristas que requieren revisión manual
"""
from typing import Dict, List, Tuple
from elk_layout_pipeline import Graph, Node, Edge
import json

class ChangeReporter:
    """Genera reportes de cambios y aristas problemáticas"""
    
    def __init__(self, original_graph: Graph, layout_results: Dict):
        self.original_graph = original_graph
        self.layout_results = layout_results
        self.changes = []
        self.problematic_edges = []
    
    def analyze_changes(self) -> Dict:
        """
        Analiza cambios entre grafo original y layout resultante
        Retorna: dict con cambios y problemas
        """
        print("📊 Analizando cambios...")
        
        # Analizar cambios de posición de nodos
        node_changes = self._analyze_node_changes()
        
        # Analizar cambios en waypoints
        waypoint_changes = self._analyze_waypoint_changes()
        
        # Identificar aristas problemáticas
        problematic = self._identify_problematic_edges()
        
        return {
            'node_changes': node_changes,
            'waypoint_changes': waypoint_changes,
            'problematic_edges': problematic,
            'summary': self._generate_summary(node_changes, waypoint_changes, problematic)
        }
    
    def _analyze_node_changes(self) -> List[Dict]:
        """Analiza cambios en posiciones de nodos"""
        changes = []
        
        for node_id, node in self.original_graph.nodes.items():
            new_pos = self.layout_results.get('nodes', {}).get(node_id)
            
            if not new_pos:
                continue
            
            old_x, old_y = node.x, node.y
            new_x, new_y = new_pos['x'], new_pos['y']
            
            dx = new_x - old_x
            dy = new_y - old_y
            distance = (dx**2 + dy**2)**0.5
            
            if distance > 10:  # Solo reportar si se movió significativamente
                change = {
                    'node_id': node_id,
                    'label': node.label[:50],
                    'node_type': node.node_type,
                    'old_position': (old_x, old_y),
                    'new_position': (new_x, new_y),
                    'displacement': (dx, dy),
                    'distance': distance,
                    'was_fixed': node.fixed_position
                }
                changes.append(change)
        
        # Ordenar por distancia de movimiento
        changes.sort(key=lambda x: x['distance'], reverse=True)
        
        return changes
    
    def _analyze_waypoint_changes(self) -> List[Dict]:
        """Analiza cambios en waypoints de edges"""
        changes = []
        
        for edge_id, edge in self.original_graph.edges.items():
            old_waypoints = edge.waypoints
            new_waypoints = self.layout_results.get('edges', {}).get(edge_id, [])
            
            # Comparar cantidad de waypoints
            if len(old_waypoints) != len(new_waypoints):
                change = {
                    'edge_id': edge_id,
                    'label': edge.label[:50],
                    'edge_type': edge.edge_type,
                    'old_waypoint_count': len(old_waypoints),
                    'new_waypoint_count': len(new_waypoints),
                    'change_type': 'waypoint_count'
                }
                changes.append(change)
            
            # Comparar posiciones si tienen la misma cantidad
            elif len(old_waypoints) > 0 and len(new_waypoints) > 0:
                max_distance = 0
                for old_wp, new_wp in zip(old_waypoints, new_waypoints):
                    dist = ((old_wp[0] - new_wp[0])**2 + (old_wp[1] - new_wp[1])**2)**0.5
                    max_distance = max(max_distance, dist)
                
                if max_distance > 50:  # Cambio significativo
                    change = {
                        'edge_id': edge_id,
                        'label': edge.label[:50],
                        'edge_type': edge.edge_type,
                        'max_waypoint_displacement': max_distance,
                        'change_type': 'waypoint_position'
                    }
                    changes.append(change)
        
        return changes
    
    def _identify_problematic_edges(self) -> List[Dict]:
        """Identifica aristas que requieren revisión manual"""
        problematic = []
        
        for edge_id, edge in self.original_graph.edges.items():
            issues = []
            
            # Verificar si tiene waypoints
            new_waypoints = self.layout_results.get('edges', {}).get(edge_id, [])
            if not new_waypoints:
                issues.append('sin_waypoints')
            
            # Verificar si tiene muchos waypoints (posible ruta compleja)
            if len(new_waypoints) > 5:
                issues.append('muchos_waypoints')
            
            # Verificar si cruza muchos otros edges (necesita saltos)
            crossing_count = self._count_edge_crossings(edge_id, edge)
            if crossing_count > 3:
                issues.append('muchos_cruces')
            
            # Verificar si es edge crítico (main pipe) sin waypoints claros
            if edge.priority.value == 1 and len(new_waypoints) < 2:
                issues.append('pipe_principal_sin_waypoints')
            
            # Verificar si conecta nodos muy distantes
            source_node = self.original_graph.nodes.get(edge.source_id)
            target_node = self.original_graph.nodes.get(edge.target_id)
            if source_node and target_node:
                new_source_pos = self.layout_results.get('nodes', {}).get(edge.source_id, {})
                new_target_pos = self.layout_results.get('nodes', {}).get(edge.target_id, {})
                
                if new_source_pos and new_target_pos:
                    dx = new_target_pos['x'] - new_source_pos['x']
                    dy = new_target_pos['y'] - new_source_pos['y']
                    distance = (dx**2 + dy**2)**0.5
                    
                    if distance > 1000:  # Muy distantes
                        issues.append('nodos_muy_distantes')
            
            if issues:
                problematic.append({
                    'edge_id': edge_id,
                    'label': edge.label[:50],
                    'edge_type': edge.edge_type,
                    'priority': edge.priority.name,
                    'issues': issues,
                    'waypoint_count': len(new_waypoints),
                    'crossing_count': crossing_count
                })
        
        # Ordenar por severidad (más issues primero)
        problematic.sort(key=lambda x: len(x['issues']), reverse=True)
        
        return problematic
    
    def _count_edge_crossings(self, edge_id: str, edge: Edge) -> int:
        """Cuenta cuántos otros edges cruza este edge"""
        # Obtener bounding box aproximado del edge
        source_node = self.original_graph.nodes.get(edge.source_id)
        target_node = self.original_graph.nodes.get(edge.target_id)
        
        if not source_node or not target_node:
            return 0
        
        source_pos = self.layout_results.get('nodes', {}).get(edge.source_id, {})
        target_pos = self.layout_results.get('nodes', {}).get(edge.target_id, {})
        
        if not source_pos or not target_pos:
            return 0
        
        # Calcular rectángulo aproximado
        min_x = min(source_pos['x'], target_pos['x'])
        max_x = max(source_pos['x'] + source_pos['width'], target_pos['x'] + target_pos['width'])
        min_y = min(source_pos['y'], target_pos['y'])
        max_y = max(source_pos['y'] + source_pos['height'], target_pos['y'] + target_pos['height'])
        
        # Contar edges que se intersectan con este rectángulo
        crossings = 0
        for other_edge_id, other_edge in self.original_graph.edges.items():
            if other_edge_id == edge_id:
                continue
            
            other_source_pos = self.layout_results.get('nodes', {}).get(other_edge.source_id, {})
            other_target_pos = self.layout_results.get('nodes', {}).get(other_edge.target_id, {})
            
            if not other_source_pos or not other_target_pos:
                continue
            
            # Verificar si el otro edge cruza el rectángulo
            other_min_x = min(other_source_pos['x'], other_target_pos['x'])
            other_max_x = max(other_source_pos['x'] + other_source_pos['width'], 
                            other_target_pos['x'] + other_target_pos['width'])
            other_min_y = min(other_source_pos['y'], other_target_pos['y'])
            other_max_y = max(other_source_pos['y'] + other_source_pos['height'],
                            other_target_pos['y'] + other_target_pos['height'])
            
            # Verificar intersección de rectángulos
            if not (max_x < other_min_x or other_max_x < min_x or 
                   max_y < other_min_y or other_max_y < min_y):
                crossings += 1
        
        return crossings
    
    def _generate_summary(self, node_changes: List, waypoint_changes: List, 
                         problematic: List) -> Dict:
        """Genera resumen de cambios"""
        return {
            'total_node_changes': len(node_changes),
            'total_waypoint_changes': len(waypoint_changes),
            'total_problematic_edges': len(problematic),
            'nodes_moved': len([c for c in node_changes if c['distance'] > 50]),
            'edges_requiring_review': len(problematic),
            'critical_issues': len([p for p in problematic if len(p['issues']) > 2])
        }
    
    def generate_report(self, output_file: str = None) -> str:
        """
        Genera reporte completo en formato texto
        Retorna: string con el reporte
        """
        analysis = self.analyze_changes()
        
        report_lines = []
        report_lines.append("="*80)
        report_lines.append("REPORTE DE CAMBIOS Y REVISIÓN MANUAL")
        report_lines.append("="*80)
        report_lines.append("")
        
        # Resumen
        summary = analysis['summary']
        report_lines.append("📊 RESUMEN")
        report_lines.append("-"*80)
        report_lines.append(f"  • Nodos movidos: {summary['nodes_moved']}")
        report_lines.append(f"  • Cambios en waypoints: {summary['total_waypoint_changes']}")
        report_lines.append(f"  • Aristas que requieren revisión: {summary['edges_requiring_review']}")
        report_lines.append(f"  • Problemas críticos: {summary['critical_issues']}")
        report_lines.append("")
        
        # Cambios de nodos
        if analysis['node_changes']:
            report_lines.append("📦 CAMBIOS EN POSICIONES DE NODOS")
            report_lines.append("-"*80)
            for i, change in enumerate(analysis['node_changes'][:10], 1):  # Top 10
                report_lines.append(f"  {i}. {change['label'][:40]}")
                report_lines.append(f"     ID: {change['node_id']} | Tipo: {change['node_type']}")
                report_lines.append(f"     Movimiento: ({change['displacement'][0]:.1f}, {change['displacement'][1]:.1f}) | Distancia: {change['distance']:.1f}px")
                if change['was_fixed']:
                    report_lines.append(f"     ⚠️ Este nodo estaba marcado como fijo pero se movió")
                report_lines.append("")
        
        # Cambios en waypoints
        if analysis['waypoint_changes']:
            report_lines.append("🔗 CAMBIOS EN WAYPOINTS")
            report_lines.append("-"*80)
            for i, change in enumerate(analysis['waypoint_changes'][:10], 1):
                report_lines.append(f"  {i}. {change['label'][:40]}")
                report_lines.append(f"     ID: {change['edge_id']} | Tipo: {change['edge_type']}")
                if change['change_type'] == 'waypoint_count':
                    report_lines.append(f"     Waypoints: {change['old_waypoint_count']} → {change['new_waypoint_count']}")
                else:
                    report_lines.append(f"     Desplazamiento máximo: {change['max_waypoint_displacement']:.1f}px")
                report_lines.append("")
        
        # Aristas problemáticas
        if analysis['problematic_edges']:
            report_lines.append("⚠️ ARISTAS QUE REQUIEREN REVISIÓN MANUAL")
            report_lines.append("-"*80)
            for i, edge in enumerate(analysis['problematic_edges'], 1):
                report_lines.append(f"  {i}. {edge['label'][:40]}")
                report_lines.append(f"     ID: {edge['edge_id']} | Tipo: {edge['edge_type']} | Prioridad: {edge['priority']}")
                report_lines.append(f"     Waypoints: {edge['waypoint_count']} | Cruces: {edge['crossing_count']}")
                report_lines.append(f"     Problemas:")
                for issue in edge['issues']:
                    issue_desc = {
                        'sin_waypoints': '❌ Sin waypoints definidos',
                        'muchos_waypoints': '⚠️ Demasiados waypoints (>5)',
                        'muchos_cruces': '⚠️ Cruza muchos otros edges (>3)',
                        'pipe_principal_sin_waypoints': '🔴 Pipe principal sin waypoints claros',
                        'nodos_muy_distantes': '⚠️ Conecta nodos muy distantes (>1000px)'
                    }.get(issue, issue)
                    report_lines.append(f"       • {issue_desc}")
                report_lines.append("")
        
        report_lines.append("="*80)
        report_lines.append("FIN DEL REPORTE")
        report_lines.append("="*80)
        
        report_text = "\n".join(report_lines)
        
        # Guardar a archivo si se especifica
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
            print(f"📄 Reporte guardado en: {output_file}")
        
        return report_text

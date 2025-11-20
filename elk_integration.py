"""
Integración con ELK (Eclipse Layout Kernel) para layout ortogonal
Usa elkjs a través de Node.js o servicio local
"""
import json
import subprocess
import os
import tempfile
from typing import Dict, List, Tuple, Optional
from elk_layout_pipeline import Graph, Node, Edge, Port

class ELKIntegration:
    """Integración con ELK para cálculo de layout"""
    
    def __init__(self, graph: Graph):
        self.graph = graph
        self.elk_script_path = os.path.join(os.path.dirname(__file__), 'elk_layout.js')
    
    def convert_to_elk_graph(self) -> Dict:
        """
        Convierte el grafo interno a formato ELK
        Retorna: grafo en formato ELK JSON
        """
        elk_nodes = []
        elk_edges = []
        
        # Convertir nodos
        for node_id, node in self.graph.nodes.items():
            elk_node = {
                'id': node_id,
                'width': node.width,
                'height': node.height,
                'labels': [{'text': node.label[:50]}],  # ELK espera labels
            }
            
            # Agregar puertos si existen
            if node.ports:
                elk_node['ports'] = []
                for port in node.ports:
                    elk_port = {
                        'id': port.id,
                        'x': port.x * node.width,
                        'y': port.y * node.height,
                    }
                    elk_node['ports'].append(elk_port)
            
            # Constraints de posición fija
            if node.fixed_position:
                elk_node['x'] = node.x
                elk_node['y'] = node.y
                elk_node['layoutOptions'] = {
                    'elk.position': f'{node.x},{node.y}',
                    'elk.fixed': 'true'
                }
            
            elk_nodes.append(elk_node)
        
        # Convertir edges
        for edge_id, edge in self.graph.edges.items():
            elk_edge = {
                'id': edge_id,
                'sources': [edge.source_id],
                'targets': [edge.target_id],
            }
            
            # Especificar puertos si existen
            if edge.source_port:
                elk_edge['sources'] = [edge.source_port]
            if edge.target_port:
                elk_edge['targets'] = [edge.target_port]
            
            # Prioridad para routing
            elk_edge['layoutOptions'] = {
                'elk.priority': str(edge.priority.value),
                'elk.edgeRouting': 'ORTHOGONAL',
                'elk.spacing.edgeEdge': '20',
                'elk.spacing.edgeNode': '30',
            }
            
            elk_edges.append(elk_edge)
        
        elk_graph = {
            'id': 'root',
            'children': elk_nodes,
            'edges': elk_edges,
            'layoutOptions': {
                'elk.algorithm': 'layered',
                'elk.direction': 'RIGHT',
                'elk.spacing.nodeNode': '100',
                'elk.layered.spacing.nodeNodeBetweenLayers': '150',
                'elk.edgeRouting': 'ORTHOGONAL',
                'elk.portAlignment': 'CENTER',
            }
        }
        
        return elk_graph
    
    def call_elk(self, elk_graph: Dict) -> Optional[Dict]:
        """
        Invoca ELK a través de Node.js (elkjs)
        Retorna: grafo con layout calculado o None si falla
        """
        # Crear script Node.js temporal si no existe
        if not os.path.exists(self.elk_script_path):
            self._create_elk_script()
        
        # Escribir grafo a archivo temporal
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(elk_graph, f, indent=2)
            input_file = f.name
        
        try:
            # Llamar a Node.js con elkjs
            result = subprocess.run(
                ['node', self.elk_script_path, input_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                print(f"⚠️ Error ejecutando ELK: {result.stderr}")
                return None
            
            # Leer resultado
            with open(input_file.replace('.json', '_out.json'), 'r') as f:
                elk_result = json.load(f)
            
            return elk_result
            
        except FileNotFoundError:
            print("⚠️ Node.js no encontrado. Usando algoritmo interno.")
            return None
        except subprocess.TimeoutExpired:
            print("⚠️ Timeout ejecutando ELK. Usando algoritmo interno.")
            return None
        except Exception as e:
            print(f"⚠️ Error ejecutando ELK: {e}. Usando algoritmo interno.")
            return None
        finally:
            # Limpiar archivos temporales
            try:
                os.unlink(input_file)
                if os.path.exists(input_file.replace('.json', '_out.json')):
                    os.unlink(input_file.replace('.json', '_out.json'))
            except:
                pass
    
    def _create_elk_script(self):
        """Crea script Node.js para invocar elkjs"""
        script_content = """const elkjs = require('elkjs');
const fs = require('fs');
const path = require('path');

const inputFile = process.argv[2];
const outputFile = inputFile.replace('.json', '_out.json');

// Leer grafo de entrada
const graph = JSON.parse(fs.readFileSync(inputFile, 'utf8'));

// Crear instancia ELK
const elk = new elkjs.default();

// Calcular layout
elk.layout(graph)
    .then(layoutedGraph => {
        // Escribir resultado
        fs.writeFileSync(outputFile, JSON.stringify(layoutedGraph, null, 2));
        console.log('✅ Layout calculado por ELK');
    })
    .catch(err => {
        console.error('❌ Error en ELK:', err);
        process.exit(1);
    });
"""
        with open(self.elk_script_path, 'w') as f:
            f.write(script_content)
        print(f"📝 Script ELK creado: {self.elk_script_path}")
    
    def extract_layout_from_elk(self, elk_result: Dict) -> Dict:
        """
        Extrae posiciones y waypoints del resultado de ELK
        Retorna: dict con 'nodes' y 'edges'
        """
        layout_results = {
            'nodes': {},
            'edges': {}
        }
        
        # Extraer posiciones de nodos
        if 'children' in elk_result:
            for elk_node in elk_result['children']:
                node_id = elk_node['id']
                layout_results['nodes'][node_id] = {
                    'x': elk_node.get('x', 0),
                    'y': elk_node.get('y', 0),
                    'width': elk_node.get('width', 0),
                    'height': elk_node.get('height', 0)
                }
        
        # Extraer waypoints de edges
        if 'edges' in elk_result:
            for elk_edge in elk_result['edges']:
                edge_id = elk_edge['id']
                waypoints = []
                
                # ELK puede incluir secciones con puntos
                if 'sections' in elk_edge:
                    for section in elk_edge['sections']:
                        # Punto de inicio
                        if 'startPoint' in section:
                            sp = section['startPoint']
                            waypoints.append((sp['x'], sp['y']))
                        
                        # Puntos intermedios (bend points)
                        if 'bendPoints' in section:
                            for bp in section['bendPoints']:
                                waypoints.append((bp['x'], bp['y']))
                        
                        # Punto final
                        if 'endPoint' in section:
                            ep = section['endPoint']
                            waypoints.append((ep['x'], ep['y']))
                
                if waypoints:
                    layout_results['edges'][edge_id] = waypoints
        
        return layout_results

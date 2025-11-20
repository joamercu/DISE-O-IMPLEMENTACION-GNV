"""
Agente para generar y actualizar diagramas draw.io según instrucciones de ingeniería
"""
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
import os
from typing import Dict, List, Optional, Tuple
import json
import math
import re

class DrawIOAgent:
    """
    Agente que maneja la creación y actualización de diagramas draw.io
    según las instrucciones de la fase de ingeniería
    """
    
    def __init__(self, output_path: str = None):
        """
        Inicializa el agente
        
        Args:
            output_path: Ruta donde guardar el diagrama generado
        """
        self.output_path = output_path
        self.components = {}
        self.variables = {}
        self.connections = []
        self.cell_id_counter = 0
        
    def _get_next_id(self) -> str:
        """Genera el siguiente ID único para celdas"""
        self.cell_id_counter += 1
        return str(self.cell_id_counter)
    
    def load_engineering_instructions(self, doc_path: str) -> Dict:
        """
        Carga las instrucciones de ingeniería desde el documento
        
        Args:
            doc_path: Ruta al documento de ingeniería
            
        Returns:
            Dict con las instrucciones estructuradas
        """
        instructions = {
            'flow_description': [],
            'components': [],
            'pressure_ranges': {},
            'variables': []
        }
        
        # Leer el documento (asumiendo formato markdown)
        if os.path.exists(doc_path):
            try:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Extraer descripción del flujo
                    if '### 3.3 Diagrama de Flujo' in content:
                        flow_section = content.split('### 3.3 Diagrama de Flujo')[1].split('---')[0]
                        # Parsear el flujo
                        for line in flow_section.split('\n'):
                            if '↓' in line or '→' in line:
                                instructions['flow_description'].append(line.strip())
            except Exception as e:
                print(f"Advertencia: No se pudo leer el documento de ingeniería: {e}")
        
        return instructions
    
    def load_calculation_variables(self, calculation_results: Dict) -> None:
        """
        Carga variables de los cálculos del sistema
        
        Args:
            calculation_results: Resultados del cálculo del sistema GNV
        """
        # Mapear resultados del cálculo a variables del diagrama
        numero_tanques = calculation_results.get('tanques', calculation_results.get('numero_tanques', 18))
        presion_llenado = calculation_results.get('presion_llenado', 200)
        volumen_gas = calculation_results.get('volumen', calculation_results.get('volumen_gas', 0))
        masa_ch4 = calculation_results.get('masa_ch4', calculation_results.get('masa_ch4_requerida', 0))
        consumo = calculation_results.get('consumo_base', 35)
        autonomia = calculation_results.get('autonomia_objetivo', 600)
        temperatura = calculation_results.get('temperatura', calculation_results.get('temperatura_operacion', 25))
        
        # Calcular volumen por tanque
        volumen_por_tanque = volumen_gas / numero_tanques if numero_tanques > 0 else 0.08
        
        self.variables = {
            'numero_tanques': int(numero_tanques),
            'presion_llenado': presion_llenado,
            'presion_llenado_max': presion_llenado * 1.25,  # 250 bar típico
            'presion_etapa1_in': presion_llenado,
            'presion_etapa1_out': 30,  # 20-40 bar
            'presion_etapa2_in': 30,
            'presion_etapa2_out': 8.5,  # 7-10 bar
            'volumen_tanque': volumen_por_tanque,
            'volumen_tanque_litros': volumen_por_tanque * 1000,
            'temperatura_operacion': temperatura,
            'consumo_diesel': consumo,
            'autonomia': autonomia,
            'masa_ch4': masa_ch4,
            'volumen_gas_total': volumen_gas,
            'energia_requerida': calculation_results.get('energia', calculation_results.get('energia_requerida', 0))
        }
    
    def create_component(self, 
                        component_id: str,
                        component_type: str,
                        label: str,
                        position: Tuple[int, int],
                        size: Tuple[int, int] = (80, 60),
                        style: Dict = None,
                        metadata: Dict = None) -> Dict:
        """
        Crea un componente del diagrama
        
        Args:
            component_id: ID único del componente
            component_type: Tipo (tank, regulator, valve, sensor, ecu, etc.)
            label: Etiqueta del componente
            position: Posición (x, y)
            size: Tamaño (width, height)
            style: Estilo personalizado
            metadata: Metadatos adicionales
            
        Returns:
            Dict con la información del componente
        """
        component = {
            'id': component_id,
            'type': component_type,
            'label': label,
            'position': position,
            'size': size,
            'style': style or self._get_default_style(component_type),
            'metadata': metadata or {}
        }
        
        self.components[component_id] = component
        return component
    
    def _get_default_style(self, component_type: str) -> Dict:
        """Obtiene el estilo por defecto según el tipo de componente"""
        styles = {
            'tank': {
                'shape': 'cylinder3',
                'fillColor': '#dae8fc',
                'strokeColor': '#6c8ebf'
            },
            'regulator': {
                'shape': 'rounded',
                'fillColor': '#d5e8d4',
                'strokeColor': '#82b366'
            },
            'valve': {
                'shape': 'valve',
                'fillColor': '#f8cecc',
                'strokeColor': '#b85450'
            },
            'sensor': {
                'shape': 'ellipse',
                'fillColor': '#fff2cc',
                'strokeColor': '#d6b656'
            },
            'ecu': {
                'shape': 'rounded',
                'fillColor': '#ffe6cc',
                'strokeColor': '#d79b00'
            },
            'filter': {
                'shape': 'cylinder',
                'fillColor': '#e1d5e7',
                'strokeColor': '#9673a6'
            },
            'motor': {
                'shape': 'cylinder',
                'fillColor': '#d5e8d4',
                'strokeColor': '#82b366'
            },
            'manifold': {
                'shape': 'rounded',
                'fillColor': '#d5e8d4',
                'strokeColor': '#82b366'
            },
            'text': {
                'shape': 'text',
                'fillColor': 'none',
                'strokeColor': 'none'
            }
        }
        return styles.get(component_type, {})
    
    def create_connection(self,
                          source_id: str,
                          target_id: str,
                          label: str = "",
                          style: Dict = None,
                          exit_point: str = "1,0.5",
                          entry_point: str = "0,0.5") -> None:
        """
        Crea una conexión entre componentes
        
        Args:
            source_id: ID del componente origen
            target_id: ID del componente destino
            label: Etiqueta de la conexión
            style: Estilo de la conexión
            exit_point: Punto de salida (x,y relativo) ej: "1,0.5" = derecha, centro
            entry_point: Punto de entrada (x,y relativo) ej: "0,0.5" = izquierda, centro
        """
        connection = {
            'source': source_id,
            'target': target_id,
            'label': label,
            'style': style or {},
            'exit_point': exit_point,
            'entry_point': entry_point
        }
        self.connections.append(connection)
    
    def generate_diagram_from_engineering(self, 
                                         calculation_results: Dict,
                                         client_name: str = "PETROLIQUIDOS",
                                         doc_path: str = None,
                                         reference_xml_path: str = None) -> str:
        """
        Genera un diagrama draw.io completo basado en las instrucciones de ingeniería
        Usa el XML de referencia como plantilla base si está disponible
        
        Args:
            calculation_results: Resultados del cálculo del sistema
            client_name: Nombre del cliente
            doc_path: Ruta al documento de ingeniería
            reference_xml_path: Ruta al XML de referencia para usar como plantilla
            
        Returns:
            String con el XML del diagrama generado
        """
        # Cargar variables de cálculo
        self.load_calculation_variables(calculation_results)
        
        # Si hay XML de referencia, usarlo como plantilla base
        if reference_xml_path and os.path.exists(reference_xml_path):
            return self._update_reference_xml(reference_xml_path, client_name)
        
        # Si no hay referencia, generar desde cero (método anterior)
        # Resetear componentes y conexiones
        self.components = {}
        self.connections = []
        self.cell_id_counter = 0
        
        # Cargar instrucciones de ingeniería si se proporciona
        if doc_path:
            instructions = self.load_engineering_instructions(doc_path)
        
        # Crear componentes según el flujo del sistema
        self._create_system_components()
        
        # Crear conexiones
        self._create_system_connections()
        
        # Generar XML
        xml_content = self._generate_xml(client_name)
        
        return xml_content
    
    def _update_reference_xml(self, reference_xml_path: str, client_name: str) -> str:
        """
        Actualiza el XML de referencia con las variables calculadas
        
        Args:
            reference_xml_path: Ruta al XML de referencia
            client_name: Nombre del cliente
            
        Returns:
            String con el XML actualizado
        """
        try:
            # Leer el XML de referencia
            tree = ET.parse(reference_xml_path)
            root = tree.getroot()
            
            # Obtener el diagrama
            diagram = root.find('.//diagram')
            if diagram is not None:
                # Actualizar nombre del diagrama con el cliente
                diagram.set('name', f'P&ID Sistema GNV - {client_name}')
            
            # Obtener todas las celdas
            cells = root.findall('.//mxCell')
            
            # Variables a actualizar
            num_tanques = self.variables.get('numero_tanques', 18)
            volumen_l = self.variables.get('volumen_tanque_litros', 80)
            presion_llenado = self.variables.get('presion_llenado', 200)
            presion_max = self.variables.get('presion_llenado_max', 250)
            presion_etapa1_in = self.variables.get('presion_etapa1_in', 200)
            presion_etapa1_out = self.variables.get('presion_etapa1_out', 30)
            presion_etapa2_out = self.variables.get('presion_etapa2_out', 8.5)
            volumen_gas_total = self.variables.get('volumen_gas_total', 0)
            masa_ch4 = self.variables.get('masa_ch4', 0)
            consumo_diesel = self.variables.get('consumo_diesel', 35)
            autonomia = self.variables.get('autonomia', 600)
            
            # Actualizar valores en las celdas
            for cell in cells:
                value = cell.get('value', '')
                if value:
                    # Actualizar tanques
                    if 'Tanque CNG' in value and '80L' in value:
                        new_value = value.replace('80L', f'{volumen_l:.0f}L')
                        new_value = new_value.replace('200 bar', f'{presion_llenado:.0f} bar')
                        cell.set('value', new_value)
                    
                    # Actualizar número de tanques
                    if 'tanques más' in value or 'Total:' in value:
                        tanques_restantes = max(0, num_tanques - 3)
                        # Usar entidades HTML codificadas como en el XML original
                        new_value = f'&lt;font style=&quot;font-size: 24px;&quot;&gt;({tanques_restantes} tanques más)&lt;br&gt;Total: {num_tanques} tanques&lt;/font&gt;'
                        cell.set('value', new_value)
                    
                    # Actualizar PRV
                    if 'PRV' in value and '250 bar' in value:
                        new_value = value.replace('250 bar', f'{presion_max:.0f} bar')
                        cell.set('value', new_value)
                    
                    # Actualizar regulador 1ra etapa
                    if 'Regulador' in value and '1ra Etapa' in value:
                        new_value = f'Regulador&#xa;1ra Etapa&#xa;{presion_etapa1_in:.0f}-{presion_max:.0f} bar →&#xa;{presion_etapa1_out-10:.0f}-{presion_etapa1_out+10:.0f} bar&#xa;+ Calentador'
                        cell.set('value', new_value)
                    
                    # Actualizar regulador 2da etapa
                    if 'Regulador' in value and '2da Etapa' in value:
                        new_value = f'Regulador&#xa;2da Etapa&#xa;{presion_etapa1_out-10:.0f}-{presion_etapa1_out+10:.0f} bar →&#xa;{presion_etapa2_out-1.5:.1f}-{presion_etapa2_out+1.5:.1f} bar'
                        cell.set('value', new_value)
                    
                    # Actualizar sensores de presión
                    if 'PT-HP-101' in value:
                        new_value = f'PT-HP-101&#xa;P = {presion_etapa1_in:.0f}-{presion_max:.0f} bar'
                        cell.set('value', new_value)
                    elif 'PT-IP-102' in value:
                        new_value = f'PT-IP-102&#xa;P = {presion_etapa1_out-10:.0f}-{presion_etapa1_out+10:.0f} bar'
                        cell.set('value', new_value)
                    elif 'PT-LP-103' in value:
                        new_value = f'PT-LP-103&#xa;P = {presion_etapa2_out-1.5:.1f}-{presion_etapa2_out+1.5:.1f} bar'
                        cell.set('value', new_value)
                    
                    # Actualizar etiquetas de conexiones con presiones
                    if 'Gas CNG' in value and '200-250 bar' in value:
                        new_value = value.replace('200-250 bar', f'{presion_etapa1_in:.0f}-{presion_max:.0f} bar')
                        cell.set('value', new_value)
                    elif 'Gas Regulado' in value and '20-40 bar' in value:
                        new_value = value.replace('20-40 bar', f'{presion_etapa1_out-10:.0f}-{presion_etapa1_out+10:.0f} bar')
                        cell.set('value', new_value)
                    elif 'Gas Regulado' in value and '7-10 bar' in value:
                        new_value = value.replace('7-10 bar', f'{presion_etapa2_out-1.5:.1f}-{presion_etapa2_out+1.5:.1f} bar')
                        cell.set('value', new_value)
                    elif 'Gas a Motor' in value and '7-10 bar' in value:
                        new_value = value.replace('7-10 bar', f'{presion_etapa2_out-1.5:.1f}-{presion_etapa2_out+1.5:.1f} bar')
                        cell.set('value', new_value)
                    
                    # Actualizar variables del proyecto
                    if 'VARIABLES DEL PROYECTO' in value:
                        # Usar entidades HTML codificadas como en el XML original
                        new_value = (
                            f'&lt;font style=&quot;font-size: 24px;&quot;&gt;VARIABLES DEL PROYECTO:&lt;br&gt;'
                            f'• Número de tanques: {num_tanques}&lt;br&gt;'
                            f'• Presión de llenado: {presion_llenado:.0f} bar&lt;br&gt;'
                            f'• Volumen total de gas: {volumen_gas_total:.2f} m³&lt;br&gt;'
                            f'• Masa CH₄ requerida: {masa_ch4:.1f} kg&lt;br&gt;'
                            f'• Consumo diésel: {consumo_diesel:.1f} L/100km&lt;br&gt;'
                            f'• Autonomía objetivo: {autonomia:.0f} km&lt;/font&gt;'
                        )
                        cell.set('value', new_value)
                    
                    # Actualizar título con cliente
                    if 'CLIENTE : PETROLIQUIDOS' in value:
                        new_value = value.replace('CLIENTE : PETROLIQUIDOS', f'CLIENTE : {client_name}')
                        cell.set('value', new_value)
            
            # Convertir a string XML formateado
            rough_string = ET.tostring(root, encoding='unicode')
            reparsed = minidom.parseString(rough_string)
            return reparsed.toprettyxml(indent="  ")
            
        except Exception as e:
            # Si falla, generar desde cero
            print(f"Advertencia: No se pudo usar XML de referencia ({e}). Generando desde cero.")
            self.components = {}
            self.connections = []
            self.cell_id_counter = 0
            self._create_system_components()
            self._create_system_connections()
            return self._generate_xml(client_name)
    
    def _create_system_components(self):
        """Crea todos los componentes del sistema según las instrucciones"""
        x_start = 80
        y_tanks = 120
        
        # Tanques CNG
        num_tanks = int(self.variables.get('numero_tanques', 23))
        volumen_l = self.variables.get('volumen_tanque_litros', 80)
        presion = self.variables.get('presion_llenado', 200)
        
        for i in range(min(3, num_tanks)):  # Mostrar máximo 3 tanques
            tank_id = f"tank{i+1}"
            label = f"Tanque CNG\nTipo 3\n{volumen_l:.0f}L, {presion:.0f} bar"
            self.create_component(
                tank_id,
                'tank',
                label,
                (x_start + i*100, y_tanks),
                (80, 100)
            )
        
        # Indicador de más tanques
        if num_tanks > 3:
            self.components['tanks_more'] = {
                'id': 'tanks_more',
                'type': 'text',
                'label': f"...\n({num_tanks-3} tanques más)\nTotal: {num_tanks} tanques",
                'position': (x_start + 300, y_tanks + 30),
                'size': (100, 40),
                'style': {'shape': 'text'}
            }
        
        # Válvulas de alivio en tanques
        presion_max = self.variables.get('presion_llenado_max', 220)
        self.create_component(
            'relief1',
            'valve',
            f"PRV\n{presion_max:.0f} bar",
            (x_start + 20, y_tanks - 40),
            (40, 40)
        )
        
        # Manifold de distribución
        self.create_component(
            'manifold',
            'manifold',
            'Manifold de\nDistribución',
            (520, y_tanks + 20),
            (120, 60)
        )
        
        # Válvula shut-off automática
        self.create_component(
            'shutoff',
            'valve',
            'Válvula\nShut-off\nAutomática',
            (680, y_tanks + 25),
            (50, 50)
        )
        
        # Regulador 1ra etapa con calentador
        p1_in = self.variables.get('presion_etapa1_in', 200)
        p1_out = self.variables.get('presion_etapa1_out', 30)
        self.create_component(
            'reg1',
            'regulator',
            f"Regulador\n1ra Etapa\n{p1_in:.0f}-{p1_in*1.25:.0f} bar →\n{p1_out-10:.0f}-{p1_out+10:.0f} bar\n+ Calentador",
            (780, y_tanks),
            (140, 100)
        )
        
        # Filtro de gas alta presión
        self.create_component(
            'filter',
            'filter',
            'Filtro de Gas\nAlta Presión',
            (960, y_tanks + 20),
            (80, 60)
        )
        
        # Regulador 2da etapa
        p2_in = self.variables.get('presion_etapa1_out', 30)
        p2_out = self.variables.get('presion_etapa2_out', 8.5)
        self.create_component(
            'reg2',
            'regulator',
            f"Regulador\n2da Etapa\n{p2_in-10:.0f}-{p2_in+10:.0f} bar →\n{p2_out-1.5:.1f}-{p2_out+1.5:.1f} bar",
            (1080, y_tanks),
            (140, 100)
        )
        
        # ECU (Engine Control Unit)
        self.create_component(
            'ecu',
            'ecu',
            'ECU\n(Engine Control Unit)',
            (780, y_tanks + 160),
            (140, 60)
        )
        
        # Sensores de presión, temperatura y lambda
        sensors = [
            (720, y_tanks + 30, 'P', 'sensor_p1', 'Presión alta'),
            (800, y_tanks + 30, 'T', 'sensor_t1', 'Temperatura'),
            (1020, y_tanks + 30, 'P', 'sensor_p2', 'Presión media'),
            (1100, y_tanks + 30, 'T', 'sensor_t2', 'Temperatura'),
            (1140, y_tanks + 30, 'P', 'sensor_p3', 'Presión baja'),
            (1080, y_tanks + 160, 'λ', 'sensor_lambda', 'Lambda (O₂)')
        ]
        
        for x, y, label, sensor_id, desc in sensors:
            self.create_component(
                sensor_id,
                'sensor',
                label,
                (x, y),
                (30, 30),
                metadata={'description': desc}
            )
        
        # Inyectores de gas secuenciales
        self.create_component(
            'injectors',
            'valve',
            'Inyectores de Gas\nSecuenciales\n(6 unidades)',
            (1080, y_tanks + 160),
            (140, 60)
        )
        
        # Motor diésel convertido
        self.create_component(
            'motor',
            'motor',
            'Motor\nDiésel\nConvertido',
            (1080, y_tanks + 260),
            (140, 100)
        )
        
        # Válvula de llenado (receptáculo)
        self.create_component(
            'fill_valve',
            'valve',
            'Válvula de\nLlenado\n(Receptáculo)',
            (x_start, y_tanks + 140),
            (60, 60)
        )
    
    def _create_system_connections(self):
        """Crea todas las conexiones del sistema"""
        # Tanques a Manifold
        num_tanks = min(3, int(self.variables.get('numero_tanques', 23)))
        for i in range(num_tanks):
            self.create_connection(
                f"tank{i+1}",
                "manifold",
                "",
                {'strokeWidth': 2, 'strokeColor': '#6c8ebf'},
                exit_point="1,0.5",
                entry_point="0,0.5"
            )
        
        # Manifold a Shut-off
        p_high = self.variables.get('presion_etapa1_in', 200)
        self.create_connection(
            "manifold",
            "shutoff",
            f"{p_high:.0f}-{p_high*1.25:.0f} bar",
            {'strokeWidth': 3, 'strokeColor': '#6c8ebf'},
            exit_point="1,0.5",
            entry_point="0,0.5"
        )
        
        # Shut-off a Regulador 1
        self.create_connection(
            "shutoff",
            "reg1",
            "",
            {'strokeWidth': 3, 'strokeColor': '#6c8ebf'},
            exit_point="1,0.5",
            entry_point="0,0.5"
        )
        
        # Regulador 1 a Filtro
        p_med = self.variables.get('presion_etapa1_out', 30)
        self.create_connection(
            "reg1",
            "filter",
            f"{p_med-10:.0f}-{p_med+10:.0f} bar",
            {'strokeWidth': 2, 'strokeColor': '#82b366'},
            exit_point="1,0.5",
            entry_point="0,0.5"
        )
        
        # Filtro a Regulador 2
        self.create_connection(
            "filter",
            "reg2",
            "",
            {'strokeWidth': 2, 'strokeColor': '#82b366'},
            exit_point="1,0.5",
            entry_point="0,0.5"
        )
        
        # Regulador 2 a Inyectores
        p_low = self.variables.get('presion_etapa2_out', 8.5)
        self.create_connection(
            "reg2",
            "injectors",
            f"{p_low-1.5:.1f}-{p_low+1.5:.1f} bar",
            {'strokeWidth': 2, 'strokeColor': '#82b366'},
            exit_point="0.5,1",
            entry_point="0.5,0"
        )
        
        # Inyectores a Motor
        self.create_connection(
            "injectors",
            "motor",
            "",
            {'strokeWidth': 2, 'strokeColor': '#b85450'},
            exit_point="0.5,1",
            entry_point="0.5,0"
        )
        
        # Conexiones ECU a componentes
        self.create_connection(
            "ecu",
            "reg1",
            "Señales",
            {'strokeWidth': 1, 'strokeColor': '#d79b00', 'dashed': True},
            exit_point="0.5,0",
            entry_point="0.5,1"
        )
        
        self.create_connection(
            "ecu",
            "injectors",
            "Señales",
            {'strokeWidth': 1, 'strokeColor': '#d79b00', 'dashed': True},
            exit_point="1,0.5",
            entry_point="0,0.5"
        )
        
        # Sensores a ECU
        self.create_connection(
            "sensor_p1",
            "ecu",
            "",
            {'strokeWidth': 1, 'strokeColor': '#d6b656', 'dashed': True},
            exit_point="0,0.5",
            entry_point="0.5,0"
        )
        
        # Válvula de llenado a tanques
        self.create_connection(
            "fill_valve",
            "tank1",
            "Llenado",
            {'strokeWidth': 2, 'strokeColor': '#6c8ebf', 'dashed': True},
            exit_point="0.5,0",
            entry_point="0.5,1"
        )
    
    def _generate_xml(self, client_name: str) -> str:
        """Genera el XML del diagrama draw.io"""
        # Crear estructura XML
        mxfile = ET.Element('mxfile')
        mxfile.set('host', 'app.diagrams.net')
        mxfile.set('modified', datetime.now().isoformat() + 'Z')
        mxfile.set('agent', '5.0')
        mxfile.set('version', '21.0.0')
        mxfile.set('etag', 'drawio')
        mxfile.set('type', 'device')
        
        diagram = ET.SubElement(mxfile, 'diagram')
        diagram.set('name', f'P&ID Sistema GNV - {client_name}')
        diagram.set('id', 'pid-gnv')
        
        mxGraphModel = ET.SubElement(diagram, 'mxGraphModel')
        mxGraphModel.set('dx', '1422')
        mxGraphModel.set('dy', '794')
        mxGraphModel.set('grid', '1')
        mxGraphModel.set('gridSize', '10')
        mxGraphModel.set('guides', '1')
        mxGraphModel.set('tooltips', '1')
        mxGraphModel.set('connect', '1')
        mxGraphModel.set('arrows', '1')
        mxGraphModel.set('fold', '1')
        mxGraphModel.set('page', '1')
        mxGraphModel.set('pageScale', '1')
        mxGraphModel.set('pageWidth', '1400')
        mxGraphModel.set('pageHeight', '900')
        mxGraphModel.set('math', '0')
        mxGraphModel.set('shadow', '0')
        
        root = ET.SubElement(mxGraphModel, 'root')
        
        # Celda raíz
        mxCell0 = ET.SubElement(root, 'mxCell')
        mxCell0.set('id', '0')
        
        mxCell1 = ET.SubElement(root, 'mxCell')
        mxCell1.set('id', '1')
        mxCell1.set('parent', '0')
        
        # Título
        self._create_cell(root, 'title', 
                         f'P&ID - Sistema GNV para Vehículos Pesados\nCliente: {client_name}',
                         'text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=16;fontStyle=1',
                         vertex=True,
                         geometry={'x': 400, 'y': 20, 'width': 370, 'height': 40})
        
        # Agregar componentes
        for comp_id, comp in self.components.items():
            if comp.get('type') == 'text':
                # Componente de texto
                self._create_cell(root, comp_id, comp['label'],
                               'text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=10;fontStyle=2',
                               vertex=True,
                               geometry={'x': comp['position'][0], 'y': comp['position'][1],
                                        'width': comp['size'][0], 'height': comp['size'][1]})
            else:
                # Componente con forma
                style_parts = []
                style_dict = comp['style']
                
                if style_dict.get('shape'):
                    style_parts.append(f"shape={style_dict['shape']}")
                style_parts.append('whiteSpace=wrap;html=1')
                
                if style_dict.get('fillColor'):
                    style_parts.append(f"fillColor={style_dict['fillColor']}")
                if style_dict.get('strokeColor'):
                    style_parts.append(f"strokeColor={style_dict['strokeColor']}")
                
                if style_dict.get('shape') == 'cylinder3':
                    style_parts.append('boundedLbl=1;backgroundOutline=1;size=15')
                elif style_dict.get('shape') == 'rounded':
                    style_parts.append('rounded=1')
                elif style_dict.get('shape') == 'valve':
                    style_parts.append('perimeter=valvePerimeter')
                
                style_str = ';'.join(style_parts)
                
                self._create_cell(root, comp_id, comp['label'],
                               style_str,
                               vertex=True,
                               geometry={'x': comp['position'][0], 'y': comp['position'][1],
                                        'width': comp['size'][0], 'height': comp['size'][1]})
        
        # Agregar conexiones
        conn_id = 1000
        for conn in self.connections:
            source = self.components.get(conn['source'])
            target = self.components.get(conn['target'])
            
            if not source or not target:
                continue
            
            # Construir estilo de conexión
            style_parts = ['endArrow=classic', 'html=1']
            if conn['style'].get('strokeWidth'):
                style_parts.append(f"strokeWidth={conn['style']['strokeWidth']}")
            if conn['style'].get('strokeColor'):
                style_parts.append(f"strokeColor={conn['style']['strokeColor']}")
            if conn['style'].get('dashed'):
                style_parts.append('dashed=1')
            if conn['label']:
                style_parts.append('fontSize=10')
            
            # Agregar puntos de entrada/salida
            exit_x, exit_y = conn['exit_point'].split(',')
            entry_x, entry_y = conn['entry_point'].split(',')
            style_parts.append(f"exitX={exit_x};exitY={exit_y};exitDx=0;exitDy=0")
            style_parts.append(f"entryX={entry_x};entryY={entry_y};entryDx=0;entryDy=0")
            
            style_str = ';'.join(style_parts)
            
            edge = self._create_cell(root, f'conn{conn_id}',
                                   conn['label'] if conn['label'] else '',
                                   style_str,
                                   edge=True,
                                   source=conn['source'],
                                   target=conn['target'],
                                   geometry={'width': 50, 'height': 50, 'relative': True})
            
            conn_id += 1
        
        # Agregar notas
        notes_text = (
            f"NOTAS:\n"
            f"• Presiones indicadas son rangos operativos\n"
            f"• Todos los componentes deben cumplir UNECE R110\n"
            f"• Válvulas de alivio (PRV) en cada tanque ({self.variables.get('presion_llenado_max', 220):.0f} bar)\n"
            f"• Sistema de llenado independiente (no mostrado en detalle)\n"
            f"• ECU controla inyección, mezcla y sincronización\n"
            f"• Sensores: P=Presión, T=Temperatura, λ=Lambda (O2)"
        )
        
        self._create_cell(root, 'notes', notes_text,
                         'text;html=1;strokeColor=#666666;fillColor=#f5f5f5;align=left;verticalAlign=top;whiteSpace=wrap;rounded=0;fontSize=9',
                         vertex=True,
                         geometry={'x': 80, 'y': 680, 'width': 400, 'height': 120})
        
        # Variables del proyecto
        vars_text = (
            f"VARIABLES DEL PROYECTO:\n"
            f"• Número de tanques: {self.variables.get('numero_tanques', 23)}\n"
            f"• Presión de llenado: {self.variables.get('presion_llenado', 200):.0f} bar\n"
            f"• Volumen total de gas: {self.variables.get('volumen_gas_total', 0):.2f} m³\n"
            f"• Masa CH₄ requerida: {self.variables.get('masa_ch4', 0):.2f} kg\n"
            f"• Consumo diésel: {self.variables.get('consumo_diesel', 35):.1f} L/100km\n"
            f"• Autonomía objetivo: {self.variables.get('autonomia', 600):.0f} km"
        )
        
        self._create_cell(root, 'vars', vars_text,
                         'text;html=1;strokeColor=#d79b00;fillColor=#fff2cc;align=left;verticalAlign=top;whiteSpace=wrap;rounded=0;fontSize=9',
                         vertex=True,
                         geometry={'x': 520, 'y': 680, 'width': 400, 'height': 120})
        
        # Leyenda
        self._create_legend(root)
        
        # Convertir a string XML formateado
        rough_string = ET.tostring(mxfile, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")
    
    def _create_cell(self, parent, cell_id, value, style, vertex=False, edge=False,
                    source=None, target=None, geometry=None):
        """Crea una celda en el XML"""
        cell = ET.SubElement(parent, 'mxCell')
        cell.set('id', cell_id)
        cell.set('value', value.replace('\n', '&#xa;'))
        cell.set('style', style)
        
        if vertex:
            cell.set('vertex', '1')
        if edge:
            cell.set('edge', '1')
        if source:
            cell.set('source', source)
        if target:
            cell.set('target', target)
        
        cell.set('parent', '1')
        
        if geometry:
            geom = ET.SubElement(cell, 'mxGeometry')
            for key, val in geometry.items():
                if key == 'relative' and val:
                    geom.set('relative', '1')
                else:
                    geom.set(key, str(val))
            geom.set('as', 'geometry')
        
        return cell
    
    def _create_legend(self, root):
        """Crea la leyenda del diagrama"""
        legend_y = 520
        
        # Título de leyenda
        self._create_cell(root, 'legend_title', 'LEYENDA',
                         'text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=12;fontStyle=1',
                         vertex=True,
                         geometry={'x': 80, 'y': legend_y, 'width': 100, 'height': 30})
        
        # Elementos de leyenda
        legend_items = [
            ('legend_tank', 'Tanque CNG', 'cylinder3', '#dae8fc', '#6c8ebf', 80, legend_y + 40),
            ('legend_reg', 'Regulador', 'rounded', '#d5e8d4', '#82b366', 160, legend_y + 40),
            ('legend_valve', 'Válvula', 'valve', '#f8cecc', '#b85450', 260, legend_y + 40),
            ('legend_sensor', 'Sensor', 'ellipse', '#fff2cc', '#d6b656', 330, legend_y + 40),
            ('legend_ecu', 'ECU', 'rounded', '#ffe6cc', '#d79b00', 390, legend_y + 40),
        ]
        
        for item_id, label, shape, fill, stroke, x, y in legend_items:
            style_parts = [f'shape={shape}', 'whiteSpace=wrap;html=1',
                          f'fillColor={fill}', f'strokeColor={stroke}']
            if shape == 'cylinder3':
                style_parts.append('boundedLbl=1;backgroundOutline=1;size=10')
            elif shape == 'rounded':
                style_parts.append('rounded=1')
            elif shape == 'valve':
                style_parts.append('perimeter=valvePerimeter')
            
            self._create_cell(root, item_id, label,
                           ';'.join(style_parts),
                           vertex=True,
                           geometry={'x': x, 'y': y, 'width': 60 if shape != 'ellipse' else 40,
                                    'height': 40 if shape != 'ellipse' else 30})
    
    def save_diagram(self, xml_content: str, filepath: str = None) -> str:
        """
        Guarda el diagrama en un archivo
        
        Args:
            xml_content: Contenido XML del diagrama
            filepath: Ruta donde guardar (si no se proporciona, usa self.output_path)
            
        Returns:
            Ruta del archivo guardado
        """
        if filepath is None:
            filepath = self.output_path
        
        if filepath is None:
            raise ValueError("Debe proporcionar una ruta para guardar el diagrama")
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        return filepath


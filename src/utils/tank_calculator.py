"""
Módulo de cálculo para capacidad y espesor de tanques GNV
Implementa fórmulas según ISO 11439 y ASME Section VIII
"""

import math
from typing import Dict, Optional, Tuple
from dataclasses import dataclass


# ============================================
# DATOS DE MATERIALES
# ============================================

MATERIALES = {
    "34CrMo4": {
        "nombre": "34CrMo4 (Temple y Revenido)",
        "limite_elastico_mpa": 835.0,  # R_e en MPa
        "resistencia_traccion_min_mpa": 930.0,  # R_m mínimo en MPa
        "resistencia_traccion_max_mpa": 1080.0,  # R_m máximo en MPa
        "elongacion_min": 12.0,  # %
        "reduccion_area_min": 50.0,  # %
        "energia_impacto_min_j": 47.0,  # J
        "esfuerzo_admisible_asme_mpa": 207.0,  # S para ASME (aproximado)
        "descripcion": "Acero aleado de alta resistencia, más común para cilindros GNV"
    },
    "30CrMo": {
        "nombre": "30CrMo",
        "limite_elastico_mpa": 800.0,
        "resistencia_traccion_min_mpa": 900.0,
        "resistencia_traccion_max_mpa": 1050.0,
        "elongacion_min": 12.0,
        "reduccion_area_min": 50.0,
        "energia_impacto_min_j": 47.0,
        "esfuerzo_admisible_asme_mpa": 200.0,
        "descripcion": "Acero aleado similar a 34CrMo4"
    },
    "35CrMo": {
        "nombre": "35CrMo",
        "limite_elastico_mpa": 850.0,
        "resistencia_traccion_min_mpa": 950.0,
        "resistencia_traccion_max_mpa": 1100.0,
        "elongacion_min": 12.0,
        "reduccion_area_min": 50.0,
        "energia_impacto_min_j": 47.0,
        "esfuerzo_admisible_asme_mpa": 210.0,
        "descripcion": "Variante con propiedades ligeramente superiores"
    },
    "Acero_Carbono_Alta_Resistencia": {
        "nombre": "Acero al Carbono de Alta Resistencia",
        "limite_elastico_mpa": 500.0,
        "resistencia_traccion_min_mpa": 650.0,
        "resistencia_traccion_max_mpa": 800.0,
        "elongacion_min": 15.0,
        "reduccion_area_min": 40.0,
        "energia_impacto_min_j": 27.0,
        "esfuerzo_admisible_asme_mpa": 125.0,
        "descripcion": "Material alternativo, menos común para GNV"
    }
}


# ============================================
# FUNCIONES DE CÁLCULO
# ============================================

def calcular_capacidad_cilindro(
    diametro_exterior_mm: float,
    longitud_mm: float,
    espesor_pared_mm: float,
    incluir_tapas_semiesfericas: bool = True
) -> Dict[str, float]:
    """
    Calcula la capacidad (volumen interno) de un cilindro
    
    Incluye el volumen del cuerpo cilíndrico y las tapas semiesféricas si se especifica.
    
    Args:
        diametro_exterior_mm: Diámetro exterior en mm
        longitud_mm: Longitud total del cilindro en mm (incluyendo tapas si aplica)
        espesor_pared_mm: Espesor de la pared en mm
        incluir_tapas_semiesfericas: Si True, incluye el volumen de las tapas semiesféricas
    
    Returns:
        Dict con:
            - radio_interno_mm: Radio interno en mm
            - diametro_interno_mm: Diámetro interno en mm
            - longitud_cuerpo_mm: Longitud del cuerpo cilíndrico (sin tapas) en mm
            - volumen_cuerpo_litros: Volumen del cuerpo cilíndrico en litros
            - volumen_tapas_litros: Volumen de las tapas semiesféricas en litros
            - volumen_total_litros: Volumen total interno en litros
            - volumen_total_m3: Volumen total interno en m³
    """
    # Validar que el espesor sea razonable
    if espesor_pared_mm >= diametro_exterior_mm / 2:
        raise ValueError(
            f"El espesor ({espesor_pared_mm} mm) debe ser menor que el radio exterior "
            f"({diametro_exterior_mm / 2} mm)"
        )
    
    # Calcular diámetro interno
    diametro_interno_mm = diametro_exterior_mm - (2 * espesor_pared_mm)
    radio_interno_mm = diametro_interno_mm / 2.0
    
    # Calcular longitud del cuerpo cilíndrico
    # Si incluye tapas semiesféricas, cada tapa tiene altura = radio_interno
    if incluir_tapas_semiesfericas:
        altura_tapas_mm = 2 * radio_interno_mm  # Altura total de ambas tapas
        longitud_cuerpo_mm = longitud_mm - altura_tapas_mm
        
        # Validar que la longitud del cuerpo sea positiva
        if longitud_cuerpo_mm <= 0:
            raise ValueError(
                f"La longitud total ({longitud_mm} mm) es insuficiente para incluir "
                f"tapas semiesféricas. Se requiere mínimo {altura_tapas_mm:.2f} mm solo para las tapas."
            )
    else:
        longitud_cuerpo_mm = longitud_mm
    
    # Calcular volumen del cuerpo cilíndrico en mm³
    volumen_cuerpo_mm3 = math.pi * (radio_interno_mm ** 2) * longitud_cuerpo_mm
    
    # Calcular volumen de las tapas semiesféricas en mm³
    # Volumen de una esfera completa: (4/3) × π × r³
    # Volumen de dos semiesferas (tapas): (4/3) × π × r³
    if incluir_tapas_semiesfericas:
        volumen_tapas_mm3 = (4.0 / 3.0) * math.pi * (radio_interno_mm ** 3)
    else:
        volumen_tapas_mm3 = 0.0
    
    # Volumen total en mm³
    volumen_total_mm3 = volumen_cuerpo_mm3 + volumen_tapas_mm3
    
    # Convertir a litros (1 L = 1,000,000 mm³)
    volumen_cuerpo_litros = volumen_cuerpo_mm3 / 1_000_000.0
    volumen_tapas_litros = volumen_tapas_mm3 / 1_000_000.0
    volumen_total_litros = volumen_total_mm3 / 1_000_000.0
    
    # Convertir a m³
    volumen_total_m3 = volumen_total_litros / 1000.0
    
    return {
        "radio_interno_mm": radio_interno_mm,
        "diametro_interno_mm": diametro_interno_mm,
        "longitud_cuerpo_mm": longitud_cuerpo_mm,
        "volumen_cuerpo_litros": volumen_cuerpo_litros,
        "volumen_tapas_litros": volumen_tapas_litros,
        "volumen_total_litros": volumen_total_litros,
        "volumen_total_m3": volumen_total_m3,
        "incluye_tapas": incluir_tapas_semiesfericas
    }


def calcular_espesor_iso11439(
    diametro_exterior_mm: float,
    presion_prueba_bar: float,
    limite_elastico_mpa: float
) -> Dict[str, float]:
    """
    Calcula el espesor requerido según ISO 11439 / NTC 3847
    
    Fórmula: e = (D × P_h) / (2 × R_e + 0.4 × P_h)
    
    Donde:
        e = Espesor mínimo (mm)
        D = Diámetro exterior (mm)
        P_h = Presión de prueba hidráulica (bar = MPa)
        R_e = Límite elástico del material (MPa)
    
    Args:
        diametro_exterior_mm: Diámetro exterior en mm
        presion_prueba_bar: Presión de prueba en bar (1 bar = 0.1 MPa)
        limite_elastico_mpa: Límite elástico del material en MPa
    
    Returns:
        Dict con:
            - espesor_minimo_mm: Espesor mínimo requerido en mm
            - espesor_con_tolerancia_mm: Espesor con tolerancia de fabricación (15%)
    """
    # Convertir presión de bar a MPa
    presion_prueba_mpa = presion_prueba_bar * 0.1
    
    # Aplicar fórmula ISO 11439
    # e = (D × P_h) / (2 × R_e + 0.4 × P_h)
    numerador = diametro_exterior_mm * presion_prueba_mpa
    denominador = (2 * limite_elastico_mpa) + (0.4 * presion_prueba_mpa)
    
    if denominador <= 0:
        raise ValueError("El denominador de la fórmula debe ser positivo")
    
    espesor_minimo_mm = numerador / denominador
    
    # Agregar tolerancia de fabricación (15%)
    espesor_con_tolerancia_mm = espesor_minimo_mm * 1.15
    
    return {
        "espesor_minimo_mm": espesor_minimo_mm,
        "espesor_con_tolerancia_mm": espesor_con_tolerancia_mm,
        "presion_prueba_mpa": presion_prueba_mpa
    }


def calcular_espesor_asme(
    radio_interior_mm: float,
    presion_diseno_bar: float,
    esfuerzo_admisible_mpa: float,
    eficiencia_junta: float = 1.0
) -> Dict[str, float]:
    """
    Calcula el espesor requerido según ASME Section VIII, Division 1
    
    Fórmula: t = (P × R) / (S × E - 0.6 × P)
    
    Donde:
        t = Espesor mínimo (mm)
        P = Presión de diseño (MPa)
        R = Radio interior (mm)
        S = Esfuerzo máximo admisible (MPa)
        E = Eficiencia de la junta (1.0 para sin costura)
    
    Condición de validez: P ≤ 0.385 × S × E
    
    Args:
        radio_interior_mm: Radio interior en mm
        presion_diseno_bar: Presión de diseño en bar
        esfuerzo_admisible_mpa: Esfuerzo admisible del material en MPa
        eficiencia_junta: Eficiencia de la junta (default 1.0 para sin costura)
    
    Returns:
        Dict con:
            - espesor_minimo_mm: Espesor mínimo requerido en mm
            - espesor_con_tolerancia_mm: Espesor con tolerancia de fabricación (15%)
            - condicion_validez: True si P ≤ 0.385 × S × E
    """
    # Convertir presión de bar a MPa
    presion_diseno_mpa = presion_diseno_bar * 0.1
    
    # Verificar condición de validez
    limite_presion = 0.385 * esfuerzo_admisible_mpa * eficiencia_junta
    condicion_validez = presion_diseno_mpa <= limite_presion
    
    if not condicion_validez:
        raise ValueError(
            f"La presión de diseño ({presion_diseno_mpa:.2f} MPa) excede el límite "
            f"permitido ({limite_presion:.2f} MPa) según ASME. "
            f"Condición: P ≤ 0.385 × S × E"
        )
    
    # Aplicar fórmula ASME
    # t = (P × R) / (S × E - 0.6 × P)
    numerador = presion_diseno_mpa * radio_interior_mm
    denominador = (esfuerzo_admisible_mpa * eficiencia_junta) - (0.6 * presion_diseno_mpa)
    
    if denominador <= 0:
        raise ValueError("El denominador de la fórmula debe ser positivo")
    
    espesor_minimo_mm = numerador / denominador
    
    # Verificar que t ≤ 0.5 × R
    if espesor_minimo_mm > 0.5 * radio_interior_mm:
        raise ValueError(
            f"El espesor calculado ({espesor_minimo_mm:.2f} mm) excede el límite "
            f"ASME (0.5 × R = {0.5 * radio_interior_mm:.2f} mm). "
            f"La fórmula no es válida para este caso."
        )
    
    # Agregar tolerancia de fabricación (15%)
    espesor_con_tolerancia_mm = espesor_minimo_mm * 1.15
    
    return {
        "espesor_minimo_mm": espesor_minimo_mm,
        "espesor_con_tolerancia_mm": espesor_con_tolerancia_mm,
        "presion_diseno_mpa": presion_diseno_mpa,
        "condicion_validez": condicion_validez,
        "limite_presion_mpa": limite_presion
    }


def validar_espesor(
    espesor_actual_mm: float,
    espesor_requerido_mm: float,
    factor_seguridad_minimo: float = 2.25
) -> Dict[str, any]:
    """
    Valida si el espesor actual cumple con los requisitos
    
    Args:
        espesor_actual_mm: Espesor actual de la pared en mm
        espesor_requerido_mm: Espesor mínimo requerido en mm
        factor_seguridad_minimo: Factor de seguridad mínimo requerido (default 2.25 según NTC 3847)
    
    Returns:
        Dict con:
            - es_valido: True si el espesor es suficiente
            - factor_seguridad: Factor de seguridad calculado
            - diferencia_mm: Diferencia entre actual y requerido
            - porcentaje_margen: Porcentaje de margen adicional
            - estado: "✅ Cumple" / "⚠️ Marginal" / "❌ Insuficiente"
            - mensaje: Mensaje descriptivo
    """
    diferencia_mm = espesor_actual_mm - espesor_requerido_mm
    porcentaje_margen = (diferencia_mm / espesor_requerido_mm) * 100.0 if espesor_requerido_mm > 0 else 0.0
    
    # Calcular factor de seguridad aproximado
    # (basado en la relación de espesores)
    factor_seguridad = espesor_actual_mm / espesor_requerido_mm if espesor_requerido_mm > 0 else 0.0
    
    # Determinar estado
    if espesor_actual_mm >= espesor_requerido_mm * 1.1:  # 10% de margen
        es_valido = True
        estado = "✅ Cumple"
        mensaje = f"El espesor actual ({espesor_actual_mm:.2f} mm) cumple con los requisitos con un margen del {porcentaje_margen:.1f}%"
    elif espesor_actual_mm >= espesor_requerido_mm:
        es_valido = True
        estado = "⚠️ Marginal"
        mensaje = f"El espesor actual ({espesor_actual_mm:.2f} mm) cumple pero está muy cerca del mínimo requerido. Se recomienda un margen adicional."
    else:
        es_valido = False
        estado = "❌ Insuficiente"
        mensaje = f"El espesor actual ({espesor_actual_mm:.2f} mm) es insuficiente. Se requiere mínimo {espesor_requerido_mm:.2f} mm"
    
    return {
        "es_valido": es_valido,
        "factor_seguridad": factor_seguridad,
        "diferencia_mm": diferencia_mm,
        "porcentaje_margen": porcentaje_margen,
        "estado": estado,
        "mensaje": mensaje
    }


def calcular_presion_prueba(presion_trabajo_bar: float, factor_seguridad: float = 1.5) -> float:
    """
    Calcula la presión de prueba a partir de la presión de trabajo
    
    Según NTC 3847: Presión de prueba = Presión de trabajo × 1.5
    
    Args:
        presion_trabajo_bar: Presión de trabajo en bar
        factor_seguridad: Factor de seguridad (default 1.5)
    
    Returns:
        Presión de prueba en bar
    """
    return presion_trabajo_bar * factor_seguridad


def obtener_propiedades_material(material_key: str) -> Dict[str, any]:
    """
    Obtiene las propiedades de un material
    
    Args:
        material_key: Clave del material (ej: "34CrMo4")
    
    Returns:
        Dict con todas las propiedades del material
    """
    if material_key not in MATERIALES:
        raise ValueError(f"Material '{material_key}' no encontrado. Materiales disponibles: {list(MATERIALES.keys())}")
    
    return MATERIALES[material_key].copy()


def listar_materiales() -> Dict[str, Dict]:
    """
    Retorna la lista completa de materiales disponibles
    
    Returns:
        Dict con todos los materiales
    """
    return MATERIALES.copy()


"""
Motor de cálculos para sistemas GNV/CNG
"""
import math

def calcular_sistema_gnv(
    consumo_diesel,
    autonomia_deseada,
    poder_calorifico_diesel,
    lhv_ch4,
    eficiencia_conversion,
    presion_llenado,
    temperatura_operacion,
    factor_compresibilidad,
    volumen_unitario_tanque,
    peso_tanque_vacio,
    peso_soportes,
    peso_accesorios,
    constante_gases=8.314,
    masa_molar_ch4=0.01604
):
    """
    Calcula todos los parámetros del sistema GNV
    
    Returns:
        dict: Diccionario con todos los resultados del cálculo
    """
    # Paso 1: Volumen diésel equivalente
    volumen_diesel_equivalente = (consumo_diesel * autonomia_deseada) / 100.0
    
    # Paso 2: Energía requerida
    energia_requerida = volumen_diesel_equivalente * poder_calorifico_diesel
    
    # Paso 3: Masa de CH₄ requerida (considerando eficiencia)
    masa_ch4_requerida = (energia_requerida / lhv_ch4) / eficiencia_conversion
    
    # Paso 4: Volumen de gas a presión de llenado
    presion_pa = presion_llenado * 100000  # bar a Pascal
    temperatura_k = temperatura_operacion + 273.15  # °C a Kelvin
    
    volumen_gas = (masa_ch4_requerida * constante_gases * temperatura_k) / \
                 (presion_pa * masa_molar_ch4 * factor_compresibilidad)
    
    # Paso 5: Número de tanques requeridos
    numero_tanques = math.ceil(volumen_gas / volumen_unitario_tanque)
    
    # Paso 6: Peso adicional
    peso_por_tanque = peso_tanque_vacio + peso_soportes + peso_accesorios
    peso_adicional_total = numero_tanques * peso_por_tanque
    
    return {
        'volumen_diesel_equivalente': volumen_diesel_equivalente,
        'energia_requerida': energia_requerida,
        'masa_ch4_requerida': masa_ch4_requerida,
        'volumen_gas': volumen_gas,
        'numero_tanques': numero_tanques,
        'peso_adicional_total': peso_adicional_total,
        'presion_llenado': presion_llenado,
        'temperatura_operacion': temperatura_operacion,
        'consumo_base': consumo_diesel,
        'autonomia_objetivo': autonomia_deseada
    }

def calcular_sensibilidad(consumo_base, autonomia_base, variacion, otros_parametros):
    """
    Calcula análisis de sensibilidad variando consumo y autonomía
    
    Args:
        consumo_base: Consumo base en L/100km
        autonomia_base: Autonomía base en km
        variacion: Porcentaje de variación
        otros_parametros: Dict con otros parámetros necesarios
    
    Returns:
        dict: Resultados de sensibilidad
    """
    resultados = {
        'variaciones_consumo': [],
        'variaciones_autonomia': []
    }
    
    # Análisis de variación de consumo
    for var in [-variacion, -variacion//2, 0, variacion//2, variacion]:
        consumo_var = consumo_base * (1 + var/100)
        resultado = calcular_sistema_gnv(
            consumo_var, autonomia_base,
            **otros_parametros
        )
        resultados['variaciones_consumo'].append({
            'variacion': var,
            'consumo': consumo_var,
            'resultado': resultado
        })
    
    # Análisis de variación de autonomía
    for var in [-variacion, -variacion//2, 0, variacion//2, variacion]:
        autonomia_var = autonomia_base * (1 + var/100)
        resultado = calcular_sistema_gnv(
            consumo_base, autonomia_var,
            **otros_parametros
        )
        resultados['variaciones_autonomia'].append({
            'variacion': var,
            'autonomia': autonomia_var,
            'resultado': resultado
        })
    
    return resultados


"""
Script para actualizar el BOM con precios actualizados basados en:
1. Diagrama del ingeniero (18 tanques según XML)
2. Documentación de proveedores y precios
3. Casos reales de implementación
"""
import pandas as pd
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def actualizar_bom():
    """Actualiza el BOM con precios y referencias actualizadas"""
    
    print("=" * 70)
    print("ACTUALIZACIÓN DE BOM - PETROLIQUIDOS GNV")
    print("=" * 70)
    
    # Leer el BOM actual
    xls = pd.ExcelFile('outputs/PETROLIQUIDOS_GNV_BOM_v1.xlsx')
    bom_df = pd.read_excel(xls, sheet_name='BOM')
    
    # Según el diagrama del ingeniero: 18 tanques (no 23)
    NUM_TANQUES = 18
    
    print(f"\n📊 Configuración del diagrama del ingeniero:")
    print(f"   - Número de tanques: {NUM_TANQUES}")
    print(f"   - BOM actual tiene: 23 tanques")
    print(f"   - Ajustando a: {NUM_TANQUES} tanques")
    
    # Precios actualizados basados en documentación (USD, Nov 2025)
    # Referencias: PROVEEDORES_PARAMETROS_GUIA_SUPUESTOS.md
    PRECIOS_ACTUALIZADOS = {
        # Tanques CNG Tipo 3, 80L, 200 bar
        # Rango documentado: 3,500,000 - 5,500,000 COP (80L)
        # Promedio: ~4,500,000 COP = ~1,184 USD (tasa 3800)
        'Tanque CNG': {
            'precio_usd': 1184,  # Basado en 4,500,000 COP / 3800
            'precio_cop': 4500000,
            'cantidad': NUM_TANQUES,
            'notas': 'Precio actualizado según mercado Colombia 2025. Rango: 3.5M-5.5M COP'
        },
        
        # Soporte tanque
        'Soporte tanque': {
            'precio_usd': 126,
            'precio_cop': 480000,
            'cantidad': NUM_TANQUES,
            'notas': 'Set completo por tanque'
        },
        
        # Regulador 1ra etapa con calentador
        # Precio documentado: 1,200-1,500 USD típico
        'Regulador 1ra etapa': {
            'precio_usd': 1421,
            'precio_cop': 5400000,
            'cantidad': 1,
            'notas': '200-250 bar → 20-40 bar, con calentador integrado'
        },
        
        # Regulador 2da etapa
        'Regulador 2da etapa': {
            'precio_usd': 895,
            'precio_cop': 3400000,
            'cantidad': 1,
            'notas': '20-40 bar → 7-10 bar'
        },
        
        # Filtro alta presión
        'Filtro alta presión': {
            'precio_usd': 189,
            'precio_cop': 720000,
            'cantidad': 1,
            'notas': 'Filtro de gas, alta presión, elemento reemplazable'
        },
        
        # Válvula shut-off
        'Válvula shut-off': {
            'precio_usd': 368,
            'precio_cop': 1400000,
            'cantidad': 1,
            'notas': 'Electroválvula automática, 200 bar, controlada por ECU'
        },
        
        # Válvulas de alivio (PRV)
        'Válvulas de alivio': {
            'precio_usd': 232,
            'precio_cop': 880000,
            'cantidad': 3,  # Una por grupo de tanques
            'notas': 'PRV 250 bar, una por cada grupo de tanques'
        },
        
        # Manifold de distribución
        'Manifold': {
            'precio_usd': 632,
            'precio_cop': 2400000,
            'cantidad': 1,
            'notas': 'Conexión múltiple para 18 tanques, fabricación local recomendada'
        },
        
        # ECU
        # Precio documentado: 1,500-2,000 USD para sistemas profesionales
        'ECU': {
            'precio_usd': 1842,
            'precio_cop': 7000000,
            'cantidad': 1,
            'notas': 'Engine Control Unit para GNV, integración CAN Bus'
        },
        
        # Inyectores secuenciales
        'Inyectores': {
            'precio_usd': 947,
            'precio_cop': 3600000,
            'cantidad': 1,
            'notas': 'Set 6 unidades, inyección secuencial, control ECU'
        },
        
        # Sensores de presión
        'Sensores presión': {
            'precio_usd': 95,
            'precio_cop': 360000,
            'cantidad': 3,
            'notas': 'Sensor presión alta (200-250 bar), media (20-40 bar), baja (7-10 bar)'
        },
        
        # Sensores de temperatura
        'Sensores temperatura': {
            'precio_usd': 74,
            'precio_cop': 280000,
            'cantidad': 2,
            'notas': 'Temperatura alta y baja presión'
        },
        
        # Sensor lambda
        'Sensor lambda': {
            'precio_usd': 189,
            'precio_cop': 720000,
            'cantidad': 1,
            'notas': 'Sensor O2, control mezcla aire-combustible'
        },
        
        # Cableado y conectores
        'Cableado': {
            'precio_usd': 368,
            'precio_cop': 1400000,
            'cantidad': 1,
            'notas': 'Kit completo cableado, conectores, protecciones'
        },
        
        # Tuberías alta presión
        'Tuberías alta presión': {
            'precio_usd': 526,
            'precio_cop': 2000000,
            'cantidad': 1,
            'notas': 'Acero inoxidable, conexiones tipo flare, 200 bar'
        },
        
        # Tuberías media presión
        'Tuberías media presión': {
            'precio_usd': 263,
            'precio_cop': 1000000,
            'cantidad': 1,
            'notas': 'Acero/cobre, 20-40 bar'
        },
        
        # Tuberías baja presión
        'Tuberías baja presión': {
            'precio_usd': 189,
            'precio_cop': 720000,
            'cantidad': 1,
            'notas': 'Flexible certificado, 7-10 bar'
        },
        
        # Válvula de llenado
        'Válvula llenado': {
            'precio_usd': 316,
            'precio_cop': 1200000,
            'cantidad': 1,
            'notas': 'Receptáculo NGV1/NGV2, conexión estación servicio'
        },
        
        # Manómetros
        'Manómetros': {
            'precio_usd': 126,
            'precio_cop': 480000,
            'cantidad': 3,
            'notas': 'Indicadores presión, tablero y sistema'
        },
        
        # Sistema de montaje
        'Sistema montaje': {
            'precio_usd': 632,
            'precio_cop': 2400000,
            'cantidad': 1,
            'notas': 'Soportes adicionales, estructura, fijaciones'
        },
        
        # Mano de obra instalación
        'Mano de obra': {
            'precio_usd': 2316,
            'precio_cop': 8800000,
            'cantidad': 1,
            'notas': 'Instalación completa, taller certificado, 40-60 horas'
        },
        
        # Pruebas y puesta en marcha
        'Pruebas': {
            'precio_usd': 632,
            'precio_cop': 2400000,
            'cantidad': 1,
            'notas': 'Pruebas de presión, fugas, calibración ECU, puesta en marcha'
        },
        
        # Homologación
        'Homologación': {
            'precio_usd': 421,
            'precio_cop': 1600000,
            'cantidad': 1,
            'notas': 'Inspección técnica, certificación, documentación'
        }
    }
    
    # Actualizar el DataFrame del BOM
    print("\n📝 Actualizando precios en BOM...")
    
    # Mapeo de items del BOM a precios actualizados
    mapeo_items = {
        'Tanque CNG Tipo 3, 80L, 200 bar, UNECE R110': 'Tanque CNG',
        'Soporte tanque tipo 3 (set completo)': 'Soporte tanque',
        'Regulador 1ra etapa, 200-250 bar → 20-40 bar, con calentador': 'Regulador 1ra etapa',
        'Regulador 2da etapa, 20-40 bar → 7-10 bar': 'Regulador 2da etapa',
        'Filtro de gas, alta presión': 'Filtro alta presión',
        'Válvula shut-off automática, 200 bar': 'Válvula shut-off',
        'Válvulas de alivio de presión, 220 bar': 'Válvulas de alivio',
        'Manifold de distribución (conexión múltiple tanques)': 'Manifold',
        'ECU (Engine Control Unit) para GNV': 'ECU',
        'Inyectores de gas secuenciales (set 6 unidades)': 'Inyectores',
        'Sensores: Presión (3 unidades)': 'Sensores presión',
        'Sensores: Temperatura (2 unidades)': 'Sensores temperatura',
        'Sensor lambda (O2)': 'Sensor lambda',
        'Cableado y conectores (kit completo)': 'Cableado',
        'Tubería y conexiones alta presión (200 bar)': 'Tuberías alta presión',
        'Tubería y conexiones media presión (20-40 bar)': 'Tuberías media presión',
        'Tubería y conexiones baja presión (7-10 bar)': 'Tuberías baja presión',
        'Válvula de llenado (receptáculo)': 'Válvula llenado',
        'Manómetros y indicadores': 'Manómetros',
        'Sistema de montaje y fijación (soportes adicionales)': 'Sistema montaje',
        'Mano de obra instalación': 'Mano de obra',
        'Pruebas y puesta en marcha': 'Pruebas',
        'Homologación e inspección técnica': 'Homologación'
    }
    
    # Actualizar cada fila
    for idx, row in bom_df.iterrows():
        if pd.isna(row['Item']) or row['Item'] == 'SUBTOTAL' or pd.isna(row['Descripción Técnica']):
            continue
            
        desc = str(row['Descripción Técnica']).strip()
        
        # Buscar coincidencia en el mapeo
        for key, precio_key in mapeo_items.items():
            if key in desc:
                if precio_key in PRECIOS_ACTUALIZADOS:
                    precio_info = PRECIOS_ACTUALIZADOS[precio_key]
                    
                    # Actualizar cantidad si es tanque
                    if precio_key == 'Tanque CNG':
                        bom_df.at[idx, 'Cantidad'] = NUM_TANQUES
                    elif precio_key == 'Soporte tanque':
                        bom_df.at[idx, 'Cantidad'] = NUM_TANQUES
                    else:
                        bom_df.at[idx, 'Cantidad'] = precio_info['cantidad']
                    
                    # Actualizar precios
                    bom_df.at[idx, 'Precio Unitario USD'] = precio_info['precio_usd']
                    bom_df.at[idx, 'Precio Unitario COP'] = precio_info['precio_cop']
                    
                    # Actualizar notas
                    if pd.isna(bom_df.at[idx, 'Notas']) or bom_df.at[idx, 'Notas'] == '':
                        bom_df.at[idx, 'Notas'] = precio_info['notas']
                    else:
                        bom_df.at[idx, 'Notas'] = f"{bom_df.at[idx, 'Notas']}. {precio_info['notas']}"
                    
                    # Calcular totales
                    cantidad = bom_df.at[idx, 'Cantidad']
                    bom_df.at[idx, 'Total USD'] = cantidad * precio_info['precio_usd']
                    bom_df.at[idx, 'Total COP'] = cantidad * precio_info['precio_cop']
                    
                    print(f"   ✓ {desc[:50]}... → {cantidad} × ${precio_info['precio_usd']} USD")
                    break
    
    # Calcular subtotales
    print("\n💰 Calculando totales...")
    
    # Filtrar filas con valores numéricos
    filas_validas = bom_df[
        (bom_df['Total USD'].notna()) & 
        (bom_df['Total USD'] != 0)
    ]
    
    subtotal_usd = filas_validas['Total USD'].sum()
    subtotal_cop = filas_validas['Total COP'].sum()
    
    # Encontrar fila de subtotal
    idx_subtotal = bom_df[bom_df['Item'] == 'SUBTOTAL'].index
    if len(idx_subtotal) > 0:
        bom_df.at[idx_subtotal[0], 'Total USD'] = subtotal_usd
        bom_df.at[idx_subtotal[0], 'Total COP'] = subtotal_cop
    
    # Contingencia 15%
    contingencia_usd = subtotal_usd * 0.15
    contingencia_cop = subtotal_cop * 0.15
    
    idx_cont = bom_df[bom_df['Item'] == 'CONTINGENCIA (15%)'].index
    if len(idx_cont) > 0:
        bom_df.at[idx_cont[0], 'Total USD'] = contingencia_usd
        bom_df.at[idx_cont[0], 'Total COP'] = contingencia_cop
    
    # Subtotal + contingencia
    subtotal_cont_usd = subtotal_usd + contingencia_usd
    subtotal_cont_cop = subtotal_cop + contingencia_cop
    
    idx_subcont = bom_df[bom_df['Item'] == 'SUBTOTAL + CONTINGENCIA'].index
    if len(idx_subcont) > 0:
        bom_df.at[idx_subcont[0], 'Total USD'] = subtotal_cont_usd
        bom_df.at[idx_subcont[0], 'Total COP'] = subtotal_cont_cop
    
    # Margen 20%
    margen_usd = subtotal_cont_usd * 0.20
    margen_cop = subtotal_cont_cop * 0.20
    
    idx_margen = bom_df[bom_df['Item'] == 'MARGEN (20%)'].index
    if len(idx_margen) > 0:
        bom_df.at[idx_margen[0], 'Total USD'] = margen_usd
        bom_df.at[idx_margen[0], 'Total COP'] = margen_cop
    
    # Total final
    total_final_usd = subtotal_cont_usd + margen_usd
    total_final_cop = subtotal_cont_cop + margen_cop
    
    idx_total = bom_df[bom_df['Item'] == 'TOTAL FINAL'].index
    if len(idx_total) > 0:
        bom_df.at[idx_total[0], 'Total USD'] = total_final_usd
        bom_df.at[idx_total[0], 'Total COP'] = total_final_cop
    
    print(f"\n📊 RESUMEN DE COSTOS:")
    print(f"   Subtotal componentes: ${subtotal_usd:,.2f} USD / ${subtotal_cop:,.0f} COP")
    print(f"   Contingencia (15%): ${contingencia_usd:,.2f} USD / ${contingencia_cop:,.0f} COP")
    print(f"   Subtotal + Contingencia: ${subtotal_cont_usd:,.2f} USD / ${subtotal_cont_cop:,.0f} COP")
    print(f"   Margen (20%): ${margen_usd:,.2f} USD / ${margen_cop:,.0f} COP")
    print(f"   TOTAL FINAL: ${total_final_usd:,.2f} USD / ${total_final_cop:,.0f} COP")
    
    # Guardar en nuevo archivo
    output_file = 'outputs/PETROLIQUIDOS_GNV_BOM_v2_ACTUALIZADO.xlsx'
    
    print(f"\n💾 Guardando BOM actualizado en: {output_file}")
    
    # Leer todas las hojas
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Guardar todas las hojas originales
        for sheet_name in xls.sheet_names:
            if sheet_name == 'BOM':
                bom_df.to_excel(writer, sheet_name=sheet_name, index=False)
            else:
                df = pd.read_excel(xls, sheet_name=sheet_name)
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # Aplicar formato
        workbook = writer.book
        worksheet = writer.sheets['BOM']
        
        # Formato de encabezados
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF", size=11)
        
        for cell in worksheet[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        
        # Ajustar ancho de columnas
        column_widths = {
            'A': 8,   # Item
            'B': 50,  # Descripción
            'C': 12,  # Cantidad
            'D': 10,  # Unidad
            'E': 18,  # Precio USD
            'F': 18,  # Precio COP
            'G': 15,  # Total USD
            'H': 15,  # Total COP
            'I': 12,  # Lead Time
            'J': 25,  # Proveedor
            'K': 20,  # Part Number
            'L': 40   # Notas
        }
        
        for col, width in column_widths.items():
            worksheet.column_dimensions[col].width = width
        
        # Formato de números
        for row in worksheet.iter_rows(min_row=2, max_row=worksheet.max_row):
            for cell in row:
                if cell.column in [5, 6, 7, 8]:  # Columnas de precios
                    cell.number_format = '#,##0'
                elif cell.column == 3:  # Cantidad
                    cell.number_format = '#,##0.0'
    
    print(f"   ✅ BOM actualizado guardado exitosamente")
    
    return output_file, {
        'subtotal_usd': subtotal_usd,
        'subtotal_cop': subtotal_cop,
        'contingencia_usd': contingencia_usd,
        'contingencia_cop': contingencia_cop,
        'subtotal_cont_usd': subtotal_cont_usd,
        'subtotal_cont_cop': subtotal_cont_cop,
        'margen_usd': margen_usd,
        'margen_cop': margen_cop,
        'total_final_usd': total_final_usd,
        'total_final_cop': total_final_cop,
        'num_tanques': NUM_TANQUES
    }

if __name__ == "__main__":
    try:
        archivo, resumen = actualizar_bom()
        print("\n" + "=" * 70)
        print("✅ ACTUALIZACIÓN COMPLETADA")
        print("=" * 70)
        print(f"\n📄 Archivo generado: {archivo}")
        print(f"\n📊 Resumen de costos:")
        print(f"   Total del proyecto: ${resumen['total_final_usd']:,.2f} USD")
        print(f"   Total del proyecto: ${resumen['total_final_cop']:,.0f} COP")
        print(f"\n📋 Configuración:")
        print(f"   - Tanques CNG: {resumen['num_tanques']} unidades")
        print(f"   - Basado en diagrama del ingeniero")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


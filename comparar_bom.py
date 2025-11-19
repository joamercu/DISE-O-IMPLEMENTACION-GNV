"""
Script para comparar dos archivos Excel BOM
Compara: BOM_PETROLIQUIDOS_GNV.xlsx vs PETROLIQUIDOS_GNV_BOM_v1.xlsx
"""

import pandas as pd
import os
from datetime import datetime
from pathlib import Path

def obtener_info_archivo(ruta_archivo):
    """Obtiene información básica del archivo"""
    archivo = Path(ruta_archivo)
    if not archivo.exists():
        return None
    
    stat = archivo.stat()
    fecha_modificacion = datetime.fromtimestamp(stat.st_mtime)
    fecha_creacion = datetime.fromtimestamp(stat.st_ctime)
    tamaño = stat.st_size
    
    return {
        'existe': True,
        'nombre': archivo.name,
        'ruta_completa': str(archivo.absolute()),
        'tamaño_bytes': tamaño,
        'tamaño_kb': round(tamaño / 1024, 2),
        'fecha_modificacion': fecha_modificacion,
        'fecha_creacion': fecha_creacion
    }

def comparar_archivos_excel(archivo1, archivo2):
    """Compara dos archivos Excel y genera un reporte detallado"""
    
    # Obtener información de archivos
    info1 = obtener_info_archivo(archivo1)
    info2 = obtener_info_archivo(archivo2)
    
    if not info1 or not info2:
        print("❌ Error: Uno o ambos archivos no existen")
        if not info1:
            print(f"   No encontrado: {archivo1}")
        if not info2:
            print(f"   No encontrado: {archivo2}")
        return
    
    print("=" * 80)
    print("COMPARACIÓN DE ARCHIVOS EXCEL BOM")
    print("=" * 80)
    print()
    
    # Información de archivos
    print("📁 INFORMACIÓN DE ARCHIVOS")
    print("-" * 80)
    print(f"\n📄 Archivo 1: {info1['nombre']}")
    print(f"   Ruta: {info1['ruta_completa']}")
    print(f"   Tamaño: {info1['tamaño_kb']} KB ({info1['tamaño_bytes']} bytes)")
    print(f"   Fecha creación: {info1['fecha_creacion'].strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Fecha modificación: {info1['fecha_modificacion'].strftime('%Y-%m-%d %H:%M:%S')}")
    
    print(f"\n📄 Archivo 2: {info2['nombre']}")
    print(f"   Ruta: {info2['ruta_completa']}")
    print(f"   Tamaño: {info2['tamaño_kb']} KB ({info2['tamaño_bytes']} bytes)")
    print(f"   Fecha creación: {info2['fecha_creacion'].strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Fecha modificación: {info2['fecha_modificacion'].strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Determinar cuál es más reciente
    if info1['fecha_modificacion'] > info2['fecha_modificacion']:
        print(f"\n⏰ El archivo 1 es más reciente (diferencia: {info1['fecha_modificacion'] - info2['fecha_modificacion']})")
    elif info2['fecha_modificacion'] > info1['fecha_modificacion']:
        print(f"\n⏰ El archivo 2 es más reciente (diferencia: {info2['fecha_modificacion'] - info1['fecha_modificacion']})")
    else:
        print("\n⏰ Ambos archivos tienen la misma fecha de modificación")
    
    print("\n" + "=" * 80)
    print("📊 COMPARACIÓN DE HOJAS")
    print("=" * 80)
    
    # Leer archivos Excel
    try:
        excel1 = pd.ExcelFile(archivo1, engine='openpyxl')
        excel2 = pd.ExcelFile(archivo2, engine='openpyxl')
    except Exception as e:
        print(f"❌ Error al leer archivos: {e}")
        print("💡 Asegúrate de tener instalado: pip install openpyxl")
        return
    
    hojas1 = excel1.sheet_names
    hojas2 = excel2.sheet_names
    
    print(f"\n📋 Archivo 1 tiene {len(hojas1)} hoja(s):")
    for i, hoja in enumerate(hojas1, 1):
        df = pd.read_excel(archivo1, sheet_name=hoja, engine='openpyxl')
        print(f"   {i}. '{hoja}' - {len(df)} filas, {len(df.columns)} columnas")
    
    print(f"\n📋 Archivo 2 tiene {len(hojas2)} hoja(s):")
    for i, hoja in enumerate(hojas2, 1):
        df = pd.read_excel(archivo2, sheet_name=hoja, engine='openpyxl')
        print(f"   {i}. '{hoja}' - {len(df)} filas, {len(df.columns)} columnas")
    
    # Comparar hojas comunes
    hojas_comunes = set(hojas1) & set(hojas2)
    hojas_solo1 = set(hojas1) - set(hojas2)
    hojas_solo2 = set(hojas2) - set(hojas1)
    
    print(f"\n✅ Hojas comunes ({len(hojas_comunes)}): {', '.join(sorted(hojas_comunes)) if hojas_comunes else 'Ninguna'}")
    if hojas_solo1:
        print(f"📄 Solo en Archivo 1 ({len(hojas_solo1)}): {', '.join(sorted(hojas_solo1))}")
    if hojas_solo2:
        print(f"📄 Solo en Archivo 2 ({len(hojas_solo2)}): {', '.join(sorted(hojas_solo2))}")
    
    # Comparar estructura de hojas comunes
    print("\n" + "=" * 80)
    print("🔍 COMPARACIÓN DETALLADA DE HOJAS COMUNES")
    print("=" * 80)
    
    for hoja in sorted(hojas_comunes):
        print(f"\n📑 Hoja: '{hoja}'")
        print("-" * 80)
        
        df1 = pd.read_excel(archivo1, sheet_name=hoja, engine='openpyxl')
        df2 = pd.read_excel(archivo2, sheet_name=hoja, engine='openpyxl')
        
        # Comparar dimensiones
        print(f"   Archivo 1: {len(df1)} filas × {len(df1.columns)} columnas")
        print(f"   Archivo 2: {len(df2)} filas × {len(df2.columns)} columnas")
        
        # Comparar columnas
        cols1 = set(df1.columns)
        cols2 = set(df2.columns)
        cols_comunes = cols1 & cols2
        cols_solo1 = cols1 - cols2
        cols_solo2 = cols2 - cols1
        
        if cols_comunes:
            print(f"   ✅ Columnas comunes ({len(cols_comunes)}): {', '.join(sorted(cols_comunes))}")
        if cols_solo1:
            print(f"   📊 Solo en Archivo 1 ({len(cols_solo1)}): {', '.join(sorted(cols_solo1))}")
        if cols_solo2:
            print(f"   📊 Solo en Archivo 2 ({len(cols_solo2)}): {', '.join(sorted(cols_solo2))}")
        
        # Comparar contenido si las columnas coinciden
        if cols_comunes and len(df1) > 0 and len(df2) > 0:
            # Mostrar primeras filas diferentes
            try:
                # Comparar solo columnas comunes
                df1_common = df1[list(cols_comunes)].copy()
                df2_common = df2[list(cols_comunes)].copy()
                
                # Resetear índices para comparar
                df1_common = df1_common.reset_index(drop=True)
                df2_common = df2_common.reset_index(drop=True)
                
                # Comparar fila por fila
                diferencias = []
                min_filas = min(len(df1_common), len(df2_common))
                
                for idx in range(min_filas):
                    fila1 = df1_common.iloc[idx]
                    fila2 = df2_common.iloc[idx]
                    
                    if not fila1.equals(fila2):
                        diferencias.append(idx)
                
                if diferencias:
                    print(f"   ⚠️  Se encontraron {len(diferencias)} filas con diferencias (de {min_filas} comparadas)")
                    if len(diferencias) <= 5:
                        print(f"   Filas diferentes: {diferencias}")
                else:
                    print(f"   ✅ Las primeras {min_filas} filas son idénticas")
                
                if len(df1_common) != len(df2_common):
                    print(f"   ⚠️  Diferencia en número de filas: {abs(len(df1_common) - len(df2_common))} filas")
                    
            except Exception as e:
                print(f"   ⚠️  Error al comparar contenido: {e}")
    
    # Comparación especial de hoja BOM
    print("\n" + "=" * 80)
    print("📦 COMPARACIÓN ESPECIAL: HOJA BOM")
    print("=" * 80)
    
    hoja_bom = None
    for nombre in ['BOM', 'bom', 'Bom', 'Lista de Materiales', 'Materiales']:
        if nombre in hojas_comunes:
            hoja_bom = nombre
            break
    
    if hoja_bom:
        print(f"\n📑 Analizando hoja: '{hoja_bom}'")
        print("-" * 80)
        
        df1_bom = pd.read_excel(archivo1, sheet_name=hoja_bom, engine='openpyxl')
        df2_bom = pd.read_excel(archivo2, sheet_name=hoja_bom, engine='openpyxl')
        
        print(f"\n📊 Resumen de datos:")
        print(f"   Archivo 1: {len(df1_bom)} ítems")
        print(f"   Archivo 2: {len(df2_bom)} ítems")
        
        # Mostrar primeras filas de cada archivo
        print(f"\n📋 Primeras 5 filas del Archivo 1:")
        print(df1_bom.head().to_string())
        
        print(f"\n📋 Primeras 5 filas del Archivo 2:")
        print(df2_bom.head().to_string())
        
        # Si hay columna de precio o costo, comparar totales
        columnas_precio = [col for col in df1_bom.columns if any(term in str(col).lower() for term in ['precio', 'costo', 'price', 'cost', 'total'])]
        if columnas_precio:
            print(f"\n💰 Comparación de precios/costos:")
            for col in columnas_precio:
                if col in df1_bom.columns and col in df2_bom.columns:
                    try:
                        total1 = pd.to_numeric(df1_bom[col], errors='coerce').sum()
                        total2 = pd.to_numeric(df2_bom[col], errors='coerce').sum()
                        if not pd.isna(total1) and not pd.isna(total2):
                            print(f"   {col}:")
                            print(f"      Archivo 1: ${total1:,.2f}")
                            print(f"      Archivo 2: ${total2:,.2f}")
                            diff = total2 - total1
                            print(f"      Diferencia: ${diff:,.2f} ({diff/total1*100:.2f}%)" if total1 != 0 else "      Diferencia: N/A")
                    except:
                        pass
    else:
        print("\n⚠️  No se encontró una hoja BOM común en ambos archivos")
        if 'BOM' in hojas1 or 'BOM' in hojas2:
            print("   (Existe una hoja BOM pero con nombre diferente)")
    
    print("\n" + "=" * 80)
    print("✅ COMPARACIÓN COMPLETADA")
    print("=" * 80)

if __name__ == "__main__":
    # Rutas de los archivos
    base_dir = Path(__file__).parent
    outputs_dir = base_dir / 'outputs'
    
    archivo1 = outputs_dir / 'BOM_PETROLIQUIDOS_GNV.xlsx'
    archivo2 = outputs_dir / 'PETROLIQUIDOS_GNV_BOM_v1.xlsx'
    
    print(f"🔍 Buscando archivos en: {outputs_dir}")
    print()
    
    comparar_archivos_excel(archivo1, archivo2)


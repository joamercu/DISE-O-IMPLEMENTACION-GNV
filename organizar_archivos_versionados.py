"""
Script para organizar PDFs y Excel en carpetas de versiones
"""
import os
import shutil
from pathlib import Path
from datetime import datetime

def obtener_timestamp_archivo(archivo):
    """Obtiene timestamp de última modificación del archivo"""
    if os.path.exists(archivo):
        mtime = os.path.getmtime(archivo)
        return datetime.fromtimestamp(mtime).strftime('%Y%m%d_%H%M%S')
    return datetime.now().strftime('%Y%m%d_%H%M%S')

def copiar_con_timestamp(origen, destino_dir):
    """Copia archivo a destino con timestamp en el nombre"""
    if not os.path.exists(origen):
        print(f"⚠️  No existe: {origen}")
        return None
    
    # Obtener información del archivo
    info = Path(origen)
    timestamp = obtener_timestamp_archivo(origen)
    nombre_base = info.stem
    extension = info.suffix
    
    # Crear nuevo nombre con timestamp
    nuevo_nombre = f"{nombre_base}_{timestamp}{extension}"
    destino = os.path.join(destino_dir, nuevo_nombre)
    
    # Copiar archivo
    shutil.copy2(origen, destino)
    print(f"✅ Copiado: {origen} -> {destino}")
    return destino

def main():
    """Función principal"""
    print("=" * 70)
    print("ORGANIZACIÓN DE ARCHIVOS VERSIONADOS")
    print("=" * 70)
    
    # Crear carpetas si no existen
    versionados_pdfs = Path("versionados/pdfs")
    versionados_excel = Path("versionados/excel")
    versionados_pdfs.mkdir(parents=True, exist_ok=True)
    versionados_excel.mkdir(parents=True, exist_ok=True)
    
    # Lista de PDFs a versionar (excepto el del ingeniero que se mantiene en raíz)
    pdfs_a_versionar = [
        "diagrama gnv.pdf",
        "docs/Informe de Cálculo Sistema GNV - PETROLIQUIDOS.pdf",
        "docs/Herramienta de Documentos - WeldTech Solutions.pdf",
        "docs/Resolución 957 de 2012 Ministerio de Comercio, Industria y Turismo.pdf",
        "docs/output 3.pdf",
        "outputs/output 1.pdf",
        "outputs/output 2.pdf"
    ]
    
    # Lista de Excel a versionar
    excel_a_versionar = [
        "outputs/archivos_antiguos/BOM_PETROLIQUIDOS_GNV.xlsx"
    ]
    
    print("\n📄 Moviendo PDFs a versionados/pdfs/...")
    pdfs_copiados = []
    for pdf in pdfs_a_versionar:
        if os.path.exists(pdf):
            destino = copiar_con_timestamp(pdf, str(versionados_pdfs))
            if destino:
                pdfs_copiados.append((pdf, destino))
        else:
            print(f"⚠️  No encontrado: {pdf}")
    
    print("\n📊 Moviendo Excel a versionados/excel/...")
    excel_copiados = []
    for excel in excel_a_versionar:
        if os.path.exists(excel):
            destino = copiar_con_timestamp(excel, str(versionados_excel))
            if destino:
                excel_copiados.append((excel, destino))
        else:
            print(f"⚠️  No encontrado: {excel}")
    
    print("\n" + "=" * 70)
    print("✅ ORGANIZACIÓN COMPLETADA")
    print("=" * 70)
    print(f"\n📄 PDFs versionados: {len(pdfs_copiados)}")
    print(f"📊 Excel versionados: {len(excel_copiados)}")
    
    return pdfs_copiados, excel_copiados

if __name__ == "__main__":
    main()


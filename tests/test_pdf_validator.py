#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests para validación de archivos PDF
Verifica que los PDFs sean válidos y que no haya conflictos de extensiones
"""

import os
import sys
import unittest
from pathlib import Path
from io import BytesIO

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.pdf_validator import (
    PDFValidator,
    validar_pdf,
    validar_pdf_bytes,
    validar_pdfs_en_directorio
)
from src.utils.file_handler import (
    obtener_nombre_sin_extensiones,
    generar_pdf_desde_html
)


class TestPDFValidator(unittest.TestCase):
    """Tests para el validador de PDFs"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.validator = PDFValidator()
        self.test_dir = Path(__file__).parent.parent
    
    def test_obtener_nombre_sin_extensiones(self):
        """Test para verificar que se eliminen correctamente las extensiones múltiples"""
        # Caso normal
        self.assertEqual(obtener_nombre_sin_extensiones("archivo.md"), "archivo")
        self.assertEqual(obtener_nombre_sin_extensiones("archivo.json"), "archivo")
        
        # Caso problemático: archivo.md.pdf
        self.assertEqual(obtener_nombre_sin_extensiones("archivo.md.pdf"), "archivo")
        self.assertEqual(obtener_nombre_sin_extensiones("archivo.json.pdf"), "archivo")
        
        # Caso con múltiples extensiones
        self.assertEqual(obtener_nombre_sin_extensiones("archivo.md.html.pdf"), "archivo")
        
        # Caso que ya es PDF
        self.assertEqual(obtener_nombre_sin_extensiones("archivo.pdf"), "archivo")
        
        # Caso sin extensión problemática
        self.assertEqual(obtener_nombre_sin_extensiones("archivo.txt"), "archivo.txt")
    
    def test_validar_pdf_inexistente(self):
        """Test para validar un PDF que no existe"""
        es_valido, info = validar_pdf("archivo_que_no_existe.pdf")
        self.assertFalse(es_valido)
        self.assertIn("no existe", info['errors'][0].lower())
    
    def test_validar_pdf_vacio(self):
        """Test para validar un PDF vacío (simulado)"""
        # Crear un archivo temporal vacío
        test_file = self.test_dir / "test_empty.pdf"
        try:
            test_file.write_bytes(b"")
            es_valido, info = validar_pdf(str(test_file))
            self.assertFalse(es_valido)
            self.assertIn("vacío", info['errors'][0].lower())
        finally:
            if test_file.exists():
                test_file.unlink()
    
    def test_validar_pdf_invalido(self):
        """Test para validar un archivo que no es PDF"""
        # Crear un archivo que no es PDF
        test_file = self.test_dir / "test_not_pdf.pdf"
        try:
            test_file.write_text("Esto no es un PDF")
            es_valido, info = validar_pdf(str(test_file))
            self.assertFalse(es_valido)
        finally:
            if test_file.exists():
                test_file.unlink()
    
    def test_validar_pdf_bytes_vacio(self):
        """Test para validar bytes vacíos"""
        es_valido, info = validar_pdf_bytes(b"")
        self.assertFalse(es_valido)
        self.assertIn("vacío", info['errors'][0].lower())
    
    def test_validar_pdf_bytes_invalido(self):
        """Test para validar bytes que no son PDF"""
        es_valido, info = validar_pdf_bytes(b"Esto no es un PDF")
        self.assertFalse(es_valido)
        self.assertIn("firma", info['errors'][0].lower())
    
    def test_validar_pdf_generado(self):
        """Test para validar un PDF generado desde HTML"""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Test PDF</title>
        </head>
        <body>
            <h1>Test PDF</h1>
            <p>Este es un PDF de prueba generado desde HTML.</p>
        </body>
        </html>
        """
        
        pdf_data, error_msg = generar_pdf_desde_html(html_content)
        
        if pdf_data:
            es_valido, info = validar_pdf_bytes(pdf_data)
            self.assertTrue(es_valido, f"PDF generado no es válido: {info.get('errors', [])}")
            self.assertGreater(info.get('page_count', 0), 0)
        else:
            self.skipTest(f"No se pudo generar PDF: {error_msg}")
    
    def test_validar_pdfs_en_directorio(self):
        """Test para validar todos los PDFs en un directorio"""
        # Buscar directorios con PDFs
        outputs_dir = self.test_dir / "outputs"
        docs_dir = self.test_dir / "docs"
        
        directorios_a_probar = []
        if outputs_dir.exists():
            directorios_a_probar.append(str(outputs_dir))
        if docs_dir.exists():
            directorios_a_probar.append(str(docs_dir))
        
        if not directorios_a_probar:
            self.skipTest("No se encontraron directorios con PDFs para probar")
        
        for directorio in directorios_a_probar:
            resultados = validar_pdfs_en_directorio(directorio, recursivo=False)
            
            self.assertIsInstance(resultados, dict)
            self.assertIn('total_archivos', resultados)
            self.assertIn('archivos_validos', resultados)
            self.assertIn('archivos_invalidos', resultados)
            self.assertIn('resultados', resultados)
            
            # Si hay archivos, mostrar resultados
            if resultados['total_archivos'] > 0:
                print(f"\n📊 Resultados para {directorio}:")
                print(f"  Total: {resultados['total_archivos']}")
                print(f"  Válidos: {resultados['archivos_validos']}")
                print(f"  Inválidos: {resultados['archivos_invalidos']}")
                
                # Mostrar errores si los hay
                for archivo, info in resultados['resultados'].items():
                    if not info.get('is_valid_pdf', False):
                        print(f"\n  ❌ {Path(archivo).name}:")
                        for error in info.get('errors', []):
                            print(f"     - {error}")
                    elif info.get('warnings'):
                        print(f"\n  ⚠️  {Path(archivo).name}:")
                        for warning in info.get('warnings', []):
                            print(f"     - {warning}")


class TestExtensionesArchivo(unittest.TestCase):
    """Tests para verificar el manejo correcto de extensiones de archivo"""
    
    def test_nombres_archivo_sin_conflictos(self):
        """Test para verificar que no se generen nombres como archivo.md.pdf"""
        from src.utils.file_handler import obtener_nombre_sin_extensiones
        
        casos = [
            ("archivo.md", "archivo"),
            ("archivo.json", "archivo"),
            ("archivo.md.pdf", "archivo"),  # Caso problemático
            ("archivo.json.pdf", "archivo"),  # Caso problemático
            ("archivo.pdf", "archivo"),
            ("archivo.md.html.pdf", "archivo"),  # Múltiples extensiones
            ("archivo_sin_ext", "archivo_sin_ext"),  # Sin extensión problemática
        ]
        
        for entrada, esperado in casos:
            resultado = obtener_nombre_sin_extensiones(entrada)
            self.assertEqual(
                resultado, 
                esperado,
                f"Falló para '{entrada}': esperado '{esperado}', obtenido '{resultado}'"
            )
    
    def test_generacion_nombres_pdf(self):
        """Test para verificar que los nombres generados para PDFs sean correctos"""
        from src.utils.file_handler import obtener_nombre_sin_extensiones
        
        # Simular el proceso de generación de nombres
        archivos_entrada = [
            "documento.md",
            "datos.json",
            "archivo.md.pdf",  # Caso problemático
            "informe.json.pdf",  # Caso problemático
        ]
        
        for archivo in archivos_entrada:
            nombre_sin_ext = obtener_nombre_sin_extensiones(archivo, ['.md', '.json', '.pdf', '.html'])
            nombre_final = f"{nombre_sin_ext}.pdf"
            
            # Verificar que no tenga extensiones duplicadas
            self.assertNotIn('.md.pdf', nombre_final, 
                          f"Nombre '{nombre_final}' tiene extensión duplicada .md.pdf")
            self.assertNotIn('.json.pdf', nombre_final,
                          f"Nombre '{nombre_final}' tiene extensión duplicada .json.pdf")
            self.assertTrue(nombre_final.endswith('.pdf'),
                          f"Nombre '{nombre_final}' no termina en .pdf")
            self.assertEqual(nombre_final.count('.pdf'), 1,
                          f"Nombre '{nombre_final}' tiene múltiples .pdf")


def ejecutar_validacion_pdfs():
    """Función auxiliar para ejecutar validación de PDFs existentes"""
    print("=" * 60)
    print("VALIDACIÓN DE PDFs EN EL PROYECTO")
    print("=" * 60)
    
    base_dir = Path(__file__).parent.parent
    directorios = [
        base_dir / "outputs",
        base_dir / "docs",
        base_dir / "cliente 1 - petroliquidos_20251119_132911" / "outputs"
    ]
    
    todos_los_resultados = {}
    
    for directorio in directorios:
        if directorio.exists():
            print(f"\n📁 Validando PDFs en: {directorio}")
            print("-" * 60)
            
            resultados = validar_pdfs_en_directorio(str(directorio), recursivo=True)
            todos_los_resultados[str(directorio)] = resultados
            
            print(f"Total de archivos PDF encontrados: {resultados['total_archivos']}")
            print(f"✅ Archivos válidos: {resultados['archivos_validos']}")
            print(f"❌ Archivos inválidos: {resultados['archivos_invalidos']}")
            print(f"⚠️  Archivos con advertencias: {resultados['archivos_con_warnings']}")
            
            # Mostrar detalles de archivos inválidos
            if resultados['archivos_invalidos'] > 0:
                print("\n❌ ARCHIVOS INVÁLIDOS:")
                for archivo, info in resultados['resultados'].items():
                    if not info.get('is_valid_pdf', False):
                        print(f"\n  📄 {Path(archivo).name}")
                        print(f"     Ruta: {archivo}")
                        for error in info.get('errors', []):
                            print(f"     Error: {error}")
            
            # Mostrar advertencias
            if resultados['archivos_con_warnings'] > 0:
                print("\n⚠️  ARCHIVOS CON ADVERTENCIAS:")
                for archivo, info in resultados['resultados'].items():
                    if info.get('warnings'):
                        print(f"\n  📄 {Path(archivo).name}")
                        for warning in info.get('warnings', []):
                            print(f"     Advertencia: {warning}")
    
    # Resumen general
    print("\n" + "=" * 60)
    print("RESUMEN GENERAL")
    print("=" * 60)
    total_archivos = sum(r['total_archivos'] for r in todos_los_resultados.values())
    total_validos = sum(r['archivos_validos'] for r in todos_los_resultados.values())
    total_invalidos = sum(r['archivos_invalidos'] for r in todos_los_resultados.values())
    
    print(f"Total de PDFs en el proyecto: {total_archivos}")
    print(f"✅ Válidos: {total_validos}")
    print(f"❌ Inválidos: {total_invalidos}")
    
    if total_invalidos > 0:
        print(f"\n⚠️  Se encontraron {total_invalidos} archivo(s) PDF inválido(s).")
        print("   Revise los detalles arriba para más información.")
        return False
    else:
        print("\n✅ Todos los PDFs son válidos.")
        return True


if __name__ == '__main__':
    # Ejecutar validación de PDFs existentes
    print("\n" + "=" * 60)
    print("EJECUTANDO VALIDACIÓN DE PDFs")
    print("=" * 60)
    
    pdfs_validos = ejecutar_validacion_pdfs()
    
    # Ejecutar tests unitarios
    print("\n" + "=" * 60)
    print("EJECUTANDO TESTS UNITARIOS")
    print("=" * 60)
    
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    sys.exit(0 if pdfs_validos else 1)


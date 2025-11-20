#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Módulo de validación de archivos PDF
Verifica que los PDFs sean válidos, no estén corruptos y tengan contenido legible
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from io import BytesIO

# Intentar importar librerías de validación de PDF
try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    try:
        import PyPDF2
        PYPDF_AVAILABLE = True
        pypdf = PyPDF2  # Alias para compatibilidad
    except ImportError:
        PYPDF_AVAILABLE = False
        pypdf = None

try:
    from pdfminer.high_level import extract_text
    from pdfminer.pdfparser import PDFParser
    from pdfminer.pdfdocument import PDFDocument
    from pdfminer.pdfpage import PDFPage
    PDFMINER_AVAILABLE = True
except ImportError:
    PDFMINER_AVAILABLE = False


class PDFValidationError(Exception):
    """Excepción personalizada para errores de validación de PDF"""
    pass


class PDFValidator:
    """Clase para validar archivos PDF"""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: Dict[str, Any] = {}
    
    def validate_pdf_file(self, file_path: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Valida un archivo PDF completo
        
        Args:
            file_path: Ruta al archivo PDF
            
        Returns:
            tuple: (es_válido, información_detallada)
        """
        self.errors = []
        self.warnings = []
        self.info = {
            'file_path': file_path,
            'file_exists': False,
            'file_size': 0,
            'is_valid_pdf': False,
            'page_count': 0,
            'has_text': False,
            'has_images': False,
            'is_encrypted': False,
            'metadata': {},
            'errors': [],
            'warnings': []
        }
        
        # Verificar que el archivo existe
        if not os.path.exists(file_path):
            self.errors.append(f"El archivo no existe: {file_path}")
            self.info['errors'] = self.errors
            return False, self.info
        
        self.info['file_exists'] = True
        
        # Verificar tamaño del archivo
        try:
            file_size = os.path.getsize(file_path)
            self.info['file_size'] = file_size
            
            if file_size == 0:
                self.errors.append("El archivo está vacío (0 bytes)")
                self.info['errors'] = self.errors
                return False, self.info
            
            if file_size < 100:  # PDF mínimo debería ser al menos 100 bytes
                self.warnings.append(f"El archivo es muy pequeño ({file_size} bytes), puede estar corrupto")
        except OSError as e:
            self.errors.append(f"Error al leer el tamaño del archivo: {str(e)}")
            self.info['errors'] = self.errors
            return False, self.info
        
        # Verificar firma PDF
        if not self._check_pdf_signature(file_path):
            self.errors.append("El archivo no tiene la firma PDF válida (%PDF)")
            self.info['errors'] = self.errors
            return False, self.info
        
        # Validar con pypdf si está disponible
        if PYPDF_AVAILABLE:
            try:
                pdf_valid, pdf_info = self._validate_with_pypdf(file_path)
                if not pdf_valid:
                    self.errors.extend(pdf_info.get('errors', []))
                self.warnings.extend(pdf_info.get('warnings', []))
                self.info.update(pdf_info)
            except Exception as e:
                self.errors.append(f"Error al validar con pypdf: {str(e)}")
        
        # Validar con pdfminer si está disponible
        if PDFMINER_AVAILABLE:
            try:
                pdfminer_info = self._validate_with_pdfminer(file_path)
                self.info.update(pdfminer_info)
            except Exception as e:
                self.warnings.append(f"Error al validar con pdfminer: {str(e)}")
        
        # Actualizar información final
        self.info['errors'] = self.errors
        self.info['warnings'] = self.warnings
        self.info['is_valid_pdf'] = len(self.errors) == 0
        
        return len(self.errors) == 0, self.info
    
    def validate_pdf_bytes(self, pdf_bytes: bytes) -> Tuple[bool, Dict[str, Any]]:
        """
        Valida bytes de un PDF en memoria
        
        Args:
            pdf_bytes: Bytes del PDF
            
        Returns:
            tuple: (es_válido, información_detallada)
        """
        self.errors = []
        self.warnings = []
        self.info = {
            'file_size': len(pdf_bytes),
            'is_valid_pdf': False,
            'page_count': 0,
            'has_text': False,
            'is_encrypted': False,
            'errors': [],
            'warnings': []
        }
        
        # Verificar que no esté vacío
        if len(pdf_bytes) == 0:
            self.errors.append("Los bytes del PDF están vacíos")
            self.info['errors'] = self.errors
            return False, self.info
        
        if len(pdf_bytes) < 100:
            self.warnings.append(f"El PDF es muy pequeño ({len(pdf_bytes)} bytes)")
        
        # Verificar firma PDF
        if not pdf_bytes.startswith(b'%PDF'):
            self.errors.append("Los bytes no tienen la firma PDF válida (%PDF)")
            self.info['errors'] = self.errors
            return False, self.info
        
        # Validar con pypdf si está disponible
        if PYPDF_AVAILABLE:
            try:
                pdf_buffer = BytesIO(pdf_bytes)
                pdf_valid, pdf_info = self._validate_pdf_bytes_with_pypdf(pdf_buffer)
                if not pdf_valid:
                    self.errors.extend(pdf_info.get('errors', []))
                self.warnings.extend(pdf_info.get('warnings', []))
                self.info.update(pdf_info)
            except Exception as e:
                self.errors.append(f"Error al validar bytes con pypdf: {str(e)}")
        
        # Actualizar información final
        self.info['errors'] = self.errors
        self.info['warnings'] = self.warnings
        self.info['is_valid_pdf'] = len(self.errors) == 0
        
        return len(self.errors) == 0, self.info
    
    def _check_pdf_signature(self, file_path: str) -> bool:
        """Verifica que el archivo tenga la firma PDF válida"""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(4)
                return header == b'%PDF'
        except Exception:
            return False
    
    def _validate_with_pypdf(self, file_path: str) -> Tuple[bool, Dict[str, Any]]:
        """Valida PDF usando pypdf/PyPDF2"""
        info = {
            'is_valid_pdf': False,
            'page_count': 0,
            'is_encrypted': False,
            'metadata': {},
            'errors': [],
            'warnings': []
        }
        
        try:
            with open(file_path, 'rb') as f:
                pdf_reader = pypdf.PdfReader(f)
                
                # Verificar si está encriptado
                if pdf_reader.is_encrypted:
                    info['is_encrypted'] = True
                    info['warnings'].append("El PDF está encriptado, puede requerir contraseña")
                
                # Contar páginas
                try:
                    page_count = len(pdf_reader.pages)
                    info['page_count'] = page_count
                    
                    if page_count == 0:
                        info['errors'].append("El PDF no tiene páginas")
                        return False, info
                    
                    # Intentar leer la primera página
                    try:
                        first_page = pdf_reader.pages[0]
                        text = first_page.extract_text()
                        info['has_text'] = len(text.strip()) > 0
                        
                        if not info['has_text']:
                            info['warnings'].append("La primera página no contiene texto legible")
                    except Exception as e:
                        info['warnings'].append(f"Error al leer primera página: {str(e)}")
                    
                    # Leer metadata
                    try:
                        if pdf_reader.metadata:
                            info['metadata'] = {
                                'title': pdf_reader.metadata.get('/Title', ''),
                                'author': pdf_reader.metadata.get('/Author', ''),
                                'subject': pdf_reader.metadata.get('/Subject', ''),
                                'creator': pdf_reader.metadata.get('/Creator', ''),
                                'producer': pdf_reader.metadata.get('/Producer', ''),
                                'creation_date': str(pdf_reader.metadata.get('/CreationDate', '')),
                                'modification_date': str(pdf_reader.metadata.get('/ModDate', ''))
                            }
                    except Exception as e:
                        info['warnings'].append(f"Error al leer metadata: {str(e)}")
                    
                    info['is_valid_pdf'] = True
                    
                except Exception as e:
                    info['errors'].append(f"Error al contar páginas: {str(e)}")
                    return False, info
                
        except pypdf.errors.PdfReadError as e:
            info['errors'].append(f"Error de lectura PDF (archivo corrupto): {str(e)}")
            return False, info
        except Exception as e:
            info['errors'].append(f"Error inesperado al validar PDF: {str(e)}")
            return False, info
        
        return True, info
    
    def _validate_pdf_bytes_with_pypdf(self, pdf_buffer: BytesIO) -> Tuple[bool, Dict[str, Any]]:
        """Valida bytes de PDF usando pypdf/PyPDF2"""
        info = {
            'is_valid_pdf': False,
            'page_count': 0,
            'is_encrypted': False,
            'has_text': False,
            'errors': [],
            'warnings': []
        }
        
        try:
            pdf_buffer.seek(0)
            pdf_reader = pypdf.PdfReader(pdf_buffer)
            
            # Verificar si está encriptado
            if pdf_reader.is_encrypted:
                info['is_encrypted'] = True
                info['warnings'].append("El PDF está encriptado")
            
            # Contar páginas
            try:
                page_count = len(pdf_reader.pages)
                info['page_count'] = page_count
                
                if page_count == 0:
                    info['errors'].append("El PDF no tiene páginas")
                    return False, info
                
                # Intentar leer la primera página
                try:
                    first_page = pdf_reader.pages[0]
                    text = first_page.extract_text()
                    info['has_text'] = len(text.strip()) > 0
                except Exception as e:
                    info['warnings'].append(f"Error al leer primera página: {str(e)}")
                
                info['is_valid_pdf'] = True
                
            except Exception as e:
                info['errors'].append(f"Error al contar páginas: {str(e)}")
                return False, info
                
        except pypdf.errors.PdfReadError as e:
            info['errors'].append(f"Error de lectura PDF (archivo corrupto): {str(e)}")
            return False, info
        except Exception as e:
            info['errors'].append(f"Error inesperado al validar PDF: {str(e)}")
            return False, info
        
        return True, info
    
    def _validate_with_pdfminer(self, file_path: str) -> Dict[str, Any]:
        """Valida PDF usando pdfminer para extraer texto"""
        info = {
            'has_text_content': False,
            'text_length': 0
        }
        
        try:
            text = extract_text(file_path)
            info['text_length'] = len(text)
            info['has_text_content'] = len(text.strip()) > 0
        except Exception as e:
            info['text_extraction_error'] = str(e)
        
        return info


def validar_pdf(file_path: str) -> Tuple[bool, Dict[str, Any]]:
    """
    Función de conveniencia para validar un PDF
    
    Args:
        file_path: Ruta al archivo PDF
        
    Returns:
        tuple: (es_válido, información_detallada)
    """
    validator = PDFValidator()
    return validator.validate_pdf_file(file_path)


def validar_pdf_bytes(pdf_bytes: bytes) -> Tuple[bool, Dict[str, Any]]:
    """
    Función de conveniencia para validar bytes de PDF
    
    Args:
        pdf_bytes: Bytes del PDF
        
    Returns:
        tuple: (es_válido, información_detallada)
    """
    validator = PDFValidator()
    return validator.validate_pdf_bytes(pdf_bytes)


def validar_pdfs_en_directorio(directorio: str, recursivo: bool = True) -> Dict[str, Any]:
    """
    Valida todos los PDFs en un directorio
    
    Args:
        directorio: Ruta al directorio
        recursivo: Si es True, busca recursivamente en subdirectorios
        
    Returns:
        dict: Resultados de validación por archivo
    """
    resultados = {
        'directorio': directorio,
        'total_archivos': 0,
        'archivos_validos': 0,
        'archivos_invalidos': 0,
        'archivos_con_warnings': 0,
        'resultados': {}
    }
    
    path = Path(directorio)
    if not path.exists():
        return resultados
    
    # Buscar todos los PDFs
    if recursivo:
        pdf_files = list(path.rglob('*.pdf'))
    else:
        pdf_files = list(path.glob('*.pdf'))
    
    resultados['total_archivos'] = len(pdf_files)
    
    validator = PDFValidator()
    for pdf_file in pdf_files:
        try:
            es_valido, info = validator.validate_pdf_file(str(pdf_file))
            resultados['resultados'][str(pdf_file)] = info
            
            if es_valido:
                resultados['archivos_validos'] += 1
                if info.get('warnings'):
                    resultados['archivos_con_warnings'] += 1
            else:
                resultados['archivos_invalidos'] += 1
        except Exception as e:
            resultados['resultados'][str(pdf_file)] = {
                'error': f"Error al procesar: {str(e)}",
                'is_valid_pdf': False
            }
            resultados['archivos_invalidos'] += 1
    
    return resultados


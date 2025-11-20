"""
Módulo de Base de Datos PostgreSQL
Gestión de envíos, datos del cliente, cálculos, diagramas y notificaciones
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.dialects.postgresql import JSONB
import enum

from config import DATABASE_URL

Base = declarative_base()


# Enums para estados
class EstadoSubmission(str, enum.Enum):
    PENDIENTE = "pendiente"
    EN_REVISION = "en_revision"
    APROBADO = "aprobado"
    RECHAZADO = "rechazado"


class TipoNotificacion(str, enum.Enum):
    EMAIL = "email"
    APP = "app"


class EstadoNotificacion(str, enum.Enum):
    ENVIADA = "enviada"
    LEIDA = "leida"
    FALLIDA = "fallida"


# Modelos de Base de Datos
class Submission(Base):
    """Tabla principal de envíos de clientes"""
    __tablename__ = 'submissions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cliente_nombre = Column(String(255), nullable=False)
    usuario_cliente = Column(String(100), nullable=False)
    estado = Column(SQLEnum(EstadoSubmission), default=EstadoSubmission.PENDIENTE, nullable=False)
    fecha_envio = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_ultima_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    administrador_asignado = Column(String(100), nullable=True)
    notas_administrador = Column(Text, nullable=True)
    
    # Relaciones
    datos = relationship("SubmissionData", back_populates="submission", uselist=False, cascade="all, delete-orphan")
    calculos = relationship("SubmissionCalculos", back_populates="submission", cascade="all, delete-orphan")
    diagramas = relationship("SubmissionDiagramas", back_populates="submission", cascade="all, delete-orphan")
    notificaciones = relationship("Notificacion", back_populates="submission", cascade="all, delete-orphan")


class SubmissionData(Base):
    """Datos del cliente enviados"""
    __tablename__ = 'submission_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    submission_id = Column(Integer, ForeignKey('submissions.id', ondelete='CASCADE'), nullable=False, unique=True)
    datos_cliente = Column(JSONB, nullable=False)
    metadata_info = Column('metadata', JSONB, nullable=True)  # Usar 'metadata' como nombre de columna en BD
    
    # Relación
    submission = relationship("Submission", back_populates="datos")


class SubmissionCalculos(Base):
    """Resultados de cálculos asociados a un envío"""
    __tablename__ = 'submission_calculos'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    submission_id = Column(Integer, ForeignKey('submissions.id', ondelete='CASCADE'), nullable=False)
    resultados_calculo = Column(JSONB, nullable=False)
    parametros_entrada = Column(JSONB, nullable=True)
    fecha_calculo = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relación
    submission = relationship("Submission", back_populates="calculos")


class SubmissionDiagramas(Base):
    """Diagramas generados asociados a un envío"""
    __tablename__ = 'submission_diagramas'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    submission_id = Column(Integer, ForeignKey('submissions.id', ondelete='CASCADE'), nullable=False)
    diagrama_xml = Column(Text, nullable=False)
    diagrama_pdf = Column(Text, nullable=True)  # Almacenado como base64 string
    ruta_archivo = Column(String(500), nullable=True)
    fecha_generacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relación
    submission = relationship("Submission", back_populates="diagramas")


class Notificacion(Base):
    """Registro de notificaciones enviadas"""
    __tablename__ = 'notificaciones'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    submission_id = Column(Integer, ForeignKey('submissions.id', ondelete='CASCADE'), nullable=False)
    tipo = Column(SQLEnum(TipoNotificacion), nullable=False)
    estado = Column(SQLEnum(EstadoNotificacion), default=EstadoNotificacion.ENVIADA, nullable=False)
    fecha_envio = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_lectura = Column(DateTime, nullable=True)
    mensaje = Column(Text, nullable=True)
    
    # Relación
    submission = relationship("Submission", back_populates="notificaciones")


# Funciones de utilidad
def get_engine():
    """Obtener engine de SQLAlchemy"""
    return create_engine(DATABASE_URL, pool_pre_ping=True)


def get_session() -> Session:
    """Obtener sesión de base de datos"""
    engine = get_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


def init_database():
    """Crear todas las tablas si no existen"""
    try:
        engine = get_engine()
        Base.metadata.create_all(engine)
        return True
    except Exception as e:
        print(f"Error al inicializar base de datos: {str(e)}")
        return False


# Funciones CRUD para Submissions
def create_submission(cliente_nombre: str, usuario_cliente: str, datos_cliente: Dict, metadata: Optional[Dict] = None) -> Tuple[Optional[int], Optional[str]]:
    """Crear un nuevo envío de cliente
    
    Returns:
        tuple: (submission_id, error_message)
        - Si éxito: (submission_id, None)
        - Si error: (None, mensaje_de_error)
    """
    session = None
    try:
        session = get_session()
        
        # Crear submission
        submission = Submission(
            cliente_nombre=cliente_nombre,
            usuario_cliente=usuario_cliente,
            estado=EstadoSubmission.PENDIENTE,
            fecha_envio=datetime.utcnow(),
            fecha_ultima_actualizacion=datetime.utcnow()
        )
        session.add(submission)
        session.flush()  # Para obtener el ID
        
        # Crear datos del cliente
        submission_data = SubmissionData(
            submission_id=submission.id,
            datos_cliente=datos_cliente,
            metadata_info=metadata or {}
        )
        session.add(submission_data)
        
        session.commit()
        submission_id = submission.id
        session.close()
        
        return (submission_id, None)
    except Exception as e:
        error_msg = str(e)
        print(f"Error al crear submission: {error_msg}")
        if session is not None:
            try:
                session.rollback()
                session.close()
            except:
                pass
        return (None, error_msg)


def get_submissions(
    estado: Optional[str] = None,
    cliente_nombre: Optional[str] = None,
    usuario_cliente: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> List[Dict]:
    """Obtener envíos con filtros"""
    try:
        session = get_session()
        query = session.query(Submission)
        
        if estado:
            query = query.filter(Submission.estado == EstadoSubmission(estado))
        if cliente_nombre:
            query = query.filter(Submission.cliente_nombre.ilike(f"%{cliente_nombre}%"))
        if usuario_cliente:
            query = query.filter(Submission.usuario_cliente == usuario_cliente)
        
        query = query.order_by(Submission.fecha_envio.desc())
        submissions = query.limit(limit).offset(offset).all()
        
        result = []
        for sub in submissions:
            result.append({
                'id': sub.id,
                'cliente_nombre': sub.cliente_nombre,
                'usuario_cliente': sub.usuario_cliente,
                'estado': sub.estado.value,
                'fecha_envio': sub.fecha_envio.isoformat() if sub.fecha_envio else None,
                'fecha_ultima_actualizacion': sub.fecha_ultima_actualizacion.isoformat() if sub.fecha_ultima_actualizacion else None,
                'administrador_asignado': sub.administrador_asignado,
                'notas_administrador': sub.notas_administrador
            })
        
        session.close()
        return result
    except Exception as e:
        print(f"Error al obtener submissions: {str(e)}")
        return []


def get_submission_by_id(submission_id: int) -> Optional[Dict]:
    """Obtener un envío completo por ID"""
    try:
        session = get_session()
        submission = session.query(Submission).filter(Submission.id == submission_id).first()
        
        if not submission:
            session.close()
            return None
        
        result = {
            'id': submission.id,
            'cliente_nombre': submission.cliente_nombre,
            'usuario_cliente': submission.usuario_cliente,
            'estado': submission.estado.value,
            'fecha_envio': submission.fecha_envio.isoformat() if submission.fecha_envio else None,
            'fecha_ultima_actualizacion': submission.fecha_ultima_actualizacion.isoformat() if submission.fecha_ultima_actualizacion else None,
            'administrador_asignado': submission.administrador_asignado,
            'notas_administrador': submission.notas_administrador,
            'datos': None,
            'calculos': [],
            'diagramas': [],
            'notificaciones': []
        }
        
        # Obtener datos del cliente
        if submission.datos:
            result['datos'] = {
                'datos_cliente': submission.datos.datos_cliente,
                'metadata': submission.datos.metadata_info
            }
        
        # Obtener cálculos
        for calc in submission.calculos:
            result['calculos'].append({
                'id': calc.id,
                'resultados_calculo': calc.resultados_calculo,
                'parametros_entrada': calc.parametros_entrada,
                'fecha_calculo': calc.fecha_calculo.isoformat() if calc.fecha_calculo else None
            })
        
        # Obtener diagramas
        for diag in submission.diagramas:
            result['diagramas'].append({
                'id': diag.id,
                'diagrama_xml': diag.diagrama_xml[:1000] + '...' if len(diag.diagrama_xml) > 1000 else diag.diagrama_xml,  # Truncar para no sobrecargar
                'ruta_archivo': diag.ruta_archivo,
                'fecha_generacion': diag.fecha_generacion.isoformat() if diag.fecha_generacion else None,
                'tiene_pdf': bool(diag.diagrama_pdf)
            })
        
        # Obtener notificaciones
        for notif in submission.notificaciones:
            result['notificaciones'].append({
                'id': notif.id,
                'tipo': notif.tipo.value,
                'estado': notif.estado.value,
                'fecha_envio': notif.fecha_envio.isoformat() if notif.fecha_envio else None,
                'fecha_lectura': notif.fecha_lectura.isoformat() if notif.fecha_lectura else None,
                'mensaje': notif.mensaje
            })
        
        session.close()
        return result
    except Exception as e:
        print(f"Error al obtener submission por ID: {str(e)}")
        return None


def update_submission_status(
    submission_id: int,
    nuevo_estado: str,
    administrador: Optional[str] = None,
    notas: Optional[str] = None
) -> bool:
    """Actualizar estado de un envío"""
    try:
        session = get_session()
        submission = session.query(Submission).filter(Submission.id == submission_id).first()
        
        if not submission:
            session.close()
            return False
        
        submission.estado = EstadoSubmission(nuevo_estado)
        submission.fecha_ultima_actualizacion = datetime.utcnow()
        
        if administrador:
            submission.administrador_asignado = administrador
        if notas is not None:
            submission.notas_administrador = notas
        
        session.commit()
        session.close()
        return True
    except Exception as e:
        print(f"Error al actualizar estado: {str(e)}")
        if 'session' in locals():
            session.rollback()
            session.close()
        return False


def add_calculos_to_submission(submission_id: int, resultados: Dict, parametros: Optional[Dict] = None) -> bool:
    """Agregar resultados de cálculos a un envío"""
    try:
        session = get_session()
        calculo = SubmissionCalculos(
            submission_id=submission_id,
            resultados_calculo=resultados,
            parametros_entrada=parametros or {},
            fecha_calculo=datetime.utcnow()
        )
        session.add(calculo)
        session.commit()
        session.close()
        return True
    except Exception as e:
        print(f"Error al agregar cálculos: {str(e)}")
        if 'session' in locals():
            session.rollback()
            session.close()
        return False


def add_diagrama_to_submission(
    submission_id: int,
    diagrama_xml: str,
    diagrama_pdf: Optional[str] = None,
    ruta_archivo: Optional[str] = None
) -> bool:
    """Agregar diagrama a un envío"""
    try:
        session = get_session()
        diagrama = SubmissionDiagramas(
            submission_id=submission_id,
            diagrama_xml=diagrama_xml,
            diagrama_pdf=diagrama_pdf,  # Base64 string
            ruta_archivo=ruta_archivo,
            fecha_generacion=datetime.utcnow()
        )
        session.add(diagrama)
        session.commit()
        session.close()
        return True
    except Exception as e:
        print(f"Error al agregar diagrama: {str(e)}")
        if 'session' in locals():
            session.rollback()
            session.close()
        return False


def create_notification(
    submission_id: int,
    tipo: str,
    estado: str = "enviada",
    mensaje: Optional[str] = None
) -> Optional[int]:
    """Crear registro de notificación"""
    try:
        session = get_session()
        notificacion = Notificacion(
            submission_id=submission_id,
            tipo=TipoNotificacion(tipo),
            estado=EstadoNotificacion(estado),
            fecha_envio=datetime.utcnow(),
            mensaje=mensaje
        )
        session.add(notificacion)
        session.commit()
        notif_id = notificacion.id
        session.close()
        return notif_id
    except Exception as e:
        print(f"Error al crear notificación: {str(e)}")
        if 'session' in locals():
            session.rollback()
            session.close()
        return None


def get_unread_notifications(limit: int = 50) -> List[Dict]:
    """Obtener notificaciones no leídas"""
    try:
        session = get_session()
        notificaciones = session.query(Notificacion).filter(
            Notificacion.estado == EstadoNotificacion.ENVIADA,
            Notificacion.tipo == TipoNotificacion.APP
        ).order_by(Notificacion.fecha_envio.desc()).limit(limit).all()
        
        result = []
        for notif in notificaciones:
            submission = session.query(Submission).filter(Submission.id == notif.submission_id).first()
            result.append({
                'id': notif.id,
                'submission_id': notif.submission_id,
                'cliente_nombre': submission.cliente_nombre if submission else 'N/A',
                'tipo': notif.tipo.value,
                'fecha_envio': notif.fecha_envio.isoformat() if notif.fecha_envio else None,
                'mensaje': notif.mensaje
            })
        
        session.close()
        return result
    except Exception as e:
        print(f"Error al obtener notificaciones: {str(e)}")
        return []


def mark_notification_read(notificacion_id: int) -> bool:
    """Marcar notificación como leída"""
    try:
        session = get_session()
        notificacion = session.query(Notificacion).filter(Notificacion.id == notificacion_id).first()
        
        if notificacion:
            notificacion.estado = EstadoNotificacion.LEIDA
            notificacion.fecha_lectura = datetime.utcnow()
            session.commit()
        
        session.close()
        return True
    except Exception as e:
        print(f"Error al marcar notificación como leída: {str(e)}")
        if 'session' in locals():
            session.rollback()
            session.close()
        return False


def get_submission_stats() -> Dict:
    """Obtener estadísticas de envíos"""
    try:
        session = get_session()
        
        total = session.query(Submission).count()
        pendientes = session.query(Submission).filter(Submission.estado == EstadoSubmission.PENDIENTE).count()
        en_revision = session.query(Submission).filter(Submission.estado == EstadoSubmission.EN_REVISION).count()
        aprobados = session.query(Submission).filter(Submission.estado == EstadoSubmission.APROBADO).count()
        rechazados = session.query(Submission).filter(Submission.estado == EstadoSubmission.RECHAZADO).count()
        
        session.close()
        
        return {
            'total': total,
            'pendientes': pendientes,
            'en_revision': en_revision,
            'aprobados': aprobados,
            'rechazados': rechazados
        }
    except Exception as e:
        print(f"Error al obtener estadísticas: {str(e)}")
        return {
            'total': 0,
            'pendientes': 0,
            'en_revision': 0,
            'aprobados': 0,
            'rechazados': 0
        }


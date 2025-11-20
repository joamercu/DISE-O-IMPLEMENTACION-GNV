"""
Sistema de Notificaciones
Envío de emails y gestión de notificaciones en la aplicación
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional, Dict
try:
    from email_validator import validate_email, EmailNotValidError
    EMAIL_VALIDATOR_AVAILABLE = True
except ImportError:
    EMAIL_VALIDATOR_AVAILABLE = False
    # Función dummy si no está disponible
    def validate_email(email):
        if '@' not in email:
            raise ValueError("Email inválido")
        return {'email': email}

from config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, ADMIN_EMAIL
from database import create_notification, get_submission_by_id


def send_email_notification(submission_id: int, cliente_nombre: str, usuario_cliente: str) -> bool:
    """
    Enviar email de notificación al administrador cuando un cliente envía datos
    
    Args:
        submission_id: ID del envío
        cliente_nombre: Nombre del cliente
        usuario_cliente: Usuario que envió los datos
    
    Returns:
        True si se envió correctamente, False en caso contrario
    """
    try:
        # Validar configuración de email
        if not SMTP_USER or not SMTP_PASSWORD or not ADMIN_EMAIL:
            print("⚠️ Configuración de email incompleta. No se enviará email.")
            return False
        
        # Validar email del administrador
        if EMAIL_VALIDATOR_AVAILABLE:
            try:
                validate_email(ADMIN_EMAIL)
            except EmailNotValidError:
                print(f"⚠️ Email del administrador inválido: {ADMIN_EMAIL}")
                return False
        else:
            # Validación básica si email-validator no está disponible
            if '@' not in ADMIN_EMAIL or '.' not in ADMIN_EMAIL.split('@')[1]:
                print(f"⚠️ Email del administrador parece inválido: {ADMIN_EMAIL}")
                return False
        
        # Obtener datos del envío
        submission = get_submission_by_id(submission_id)
        if not submission:
            print(f"⚠️ No se encontró el envío {submission_id}")
            return False
        
        # Crear mensaje
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"📋 Nuevo Envío de Datos - {cliente_nombre}"
        msg['From'] = SMTP_USER
        msg['To'] = ADMIN_EMAIL
        
        # Crear contenido HTML del email
        fecha_envio = datetime.fromisoformat(submission['fecha_envio']).strftime("%d/%m/%Y %H:%M:%S") if submission['fecha_envio'] else "N/A"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                }}
                .header {{
                    background-color: #2AA1FF;
                    color: white;
                    padding: 20px;
                    border-radius: 5px 5px 0 0;
                    margin: -20px -20px 20px -20px;
                }}
                .content {{
                    padding: 20px 0;
                }}
                .info-box {{
                    background-color: #f4f4f4;
                    padding: 15px;
                    border-left: 4px solid #2AA1FF;
                    margin: 15px 0;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 24px;
                    background-color: #2AA1FF;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    font-size: 12px;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⛽ Nuevo Envío de Datos - Sistema GNV</h1>
                </div>
                <div class="content">
                    <p>Se ha recibido un nuevo envío de datos del cliente:</p>
                    
                    <div class="info-box">
                        <strong>Cliente:</strong> {cliente_nombre}<br>
                        <strong>Usuario:</strong> {usuario_cliente}<br>
                        <strong>Fecha de Envío:</strong> {fecha_envio}<br>
                        <strong>ID de Envío:</strong> #{submission_id}<br>
                        <strong>Estado:</strong> Pendiente
                    </div>
                    
                    <p>El envío incluye:</p>
                    <ul>
                        <li>✅ Datos del cliente</li>
                        {'<li>✅ Resultados de cálculos</li>' if submission.get('calculos') else ''}
                        {'<li>✅ Diagrama generado</li>' if submission.get('diagramas') else ''}
                    </ul>
                    
                    <p>Por favor, revise el envío en el Panel de Administración de la aplicación.</p>
                    
                    <div class="footer">
                        <p>Este es un mensaje automático del Sistema de Cálculos GNV - WELDTECH SOLUTIONS</p>
                        <p>No responda a este email.</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Versión texto plano
        text_content = f"""
        Nuevo Envío de Datos - Sistema GNV
        
        Se ha recibido un nuevo envío de datos del cliente:
        
        Cliente: {cliente_nombre}
        Usuario: {usuario_cliente}
        Fecha de Envío: {fecha_envio}
        ID de Envío: #{submission_id}
        Estado: Pendiente
        
        Por favor, revise el envío en el Panel de Administración de la aplicación.
        
        ---
        Este es un mensaje automático del Sistema de Cálculos GNV - WELDTECH SOLUTIONS
        """
        
        # Agregar contenido al mensaje
        part1 = MIMEText(text_content, 'plain', 'utf-8')
        part2 = MIMEText(html_content, 'html', 'utf-8')
        
        msg.attach(part1)
        msg.attach(part2)
        
        # Enviar email
        try:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)
            
            # Registrar notificación en BD
            create_notification(
                submission_id=submission_id,
                tipo="email",
                estado="enviada",
                mensaje=f"Email enviado a {ADMIN_EMAIL}"
            )
            
            return True
        except smtplib.SMTPException as e:
            print(f"❌ Error SMTP al enviar email: {str(e)}")
            # Registrar notificación fallida
            create_notification(
                submission_id=submission_id,
                tipo="email",
                estado="fallida",
                mensaje=f"Error al enviar email: {str(e)}"
            )
            return False
            
    except Exception as e:
        print(f"❌ Error al enviar email: {str(e)}")
        # Registrar notificación fallida
        try:
            create_notification(
                submission_id=submission_id,
                tipo="email",
                estado="fallida",
                mensaje=f"Error: {str(e)}"
            )
        except:
            pass
        return False


def create_app_notification(submission_id: int, cliente_nombre: str, usuario_cliente: str) -> Optional[int]:
    """
    Crear notificación en la aplicación
    
    Args:
        submission_id: ID del envío
        cliente_nombre: Nombre del cliente
        usuario_cliente: Usuario que envió los datos
    
    Returns:
        ID de la notificación creada o None si hay error
    """
    try:
        mensaje = f"Nuevo envío de {cliente_nombre} (Usuario: {usuario_cliente})"
        notif_id = create_notification(
            submission_id=submission_id,
            tipo="app",
            estado="enviada",
            mensaje=mensaje
        )
        return notif_id
    except Exception as e:
        print(f"❌ Error al crear notificación en app: {str(e)}")
        return None


def get_unread_notifications(limit: int = 50) -> list:
    """Obtener notificaciones no leídas de la aplicación"""
    from database import get_unread_notifications as db_get_unread
    return db_get_unread(limit)


def mark_notification_read(notificacion_id: int) -> bool:
    """Marcar notificación como leída"""
    from database import mark_notification_read as db_mark_read
    return db_mark_read(notificacion_id)


def send_notifications(submission_id: int, cliente_nombre: str, usuario_cliente: str) -> Dict[str, bool]:
    """
    Enviar todas las notificaciones (email + app) cuando un cliente envía datos
    
    Returns:
        Dict con el estado de cada tipo de notificación
    """
    results = {
        'email': False,
        'app': False
    }
    
    # Enviar email
    results['email'] = send_email_notification(submission_id, cliente_nombre, usuario_cliente)
    
    # Crear notificación en app
    notif_id = create_app_notification(submission_id, cliente_nombre, usuario_cliente)
    results['app'] = notif_id is not None
    
    return results


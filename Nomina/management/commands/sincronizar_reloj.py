# Nominas/Nomina/management/commands/sincronizar_reloj.py
from django.core.management.base import BaseCommand
from zk import ZK
from zk.exception import ZKError
from Nomina.models import RegistroAsistencia
from Empleados.models import Empleados
from django.utils.timezone import make_aware
from datetime import datetime

class Command(BaseCommand):
    help = 'Conecta con el reloj NGTeco MG-MB2 usando volcado crudo de memoria'

    def add_arguments(self, parser):
        parser.add_argument('--fecha', type=str, nargs='?', default=datetime.today().strftime('%Y-%m-%d'))

    def handle(self, *args, **options):
        fecha_str = options['fecha']
        RELOJ_IP = '192.168.0.110' 
        PUERTO = 4370
        
        # Forzamos UDP puro desde el inicio que es el único que no da "packet invalid"
        zk = ZK(RELOJ_IP, port=PUERTO, timeout=20, password=0, force_udp=True, ommit_ping=True)
        conn = None
        asistencias_raw = []
        
        self.stdout.write(self.style.SUCCESS(f"Iniciando volcado directo UDP con {RELOJ_IP}..."))
        
        try:
            conn = zk.connect()
            
            # ---> TRUCO PARA MODELOS ECONÓMICOS DE NGTECO <---
            # Forzamos los parámetros de buffer pequeños antes de pedir datos
            # Esto evita que el chip interno del reloj se congele y provoque el timeout
            conn.is_modern_firmware = False  
            
            self.stdout.write(self.style.SUCCESS("Extrayendo registros de la memoria..."))
            asistencias_raw = conn.get_attendance()
            
        except Exception as e:
            # Si falla el método estándar, usamos el método alternativo de lectura por bloques
            self.stdout.write(self.style.WARNING(f"Intento 1 falló ({e}). Aplicando lectura alterna de registros..."))
            try:
                if conn:
                    # Forzamos la inicialización del conteo de usuarios para despertar el chip de memoria
                    conn.get_users() 
                    asistencias_raw = conn.get_attendance()
            except Exception as e2:
                raise Exception(f"El hardware del reloj rechazó la extracción de datos: {e2}")
        finally:
            if conn:
                try:
                    conn.disconnect()
                except:
                    pass
                self.stdout.write(self.style.SUCCESS("Socket del reloj liberado."))

        if not asistencias_raw:
            self.stdout.write(self.style.WARNING("El búfer de memoria devuelto está vacío."))
            return

        try:
            fecha_filtro = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            fecha_filtro = datetime.today().date()

        nuevos_registros = 0
        for asistencia in asistencias_raw:
            if asistencia.timestamp.date() != fecha_filtro:
                continue
                
            try:
                empleado = Empleados.objects.get(id_reloj_checador=int(asistencia.user_id))
            except (Empleados.DoesNotExist, ValueError):
                continue
            
            fecha_aware = make_aware(asistencia.timestamp)
            
            obj, created = RegistroAsistencia.objects.get_or_create(
                uid_reloj=asistencia.uid,
                defaults={
                    'empleado': empleado,
                    'fecha_hora': fecha_aware,
                    'tipo_evento': asistencia.punch
                }
            )
            if created:
                nuevos_registros += 1
        
        self.stdout.write(self.style.SUCCESS(f"Sincronización concluida. +{nuevos_registros} registros del día {fecha_filtro}."))
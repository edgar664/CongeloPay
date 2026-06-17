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
        
        # MEJORA 1: Bajamos el timeout a 7 segundos estrictos.
        # Quitamos ommit_ping=True para forzar un ping de red rápido antes de comprometer los sockets UDP.
        zk = ZK(RELOJ_IP, port=PUERTO, timeout=7, password=0, force_udp=True, ommit_ping=False)
        conn = None
        asistencias_raw = []
        
        self.stdout.write(self.style.SUCCESS(f"Iniciando volcado directo UDP con {RELOJ_IP}..."))
        
        try:
            conn = zk.connect()
            
            # TRUCO NGTeco: Forzamos parámetros legacy
            conn.is_modern_firmware = False  
            
            self.stdout.write(self.style.SUCCESS("Extrayendo registros de la memoria..."))
            asistencias_raw = conn.get_attendance()
            
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Intento 1 falló ({e}). Aplicando lectura alterna de registros..."))
            
            # MEJORA 2: Solo intentamos la lectura alterna SI logramos obtener una conexión inicial.
            # Si el error del Intento 1 fue que el reloj no existe en la red, conn es None y get_users() tirará un Crash feo.
            if conn is not None:
                try:
                    conn.get_users() # Despierta el chip de memoria
                    asistencias_raw = conn.get_attendance()
                except Exception as e2:
                    self.stdout.write(self.style.ERROR(f"Lectura alterna también falló: {e2}"))
            else:
                self.stdout.write(self.style.ERROR("No se pudo intentar la lectura alterna porque el socket principal nunca conectó."))
                
        finally:
            if conn:
                try:
                    # MEJORA 3: Forzar el cierre inmediato de buffers nativos de la librería pyzk
                    conn.enable_device() # Se asegura de dejar el reloj operativo para los empleados
                    conn.disconnect()
                except:
                    pass
                self.stdout.write(self.style.SUCCESS("Socket del reloj liberado de forma segura."))

        # Si no hay registros recuperados, salimos rápido antes de iterar la base de datos
        if not asistencias_raw:
            self.stdout.write(self.style.WARNING("El búfer de memoria devuelto está vacío o el dispositivo no respondió."))
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
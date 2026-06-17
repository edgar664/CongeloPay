from datetime import datetime

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny

# IMPORTANTE: Necesitamos call_command para activar tu script del reloj
from django.core.management import call_command 

from .models import Empleados, Nomina, DetalleNomina, RegistroAsistencia
from .serializers import NominaSerializer


class NominaViewSet(viewsets.ModelViewSet):
    queryset = Nomina.objects.all().order_by('-fecha_inicio')
    serializer_class = NominaSerializer
    permission_classes = [AllowAny]

    # Esta es tu lógica de cálculo movida aquí adentro
    @action(detail=True, methods=['post'])
    def calcular(self, request, pk=None):
        try:
            nomina = self.get_object()
            if nomina.estado == 'CERRADA':
                return Response(
                    {"error": "Esta nómina ya ha sido cerrada."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            nomina.cerrar_y_calcular() # Método de tu modelo
            serializer = NominaSerializer(nomina)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Nomina.DoesNotExist:
            return Response({"error": "Nómina no encontrada"}, status=status.HTTP_404_NOT_FOUND)


class CalcularNominaView(APIView):
    """
    Endpoint para disparar el cálculo de la nómina.
    POST /api/nominas/1/calcular/
    """
    def post(self, request, pk):
        try:
            nomina = Nomina.objects.get(pk=pk)
            
            if nomina.estado == 'CERRADA':
                return Response(
                    {"error": "Esta nómina ya ha sido cerrada y no puede recalcularse."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Ejecutamos el método que definimos en el model.py
            nomina.cerrar_y_calcular()
            
            serializer = NominaSerializer(nomina)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Nomina.DoesNotExist:
            return Response({"error": "Nómina no encontrada"}, status=status.HTTP_404_NOT_FOUND)
        

class SincronizarRelojAPIView(APIView):
    """
    Endpoint para sincronizar el reloj checador local filtrando por la fecha de React.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        # 1. Recuperamos la fecha que mandó React. Si no viene, usamos la de hoy.
        fecha_str = request.data.get('fecha', datetime.today().strftime('%Y-%m-%d'))
        
        try:
            # 2. Le pasamos la fecha al comando de consola como un argumento (--fecha)
            call_command('sincronizar_reloj', fecha=fecha_str)
            
            return Response({
                "status": "success", 
                "message": f"Reloj sincronizado correctamente para el día {fecha_str}"
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            # Si el comando falla por un timeout o desconexión del reloj, devolvemos un error controlado
            error_msg = str(e)
            if "timed out" in error_msg.lower():
                return Response({
                    "status": "error", 
                    "message": "El reloj checador no respondió a la solicitud (Timeout UDP)."
                }, status=status.HTTP_408_REQUEST_TIMEOUT)
                
            return Response({
                "status": "error", 
                "message": f"Fallo interno en la sincronización: {error_msg}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    # REGLA: Eliminamos el método get_extra_actions() de aquí ya que causaba el crash.
class ConsultarAsistenciasRelojView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # Capturamos la fecha que manda React (?fecha=2026-06-13)
        fecha_str = request.query_params.get('fecha', None)
        
        if not fecha_str:
            return Response([], status=200)
            
        try:
            # Convertimos el string a un objeto de fecha para filtrar
            fecha_filtro = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            
            # Buscamos las asistencias de ese día y extraemos solo los id de los empleados
            # 'empleado_id' es el nombre de la columna FK en tu BD
            asistencias_del_dia = RegistroAsistencia.objects.filter(
                fecha_hora__date=fecha_filtro
            ).values_list('empleado_id', flat=True).distinct()
            
            # Convertimos a lista normal de Python (ej: [1, 4, 12])
            lista_empleados_ids = list(asistencias_del_dia)
            
            return Response(lista_empleados_ids, status=200)
            
        except Exception as e:
            return Response({"error": str(e)}, status=400)
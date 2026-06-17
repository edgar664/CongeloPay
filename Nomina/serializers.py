from rest_framework import serializers, generics
from .models import Nomina, DetalleNomina, Empleados, RegistroAsistencia

class EmpleadoSimpleSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()

    class Meta:
        model = Empleados
        fields = ['id', 'nombre_completo', 'Puesto', 'grupo']

    def get_nombre_completo(self, obj):
        return f"{obj.nombre} {obj.apellido}"

class DetalleNominaSerializer(serializers.ModelSerializer):
    empleado = EmpleadoSimpleSerializer(read_only=True)
    
    class Meta:
        model = DetalleNomina
        fields = '__all__'

class NominaSerializer(serializers.ModelSerializer):
    # Esto permite que cuando consultes una nómina, veas a todos los empleados pagados dentro
    detalles = DetalleNominaSerializer(many=True, read_only=True)

    class Meta:
        model = Nomina
        fields = ['id', 'descripcion', 'fecha_inicio', 'fecha_fin', 'estado', 'detalles']


class AsistenciaSerializer(serializers.ModelSerializer):
    nombre_empleado = serializers.CharField(source='empleado.nombre', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_evento_display', read_only=True)

    class Meta:
        model = RegistroAsistencia
        fields = ['id', 'nombre_empleado', 'fecha_hora', 'tipo_display', 'tipo_evento']



class ListaAsistenciasAPIView(generics.ListAPIView):
    queryset = RegistroAsistencia.objects.all().order_by('-fecha_hora')
    serializer_class = AsistenciaSerializer
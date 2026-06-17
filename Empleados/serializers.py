from rest_framework import serializers
from .models import Empleados


class EmpleadoSerializer(serializers.ModelSerializer):
    nombre_supervisor = serializers.SerializerMethodField()
    nombre_puesto = serializers.SerializerMethodField()
    nombre_departamento = serializers.SerializerMethodField()


    class Meta:
        model = Empleados
        fields = '__all__' 
        read_only_fields = ('id_empleado',) 

    def get_nombre_supervisor(self, obj):
        try:
            # 1. Si tiene supervisor asignado y existe en la Base de Datos
            if obj.supervisor:
                return f"{obj.supervisor.nombre} {obj.supervisor.apellido}"
        except Empleados.DoesNotExist:
            # 2. Si el ID asignado no existe, buscamos si el ID propuesto coincide con un código de empleado conocido
            # O simplemente mostramos el ID faltante de forma limpia:
            return f"ID inexistente ({obj.supervisor_id})"
        
        # 3. Si de plano viene vacío o NULL en la BD
        return "Sin jefe asignado"
    def get_nombre_puesto(self, obj):
        try:
            # 1. Si tiene supervisor asignado y existe en la Base de Datos
            if obj.puesto:
                return f"{obj.puesto.nombre}"
        except Empleados.DoesNotExist:
            # 2. Si el ID asignado no existe, buscamos si el ID propuesto coincide con un código de empleado conocido
            # O simplemente mostramos el ID faltante de forma limpia:
            return f"ID inexistente ({obj.puesto_id})"
        
        # 3. Si de plano viene vacío o NULL en la BD
        return "Sin puesto asignado"
    def get_nombre_departamento(self, obj):
        try:
            # 1. Si tiene supervisor asignado y existe en la Base de Datos
            if obj.departamento:
                return f"{obj.departamento.nombre}"
        except Empleados.DoesNotExist:
            # 2. Si el ID asignado no existe, buscamos si el ID propuesto coincide con un código de empleado conocido
            # O simplemente mostramos el ID faltante de forma limpia:
            return f"ID inexistente ({obj.departamento_id})"
        
        # 3. Si de plano viene vacío o NULL en la BD
        return "Sin departamento asignado"
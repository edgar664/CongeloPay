from rest_framework import serializers
from .models import Proveedor, factura

class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = '__all__'

class FacturaSerializer(serializers.ModelSerializer):
    # 1. FORZAMOS a Django a recibir únicamente el ID numérico del proveedor en el POST/PUT
    proveedor = serializers.PrimaryKeyRelatedField(queryset=Proveedor.objects.all(), required=True)
    
    
    # 2. Tu campo personalizado para solucionar el listado en la tabla de React
    nombre_proveedor = serializers.SerializerMethodField()

    class Meta:
        model = factura  
        # Explicitamos los campos para asegurarnos de que no herede validaciones fantasma
        fields = [
            'id', 
            'proveedor', 
            'nombre_proveedor', 
            'movimiento', 
            'numero_factura', 
            'fecha_emision', 
            'fecha_vencimiento', 
            'monto_total'
        ]

    def get_nombre_proveedor(self, obj):
        # Evita crasheos si el proveedor fue eliminado de la BD
        proveedor = getattr(obj, 'proveedor', None)
        if proveedor:
            return getattr(proveedor, 'nombre', 'Sin nombre')
        return "Sin Proveedor asignado"


class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = factura  
        fields = '__all__'
from rest_framework import serializers
from . import models

# Forzamos la exportación vacía inicialmente
class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.producto
        fields = '__all__'
class MovimientosSerializer(serializers.ModelSerializer):
    nombre_producto = serializers.SerializerMethodField()
    nombre_almacen = serializers.SerializerMethodField()
    nombre_embace = serializers.SerializerMethodField()
    nombre_proveedor = serializers.SerializerMethodField()
    nombre_cliente = serializers.SerializerMethodField()
    class Meta:
        model = models.movimientos
        fields = '__all__'
    def get_nombre_producto(self, obj):
        producto = getattr(obj, 'producto', None)
        if producto:
            return getattr(producto, 'nombre', 'Sin nombre')
        return "Sin Producto asignado"
    def get_nombre_almacen(self, obj):
        almacen = getattr(obj, 'almacen', None)
        if almacen:
            return getattr(almacen, 'nombre', 'Sin nombre')
        return "Sin Almacén asignado"
    def get_nombre_embace(self, obj):
        embace = getattr(obj, 'embace', None)
        if embace:
            return getattr(embace, 'nombre', 'Sin nombre')
        return "Sin Embace asignado"
    def get_nombre_proveedor(self, obj):
        proveedor = getattr(obj, 'proveedor', None)
        if proveedor:
            return getattr(proveedor, 'nombre', 'Sin nombre')
        return "Sin Proveedor asignado"
    def get_nombre_cliente(self, obj):
        cliente = getattr(obj, 'cliente', None)
        if cliente:
            return getattr(cliente, 'nombre', 'Sin nombre')
        return "Sin Proveedor asignado"
    
class AlmacenSerializer(serializers.ModelSerializer):    
    class Meta:
        model = models.almacen
        fields = '__all__'
class EmbaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.embace
        fields = '__all__'      
class ConceptosSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.conceptos
        fields = '__all__'

# Ejemplo de validación en tu serializers.py utilizando IDs
def validate(self, data):
    concepto = data.get('concepto')
    tipo = data.get('tipo_movimiento')
    
    # Nos aseguramos de que el concepto no sea None antes de evaluar su ID
    if concepto:
        # Supongamos que en tu BD el ID de 'Compra' es 1
        if tipo == 'ENTRADA' and concepto.id == 1 and not data.get('proveedor'):
            raise serializers.ValidationError({
                "proveedor": "Las entradas por compra requieren asignar un proveedor."
            })
            
        # Supongamos que en tu BD el ID de 'Venta' es 4
        if tipo == 'SALIDA' and concepto.id == 4 and not data.get('cliente'):
            raise serializers.ValidationError({
                "cliente": "Las salidas por venta requieren asignar un cliente."
            })
            
    return data
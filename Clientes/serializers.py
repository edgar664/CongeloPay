from rest_framework import serializers
from .models import Cliente, factura_cliente, pago_cliente


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'
        
class FacturaClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = factura_cliente
        fields = '__all__'

class PagoClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = pago_cliente
        fields = '__all__'


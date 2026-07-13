from rest_framework import serializers
from .models import Proveedor
from rest_framework import serializers
from django.db import transaction
from decimal import Decimal
from .models import Factura, Proveedor
from Inventarios.models import Movimiento


class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = '__all__'

class FacturaProveedorSerializer(serializers.ModelSerializer):
    nombre_proveedor = serializers.ReadOnlyField(source='proveedor.nombre')
    # Recibe una lista de IDs de movimientos desde el frontend
    movimientos_ids = serializers.ListField(
        child=serializers.IntegerField(), 
        write_only=True, 
        required=False
    )
    # Permite capturar el precio acordado por kilo para calcular el total
    precio_por_kilo = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        write_only=True, 
        required=False,
        default=0.00
    )

    class Meta:
        model = Factura
        fields = [
            'id', 'proveedor', 'nombre_proveedor', 'numero', 'uuid', 
            'fecha', 'fecha_vencimiento', 'subtotal', 'iva', 'total', 
            'estatus', 'saldo_pendiente', 'concepto', 'observaciones',
            'movimientos_ids', 'precio_por_kilo', 'xml_file', 'pdf_file'
        ]
        # El backend calculará estos campos de forma segura, el frontend solo los lee
        read_only_fields = ['subtotal', 'iva', 'total', 'saldo_pendiente', 'estatus']

    def validate(self, data):
        # Evitar registrar el mismo número de factura para el mismo proveedor
        proveedor = data.get('proveedor')
        numero = data.get('numero')
        if Factura.objects.filter(proveedor=proveedor, numero=numero).exists():
            raise serializers.ValidationError({
                "numero": f"Ya existe la factura {numero} registrada para este proveedor."
            })
        return data

    def create(self, validated_data):
        movimientos_ids = validated_data.pop('movimientos_ids', [])
        precio_por_kilo = validated_data.pop('precio_por_kilo', Decimal('0.00'))
        
        with transaction.atomic():
            # 1. Crear la factura inicialmente en ceros
            factura = Factura.objects.create(**validated_data)
            
            # 2. Si se seleccionaron entradas (movimientos), calculamos los montos
            if movimientos_ids:
                movimientos_queryset = Movimiento.objects.filter(id__in=movimientos_ids)
                
                # Asociamos los movimientos a la factura
                factura.movimientos.set(movimientos_queryset)
                
                # Sumamos el total de kilos netos acumulados en esas entradas
                total_kilos = sum(Decimal(str(m.kilos_netos)) for m in movimientos_queryset)
                
                # Lógica financiera básica (Subtotal = Kilos * Precio)
                subtotal_calculado = total_kilos * precio_por_kilo
                iva_calculado = subtotal_calculado * Decimal('0.16') # Ajusta si manejas tasa 0% o 16%
                total_calculado = subtotal_calculado + iva_calculado
                
                # Asignamos los totales calculados y el saldo inicial de la deuda
                factura.subtotal = subtotal_calculado
                factura.iva = iva_calculado
                factura.total = total_calculado
                factura.saldo_pendiente = total_calculado
                factura.save()
            
            return factura
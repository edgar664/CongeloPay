from rest_framework import serializers
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from .models import Movimiento, StockActual, almacen, embace, tarima, Concepto, producto
from rest_framework import serializers
from .models import producto, almacen, Concepto, embace, tarima
# Nota: Si Clientes y Proveedores están en otra app (ej. Ventas/Personal), 
# impórtalos desde allá. Aquí asumimos que están accesibles.
from Proveedores.models import Proveedor
from Clientes.models import Cliente 
from decimal import Decimal

class ProductoLookupSerializer(serializers.ModelSerializer):
    class Meta:
        model = producto
        fields = ['id', 'nombre']

class AlmacenLookupSerializer(serializers.ModelSerializer):
    class Meta:
        model = almacen
        fields = ['id', 'nombre', 'descripcion']

class ConceptoLookupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Concepto
        fields = ['id', 'nombre']

class EmbaceLookupSerializer(serializers.ModelSerializer):
    class Meta:
        model = embace
        fields = ['id', 'nombre', 'peso']

class TarimaLookupSerializer(serializers.ModelSerializer):
    class Meta:
        model = tarima
        fields = ['id', 'nombre', 'peso']

class ProveedorLookupSerializer(serializers.ModelSerializer):
    # Usamos un campo calculado por si tu modelo usa 'razon_social' o 'nombre'
    nombre = serializers.SerializerMethodField()

    class Meta:
        model = Proveedor
        fields = ['id', 'nombre']

    def get_nombre(self, obj):
        return getattr(obj, 'nombre', getattr(obj, 'razon_social', f"Proveedor #{obj.id}"))

class ClienteLookupSerializer(serializers.ModelSerializer):
    nombre = serializers.SerializerMethodField()

    class Meta:
        model = Cliente
        fields = ['id', 'nombre']

    def get_nombre(self, obj):
        return getattr(obj, 'nombre', getattr(obj, 'razon_social', f"Cliente #{obj.id}"))
class MovimientoSerializer(serializers.ModelSerializer):
    nombre_producto = serializers.ReadOnlyField(source='producto.nombre')
    nombre_concepto = serializers.ReadOnlyField(source='concepto.nombre')
    nombre_embace = serializers.ReadOnlyField(source='embace.nombre')

    origen_modelo = serializers.SerializerMethodField()
    destino_modelo = serializers.SerializerMethodField()
    nombre_origen = serializers.SerializerMethodField()
    nombre_destino = serializers.SerializerMethodField()

    materia_prima_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Movimiento
        fields = [
            'id', 'producto', 'nombre_producto', 'concepto', 'nombre_concepto', 
            'lote', 'lote_origen', 'unidades', 
            'kilos_brutos', 'kilos_netos', 'embace', 'nombre_embace', 'tarima', 
            'observaciones', 'origen_modelo', 'origen_id', 'nombre_origen',
            'destino_modelo', 'destino_id', 'nombre_destino', 'fecha', 'hora',
            'materia_prima_id' 
        ]
        read_only_fields = ['kilos_netos']

    def get_origen_modelo(self, obj):
        return obj.origen_content_type.model if obj.origen_content_type else None

    def get_destino_modelo(self, obj):
        return obj.destino_content_type.model if obj.destino_content_type else None

    def get_nombre_origen(self, obj):
        return str(obj.origen) if obj.origen else "Desconocido"

    def get_nombre_destino(self, obj):
        return str(obj.destino) if obj.destino else "Desconocido"

    def validate(self, data):
        unidades = data.get('unidades', 0)
        kilos_brutos = data.get('kilos_brutos', 0)
        id_envase = data.get('embace')
        id_tarima = data.get('tarima')

        peso_tara = 0
        if id_envase:
            peso_tara += unidades * id_envase.peso
        if id_tarima:
            peso_tara += id_tarima.peso

        data['kilos_netos'] = kilos_brutos - peso_tara
        if data['kilos_netos'] < 0:
            raise serializers.ValidationError({"kilos_brutos": "Los kilos netos calculados no pueden ser menores a cero. Revisa los pesos."})

        initial_data = getattr(self, 'initial_data', {}) or {}
        origen_modelo_raw = initial_data.get('origen_modelo') or ''
        origen_modelo_name = origen_modelo_raw.lower() if isinstance(origen_modelo_raw, str) else ''
        origen_id = initial_data.get('origen_id')
        
        if origen_modelo_name == 'almacen':
            if not origen_id:
                raise serializers.ValidationError({"origen_id": "El ID del almacén de origen es requerido."})

            stock = StockActual.objects.filter(
                producto=data['producto'],
                almacen_id=origen_id,
                lote=data['lote']
            ).first()

            if not stock:
                raise serializers.ValidationError({
                    "inventario": f"No existe registro de inventario para el lote {data['lote']} en el almacén especificado (Disponible: 0 unds / 0 kg)."
                })

            if stock.kilos_netos < data['kilos_netos'] or stock.unidades < unidades:
                raise serializers.ValidationError({
                    "inventario": f"Inventario insuficiente en el almacén de origen para el lote {data['lote']}. "
                                  f"Disponible: {stock.unidades} unds / {stock.kilos_netos} kg. "
                                  f"Solicitado: {unidades} unds / {data['kilos_netos']} kg."
                })

        return data

    def create(self, validated_data):
        initial_data = getattr(self, 'initial_data', {}) or {}
        
        origen_modelo_raw = initial_data.get('origen_modelo') or ''
        destino_modelo_raw = initial_data.get('destino_modelo') or ''
        
        origen_modelo = origen_modelo_raw.lower() if isinstance(origen_modelo_raw, str) else ''
        destino_modelo = destino_modelo_raw.lower() if isinstance(destino_modelo_raw, str) else ''
        
        origen_id = initial_data.get('origen_id', None)
        destino_id = initial_data.get('destino_id', None)

        materia_prima_id = validated_data.pop('materia_prima_id', None) 
        lote_origen_str = validated_data.get('lote_origen', None)      

        validated_data.pop('origen_modelo', None)
        validated_data.pop('origen_id', None)
        validated_data.pop('destino_modelo', None)
        validated_data.pop('destino_id', None)

        try:
            origen_ct = ContentType.objects.get(model=origen_modelo) if origen_modelo else None
            destino_ct = ContentType.objects.get(model=destino_modelo) if destino_modelo else None
        except ContentType.DoesNotExist:
            raise serializers.ValidationError({"error": "El modelo de origen o destino especificado no es válido."})

        with transaction.atomic():
            movimiento = Movimiento.objects.create(
                origen_content_type=origen_ct,
                origen_id=origen_id,
                destino_content_type=destino_ct,
                destino_id=destino_id,
                **validated_data
            )

            producto_obj = validated_data['producto']
            lote_str = validated_data['lote']
            unidades_mov = validated_data['unidades']
            kilos_netos_mov = validated_data['kilos_netos']

            # A. Si el origen es un ALMACÉN, RESTAMOS de su stock actual
            if origen_modelo == 'almacen' and origen_id:
                producto_a_descontar_id = materia_prima_id if materia_prima_id else producto_obj.id
                lote_a_descontar = lote_origen_str if lote_origen_str else lote_str

                stock_origen = StockActual.objects.filter(
                    producto_id=producto_a_descontar_id,
                    almacen_id=origen_id,
                    lote=lote_a_descontar
                ).first()
                
                if stock_origen:
                    stock_origen.unidades -= unidades_mov
                    stock_origen.kilos_netos -= kilos_netos_mov
                    
                    # 💡 SOLUCIÓN: Si tras el traspaso el stock queda vacío, eliminamos el registro
                    if stock_origen.unidades <= 0 or stock_origen.kilos_netos <= 0:
                        stock_origen.delete()
                    else:
                        stock_origen.save()
                else:
                    raise serializers.ValidationError({
                        "inventario": f"No hay inventario para la Materia Prima con lote '{lote_a_descontar}' en el almacén de origen asignado."
                    })

            # B. Si el destino es un ALMACÉN, SUMAMOS a su stock actual
            if destino_modelo == 'almacen' and destino_id:
                stock_destino, created = StockActual.objects.get_or_create(
                    producto=producto_obj,
                    almacen_id=destino_id,
                    lote=lote_str,
                    defaults={'unidades': 0, 'kilos_netos': 0.00}
                )
                stock_destino.unidades += unidades_mov
                
                stock_destino.kilos_netos = float(Decimal(str(stock_destino.kilos_netos)) + Decimal(str(kilos_netos_mov)))
                stock_destino.save()

            return movimiento
class StockActualSerializer(serializers.ModelSerializer):
    # 👈 Traemos los nombres de los modelos relacionados
    nombre_producto = serializers.ReadOnlyField(source='producto.nombre')
    nombre_almacen = serializers.ReadOnlyField(source='almacen.nombre')

    class Meta:
        model = StockActual
        fields = ['id', 'producto', 'nombre','nombre_producto', 'almacen', 'nombre_almacen', 'lote', 'kilos_netos', 'unidades']

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Movimiento, StockActual
from .serializers import MovimientoSerializer
from rest_framework.generics import ListAPIView
from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.permissions import AllowAny # O IsAuthenticated si usas tokens
from .models import producto, almacen, Concepto, embace, tarima
from Proveedores.models import Proveedor
from Clientes.models import Cliente 

from .serializers import (
    ProductoLookupSerializer, AlmacenLookupSerializer, ConceptoLookupSerializer,
    EmbaceLookupSerializer, TarimaLookupSerializer, ProveedorLookupSerializer, ClienteLookupSerializer, StockActualSerializer
)

class ProductoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = producto.objects.all()
    serializer_class = ProductoLookupSerializer
    permission_classes = [AllowAny] # Ajusta según tu seguridad

class AlmacenViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = almacen.objects.all()
    serializer_class = AlmacenLookupSerializer
    permission_classes = [AllowAny]

class ConceptoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Concepto.objects.all()
    serializer_class = ConceptoLookupSerializer
    permission_classes = [AllowAny]

class EmbaceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = embace.objects.all()
    serializer_class = EmbaceLookupSerializer
    permission_classes = [AllowAny]

class TarimaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = tarima.objects.all()
    serializer_class = TarimaLookupSerializer
    permission_classes = [AllowAny]

class ProveedorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorLookupSerializer
    permission_classes = [AllowAny]

class ClienteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteLookupSerializer
    permission_classes = [AllowAny]
class MovimientoViewSet(viewsets.ModelViewSet):
    """
    Endpoint para crear y listar los movimientos del almacén.
    - POST: Registra un movimiento (compra, venta, traspaso) y actualiza el stock de forma automática.
    - GET: Obtiene el historial de transacciones para auditoría.
    """
    queryset = Movimiento.objects.all().order_by('-fecha', '-hora')
    serializer_class = MovimientoSerializer
    permission_classes = [AllowAny] # 👈 CAMBIA ESTO TEMPORALMENTE
    
    # Opcional: Bloqueamos PUT, PATCH y DELETE de movimientos individuales
    # En inventarios, un movimiento guardado NO se debe editar ni borrar por seguridad; 
    # si hubo un error, se debe capturar un movimiento de ajuste o contra-movimiento.
    def destroy(self, request, *args, **kwargs):
        return Response({"error": "No se permite eliminar movimientos históricos."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
    def update(self, request, *args, **kwargs):
        return Response({"error": "No se permite modificar movimientos históricos."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class StockActualListView(APIView):
    """
    Endpoint para consultar la 'Foto' actual del inventario.
    Permite filtrar los resultados usando parámetros en la URL (Query Params).
    Ejemplo: /api/inventarios/stock/?almacen_id=1&producto_id=3
    """
    permission_classes = [AllowAny]
    nombre_producto = serializers.ReadOnlyField(source='producto.nombre')

    def get(self, request):
        # Empezamos con todos los registros de stock que tengan existencias reales
        # (Filtramos > 0 para no mostrar filas vacías de lotes que ya se agotaron)
        queryset = StockActual.objects.filter(kilos_netos__gt=0)

        # Capturamos filtros desde la URL si es que el frontend los envía
        almacen_id = request.query_params.get('almacen_id')
        producto_id = request.query_params.get('producto_id')
        lote = request.query_params.get('lote')

        if almacen_id:
            queryset = queryset.filter(almacen_id=almacen_id)
        if producto_id:
            queryset = queryset.filter(producto_id=producto_id)
        if lote:
            queryset = queryset.filter(lote__icontains=lote)

        # Mapeamos los datos manualmente a un JSON limpio y rápido
        data = [
            {
                "id": stock.id,
                "producto_id": stock.producto.id,
                "producto_nombre": stock.producto.nombre,
                "almacen_id": stock.almacen.id,
                "almacen_nombre": stock.almacen.nombre,
                "lote": stock.lote,
                "unidades": stock.unidades,
                "kilos_netos": float(stock.kilos_netos)
            }
            for stock in queryset
        ]

        return Response(data, status=status.HTTP_200_OK)

# En tu views.py
def get(self, request):
    stocks = StockActual.objects.all()
    serializer = StockActualSerializer(stocks, many=True)
    return Response(serializer.data)
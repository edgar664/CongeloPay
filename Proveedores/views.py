from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Factura, Proveedor
from .serializers import ProveedorSerializer
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Factura, Proveedor
from .serializers import FacturaProveedorSerializer, PagoSerializer
from Inventarios.models import Movimiento
from Inventarios.serializers import MovimientoSerializer

# Create your views here.
class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
    permission_classes = [AllowAny]

class FacturaProveedorViewSet(viewsets.ModelViewSet):
    queryset = Factura.objects.all().order_by('-fecha')
    serializer_class = FacturaProveedorSerializer
    permission_classes = [AllowAny] # Actívalo si usas autenticación

    @action(detail=False, methods=['get'], url_path='entradas-pendientes/(?P<proveedor_id>[0-9]+)')
    def entradas_pendientes(self, request, proveedor_id=None):
        """
        Endpoint que devuelve las entradas de almacén (compras) de un proveedor específico
        que NO han sido ligadas a ninguna factura todavía.
        Ruta: /api/facturas/entradas-pendientes/<proveedor_id>/
        """
        try:
            # Filtramos movimientos donde:
            # 1. El origen_id corresponda al proveedor seleccionado
            # 2. El origen_content_type sea de tipo 'proveedor'
            # 3. No formen parte de ninguna factura actualmente (factura__isnull=True)
            entradas = Movimiento.objects.filter(
                origen_id=proveedor_id,
                origen_content_type__model='proveedor',
                factura__isnull=True 
            )
            
            # Reutilizamos tu MovimientoSerializer para mandar los datos limpios al Front
            serializer = MovimientoSerializer(entradas, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": f"Error al consultar entradas pendientes: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
class PagoViewSet(viewsets.ModelViewSet):
    queryset = Factura.objects.all()
    serializer_class = PagoSerializer
    permission_classes = [AllowAny]  # Cambia a IsAuthenticated si quieres proteger este endpoint

    @action(detail=True, methods=['post'], url_path='registrar-pago')
    def registrar_pago(self, request, pk=None):
        """
        Endpoint para registrar un pago parcial o total de una factura.
        Se espera un JSON con el monto del pago.
        """
        try:
            factura = self.get_object()
            monto_pago = request.data.get('monto_pago')

            if monto_pago is None:
                return Response({"error": "Se requiere el monto del pago."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                monto_pago = float(monto_pago)
            except ValueError:
                return Response({"error": "El monto del pago debe ser un número válido."}, status=status.HTTP_400_BAD_REQUEST)

            if monto_pago <= 0:
                return Response({"error": "El monto del pago debe ser mayor a cero."}, status=status.HTTP_400_BAD_REQUEST)

            # Actualizamos el saldo pendiente
            factura.saldo_pendiente -= monto_pago

            # Validamos que el saldo pendiente no sea negativo
            if factura.saldo_pendiente < 0:
                return Response({"error": "El monto del pago excede el saldo pendiente de la factura."}, status=status.HTTP_400_BAD_REQUEST)

            # Actualizamos el estatus de la factura según el nuevo saldo pendiente
            if factura.saldo_pendiente == 0:
                factura.estatus = 'PAGADA'
            elif factura.saldo_pendiente < factura.total:
                factura.estatus = 'PARCIAL'
            else:
                factura.estatus = 'PENDIENTE'

            factura.save()

            serializer = self.get_serializer(factura)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"Error al registrar el pago: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Cliente, factura_cliente, pago_cliente
from .serializers import ClienteSerializer, FacturaClienteSerializer, PagoClienteSerializer

# Create your views here.
class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [AllowAny]

class FacturaClienteViewSet(viewsets.ModelViewSet):
    queryset = factura_cliente.objects.all()
    serializer_class = FacturaClienteSerializer
    permission_classes = [AllowAny]

class PagoClienteViewSet(viewsets.ModelViewSet):
    queryset = pago_cliente.objects.all()
    serializer_class = PagoClienteSerializer
    permission_classes = [AllowAny]

from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Proveedor, factura, pago
from .serializers import ProveedorSerializer, FacturaSerializer, PagoSerializer

# Create your views here.
class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
    permission_classes = [AllowAny]

class FacturaViewSet(viewsets.ModelViewSet):
    queryset = factura.objects.all()  # Reemplaza con el modelo Factura real
    serializer_class = FacturaSerializer  # Reemplaza con el serializer Factura real
    permission_classes = [AllowAny]

class PagoViewSet(viewsets.ModelViewSet):
    queryset = pago.objects.all()  # Reemplaza con el modelo Pago real
    serializer_class = PagoSerializer  # Reemplaza con el serializer Pago real
    permission_classes = [AllowAny]

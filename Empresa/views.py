from django.shortcuts import render
# CORRECCIÓN 1: Importar Response correcto de DRF
from rest_framework.response import Response 
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action

# CORRECCIÓN 2: Importar la clase del Modelo específica de tu archivo models.py
from .models import empresa
from Empresa.serializers import EmpresaSerializer

class EmpresaViewSet(viewsets.ModelViewSet):
    # Ahora sí apunta a la tabla física en la Base de Datos
    queryset = empresa.objects.all()
    serializer_class = EmpresaSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'], url_path='principal')
    def principal(self, request):
        empresas = empresa.objects.first() 
        if not empresas:
            return Response({
                "nombre": "PRODUCTOS SNZ S.A. DE C.V.",
                "rfc": "PSNZ900101ABC",
                "direccion": "Av. de la Industria #450",
                "telefono": "+52 (351) 123-4567",
                "correo": "finanzas@snz.com"
            }, status=200) 
        
        serializer = self.get_serializer(empresas)
        return Response(serializer.data)
from django.shortcuts import render
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Sum, F
from django.http import JsonResponse
from django.views import View
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny


# Modelos y Serializadores unificados
from .models import producto, movimientos, almacen, embace, conceptos
from .serializers import ProductoSerializer, MovimientosSerializer, AlmacenSerializer, EmbaceSerializer, ConceptosSerializer

# views.py (MAL)
class ProductoViewSet(viewsets.ModelViewSet):
    queryset = producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend] # Nota: Asegúrate de que use "filter_backends" en plural
    filterset_fields = ['categoria'] # <-- AQUÍ ESTÁ EL CAMPO QUE NO EXISTE

class MovimientoInventarioViewSet(viewsets.ModelViewSet):
    queryset = movimientos.objects.all()
    serializer_class = MovimientosSerializer 
    permission_classes = [AllowAny] 
    filter_backends = [DjangoFilterBackend]
    
    # CORRECCIÓN AQUÍ: Cambiar 'tipo' por 'tipo_movimiento'
    filterset_fields = ['producto', 'tipo_movimiento', 'usuario', 'fecha']

    def get_queryset(self):
        # Mantenemos el resguardo seguro para usuarios anónimos que pusimos antes
        if self.request.user.is_anonymous:
            return movimientos.objects.all().order_by('-fecha')
            
        return movimientos.objects.filter(
            usuario=self.request.user
        ).order_by('-fecha')
    
class AlmacenViewSet(viewsets.ModelViewSet):
    queryset = almacen.objects.all()
    serializer_class = AlmacenSerializer
    permission_classes = [AllowAny]


class EmbaceViewSet(viewsets.ModelViewSet):
    queryset = embace.objects.all()
    serializer_class = EmbaceSerializer
    permission_classes = [AllowAny]

class ConceptosViewSet(viewsets.ModelViewSet):
    queryset = conceptos.objects.all()
    serializer_class = ConceptosSerializer
    permission_classes = [AllowAny]
from django.urls import include, path
from rest_framework.routers import DefaultRouter

# CORRECCIÓN: Asegúrate de importar ConceptosViewSet aquí
from .views import ProductoViewSet, MovimientoInventarioViewSet, AlmacenViewSet, EmbaceViewSet, ConceptosViewSet

router = DefaultRouter()

router.register(r'productos', ProductoViewSet, basename='producto')
router.register(r'movimientos', MovimientoInventarioViewSet, basename='movimiento')
router.register(r'almacenes', AlmacenViewSet, basename='almacen')
router.register(r'embaces', EmbaceViewSet, basename='embace')
router.register(r'entradas', MovimientoInventarioViewSet, basename='entrada')

# CORRECCIÓN: Apuntar al ViewSet correcto de Conceptos
router.register(r'conceptos', ConceptosViewSet, basename='concepto') 

urlpatterns = [
    path('apiInv/', include(router.urls)),
]
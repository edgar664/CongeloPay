from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MovimientoViewSet, StockActualListView,
    ProductoViewSet, AlmacenViewSet, ConceptoViewSet,
    EmbaceViewSet, TarimaViewSet, ProveedorViewSet, ClienteViewSet
)

# El router unifica todos los ViewSets
router = DefaultRouter()
router.register(r'movimientos', MovimientoViewSet, basename='movimiento')
router.register(r'productos', ProductoViewSet, basename='producto')
router.register(r'almacenes', AlmacenViewSet, basename='almacen')
router.register(r'conceptos', ConceptoViewSet, basename='concepto')
router.register(r'embaces', EmbaceViewSet, basename='embace')
router.register(r'tarimas', TarimaViewSet, basename='tarima')
router.register(r'proveedores', ProveedorViewSet, basename='proveedor')
router.register(r'clientes', ClienteViewSet, basename='cliente')

urlpatterns = [
    # Endpoints del router: /apiInv/productos/, /apiInv/almacenes/, etc.
    path('apiInv/', include(router.urls)),
    
    # Endpoint manual
    path('apiInv/stockActual/', StockActualListView.as_view(), name='stockActual'),
]
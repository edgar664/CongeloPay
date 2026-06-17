# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProveedorViewSet, FacturaViewSet, PagoViewSet  # Reemplaza con los ViewSets reales de Factura y Pago

router = DefaultRouter()
# Esto crea las rutas para GET (listar) y POST (crear - EL QUE TE DABA 404)
router.register(r'proveedores', ProveedorViewSet, basename='proveedor')
router.register(r'facturas', FacturaViewSet, basename='factura')  # Reemplaza con el ViewSet real de Factura
router.register(r'pagos', PagoViewSet, basename='pago')  # Reemplaza con el ViewSet real de Pago

urlpatterns = [
    # Esto incluye todas las rutas del router bajo el prefijo api/
    path('apiProv/', include(router.urls)),
]
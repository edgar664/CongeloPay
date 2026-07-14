# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FacturaProveedorViewSet, ProveedorViewSet, PagoViewSet

router = DefaultRouter()
# Esto crea las rutas para GET (listar) y POST (crear - EL QUE TE DABA 404)
router.register(r'proveedores', ProveedorViewSet, basename='proveedor')
router.register(r'facturas', FacturaProveedorViewSet, basename='facturaProveedor')
router.register(r'pagos', PagoViewSet, basename='pago')  # Agrega el ViewSet de pagos al router

urlpatterns = [
    # Esto incluye todas las rutas del router bajo el prefijo api/
    path('apiProv/', include(router.urls)),
]
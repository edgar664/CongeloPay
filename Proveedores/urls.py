# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProveedorViewSet

router = DefaultRouter()
# Esto crea las rutas para GET (listar) y POST (crear - EL QUE TE DABA 404)
router.register(r'proveedores', ProveedorViewSet, basename='proveedor')

urlpatterns = [
    # Esto incluye todas las rutas del router bajo el prefijo api/
    path('apiProv/', include(router.urls)),
]
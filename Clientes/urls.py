from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'clientes', views.ClienteViewSet, basename='clientes')
router.register(r'facturas', views.FacturaClienteViewSet, basename='facturas')
router.register(r'pagos', views.PagoClienteViewSet, basename='pagos')


urlpatterns = [
    path('apiCli/', include(router.urls)),

]
# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
# Importamos la nueva vista que acabamos de crear
from .views import NominaViewSet, CalcularNominaView, SincronizarRelojAPIView, ConsultarAsistenciasRelojView

router = DefaultRouter()
router.register(r'nominas', NominaViewSet, basename='nominas')

urlpatterns = [
    path('apiNom/', include(router.urls)),
    
    # NUEVA RUTA: Ahora sí existirá /apiNom/asistencias/
    path('apiNom/asistencias/', ConsultarAsistenciasRelojView.as_view(), name='consultar-asistencias'),
    
    path('apiNom/reloj/sincronizar/', SincronizarRelojAPIView.as_view(), name='sincronizar-reloj'),
    path('apiNom/calcular-nomina/<int:pk>/', CalcularNominaView.as_view(), name='calcular-nomina'),
]
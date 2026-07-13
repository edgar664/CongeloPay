from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmpresaViewSet

router = DefaultRouter()
router.register(r'empresa', EmpresaViewSet, basename='empresa')

urlpatterns = [
    path('apiEmpr/', include(router.urls)),  
   
    ]
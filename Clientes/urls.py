from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'clientes', views.ClienteViewSet, basename='clientes')



urlpatterns = [
    path('apiCli/', include(router.urls)),

]
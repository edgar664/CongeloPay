from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'empleados', views.EmpleadoViewSet, basename='empleados')


urlpatterns = [
    path('apiEmp/', include(router.urls)),

]
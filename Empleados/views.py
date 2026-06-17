from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Empleados
from .serializers import EmpleadoSerializer



class EmpleadoViewSet(viewsets.ModelViewSet):
    queryset = Empleados.objects.all()
    serializer_class = EmpleadoSerializer
    permission_classes = [AllowAny]
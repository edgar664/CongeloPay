from rest_framework import serializers
from Empresa.models import empresa

class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = empresa
        fields = '__all__'

from django.db import models
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

# Create your models here.
class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    rfc = models.CharField(max_length=13, unique=True)
    direccion = models.TextField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.nombre

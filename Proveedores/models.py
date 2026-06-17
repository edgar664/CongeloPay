from django.db import models
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
# Create your models here.

class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    rfc = models.CharField(max_length=13, unique=True)
    direccion = models.TextField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.nombre


class factura(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    movimiento = models.ManyToManyField('Inventarios.movimientos', blank=True)
    numero_factura = models.CharField(max_length=50, unique=True)
    fecha_emision = models.DateField()
    fecha_vencimiento = models.DateField()
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.proveedor.nombre} - {self.numero_factura}"
    
  
    
class pago(models.Model):
    factura = models.ForeignKey(factura, on_delete=models.CASCADE)
    fecha_pago = models.DateField()
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.factura.proveedor.nombre} - {self.factura.numero_factura} - {self.fecha_pago}"
    



# ─── PARA FACTURAS DE PROVEEDORES (ENTRADAS) ───
@receiver(m2m_changed, sender=factura.movimiento.through)
def marcar_movimientos_proveedor_facturados(sender, instance, action, reverse, model, pk_set, **kwargs):
    """
    Cuando se añaden movimientos a una factura de proveedor, 
    cambia su estado 'enFactura' a True.
    """
    if action == "post_add":
        model.objects.filter(id__in=pk_set).update(enFactura=True)
        
    elif action == "post_remove":
        model.objects.filter(id__in=pk_set).update(enFactura=False)
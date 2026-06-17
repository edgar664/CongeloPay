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
class factura_cliente(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    movimiento = models.ManyToManyField('Inventarios.movimientos', blank=True)
    numero_factura = models.CharField(max_length=50, unique=True)
    fecha_emision = models.DateField()
    fecha_vencimiento = models.DateField()
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.cliente.nombre} - {self.numero_factura}"

class pago_cliente(models.Model):
    factura = models.ForeignKey(factura_cliente, on_delete=models.CASCADE)
    fecha_pago = models.DateField()
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.factura.cliente.nombre} - {self.factura.numero_factura} - {self.fecha_pago}"



# ─── PARA FACTURAS DE CLIENTES (SALIDAS) ───
@receiver(m2m_changed, sender=factura_cliente.movimiento.through)
def marcar_movimientos_cliente_facturados(sender, instance, action, reverse, model, pk_set, **kwargs):
    """
    Cuando se añaden movimientos a una factura de cliente, 
    cambia su estado 'enFactura' a True.
    """
    if action == "post_add": # Se ejecuta justo después de ligar los movimientos
        model.objects.filter(id__in=pk_set).update(enFactura=True)
    
    elif action == "post_remove": # Por si editas la factura y quitas un movimiento
        model.objects.filter(id__in=pk_set).update(enFactura=False)
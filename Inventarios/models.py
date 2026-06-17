from django.db import models
# Signal para actualizar las unidades y kilos del producto cuando hay un movimiento
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.

class conceptos(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class embace(models.Model):
    nombre = models.CharField(max_length=100)
    peso = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nombre
    
class tarima(models.Model):
    nombre = models.CharField(max_length=100)
    peso = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nombre
    
class almacen(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.nombre
    
class categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    
class producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    unidades = models.IntegerField(default=0)
    kilos = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.CharField(max_length=100, default='General')
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    
    def __str__(self):
        return self.nombre
    
class movimientos(models.Model):
    TIPO_MOVIMIENTO = (
        ('ENTRADA', 'Entrada'),
        ('SALIDA', 'Salida'),
    )
    producto = models.ForeignKey(producto, on_delete=models.CASCADE)
    tipo_movimiento = models.CharField(max_length=10, choices=TIPO_MOVIMIENTO)
    unidades = models.IntegerField(default=0)
    kilos = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField(auto_now_add=True)
    hora = models.TimeField(auto_now_add=True)
    lote = models.CharField(max_length=50, blank=True, null=True)
    almacen = models.ForeignKey(almacen, on_delete=models.CASCADE)
    embace = models.ForeignKey(embace, on_delete=models.SET_NULL, null=True, blank=True)
    usuario = models.ForeignKey('Usuarios.Usuario', on_delete=models.SET_NULL, null=True, blank=True)
    enFactura = models.BooleanField(default=False)
    concepto = models.ForeignKey(conceptos, on_delete=models.SET_NULL, null=True, blank=True)
    
    # ─── LOGICAMENTE SEPARADOS ───
    # Si es ENTRADA, se llena este y 'cliente' queda en NULL
    proveedor = models.ForeignKey('Proveedores.Proveedor', on_delete=models.SET_NULL, null=True, blank=True)
    # Si es SALIDA, se llena este y 'proveedor' queda en NULL
    cliente = models.ForeignKey('Clientes.Cliente', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.tipo_movimiento} - {self.producto.nombre} - {self.fecha}"




@receiver(post_save, sender=movimientos)
def actualizar_producto_desde_movimiento(sender, instance, created, **kwargs):
    """
    Actualiza las unidades y kilos del producto cuando se registra un movimiento.
    - ENTRADA: suma los valores del proveedor
    - SALIDA: resta los valores asignados al cliente
    """
    if created:  # Solo se ejecuta cuando se crea un nuevo movimiento
        producto_obj = instance.producto  # Se removió la línea errónea de movimiento_obj

        if instance.tipo_movimiento == 'ENTRADA':
            producto_obj.unidades += instance.unidades
            producto_obj.kilos += instance.kilos
           
        elif instance.tipo_movimiento == 'SALIDA':
            producto_obj.unidades -= instance.unidades
            producto_obj.kilos -= instance.kilos
            
        # Protección para que la base de datos no guarde stock negativo por error involuntario
        if producto_obj.unidades < 0:
            producto_obj.unidades = 0
        if producto_obj.kilos < 0:
            producto_obj.kilos = 0.00

        producto_obj.save()        
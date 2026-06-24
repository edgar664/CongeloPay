from django.db import models
# Signal para actualizar las unidades y kilos del producto cuando hay un movimiento
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
# Create your models here.



#CATALOGOS DE INVENTARIOS
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
    
class categorias(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    
class producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    categoria = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    
    def __str__(self):
        return self.nombre
    
class Concepto(models.Model):
    # Ejemplos: 'COMPRA', 'TRASPASO ENTRE ALMACENES', 'SALIDA A PRODUCCION', 'VENTA'
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

#INVENTARIOS 
class StockActual(models.Model):
    """
    La 'Foto' en tiempo real. 
    Responde a: ¿Cuánto hay de X producto, en X almacén y de X lote?
    """
    producto = models.ForeignKey('producto', on_delete=models.CASCADE, related_name='existencias')
    almacen = models.ForeignKey('almacen', on_delete=models.CASCADE, related_name='inventario')
    lote = models.CharField(max_length=50)
    unidades = models.IntegerField(default=0)
    kilos_netos = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    class Meta:
        # Evita que se dupliquen registros para la misma combinación
        unique_together = ('producto', 'almacen', 'lote')
        verbose_name_plural = "Stock Actual"

    def __str__(self):
        return f"{self.producto.nombre} - Almacén: {self.almacen.nombre} - Lote: {self.lote}"


class Movimiento(models.Model):
    """
    La 'Película' o Historial de transacciones.
    Registra entradas, salidas y traspasos con Origen y Destino flexibles.
    """
    producto = models.ForeignKey('producto', on_delete=models.PROTECT)
    concepto = models.ForeignKey(Concepto, on_delete=models.PROTECT)
    lote = models.CharField(max_length=50)
    
    # Cantidades brutas y netas
    unidades = models.IntegerField(default=0)
    kilos_brutos = models.DecimalField(max_digits=12, decimal_places=2)
    kilos_netos = models.DecimalField(max_digits=12, decimal_places=2) # Descontando envase/tarima
    
    # Envases usados en el movimiento para auditoría
    embace = models.ForeignKey('embace', on_delete=models.SET_NULL, null=True, blank=True)
    tarima = models.ForeignKey('tarima', on_delete=models.SET_NULL, null=True, blank=True)
    
    fecha = models.DateField(auto_now_add=True)
    hora = models.TimeField(auto_now_add=True)
    usuario = models.ForeignKey('Usuarios.Usuario', on_delete=models.SET_NULL, null=True, blank=True)
    observaciones = models.TextField(blank=True, null=True)

    # ─── RELACIÓN GENÉRICA PARA EL ORIGEN ───
    # Puede apuntar a un Proveedor, a un Almacén o a un proceso interno
    origen_content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT, related_name='movimientos_origen')
    origen_id = models.PositiveIntegerField()
    origen = GenericForeignKey('origen_content_type', 'origen_id')

    # ─── RELACIÓN GENÉRICA PARA EL DESTINO ───
    # Puede apuntar a un Cliente, a un Almacén o a un proceso interno
    destino_content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT, related_name='movimientos_destino')
    destino_id = models.PositiveIntegerField()
    destino = GenericForeignKey('destino_content_type', 'destino_id')
    # Puede ser nulo porque las "Compras" no tienen un lote previo.
    lote_origen = models.CharField(max_length=50, blank=True, null=True, help_text="Lote del cual proviene (ej: Materia Prima)")

    def __str__(self):
        return f"Mov {self.id}: {self.concepto.nombre} - {self.producto.nombre}"
    

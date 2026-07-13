from django.db import models
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from decimal import Decimal

class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    rfc = models.CharField(max_length=13, unique=True)
    direccion = models.TextField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    # Pro-tip opcional: Días de crédito que te da este proveedor por defecto
    dias_credito = models.PositiveIntegerField(default=0, help_text="Días de crédito asignados")

    def __str__(self):
        return self.nombre


class Factura(models.Model):
    ESTATUS_CHOICES = [
        ('PENDIENTE', 'Pendiente de Pago'),
        ('PARCIAL', 'Pagada Parcialmente'),
        ('PAGADA', 'Pagada'),
        ('CANCELADA', 'Cancelada'),
    ]

    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    numero = models.CharField(max_length=50, help_text="Número de factura o serie del proveedor")
    
    # Fiscal
    uuid = models.UUIDField(unique=True, null=True, blank=True, help_text="Folio Fiscal (UUID) del SAT")
    xml_file = models.FileField(upload_to='facturas/xml/', null=True, blank=True)
    pdf_file = models.FileField(upload_to='facturas/pdf/', null=True, blank=True)
    
    # Fechas y plazos
    fecha = models.DateField(help_text="Fecha de emisión de la factura")
    fecha_vencimiento = models.DateField(null=True, blank=True, help_text="Fecha límite de pago")
    
    # Finanzas (Desglose)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    iva = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    # Estado de cuenta
    estatus = models.CharField(max_length=15, choices=ESTATUS_CHOICES, default='PENDIENTE')
    saldo_pendiente = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Cuánto se debe aún de esta factura")

    # Relaciones
    movimientos = models.ManyToManyField('Inventarios.Movimiento', blank=True)
    concepto = models.ForeignKey('Inventarios.Concepto', on_delete=models.SET_NULL, null=True, blank=True)
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        # Evita que te registren la misma factura del mismo proveedor dos veces
        unique_together = ('proveedor', 'numero') 

    def __str__(self):
        return f"Factura {self.numero} - {self.proveedor.nombre} ({self.estatus})"

    def save(self, *args, **kwargs):
        # Si no se define saldo pendiente al crear, por defecto es igual al total
        if not self.id:
            self.saldo_pendiente = self.total
            
        # Calcular fecha de vencimiento automática si el proveedor tiene días de crédito
        if self.fecha and not self.fecha_vencimiento and self.proveedor.dias_credito > 0:
            import datetime
            self.fecha_vencimiento = self.fecha + datetime.timedelta(days=self.proveedor.dias_credito)
            
        super().save(*args, **kwargs)


# 💡 AQUÍ USAMOS TU SEÑAL PARA RECALCULAR EL TOTAL BASADO EN LOS MOVIMIENTOS ASOCIADOS
@receiver(m2m_changed, sender=Factura.movimientos.through)
def actualizar_totales_factura(sender, instance, action, **kwargs):
    """
    Cuando agregas o quitas movimientos de inventario a la factura,
    esta señal sumará el costo de los movimientos para actualizar el subtotal, IVA y Total.
    Nota: Esto asume que tu modelo 'Movimiento' tiene una forma de saber su costo total 
    (por ejemplo, precio_unitario * unidades). Ajusta los campos según tu modelo de Inventarios.
    """
    if action in ["post_add", "post_remove", "post_clear"]:
        total_movimientos = Decimal('0.00')
        
        for mov in instance.movimientos.all():
            # Cambia 'precio_total' por la propiedad o campo real que use tu modelo Movimiento
            if hasattr(mov, 'precio_total'):
                total_movimientos += Decimal(str(mov.precio_total))
            elif hasattr(mov, 'costo_unitario'):
                # Si tienes costo unitario y unidades/kilos en el movimiento
                total_movimientos += Decimal(str(mov.costo_unitario)) * Decimal(str(mov.unidades))

        # Ejemplo de cálculo: Supongamos IVA del 16% integrado o desglosado
        instance.subtotal = total_movimientos
        instance.iva = instance.subtotal * Decimal('0.16')
        instance.total = instance.subtotal + instance.iva
        
        # Si es nueva o no se ha pagado, actualizamos el saldo pendiente
        if instance.estatus == 'PENDIENTE':
            instance.saldo_pendiente = instance.total
            
        # Guardamos los cambios usando save con update_fields para no disparar bucles infinitos
        instance.save(update_fields=['subtotal', 'iva', 'total', 'saldo_pendiente'])
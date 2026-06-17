from django.db import models
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from Empleados.models import Empleados
from decimal import Decimal

# 2. CABECERA DE NÓMINA (EL CONTENEDOR SEMANAL)
class Nomina(models.Model):
    ESTADOS = (('ABIERTA', 'Abierta'), ('CERRADA', 'Cerrada'))
    
    descripcion = models.CharField(max_length=200, help_text="Ej: Semana 15 - Abril")
    fecha_inicio = models.DateField(help_text="Viernes")
    fecha_fin = models.DateField(help_text="Jueves")
    estado = models.CharField(max_length=10, choices=ESTADOS, default='ABIERTA')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.descripcion} ({self.fecha_inicio} - {self.fecha_fin})"

    
# 3. REGISTRO DIARIO (CAPTURA DE DATOS DÍA A DÍA)
class RegistroAsistencia(models.Model):
    # Relacionamos el registro directamente con nuestro empleado
    empleado = models.ForeignKey(Empleados, on_delete=models.CASCADE, related_name='asistencias')
    fecha_hora = models.DateTimeField()
    
    # Tipo: Entrada, Salida, Salida a Comer, Regreso de Comer, etc.
    TIPO_CHOICES = [
        (0, 'Entrada'),
        (1, 'Salida'),
        (4, 'Entrada Almuerzo'),
        (5, 'Salida Almuerzo'),
    ]
    tipo_evento = models.IntegerField(choices=TIPO_CHOICES, default=0)
    
    # Un identificador único para evitar registrar la misma checada dos veces
    uid_reloj = models.IntegerField(unique=True)

    def __str__(self):
        return f"{self.empleado.nombre} - {self.fecha_hora} ({self.get_tipo_evento_display()})"
# 4. DETALLE DE NÓMINA (EL DESGLOSE QUE SE VE EN REACT)
class DetalleNomina(models.Model):
    nomina = models.ForeignKey(Nomina, related_name='detalles', on_delete=models.CASCADE)
    empleado = models.ForeignKey(Empleados, on_delete=models.CASCADE)
    
    # Valores calculados al momento del cierre (congelados)
    monto_fijo = models.DecimalField(max_digits=10, decimal_places=2)
    monto_destajos = models.DecimalField(max_digits=10, decimal_places=2)
    monto_bonos = models.DecimalField(max_digits=10, decimal_places=2)
    monto_horas_extra = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_neto = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Detalle {self.empleado.nombre} - {self.nomina.descripcion}"
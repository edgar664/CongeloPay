from django.db import models

# Create your models here.

class Departamento(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class Puesto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    numero_empleados = models.IntegerField(default=0)
    departamento = models.ForeignKey(Departamento, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.nombre
    


class Empleados(models.Model):
    id_empleado = models.CharField(max_length=15, unique=True, editable=False, blank=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    puesto = models.ForeignKey(Puesto, on_delete=models.SET_NULL, null=True)
    salarioDiario = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.BooleanField(default=True)
    fecha_contratacion = models.DateField(blank=True, null=True)
    nss = models.CharField(max_length=50, blank=True, null=True)
    rfc = models.CharField(max_length=50, blank=True, null=True)
    
    # ESTADO Y SEGURIDAD SOCIAL:
    statusImss = models.BooleanField(default=True)
    email = models.EmailField(blank=True, null=True)
    cellular = models.CharField(max_length=20, blank=True, null=True)
    usuaio = models.CharField(max_length=50, blank=True, null=True)
    password = models.CharField(max_length=128, blank=True, null=True)
    departamento = models.ForeignKey(Departamento, on_delete=models.SET_NULL, null=True)
    dias_vacaciones = models.IntegerField(default=0)
    jornada_laboral = models.CharField(max_length=50, blank=True, null=True)
    telefonoEmergencia = models.CharField(max_length=20, blank=True, null=True)
    avisarA = models.CharField(max_length=100, blank=True, null=True)
    isSupervisor = models.BooleanField(default=False)
    id_reloj_checador = models.IntegerField(unique=True, null=True, blank=True)
    
    # RELACIÓN REFLEXIVA PARA LA JERARQUÍA:
    supervisor = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='subordinados'
    )
    def save(self, *args, **kwargs):
        # Solo generamos el ID si el empleado es nuevo (no tiene id_empleado asignado aún)
        if not self.id_empleado:
            # Buscamos el último empleado registrado para seguir la secuencia
            ultimo_empleado = Empleados.objects.order_by('-id').first()
            
            if ultimo_empleado and ultimo_empleado.id_empleado:
                # Extraemos el número del ID actual (ej: de "SNZ0025" toma "0025" -> 25)
                try:
                    ultimo_numero = int(ultimo_empleado.id_empleado.replace("SNZ", ""))
                    nuevo_numero = ultimo_numero + 1
                except ValueError:
                    # Por si hay algún dato corrupto o manual que no empiece con SNZ
                    nuevo_numero = Empleados.objects.count() + 1
            else:
                # Si es el primer empleado de la base de datos
                nuevo_numero = 1
            
            # Formateamos el número con ceros a la izquierda (zfill(4) asegura 4 dígitos: 0001)
            self.id_empleado = f"SNZ{str(nuevo_numero).zfill(4)}"
            
        super(Empleados, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.nombre} {self.apellido}'

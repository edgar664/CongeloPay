from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager

# Create your models here.



class Rol(models.Model):
    modulo = models.CharField('Nombre del Rol',max_length=30,)
    

class UsuarioManager(BaseUserManager):
    def create_user(self,  username, rol,email ,password=None):
        user = self.model(
            username=username,
            rol=rol,
            email=self.normalize_email(email)
        )

        user.set_password(password)  # Encriptar el password antes de guardarlo
        user.save()
        return user

    def create_superuser(self, username, email, rol, password):
        # Buscar la instancia del rol a partir del ID proporcionado
        try:
            rol_instance = Rol.objects.get(id=rol)
        except Rol.DoesNotExist:
            raise ValueError('El rol especificado no existe.')

        user = self.create_user(
            username=username,
            rol=rol_instance,
            email=email
            
        )
        user.set_password(password)
        user.usuario_administrador = True
        user.save(using=self._db)
        return user

class Usuario(AbstractBaseUser):
    username = models.CharField('Nombre de usuario', unique=True, max_length=100)
    nombres = models.CharField('Nombres', max_length=200, blank=True, null=True)
    apellidos = models.CharField('Apellidos', max_length=200, blank=True, null=True)
    email =models.EmailField("Correo Electronico", max_length=254, unique=True)
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True,verbose_name='Rol')
    usuario_activo = models.BooleanField(default=True)
    usuario_administrador = models.BooleanField(default=False)
    objects = UsuarioManager()
    foto = models.ImageField(upload_to='fotos_perfil/', null=True, blank=True)
    capturando = models.BooleanField(default=False)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['rol','email']

    def __str__(self):
        return f'{self.nombres}, {self.rol}'

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.usuario_administrador
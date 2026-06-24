from django.apps import AppConfig


class InventariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Inventarios'
    
    def ready(self):
        import Inventarios.signals  # Importa los signals al iniciar la app

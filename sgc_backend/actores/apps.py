from django.apps import AppConfig
from django.db.models.signals import m2m_changed

class ActoresConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'actores'
    def ready(self):
        import actores.signals

        
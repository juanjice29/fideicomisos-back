from django.apps import AppConfig
from django.db.models.signals import m2m_changed
from django.db.models.signals import pre_delete, pre_save, post_save
class ActoresConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'actores'
    def ready(self):
        return super().ready()


        
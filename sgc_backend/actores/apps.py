from django.apps import AppConfig
from django.db.models.signals import m2m_changed
from django.db.models.signals import pre_delete, pre_save, post_save
class ActoresConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'actores'
    def ready(self):
        from logs_transactions.signals import pre_delete_receiver,post_save_receiver, pre_save_receiver
        all_models = self.get_models()

        # Connect pre_delete signal to all models
        for model in all_models:
            pre_save.connect(pre_save_receiver, sender=model)
            post_save.connect(post_save_receiver, sender=model)
            pre_delete.connect(pre_delete_receiver, sender=model) 

        
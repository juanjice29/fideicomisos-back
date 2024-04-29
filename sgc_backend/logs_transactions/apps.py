from django.apps import AppConfig
#from django.db.models.signals import pre_delete, pre_save, post_save,m2m_changed


class LogTransactionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'logs_transactions'

    def ready(self):
        #from .models import pre_delete_receiver,post_save_receiver, pre_save_receiver,m2m_changed_receiver  # import your signal receiver function
        # Get all models
        all_models = self.get_models()

        # Connect pre_delete signal to all models
        #for model in all_models:
        #    pre_save.connect(pre_save_receiver, sender=model)
        #    post_save.connect(post_save_receiver, sender=model)
        #    pre_delete.connect(pre_delete_receiver, sender=model)            
        #    m2m_changed.connect(m2m_changed_receiver, sender=model)
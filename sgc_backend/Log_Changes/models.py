from django.db import models
from accounts.models import User
from django.shortcuts import render
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
from sgc_backend.middleware import get_current_request
# Create your models here.
class Log_Cambios(models.Model):
    Usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    Ip = models.GenericIPAddressField()
    Tiempo_Accion = models.DateTimeField(auto_now_add=True)
    Accion = models.CharField(max_length=50)
    Nombre_Modelo = models.CharField(max_length=50)
    Nombre_Campo = models.CharField(max_length=50)
    Antiguo_Valor = models.TextField(null=True)
    Nuevo_Valor = models.TextField(null=True)
    


# Function to get client's IP address
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# Signal receiver functions
@receiver(pre_save)
def pre_save_receiver(sender, instance, **kwargs):
    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except ObjectDoesNotExist:
        # Instance is new, so no fields have been changed
        return

    for field in instance._meta.fields:
        old_value = getattr(old_instance, field.name)
        new_value = getattr(instance, field.name)
        if old_value != new_value:
            Log_Cambios.objects.create(
                user=request.user,
                ip=get_client_ip(request),
                action='Updated',
                model_name=sender.__name__,
                field_name=field.name,
                old_value=str(old_value),
                new_value=str(new_value),
            )

@receiver(post_save)
def post_save_receiver(sender, instance, created, **kwargs):
    if created:
        Log_Cambios.objects.create(
            user=request.user,
            ip=get_client_ip(request),
            action='Created',
            model_name=sender.__name__,
        )

@receiver(pre_delete)
def pre_delete_receiver(sender, instance, **kwargs):
    request = get_current_request()
    if request is None:
        # No current request
        return

    Log_Cambios.objects.create(
        Usuario=request.user,
        Ip=get_client_ip(request),
        Accion='Deleted',
        Nombre_Modelo=sender.__name__,
    )
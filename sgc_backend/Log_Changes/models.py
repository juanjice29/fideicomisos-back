from django.db import models
from accounts.models import User
from django.shortcuts import render
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
from sgc_backend.middleware import get_current_request
from django.db import IntegrityError
from django.core.exceptions import ValidationError
import logging


# Create your models here.
class Log_Cambios_Create(models.Model):
    Usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    Ip = models.GenericIPAddressField()
    Tiempo_Accion = models.DateTimeField(auto_now_add=True)
    Nombre_Modelo = models.CharField(max_length=50)
    Nombre_Campo = models.CharField(max_length=50)
    Nuevo_Valor = models.TextField(null=True)

class Log_Cambios_Update(models.Model):
    Usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    Ip = models.GenericIPAddressField()
    Tiempo_Accion = models.DateTimeField(auto_now_add=True)
    Nombre_Modelo = models.CharField(max_length=50)
    Nombre_Campo = models.CharField(max_length=50)
    Antiguo_Valor = models.TextField(null=True)
    Nuevo_Valor = models.TextField(null=True)

class Log_Cambios_Delete(models.Model):
    Usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    Ip = models.GenericIPAddressField()
    Tiempo_Accion = models.DateTimeField(auto_now_add=True)
    Nombre_Modelo = models.CharField(max_length=50)   
    Antiguo_Valor = models.TextField(null=True) 


# Function to get client's IP address
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
logger = logging.getLogger(__name__)
@receiver(post_save)
def post_save_receiver(sender, instance, created, **kwargs):
    try:
        if sender in [Log_Cambios_Create, Log_Cambios_Update, Log_Cambios_Delete]:
            return
        request = get_current_request()
        if request is None:
            # No current request
            return

        if created:
            for field in instance._meta.fields:
                field_name = field.name
                new_value = getattr(instance, field_name)
                Log_Cambios_Create.objects.create(
                    Usuario=request.user.username,
                    Ip=get_client_ip(request),
                    Nombre_Modelo=sender.__name__,
                    Nombre_Campo=field_name,
                    Nuevo_Valor=str(new_value),
                )
    except IntegrityError:
        # Handle the case where the instance violates a database constraint
        logger.info("Ocurrio un error de integridad en la base de datos debido a un constraint")
    except ValidationError:
        # Handle the case where an instance's field data is invalid
        logger.info("Un campo contiene un valor invalido")
    except Exception as e:
        # Handle all other types of errors
        logger.info(f"Un error ocurrio: {str(e)}")
@receiver(pre_save)
def pre_save_receiver(sender, instance, **kwargs):
    try:
        if sender in [Log_Cambios_Create, Log_Cambios_Update, Log_Cambios_Delete]:
            return
        request = get_current_request()
        if request is None:
            # No current request
            return

        if instance.pk is None:
            # Instance is new, so it has no old value
            return

        old_instance = sender.objects.get(pk=instance.pk)

        for field in instance._meta.fields:
            old_value = getattr(old_instance, field.name)
            new_value = getattr(instance, field.name)
            if old_value != new_value:
                Log_Cambios_Update.objects.create(
                    Usuario=request.user.username,
                    Ip=get_client_ip(request),
                    Nombre_Modelo=sender.__name__,
                    Nombre_Campo=field.name,
                    Antiguo_Valor=str(old_value),
                    Nuevo_Valor=str(new_value),
                )
    except IntegrityError:
        # Handle the case where the instance violates a database constraint
        logger.info("Ocurrio un error de integridad en la base de datos debido a un constraint")
    except ValidationError:
        # Handle the case where an instance's field data is invalid
        logger.info("Un campo contiene un valor invalido")
    except Exception as e:
        # Handle all other types of errors
        logger.info(f"Un error ocurrio: {str(e)}")
@receiver(pre_delete)
def pre_delete_receiver(sender, instance, **kwargs):
    try:
        if sender in [Log_Cambios_Create, Log_Cambios_Update, Log_Cambios_Delete]:
            return
        request = get_current_request()
        if request is None:
            # No current request
            return

        for field in instance._meta.fields:
            old_value = getattr(instance, field.name)
            Log_Cambios_Delete.objects.create(
                Usuario=request.user.username,
                Ip=get_client_ip(request),
                Nombre_Modelo=sender.__name__,
                Nombre_Campo=field.name,
                Antiguo_Valor=str(old_value),
            )
    except IntegrityError:
        # Handle the case where the instance violates a database constraint
        logger.info("Ocurrio un error de integridad en la base de datos debido a un constraint")
    except ValidationError:
        # Handle the case where an instance's field data is invalid
        logger.info("Un campo contiene un valor invalido")
    except Exception as e:
        # Handle all other types of errors
        logger.info(f"Un error ocurrio: {str(e)}")
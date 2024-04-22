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
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
import uuid

# Create your models here.
class Log_Cambios_Create(models.Model):
    Usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    Ip = models.GenericIPAddressField()
    TiempoAccion = models.DateTimeField(auto_now_add=True)
    NombreModelo = models.CharField(max_length=50)
    NombreCampo = models.CharField(max_length=50)
    NuevoValor = models.TextField(null=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    request_id = models.CharField(max_length=36, default=uuid.uuid4,null=True)

class Log_Cambios_Update(models.Model):
    Usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    Ip = models.GenericIPAddressField()
    TiempoAccion = models.DateTimeField(auto_now_add=True)
    NombreModelo = models.CharField(max_length=50)
    NombreCampo = models.CharField(max_length=50)
    AntiguoValor = models.TextField(null=True)
    NuevoValor = models.TextField(null=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    request_id = models.CharField(max_length=36, default=uuid.uuid4,null=True)

class Log_Cambios_Delete(models.Model):
    Usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    Ip = models.GenericIPAddressField()
    TiempoAccion = models.DateTimeField(auto_now_add=True)
    NombreModelo = models.CharField(max_length=50)
    NombreCampo = models.CharField(max_length=255)
    AntiguoValor = models.TextField(null=True) 
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,null=True)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    request_id = models.CharField(max_length=36, default=uuid.uuid4,null=True)

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
    request_id = str(uuid.uuid4())
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
                user = User.objects.get(username=request.user.username)  # get the User instance
                Log_Cambios_Create.objects.create(
                    request_id=request_id,
                    content_object=instance,
                    Usuario=user,  # assign the User instance
                    Ip=get_client_ip(request),
                    NombreModelo=sender.__name__,
                    NombreCampo=field_name,
                    NuevoValor=str(new_value),
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
    request_id = str(uuid.uuid4())
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
            user = User.objects.get(username=request.user.username)
            if old_value != new_value:
                Log_Cambios_Update.objects.create(
                    request_id=request_id,
                    content_object=instance,
                    Usuario=user,
                    Ip=get_client_ip(request),
                    NombreModelo=sender.__name__,
                    NombreCampo=field.name,
                    AntiguoValor=str(old_value),
                    NuevoValor=str(new_value),
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
    request_id = str(uuid.uuid4())
    try:
        if sender in [Log_Cambios_Create, Log_Cambios_Update, Log_Cambios_Delete]:
            return
        request = get_current_request()
        if request is None:
            # No current request
            return

        for field in instance._meta.fields:
            old_value = getattr(instance, field.name)
            user = User.objects.get(username=request.user.username)
            Log_Cambios_Delete.objects.create(
                request_id=request_id,
                content_object=instance,
                Usuario=user,
                Ip=get_client_ip(request),
                NombreModelo=sender.__name__,
                NombreCampo=field.name,
                AntiguoValor=str(old_value),
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
        

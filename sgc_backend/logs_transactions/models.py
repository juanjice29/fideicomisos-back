from django.db import models
from accounts.models import User
from django.shortcuts import render
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save, post_save, pre_delete,m2m_changed
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
    usuario = models.ForeignKey(User, on_delete=models.CASCADE,db_column='usuario')
    ip = models.GenericIPAddressField(db_column='ip')
    tiempoAccion = models.DateTimeField(auto_now_add=True,db_column='tiempo_accion')
    nombreModelo = models.CharField(max_length=50,db_column='nombre_modelo')
    nombreCampo = models.CharField(max_length=50,db_column='nombre_campo')
    nuevoValor = models.TextField(null=True,db_column='nuevo_valor')    
    contentType = models.ForeignKey(ContentType, on_delete=models.CASCADE,db_column='content_type')    
    objectId = models.PositiveIntegerField(db_column='object_id')
    contentObject = GenericForeignKey('contentType', 'objectId')
    requestId = models.CharField(max_length=36, default=uuid.uuid4,null=True,db_column='request_id')
    class Meta:
        # Especifica el nombre de la tabla aquí
        db_table = 'logs_create'

class Log_Cambios_Update(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE,db_column='usuario')
    ip = models.GenericIPAddressField(db_column='ip')
    tiempoAccion = models.DateTimeField(auto_now_add=True,db_column='tiempo_accion')
    nombreModelo = models.CharField(max_length=50,db_column='nombre_modelo')
    nombreCampo = models.CharField(max_length=50,db_column='nombre_campo')
    antiguoValor = models.TextField(null=True,db_column='antiguo_valor')    
    nuevoValor = models.TextField(null=True,db_column='nuevo_valor')    
    contentType = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True,db_column='content_type')
    objectId = models.PositiveIntegerField(null=True,db_column='object_id')
    contentObject = GenericForeignKey('contentType', 'objectId')
    requestId = models.CharField(max_length=36, default=uuid.uuid4,null=True,db_column='request_id')
    class Meta:
        # Especifica el nombre de la tabla aquí
        db_table = 'logs_update'

class Log_Cambios_Delete(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE,db_column='usuario')
    ip = models.GenericIPAddressField(db_column='ip')
    tiempoAccion = models.DateTimeField(auto_now_add=True,db_column='tiempo_accion')
    nombreModelo = models.CharField(max_length=50,db_column='nombre_modelo')
    nombreCampo = models.CharField(max_length=255,db_column='nombre_campo')
    antiguoValor = models.TextField(null=True,db_column='antiguo_valor')
    contentType = models.ForeignKey(ContentType, on_delete=models.CASCADE,null=True,db_column='content_type')
    objectId = models.PositiveIntegerField(null=True,db_column='object_id')
    contentObject = GenericForeignKey('contentType', 'objectId')
    requestId = models.CharField(max_length=36, default=uuid.uuid4,null=True,db_column='request_id')
    class Meta:
        # Especifica el nombre de la tabla aquí
        db_table = 'logs_delete'

class Log_Cambios_M2M(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE,db_column='usuario')
    ip = models.GenericIPAddressField(db_column='ip')
    tiempoAccion = models.DateTimeField(auto_now_add=True,db_column='tiempo_accion')
    nombreModelo = models.CharField(max_length=50,db_column='nombre_modelo')
    nombreCampo = models.CharField(max_length=50,db_column='nombre_campo')
    valor = models.TextField(null=True,db_column='valor')
    jsonValue=models.TextField(null=True,db_column='json_value')
    action=models.CharField(max_length=50,null=True,db_column='action')
    contentType = models.ForeignKey(ContentType, on_delete=models.CASCADE,db_column='content_type')
    objectId = models.PositiveIntegerField(null=True,db_column='object_id')
    contentObject = GenericForeignKey('contentType', 'objectId')
    requestId = models.CharField(max_length=36, default=uuid.uuid4,null=True,db_column='request_id')
    class Meta:
        # Especifica el nombre de la tabla aquí
        db_table = 'logs_relate'

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
        if sender in [Log_Cambios_Create, Log_Cambios_Update, Log_Cambios_Delete,Log_Cambios_M2M]:
            return
        request = get_current_request()
        if request is None:
            # No current request
            return

        if created:
            print(instance)
            """ for field in instance._meta.fields:
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
                ) """
    except IntegrityError:
        # Handle the case where the instance violates a database constraint
        logger.info("Ocurrio un error de integridad en la base de datos debido a un constraint")
    except ValidationError:
        # Handle the case where an instance's field data is invalid
        logger.info("Un campo contiene un valor invalido")
    except Exception as e:
        # Handle all other types of errors
        logger.info(f"Un error ocurrio: {str(e)}")

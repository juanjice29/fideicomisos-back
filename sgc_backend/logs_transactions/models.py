from django.db import models
from accounts.models import User
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
import uuid


# Create your models here.
class Log_Cambios_Create(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE,db_column='usuario')
    ip = models.GenericIPAddressField(db_column='ip')
    tiempoAccion = models.DateTimeField(auto_now_add=True,db_column='tiempo_accion')
    nombreModelo = models.CharField(max_length=50,db_column='nombre_modelo')    
    nuevoValor = models.TextField(null=True,db_column='nuevo_valor')    
    contentType = models.ForeignKey(ContentType, on_delete=models.CASCADE,db_column='content_type')    
    objectId = models.TextField(db_column='object_id')
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
    cambiosValor = models.TextField(null=True,db_column='cambios_valor')    
    contentType = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True,db_column='content_type')
    objectId = models.TextField(null=True,db_column='object_id')
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
    antiguoValor = models.TextField(null=True,db_column='antiguo_valor')
    contentType = models.ForeignKey(ContentType, on_delete=models.CASCADE,null=True,db_column='content_type')
    objectId = models.TextField(null=True,db_column='object_id')
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
    jsonValue=models.TextField(null=True,db_column='json_value')
    accion=models.CharField(max_length=50,null=True,db_column='accion')
    contentType = models.ForeignKey(ContentType, on_delete=models.CASCADE,db_column='content_type')
    objectId = models.TextField(null=True,db_column='object_id')
    contentObject = GenericForeignKey('contentType', 'objectId')
    requestId = models.CharField(max_length=36, default=uuid.uuid4,null=True,db_column='request_id')
    nombreModeloPadre=models.CharField(max_length=50,db_column='nombre_modelo_padre')
    class Meta:
        # Especifica el nombre de la tabla aquí
        db_table = 'logs_relate'

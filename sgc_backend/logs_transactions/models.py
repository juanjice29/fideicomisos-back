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
    nuevoJsonValue=models.TextField(null=True,db_column='nuevo_json_value')
    contentType = models.ForeignKey(ContentType, on_delete=models.CASCADE,db_column='content_type')    
    objectId = models.PositiveIntegerField(db_column='object_id')
    contentObject = GenericForeignKey('contentType', 'objectId')
    requestId = models.CharField(max_length=36, default=uuid.uuid4,null=True,db_column='request_id')

class Log_Cambios_Update(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE,db_column='usuario')
    ip = models.GenericIPAddressField(db_column='ip')
    tiempoAccion = models.DateTimeField(auto_now_add=True,db_column='tiempo_accion')
    nombreModelo = models.CharField(max_length=50,db_column='nombre_modelo')
    nombreCampo = models.CharField(max_length=50,db_column='nombre_campo')
    antiguoValor = models.TextField(null=True,db_column='antiguo_valor')
    antiguoJsonValue=models.TextField(null=True,db_column='antiguo_json_value')
    nuevoValor = models.TextField(null=True,db_column='nuevo_valor')
    nuevoJsonValue=models.TextField(null=True,db_column='nuevo_json_value')
    contentType = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True,db_column='content_type')
    objectId = models.PositiveIntegerField(null=True,db_column='object_id')
    contentObject = GenericForeignKey('contentType', 'objectId')
    requestId = models.CharField(max_length=36, default=uuid.uuid4,null=True,db_column='request_id')

class Log_Cambios_Delete(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE,db_column='usuario')
    ip = models.GenericIPAddressField(db_column='ip')
    tiempoAccion = models.DateTimeField(auto_now_add=True,db_column='tiempo_accion')
    nombreModelo = models.CharField(max_length=50,db_column='nombre_modelo')
    nombreCampo = models.CharField(max_length=255,db_column='nombre_campo')
    antiguoValor = models.TextField(null=True,db_column='antiguo_valor') 
    antiguoJsonValue=models.TextField(null=True,db_column='antiguo_json_value')
    contentType = models.ForeignKey(ContentType, on_delete=models.CASCADE,null=True,db_column='content_type')
    objectId = models.PositiveIntegerField(null=True,db_column='object_id')
    contentObject = GenericForeignKey('contentType', 'objectId')
    requestId = models.CharField(max_length=36, default=uuid.uuid4,null=True,db_column='request_id')

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


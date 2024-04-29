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
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    ip = models.GenericIPAddressField()
    tiempoAccion = models.DateTimeField(auto_now_add=True)
    nombreModelo = models.CharField(max_length=50)
    nombreCampo = models.CharField(max_length=50)
    nuevoValor = models.TextField(null=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    request_id = models.CharField(max_length=36, default=uuid.uuid4,null=True)

class Log_Cambios_Update(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    ip = models.GenericIPAddressField()
    tiempoAccion = models.DateTimeField(auto_now_add=True)
    nombreModelo = models.CharField(max_length=50)
    nombreCampo = models.CharField(max_length=50)
    antiguoValor = models.TextField(null=True)
    nuevoValor = models.TextField(null=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    request_id = models.CharField(max_length=36, default=uuid.uuid4,null=True)

class Log_Cambios_Delete(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    ip = models.GenericIPAddressField()
    tiempoAccion = models.DateTimeField(auto_now_add=True)
    nombreModelo = models.CharField(max_length=50)
    nombreCampo = models.CharField(max_length=255)
    antiguoValor = models.TextField(null=True) 
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,null=True)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    request_id = models.CharField(max_length=36, default=uuid.uuid4,null=True)

class Log_Cambios_M2M(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    ip = models.GenericIPAddressField()
    tiempoAccion = models.DateTimeField(auto_now_add=True)
    nombreModelo = models.CharField(max_length=50)
    nombreCampo = models.CharField(max_length=50)
    valor = models.TextField(null=True)
    jsonValue=models.TextField(null=True)
    action=models.CharField(max_length=50,null=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    request_id = models.CharField(max_length=36, default=uuid.uuid4,null=True)


from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from fidecomisos.models import Fideicomiso, Encargo
from public.models import TipoDeDocumento

class TipoActorDeContrato(models.Model):
    tipoActor = models.CharField(max_length=90)
    descripcion = models.CharField(max_length=90)

class ActorDeContrato(models.Model):
    
    pipoIdentificacion = models.ForeignKey(TipoDeDocumento, on_delete=models.CASCADE)
    numeroIdentificacion = models.CharField(max_length=12)
    primerNombre = models.CharField(max_length=100)
    segundoNombre = models.CharField(max_length=100,null=True,blank=True)
    primerApellido = models.CharField(max_length=100)
    segundoApellido = models.CharField(max_length=100,null=True,blank=True)
    fideicomisoAsociado = models.ManyToManyField(Fideicomiso,through='RelacionFideicomisoActor')
    fechaCreacion = models.DateTimeField(auto_now_add=True)
    fechaActualizacion = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['tipoIdentificacion','numeroIdentificacion'], name='unique_identificacion')
        ]        
    
class RelacionFideicomisoActor(models.Model):
    actor = models.ForeignKey(ActorDeContrato, on_delete=models.CASCADE)
    fideicomiso = models.ForeignKey(Fideicomiso, on_delete=models.CASCADE)
    tipoActor = models.ForeignKey(TipoActorDeContrato, on_delete=models.CASCADE,null=False)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['actor','fideicomiso'], name='unique_fideicomiso_actor')
        ]
from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from fidecomisos.models import TipoDeDocumento
from fidecomisos.models import Fideicomiso, Encargo

class TipoActorDeContrato(models.Model):
    TipoActor = models.CharField(max_length=90)
    Descripcion = models.CharField(max_length=90)

class ActorDeContrato(models.Model):
    
    TipoIdentificacion = models.ForeignKey(TipoDeDocumento, on_delete=models.CASCADE)
    NumeroIdentificacion = models.CharField(max_length=12)
    PrimerNombre = models.CharField(max_length=100)
    SegundoNombre = models.CharField(max_length=100,null=True,blank=True)
    PrimerApellido = models.CharField(max_length=100)
    SegundoApellido = models.CharField(max_length=100,null=True,blank=True)
    FideicomisoAsociado = models.ManyToManyField(Fideicomiso,through='RelacionFideicomisoActor')
    FechaCreacion = models.DateTimeField(auto_now_add=True)
    FechaActualizacion = models.DateTimeField(auto_now=True)
    Activo = models.BooleanField(default=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['TipoIdentificacion','NumeroIdentificacion'], name='unique_identificacion')
        ]        
    
class RelacionFideicomisoActor(models.Model):
    Actor = models.ForeignKey(ActorDeContrato, on_delete=models.CASCADE)
    Fideicomiso = models.ForeignKey(Fideicomiso, on_delete=models.CASCADE)
    TipoActor = models.ForeignKey(TipoActorDeContrato, on_delete=models.CASCADE,null=False)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['Actor','Fideicomiso'], name='unique_fideicomiso_actor')
        ]
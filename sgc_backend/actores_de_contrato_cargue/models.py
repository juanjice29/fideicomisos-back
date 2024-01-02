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
    Primer_Nombre = models.CharField(max_length=100)
    Segundo_Nombre = models.CharField(max_length=100)
    Primer_Apellido = models.CharField(max_length=100)
    Segundo_Apellido = models.CharField(max_length=100)
    TipoActor = models.ForeignKey(TipoActorDeContrato, on_delete=models.CASCADE)
    FideicomisoAsociado = models.ManyToManyField(Fideicomiso)
    FechaActualizacion = models.DateField()
    Activo = models.BooleanField(default=True)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['NumeroIdentificacion'], name='unique_identificacion')
        ]
        

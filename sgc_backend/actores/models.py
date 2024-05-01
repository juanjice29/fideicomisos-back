from django.db import models
# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from fidecomisos.models import Fideicomiso, Encargo
from public.models import TipoDeDocumento

class TipoActorDeContrato(models.Model):
    tipoActor = models.CharField(max_length=90,db_column='tipo_actor')
    descripcion = models.CharField(max_length=90,db_column='descripcion')
    class Meta:
        # Especifica el nombre de la tabla aquí
        db_table = 'params_tipo_actor'

class ActorDeContrato(models.Model):
    
    tipoIdentificacion = models.ForeignKey(TipoDeDocumento, on_delete=models.CASCADE,db_column='tipo_identificacion')
    numeroIdentificacion = models.CharField(max_length=12,db_column='numero_identificacion')
    primerNombre = models.CharField(max_length=100,db_column='primer_nombre')
    segundoNombre = models.CharField(max_length=100,null=True,blank=True,db_column='segundo_nombre')
    primerApellido = models.CharField(max_length=100,db_column='primer_apellido')
    segundoApellido = models.CharField(max_length=100,null=True,blank=True,db_column='segundo_apellido')
    fideicomisoAsociado = models.ManyToManyField(Fideicomiso,through='RelacionFideicomisoActor')
    fechaCreacion = models.DateTimeField(auto_now_add=True,db_column='fecha_creacion')
    fechaActualizacion = models.DateTimeField(auto_now=True,db_column='fecha_actualizacion')
    estado = models.CharField(max_length=100, default='ACT',db_column='estado')
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['tipoIdentificacion','numeroIdentificacion'], name='unique_identificacion')
        ] 
        db_table = 'fidei_actor'       
    
class RelacionFideicomisoActor(models.Model):
    actor = models.ForeignKey(ActorDeContrato, on_delete=models.CASCADE,db_column='actor')
    fideicomiso = models.ForeignKey(Fideicomiso, on_delete=models.CASCADE,db_column='fideicomiso')
    tipoActor = models.ForeignKey(TipoActorDeContrato, on_delete=models.CASCADE,null=False,db_column='tipo_actor')
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['actor','fideicomiso'], name='unique_fideicomiso_actor')
        ]
        db_table = 'fidei_actor_fideicomiso'
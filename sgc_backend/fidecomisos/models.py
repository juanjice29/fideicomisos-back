from django.db import models
from django.db.models import Max
from django.db.models.functions import Cast

from sgc_backend.public.models import TipoDeDocumento

class Fideicomiso(models.Model):
    codigoSFC = models.IntegerField(primary_key=True,  db_index=True)
    tipoIdentificacion = models.ForeignKey(TipoDeDocumento, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    fechaCreacion = models.DateField()
    fechaVencimiento = models.DateField()
    fechaProrroga = models.DateField()
    estado = models.CharField(max_length=1)
    
class Encargo(models.Model):
    
    numeroEncargo = models.CharField(max_length=50)
    fideicomiso = models.ForeignKey(Fideicomiso, on_delete=models.CASCADE, related_name='encargos')
    descripcion = models.CharField(max_length=300)
    class Meta:
        unique_together = (('numeroEncargo', 'fideicomiso'),)
class EncargoTemporal(models.Model):
    
    numeroEncargo = models.CharField(max_length=50)
    fideicomiso = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=300)
    class Meta:
        unique_together = (('numeroEncargo', 'fideicomiso'),)
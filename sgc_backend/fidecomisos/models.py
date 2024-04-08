from django.db import models
from django.db.models import Max
from django.db.models.functions import Cast
class TipoDePersona(models.Model):
    Id = models.AutoField(primary_key=True)
    TipoPersona = models.CharField(max_length=3)
    Description = models.CharField(max_length=100)

class TipoDeDocumento(models.Model):
    TipoDocumento = models.CharField(max_length=3, primary_key=True)
    Descripcion = models.CharField(max_length=100)
    idTipoPersona = models.ForeignKey(TipoDePersona, on_delete=models.CASCADE)

class Fideicomiso(models.Model):
    CodigoSFC = models.IntegerField(primary_key=True,  db_index=True)
    TipoIdentificacion = models.ForeignKey(TipoDeDocumento, on_delete=models.CASCADE)
    Nombre = models.CharField(max_length=100)
    FechaCreacion = models.DateField()
    FechaVencimiento = models.DateField()
    FechaProrroga = models.DateField()
    Estado = models.CharField(max_length=1)
    
class Encargo(models.Model):
    
    NumeroEncargo = models.CharField(max_length=50)
    Fideicomiso = models.ForeignKey(Fideicomiso, on_delete=models.CASCADE, related_name='encargos')
    Descripcion = models.CharField(max_length=300)
    class Meta:
        unique_together = (('NumeroEncargo', 'Fideicomiso'),)
class EncargoTemporal(models.Model):
    
    NumeroEncargo = models.CharField(max_length=50)
    Fideicomiso = models.CharField(max_length=50)
    Descripcion = models.CharField(max_length=300)
    class Meta:
        unique_together = (('NumeroEncargo', 'Fideicomiso'),)
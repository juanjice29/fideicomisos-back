from django.db import models

class TipoDePersona(models.Model):
    id = models.AutoField(primary_key=True)
    tipoPersona = models.CharField(max_length=3)
    description = models.CharField(max_length=40)

class TipoDeDocumento(models.Model):
    TipoDocumento = models.CharField(max_length=3, primary_key=True)
    Descripcion = models.CharField(max_length=40)
    idTipoPersona = models.ForeignKey(TipoDePersona, on_delete=models.CASCADE)

class Fideicomiso(models.Model):
    CodigoSFC = models.IntegerField(primary_key=True)
    TipoIdentificacion = models.ForeignKey(TipoDeDocumento, on_delete=models.CASCADE)
    Nombre = models.CharField(max_length=60)
    FechaCreacion = models.DateField()
    FechaVencimiento = models.DateField()
    FechaProrroga = models.DateField()
    Estado = models.CharField(max_length=1)
    
class Encargo(models.Model):
    NumeroEncargo = models.IntegerField()
    Fideicomiso = models.ForeignKey(Fideicomiso, on_delete=models.CASCADE, related_name='encargos')
    Descripcion = models.CharField(max_length=100)
from django.db import models

# Create your models here.

class TipoDePersona(models.Model):
    id = models.AutoField(primary_key=True)
    tipoPersona = models.CharField(max_length=3)
    description = models.CharField(max_length=100)

class TipoDeDocumento(models.Model):
    tipoDocumento = models.CharField(max_length=3, primary_key=True)
    descripcion = models.CharField(max_length=100)
    idTipoPersona = models.ForeignKey(TipoDePersona, on_delete=models.CASCADE)
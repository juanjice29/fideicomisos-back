from django.db import models

# Create your models here.

class TipoDePersona(models.Model):
    id = models.AutoField(primary_key=True,db_column='id')
    tipoPersona = models.CharField(max_length=3,db_column='tipo_persona')
    descripcion = models.CharField(max_length=100,db_column='descripcion')
    class Meta:
        # Especifica el nombre de la tabla aquí
        db_table = 'params_tipo_persona'

class TipoDeDocumento(models.Model):
    tipoDocumento = models.CharField(max_length=3, primary_key=True,db_column='tipo_documento')
    descripcion = models.CharField(max_length=100,db_column='descripcion')
    idTipoPersona = models.ForeignKey(TipoDePersona, on_delete=models.CASCADE,db_column='id_tipo_persona')
    class Meta:
        # Especifica el nombre de la tabla aquí
        db_table = 'params_tipo_documento'

class TipoNovedadRPBF(models.Model):
    id = models.IntegerField(primary_key=True)
    descripcion = models.CharField(max_length=255)
    class Meta:
        db_table="params_tipo_novedad_rpbf"
    
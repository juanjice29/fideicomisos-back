from django.db import models
from enum import Enum
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

class ParametrosRpbf(models.Model):
    fondo=models.CharField(max_length=3,db_column='fondo')
    novedad=models.CharField(max_length=3,db_column='novedad')
    bepjtit=models.CharField(max_length=3,db_column='bepjtit')
    bepjben=models.CharField(max_length=3,db_column='bepjben')
    bepjcon=models.CharField(max_length=3,db_column='bepjcon')
    bepjrl=models.CharField(max_length=3,db_column='bepjrl')
    bespjfcp=models.CharField(max_length=3,db_column='bespjfcp')
    bespjf=models.CharField(max_length=3,db_column='bespjf')
    bespjcf=models.CharField(max_length=3,db_column='bespjcf')
    bespjfb=models.CharField(max_length=3,db_column='bespjfb')
    bespjcfe=models.CharField(max_length=3,db_column='bespjcfe')
    becespj=models.CharField(max_length=3,db_column='becespj')
    pppjepj=models.CharField(max_length=3,db_column='pppjepj')
    pbpjepj=models.CharField(max_length=3,db_column='pbpjepj')
    
    class Meta:
        db_table="params_reporte_rpbf"

class TipoParametrizacion(models.Model):
    acronimo = models.CharField(max_length=50,verbose_name='Acronimo de el tipo de parametrizacion', primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    class Meta:
        db_table = 'PARAMS_TIPO_PARAMETRIZACION'
    
    
class ParametrosGenericos(models.Model):
    tipoParametrizacion=models.ForeignKey(TipoParametrizacion, on_delete=models.CASCADE, verbose_name='Tipo de parametrizacion general',db_column='tipo_parametrizacion')
    nombre = models.CharField(max_length=100,unique=True)
    valorParametro=models.TextField(db_column='valor_parametro',verbose_name='Mensaje del log')
    descripcion = models.TextField()
    class Meta:
        db_table = 'PARAMS_GENERIC_PARAM'

class TipoParamEnum(Enum):
    SALIDA_RPBF = "SALIDA_RPBF"  
    ENTRADA_RPBF= "ENTRADA_RPBF"
    
class PriodoTrimestral(models.Model):
    periodo=models.CharField(max_length=7,primary_key=True)
    class Meta:
        db_table = 'PARAMS_PERIODO_TRIMESTRAL'
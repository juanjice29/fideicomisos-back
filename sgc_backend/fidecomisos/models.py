from django.db import models
from django.db.models import Max
from django.db.models.functions import Cast
from public.models import TipoDeDocumento

class Fideicomiso(models.Model):
    codigoSFC = models.IntegerField(primary_key=True,  db_index=True,db_column='codigo_sfc')
    tipoIdentificacion = models.ForeignKey(TipoDeDocumento, on_delete=models.CASCADE,db_column='tipo_identificacion')
    nombre = models.CharField(max_length=100,db_column='nombre')
    fechaCreacion = models.DateField(db_column='fecha_creacion')
    fechaVencimiento = models.DateField(db_column='fecha_vencimiento')
    fechaProrroga = models.DateField(db_column='fecha_prorroga')
    estado = models.CharField(max_length=1,db_column='estado')
    class Meta:
        # Especifica el nombre de la tabla aquí
        db_table = 'fidei_fideicomiso'
    
class Encargo(models.Model):
    
    numeroEncargo = models.CharField(max_length=50,db_column='numero_encargo')
    fideicomiso = models.ForeignKey(Fideicomiso, on_delete=models.CASCADE, related_name='encargos',db_column='fideicomiso')
    descripcion = models.CharField(max_length=300,null=True,db_column='descripcion')
    class Meta:
        unique_together = (('numeroEncargo', 'fideicomiso'),)
        db_table = 'encargo'
class EncargoTemporal(models.Model):
    
    numeroEncargo = models.CharField(max_length=50,db_column='numero_encargo')
    fideicomiso = models.CharField(max_length=50,db_column='fideicomiso')
    descripcion = models.CharField(max_length=300,db_column='descripcion')
    class Meta:
        unique_together = (('numeroEncargo', 'fideicomiso'),)
    db_table = 'encargo_temporal'
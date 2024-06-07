from django.db import models
from public.models import TipoNovedadRPBF

class RpbfCandidatos(models.Model):    
    nroIdentif= models.CharField(max_length=20)
    fondo=models.CharField(max_length=2)
    tipoNovedad=models.ForeignKey(TipoNovedadRPBF,on_delete=models.CASCADE)
    fechaCreacion=models.CharField(max_length=10)
    fechaCancelacion=models.CharField(max_length=10,null=True)
    porcentaje=models.CharField(max_length=7)
    class Meta:
        db_table='rpbf_candidatos'
        
#longitud de datos basados en el anexo tecnico de la dian
class RpbfHistorico(models.Model):
    periodo=models.CharField(max_length=6)
    fondo=models.CharField(max_length=2)
    tipoNovedad=models.ForeignKey(TipoNovedadRPBF,on_delete=models.CASCADE)
    bepjtit=models.CharField(max_length=2)
    bepjben=models.CharField(max_length=2)
    bepjcon=models.CharField(max_length=2)
    bepjrl=models.CharField(max_length=2)
    bespjfcp=models.CharField(max_length=2)
    bespjf=models.CharField(max_length=2)
    bespjcf=models.CharField(max_length=2)
    bespjfb=models.CharField(max_length=2)
    bespjcfe=models.CharField(max_length=2)
    tdocben=models.CharField(max_length=2)
    niben=models.CharField(max_length=20)
    paexben=models.CharField(max_length=4)
    nitben=models.CharField(max_length=20)
    paexnitben=models.CharField(max_length=4)
    pape=models.CharField(max_length=60)
    sape=models.CharField(max_length=60)
    pnom=models.CharField(max_length=60)
    onom=models.CharField(max_length=60)
    fecnac=models.CharField(max_length=10)
    panacb=models.CharField(max_length=4)
    pnacion=models.CharField(max_length=4)
    paresb=models.CharField(max_length=4)
    dptoben=models.CharField(max_length=2)
    munben=models.CharField(max_length=3)
    dirben=models.CharField(max_length=250)
    codpoben=models.CharField(max_length=10)
    emailben=models.CharField(max_length=50)
    pppjepj=models.CharField(max_length=8)
    pbpjepj=models.CharField(max_length=8)    
    feiniben=models.CharField(max_length=10)
    fecfinben=models.CharField(max_length=10)
    tnov=models.CharField(max_length=1)
    class Meta:
        db_table='rpbf_historico'
        
class Beneficiario_Reporte_Dian(models.Model):
    Id_Cliente = models.CharField(max_length=255)
    Periodo = models.CharField(max_length=255)#Ultimo Estado
    Tipo_Novedad = models.ForeignKey(TipoNovedadRPBF, on_delete=models.CASCADE)
    Tipo_Producto = models.CharField(max_length=255)
    
    def __str__(self):
        return self.client_id
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['Id_Cliente', 'Tipo_Novedad', 'Tipo_Producto'], name='unique_identificacion_beneficiario')
        ]
        
class File(models.Model):
    file_name = models.CharField(max_length=255)
    file_hash = models.CharField(max_length=32)
    date_inserted = models.DateTimeField(auto_now_add=True)
    
class ConsecutivosRpbf(models.Model):
    fondo=models.CharField(max_length=3)
    consecutivo = models.IntegerField(db_column='consecutivo')
    class Meta:
        db_table='rpbf_consecutivos'
        
"""    
class RPBF_PERIODOS(models.Model):
    PERIODO = models.CharField(max_length=6, primary_key=True)
    FECHA_INCIAL = models.DateField()
    FECHA_FINAL = models.DateField()


    

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['TIPO_IDENTIF', 'NRO_IDENTIF', 'FONDO', 'PERIODO_REPORTADO', 'TIPO_NOVEDAD'], name='pk_rpbf_historico')
        ]
"""


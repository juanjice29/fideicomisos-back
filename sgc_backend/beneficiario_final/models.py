from django.db import models

class Tipo_Novedad(models.Model):
    type_id = models.IntegerField(primary_key=True)
    type_name = models.CharField(max_length=255)

    def __str__(self):
        return self.type_name

class Beneficiario_Reporte_Dian(models.Model):
    Id_Cliente = models.CharField(max_length=255)
    Periodo = models.CharField(max_length=255)#Ultimo Estado
    Tipo_Novedad = models.ForeignKey(Tipo_Novedad, on_delete=models.CASCADE)
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
    
class RPBF_PERIODOS(models.Model):
    PERIODO = models.CharField(max_length=6, primary_key=True)
    FECHA_INCIAL = models.DateField()
    FECHA_FINAL = models.DateField()

class RPBF_HISTORICO(models.Model):
    TIPO_IDENTIF = models.CharField(max_length=3)
    NRO_IDENTIF = models.CharField(max_length=20)
    FONDO = models.CharField(max_length=2)
    TIPO_NOVEDAD = models.CharField(max_length=2)
    PORCENTAJE_SALDO = models.CharField(max_length=100,blank=True)
    FECHA_CREACION= models.CharField(max_length=10,blank=True)
    FECHA_CANCELACION=models.CharField(max_length=10,blank=True)
    PERIODO_REPORTADO = models.ForeignKey(RPBF_PERIODOS, on_delete=models.CASCADE)
    

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['TIPO_IDENTIF', 'NRO_IDENTIF', 'FONDO', 'PERIODO_REPORTADO', 'TIPO_NOVEDAD'], name='pk_rpbf_historico')
        ]
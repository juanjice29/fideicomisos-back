from django.db import models

class Tipo_Novedad(models.Model):
    type_id = models.IntegerField(primary_key=True)
    type_name = models.CharField(max_length=255)

    def __str__(self):
        return self.type_name

class Beneficiario_Reporte_Dian(models.Model):
    Id_Cliente = models.CharField(max_length=255)
    Fecha_Añadido = models.DateTimeField(auto_now_add=True)
    Fecha_Creado = models.DateTimeField(auto_now_add=True)
    Periodo = models.CharField(max_length=255)#Ultimo Estado
    Tipo_Novedad = models.ForeignKey(Tipo_Novedad, on_delete=models.CASCADE)
    Activo = models.BooleanField(default=True)
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
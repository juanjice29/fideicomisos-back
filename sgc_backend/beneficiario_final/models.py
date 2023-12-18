from django.db import models

class Tipo_Novedad(models.Model):
    type_id = models.IntegerField(primary_key=True)
    type_name = models.CharField(max_length=255)

    def __str__(self):
        return self.type_name
class Beneficiario_Reporte(models.Model):
    client_id = models.CharField(max_length=255)
    date_added = models.DateTimeField(auto_now_add=True)
    date_created = models.DateTimeField(auto_now_add=True)
    period = models.CharField(max_length=255)#Ultimo Estado
    tipo_Novedad = models.ForeignKey(Tipo_Novedad, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    type_product = models.CharField(max_length=255)
    
    def __str__(self):
        return self.client_id
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['client_id', 'tipo_Novedad', 'type_product'], name='unique_identificacion_beneficiario')
        ]
        
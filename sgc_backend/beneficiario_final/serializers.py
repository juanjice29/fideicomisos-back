from rest_framework import serializers
from .models import Beneficiario_Reporte_Dian

class Beneficiario_ReporteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Beneficiario_Reporte_Dian
        fields = '__all__'
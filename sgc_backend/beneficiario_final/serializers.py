from rest_framework import serializers
from .models import Beneficiario_Reporte

class Beneficiario_ReporteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Beneficiario_Reporte
        fields = '__all__'
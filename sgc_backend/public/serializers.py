from rest_framework import serializers
from .models import TipoDeDocumento,PriodoTrimestral,ParametrosGenericos

class TipoDeDocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDeDocumento
        fields = '__all__'
        depth=1
        
class PriodoTrimestralSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriodoTrimestral
        fields = '__all__'
        depth=1

class ParametrosGenericosSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParametrosGenericos
        fields = '__all__'
        depth=1
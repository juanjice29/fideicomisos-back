import datetime
from rest_framework import serializers
from .models import Fideicomiso, Encargo, TipoDeDocumento
from rest_framework import generics
class FideicomisoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fideicomiso
        fields = '__all__'


class EncargoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Encargo
        fields = '__all__'
        
class FideicomisoEncargosList(generics.ListAPIView):
    serializer_class = EncargoSerializer

    def get_queryset(self):
        fideicomiso_id = self.kwargs['fideicomiso_id']
        return Encargo.objects.filter(Fideicomiso__id=fideicomiso_id)
    
class TipoDeDocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDeDocumento
        fields = '__all__'
        depth=1
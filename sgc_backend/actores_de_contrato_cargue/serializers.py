from rest_framework import serializers
from .models import ActorDeContrato
from fidecomisos.models import Encargo
from fidecomisos.serializers import EncargoSerializer,FideicomisoSerializer
from rest_framework import serializers
from .models import TipoActorDeContrato,RelacionFideicomisoActor
from rest_framework import serializers
from .models import Encargo


class EncargoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Encargo
        fields = '__all__'
        
class TipoActorDeContratoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoActorDeContrato
        fields = '__all__'


class ActorDeContratoSerializer(serializers.ModelSerializer):    
    class Meta:
        model = ActorDeContrato
        fields = '__all__'     
          
class RelacionFideicomisoActorCreateSerializer(serializers.ModelSerializer):   
    class Meta:
        model=RelacionFideicomisoActor
        fields=['Fideicomiso','TipoActor']
        
class RelacionFideicomisoActorReadSerializer(serializers.ModelSerializer):
    Fideicomiso = FideicomisoSerializer()
    TipoActor= TipoActorDeContratoSerializer()
    class Meta:
        model=RelacionFideicomisoActor
        fields='__all__'
        
class ActorDeContratoReadSerializer(serializers.ModelSerializer):   
    FideicomisosAsociados = serializers.SerializerMethodField()
    class Meta:
        model = ActorDeContrato
        fields = '__all__'  
        
    def get_FideicomisosAsociados(self, obj):
        relaciones = RelacionFideicomisoActor.objects.filter(Actor=obj)
        serializer = RelacionFideicomisoActorReadSerializer(instance=relaciones, many=True)
        return serializer.data

class ActorDeContratoCreateSerializer(serializers.ModelSerializer):   
    FideicomisosAsociados = serializers.SerializerMethodField()
    class Meta:
        model = ActorDeContrato
        fields = '__all__'  
        
    def get_FideicomisosAsociados(self, obj):
        relaciones = RelacionFideicomisoActor.objects.filter(Actor=obj)
        serializer = RelacionFideicomisoActorCreateSerializer(instance=relaciones, many=True)
        return serializer.data


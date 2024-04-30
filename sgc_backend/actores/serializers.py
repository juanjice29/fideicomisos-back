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
        fields=['fideicomiso','tipoActor']
        
class RelacionFideicomisoActorReadSerializer(serializers.ModelSerializer):
    fideicomiso = FideicomisoSerializer()
    tipoActor= TipoActorDeContratoSerializer()
    class Meta:
        model=RelacionFideicomisoActor
        fields='__all__'
        
class ActorDeContratoReadSerializer(serializers.ModelSerializer):   
    fideicomisoAsociado = RelacionFideicomisoActorReadSerializer(source="relacionfideicomisoactor_set", many=True)
    class Meta:
        model = ActorDeContrato
        fields = '__all__'  
    
class ActorDeContratoCreateSerializer(serializers.ModelSerializer):   
    fideicomisoAsociado = RelacionFideicomisoActorCreateSerializer(source="relacionfideicomisoactor_set", many=True)    
    class Meta:
        model = ActorDeContrato
        fields = '__all__'  
    
    def create(self, validated_data):
        print("validated data",validated_data)
        fideicomisos_data = validated_data.pop('relacionfideicomisoactor_set')
        print("fideicomiso_data,",fideicomisos_data)
        for fideicomiso_data in fideicomisos_data:
            print("fideicomiso data",fideicomiso_data)
        actor = ActorDeContrato.objects.create(**validated_data)
        for fideicomiso_data in fideicomisos_data:
            print(fideicomiso_data)
            RelacionFideicomisoActor.objects.create(actor=actor, **fideicomiso_data)
        return actor
    


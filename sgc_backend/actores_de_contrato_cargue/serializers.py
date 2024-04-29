from rest_framework import serializers
from .models import ActorDeContrato
from fidecomisos.models import Encargo
from fidecomisos.serializers import EncargoSerializer
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
    TipoActor=TipoActorDeContratoSerializer()
    class Meta:
        model = ActorDeContrato
        fields = '__all__'       
    
class ActorDeContratoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActorDeContrato
        fields = '__all__' 

class RelacionFideicomisoActorSerializer(serializers.ModelSerializer):
    class Meta:
        model=RelacionFideicomisoActor
        fields='__all__'
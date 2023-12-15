from rest_framework import serializers
from .models import ActorDeContrato
from fidecomisos.models import Encargo
from fidecomisos.serializers import EncargoSerializer
from rest_framework import serializers
from .models import TipoActorDeContrato
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
    
   
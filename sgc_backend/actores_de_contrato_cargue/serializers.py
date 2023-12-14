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
        fields = ['TipoIdentificacion', 'NumeroIdentificacion', 'Nombre', 'TipoActor', 'FideicomisoAsociado','EncargoAsociado', 'FechaActualizacion']
    
    def validate(self, data):
        numero_identificacion = data.get('NumeroIdentificacion')
        fideicomiso_asociado = data.get('FideicomisoAsociado')

        if ActorDeContrato.objects.filter(NumeroIdentificacion=numero_identificacion, FideicomisoAsociado=fideicomiso_asociado).exists():
            raise serializers.ValidationError("ActorDeContrato with this NumeroIdentificacion and FideicomisoAsociado already exists")
        return data  

    def validate_NumeroIdentificacion(self, value):
        # Add your validations here
        if not value.isdigit():
            raise serializers.ValidationError("NumeroIdentificacion must be a number")
        return value

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        encargos = Encargo.objects.filter(FideicomisoAsociado=instance.FideicomisoAsociado)
        representation['EncargoAsociado'] = EncargoSerializer(encargos, many=True).data
        return representation
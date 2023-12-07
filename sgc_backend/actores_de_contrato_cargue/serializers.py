from rest_framework import serializers
from .models import ActorDeContrato

class ActorDeContratoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActorDeContrato
        fields = ['TipoIdentificacion', 'NumeroIdentificacion', 'Nombre', 'TipoActor', 'FideicomisoAsociado', 'FechaActualizacion']
    
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
from rest_framework import serializers
from .models import ActorDeContrato
from fidecomisos.models import Encargo
from fidecomisos.serializers import EncargoSerializer,FideicomisoSerializer
from rest_framework import serializers
from .models import TipoActorDeContrato,RelacionFideicomisoActor
from rest_framework import serializers
from .models import Encargo,Fideicomiso


class EncargoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Encargo
        fields = '__all__'
        
class TipoActorDeContratoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoActorDeContrato
        fields = '__all__'
        
class RelacionFideicomisoActorSerializer(serializers.ModelSerializer):
    fideicomiso = FideicomisoSerializer()
    tipoActor= TipoActorDeContratoSerializer()
    class Meta:
        model=RelacionFideicomisoActor
        fields='__all__'

class RelacionFideicomisoActorCreateSerializer(serializers.ModelSerializer):
    fideicomiso = serializers.PrimaryKeyRelatedField(queryset=Fideicomiso.objects.all())
    tipoActor = serializers.PrimaryKeyRelatedField(queryset=TipoActorDeContrato.objects.all())
    class Meta:
        model = RelacionFideicomisoActor
        fields = ['fideicomiso', 'tipoActor']

class ActorDeContratoSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    fideicomisoAsociado = RelacionFideicomisoActorSerializer(source="relacionfideicomisoactor_set", many=True,read_only=True)
    class Meta:
        model = ActorDeContrato
        fields = '__all__'   

class ActorDeContratoSerializerCreate(serializers.ModelSerializer):   
    fideicomisoAsociado = RelacionFideicomisoActorCreateSerializer(source="relacionfideicomisoactor_set", many=True)
    class Meta:
        model = ActorDeContrato
        fields = '__all__' 
        read_only_fields = ['fechaCreacion', 'fechaActualizacion'] 
    def create(self,validate_data):
        fideicomiso_data=validate_data.pop('relacionfideicomisoactor_set')
        actor=ActorDeContrato.objects.create(**validate_data)
        for fideicomiso in fideicomiso_data:            
            actor.fideicomisoAsociado.add(fideicomiso['fideicomiso'],through_defaults={'tipoActor':fideicomiso['tipoActor']})
        return actor
    
class ActorDeContratoSerializerUpdate(serializers.ModelSerializer):   
    fideicomisoAsociado = RelacionFideicomisoActorCreateSerializer(source="relacionfideicomisoactor_set", many=True)
    class Meta:
        model = ActorDeContrato
        fields = '__all__' 
        read_only_fields = ['fechaCreacion', 'fechaActualizacion', 'tipoIdentificacion', 'numeroIdentificacion']       
    def update(self,instance,validated_data):
        fideicomiso_data = validated_data.pop('relacionfideicomisoactor_set')
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        for fideicomiso in fideicomiso_data:            
            instance.fideicomisoAsociado.add(fideicomiso['fideicomiso'], through_defaults={'tipoActor': fideicomiso['tipoActor']})
            try:            
                relacion = instance.relacionfideicomisoactor_set.get(fideicomiso=fideicomiso['fideicomiso'])
            # Si la relación existe, actualizarla
                for attr, value in fideicomiso.items():
                    setattr(relacion, attr, value)
                relacion.save()
            except RelacionFideicomisoActor.DoesNotExist:
            # Si la relación no existe, agregarla
                instance.fideicomisoAsociado.add(fideicomiso['fideicomiso'], through_defaults={'tipoActor': fideicomiso['tipoActor']})
        # Obtener los fideicomisos actuales
        delete_non_serialized=validated_data.pop('delete_non_serialized', False)
        if delete_non_serialized:
            relaciones_current = set(instance.relacionfideicomisoactor_set.all().values_list('fideicomiso', flat=True)) 
            to_delete = relaciones_current - set(f['fideicomiso'].codigoSFC for f in fideicomiso_data)            
            instance.relacionfideicomisoactor_set.filter(fideicomiso__in=to_delete).delete()
    
        instance.save()
        return instance


    


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
        fideicomisos_data = validated_data.pop('relacionfideicomisoactor_set')  
        actor = ActorDeContrato.objects.create(**validated_data)
        for fideicomiso_data in fideicomisos_data:
            print(fideicomiso_data)
            RelacionFideicomisoActor.objects.create(actor=actor, **fideicomiso_data)
        return actor
    
    def update(self,instance,validated_data):
        restart_relations = self.context.get('restart_relations', False)
        relaciones_todas = instance.relacionfideicomisoactor_set.all()
        fideicomisos_data = validated_data.pop('relacionfideicomisoactor_set',[])        
        fideicomisos_ids = [item['fideicomiso'] for item in fideicomisos_data]
        relaciones_existente = relaciones_todas.filter(fideicomiso__in=fideicomisos_ids)        
        relaciones_existente_ids = [item.fideicomiso for item in relaciones_existente]
        
        for relacion in relaciones_existente:            
            relacion_data = next(item for item in fideicomisos_data if item['fideicomiso'] == relacion.fideicomiso)            
            relacion.tipoActor = relacion_data['tipoActor']
            relacion.save() 

        nuevos_fideicomisos = [item for item in fideicomisos_data if item['fideicomiso'] not in relaciones_existente_ids]    

        for nuevo_fideicomiso in nuevos_fideicomisos:            
            RelacionFideicomisoActor.objects.create(actor=instance, **nuevo_fideicomiso)

        if restart_relations:
            for relacion in relaciones_todas:
                if relacion.fideicomiso not in fideicomisos_ids:
                    relacion.delete()                    

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance
    


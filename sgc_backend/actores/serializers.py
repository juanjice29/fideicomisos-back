from rest_framework import serializers
from .models import ActorDeContrato
from fidecomisos.models import Encargo
from fidecomisos.serializers import EncargoSerializer,FideicomisoSerializer
from rest_framework import serializers
from .models import TipoActorDeContrato,RelacionFideicomisoActor,ActorDeContratoNatural,ActorDeContratoJuridico,RelacionFideicomisoFuturoComprador
from rest_framework import serializers
from .models import Encargo,Fideicomiso,FuturoComprador
from django.db import transaction

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
    tipoActor = TipoActorDeContratoSerializer(many=True)
    class Meta:
        model=RelacionFideicomisoActor
        fields='__all__'
class RelacionFideicomisoFuturoSerializer(serializers.ModelSerializer):
    fideicomiso = FideicomisoSerializer()    
    class Meta:
        model=RelacionFideicomisoFuturoComprador
        fields='__all__'
class RelacionFideicomisoActorCreateSerializer(serializers.ModelSerializer):
    fideicomiso = serializers.PrimaryKeyRelatedField(queryset=Fideicomiso.objects.all())    
    class Meta:
        model = RelacionFideicomisoActor
        fields = ['fideicomiso', 'tipoActor']
class RelacionFideicomisoFuturoCreateSerializer(serializers.ModelSerializer):
    fideicomiso = serializers.PrimaryKeyRelatedField(queryset=Fideicomiso.objects.all())    
    class Meta:
        model = RelacionFideicomisoFuturoComprador
        fields = ['fideicomiso']

class ActorDeContratoNaturalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActorDeContratoNatural
        fields = '__all__'

class ActorDeContratoJuridicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActorDeContratoJuridico
        fields = '__all__'

class ActorDeContratoSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    fideicomisoAsociado = RelacionFideicomisoActorSerializer(source="relacionfideicomisoactor_set", many=True,read_only=True)    
    actorNatural = ActorDeContratoNaturalSerializer(source='actordecontratonatural',read_only=True)
    actorJuridico = ActorDeContratoJuridicoSerializer(source='actordecontratojuridico',read_only=True)
    
    class Meta:
        model = ActorDeContrato
        fields='__all__'  

class FuturoCompradorSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    numeroIdentificacion = serializers.CharField(allow_blank=True, required=False)
    fideicomisoAsociado = RelacionFideicomisoFuturoCreateSerializer(source="relacionfideicomisofuturo_set", many=True,read_only=True)    
    class Meta:
        model = FuturoComprador
        fields = '__all__'
class ActorDeContratoNaturalCreateSerializer(serializers.ModelSerializer):   
    fideicomisoAsociado = RelacionFideicomisoActorCreateSerializer(source="relacionfideicomisoactor_set", many=True)
    class Meta:
        model = ActorDeContratoNatural
        fields = '__all__' 
        read_only_fields = ['fechaCreacion', 'fechaActualizacion'] 
    @transaction.atomic
    def create(self,validate_data):
        fideicomiso_data=validate_data.pop('relacionfideicomisoactor_set')
        actor=ActorDeContratoNatural.objects.create(**validate_data)
        grupo_fideicomiso = {}             
        for fideicomiso in fideicomiso_data:  
            fideicomiso_inst=fideicomiso['fideicomiso']
            tipo_actor_ids=fideicomiso['tipoActor']  
            relacion = RelacionFideicomisoActor.objects.create(actor=actor, fideicomiso=fideicomiso_inst)

            if tipo_actor_ids:
                relacion.tipoActor.set(tipo_actor_ids)        
            #actor.fideicomisoAsociado.add(fideicomiso['fideicomiso'],through_defaults={'tipoActor':fideicomiso['tipoActor']})
        return actor

class ActorDeContratoNaturalUpdateSerializer(serializers.ModelSerializer):   
    fideicomisoAsociado = RelacionFideicomisoActorCreateSerializer(source="relacionfideicomisoactor_set", many=True)
    class Meta:
        model = ActorDeContratoNatural
        fields = '__all__' 
        read_only_fields = ['fechaCreacion', 'fechaActualizacion', 'tipoIdentificacion', 'numeroIdentificacion']      
    @transaction.atomic    
    def update(self,instance,validated_data):
        
        fideicomiso_data = validated_data.pop('relacionfideicomisoactor_set')
        preserve_non_serialized_tp_actor = validated_data.pop('preserve_non_serialized_tp_actor', False) 
        delete_non_serialized=validated_data.pop('delete_non_serialized', False)
        
        super().update(instance, validated_data)

    
        ActorDeContratoNatural.objects.filter(id=instance.id).update(
         primerNombre=validated_data.get('primerNombre'),
         segundoNombre=validated_data.get('segundoNombre'),
         primerApellido=validated_data.get('primerApellido'),
         segundoApellido=validated_data.get('segundoApellido')
        )
        # instance.primerNombre = validated_data.get('primerNombre', instance.primerNombre)
        # instance.segundoNombre = validated_data.get('segundoNombre', instance.segundoNombre)
        # instance.primerApellido = validated_data.get('primerApellido', instance.primerApellido)
        # instance.segundoApellido = validated_data.get('segundoApellido', instance.segundoApellido)

        # instance.save()        
        print("valor instancia : ",instance.primerNombre)
        for fideicomiso in fideicomiso_data:            
            fideicomiso_inst = fideicomiso['fideicomiso']
            tipo_actor_ids = fideicomiso['tipoActor']
            # Try to get the existing instance
            
            relacion = instance.relacionfideicomisoactor_set.filter(fideicomiso=fideicomiso_inst).first()
            if relacion:                
                if tipo_actor_ids:
                    if preserve_non_serialized_tp_actor:
                    # Get the existing tipoActor ids
                        existing_tipo_actor_ids = list(relacion.tipoActor.values_list('id', flat=True))
                    # Add the new ids to the existing ones
                        tipo_actor_ids += [id for id in existing_tipo_actor_ids if id not in tipo_actor_ids]                
                    relacion.tipoActor.set(tipo_actor_ids)
                # If it doesn't exist, create a new one
            else:
                relacion = RelacionFideicomisoActor.objects.create(actor=instance, fideicomiso=fideicomiso_inst)
                if tipo_actor_ids:
                    relacion.tipoActor.set(tipo_actor_ids)           
        
        if delete_non_serialized:
            relaciones_current = set(instance.relacionfideicomisoactor_set.all().values_list('fideicomiso', flat=True)) 
            to_delete = relaciones_current - set(f['fideicomiso'].codigoSFC for f in fideicomiso_data)            
            instance.relacionfideicomisoactor_set.filter(fideicomiso__in=to_delete).delete()
        
        #instance.save()
        return instance
class ActorDeContratoJuridicoCreateSerializer(serializers.ModelSerializer):   
    fideicomisoAsociado = RelacionFideicomisoActorCreateSerializer(source="relacionfideicomisoactor_set", many=True)
    class Meta:
        model = ActorDeContratoJuridico
        fields = '__all__' 
        read_only_fields = ['fechaCreacion', 'fechaActualizacion'] 
    @transaction.atomic
    def create(self,validate_data):
        fideicomiso_data=validate_data.pop('relacionfideicomisoactor_set')
        actor=ActorDeContratoJuridico.objects.create(**validate_data)
        grupo_fideicomiso = {}             
        for fideicomiso in fideicomiso_data:  
            fideicomiso_inst=fideicomiso['fideicomiso']
            tipo_actor_ids=fideicomiso['tipoActor']  
            relacion = RelacionFideicomisoActor.objects.create(actor=actor, fideicomiso=fideicomiso_inst)

            if tipo_actor_ids:
                relacion.tipoActor.set(tipo_actor_ids)        
            #actor.fideicomisoAsociado.add(fideicomiso['fideicomiso'],through_defaults={'tipoActor':fideicomiso['tipoActor']})
        return actor

class ActorDeContratoJuridicoUpdateSerializer(serializers.ModelSerializer):   
    fideicomisoAsociado = RelacionFideicomisoActorCreateSerializer(source="relacionfideicomisoactor_set", many=True)
    class Meta:
        model = ActorDeContratoJuridico
        fields = '__all__' 
        read_only_fields = ['fechaCreacion', 'fechaActualizacion', 'tipoIdentificacion', 'numeroIdentificacion']      
    @transaction.atomic    
    def update(self,instance,validated_data):
        fideicomiso_data = validated_data.pop('relacionfideicomisoactor_set')
        for attr, value in validated_data.items():            
            setattr(instance, attr, value)
        instance.save()
        ActorDeContratoJuridico.objects.filter(id=instance.id).update(
            razonSocialNombre=validated_data.get('razonSocialNombre')
        )
        preserve_non_serialized_tp_actor = validated_data.pop('preserve_non_serialized_tp_actor', False) 
        delete_non_serialized=validated_data.pop('delete_non_serialized', False)           
        for fideicomiso in fideicomiso_data:            
            fideicomiso_inst = fideicomiso['fideicomiso']
            tipo_actor_ids = fideicomiso['tipoActor']
            # Try to get the existing instance
            try:
                relacion = instance.relacionfideicomisoactor_set.get(fideicomiso=fideicomiso_inst)                
                if tipo_actor_ids:
                    if preserve_non_serialized_tp_actor:
                    # Get the existing tipoActor ids
                        existing_tipo_actor_ids = list(relacion.tipoActor.values_list('id', flat=True))
                    # Add the new ids to the existing ones
                        tipo_actor_ids += [id for id in existing_tipo_actor_ids if id not in tipo_actor_ids]                
                    relacion.tipoActor.set(tipo_actor_ids)
            # If it doesn't exist, create a new one
            except RelacionFideicomisoActor.DoesNotExist:                
                relacion = RelacionFideicomisoActor.objects.create(actor=instance, fideicomiso=fideicomiso_inst)
                if tipo_actor_ids:
                    relacion.tipoActor.set(tipo_actor_ids)
            except Exception as e:                
                print(e)
        
        if delete_non_serialized:
            relaciones_current = set(instance.relacionfideicomisoactor_set.all().values_list('fideicomiso', flat=True)) 
            to_delete = relaciones_current - set(f['fideicomiso'].codigoSFC for f in fideicomiso_data)            
            instance.relacionfideicomisoactor_set.filter(fideicomiso__in=to_delete).delete()        
        instance.save()
        print("valor instancia : ",instance.razonSocialNombre)
        return instance




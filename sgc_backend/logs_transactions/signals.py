from django.db.models.signals import pre_save, post_save, pre_delete,m2m_changed
from django.dispatch import receiver
from django.core.serializers.json import DjangoJSONEncoder
from sgc_backend.middleware import get_current_request,get_request_id
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from .models import Log_Cambios_Create, Log_Cambios_Update, Log_Cambios_Delete,Log_Cambios_M2M
from django.contrib.contenttypes.models import ContentType
import logging
import json
import uuid
import sgc_backend.settings 
from django.core.mail import send_mail
from celery import current_task
from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from celery.result import AsyncResult
from process.models import DisparadorEjecucion
from django.forms.models import model_to_dict
from django.db import models
import requests
import logging
from actores.models import ActorDeContratoNatural, ActorDeContratoJuridico, ActorDeContrato
from django.db.models.signals import post_init
from django.dispatch import receiver
from actores.models import ActorDeContrato
from django.core import serializers
import threading
_thread_locals = threading.local()
valid_sender=['fideicomisos','accounts','public','actores','ActorDeContrato','ActorDeContratoNatural','ActorDeContratoJuridico']
def get_current_user():
    return getattr(_thread_locals, 'user', None)

def set_current_user(user):
    _thread_locals.user = user
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

logger = logging.getLogger(__name__)
@receiver(post_save)
def post_save_receiver(sender, instance, created, **kwargs):
    def _post_save_receiver():
        try:
            logger.info(f"post_save signal received from {sender}")
            logger.info(f"Instance: {instance}")
            if sender is not None:
                logger.info(f"Sender: {sender.__name__}")
                app_name_sender = sender.__name__
            else:
                logger.error("Sender is None")
                return 
            if app_name_sender not in valid_sender:
                #logger.info(f"Invalid sender: {app_name_sender}")
                return
            request_signal = str(uuid.uuid4())
            request_id=get_request_id()    
            request = get_current_request()
            tipo_proceso = DisparadorEjecucion.objects.get(acronimo='MAN')
            logger.info(f"Request: {request}")
            #logger.info(f"Current task: {current_task}")
            #logger.info(f"Is current task eager: {current_task.request.is_eager if current_task else None}")
            if current_task and current_task.request.is_eager == False:
                task_result = AsyncResult(current_task.request.id)
                if 'usuario_id' in task_result.result:
                    try:
                        user_id = task_result.result['usuario_id']
                        user = User.objects.get(pk=user_id)
                        ip = task_result.result['ip_address']
                        request_id=task_result.result['request_id']
                        tp_proceso=task_result.result['disparador']
                        tipo_proceso = DisparadorEjecucion.objects.get(acronimo=tp_proceso)
                    except User.DoesNotExist:
                        logger.error("User does not exist")
                        return 
                else:
                    logger.error("No usuario_id in current task request")
                    return
            else:
                if request is None:
                    logger.error("No current request")
                    return
                if request is not None:
                    ip = get_client_ip(request)
                else:
                    logger.error("Request is None")
                    return
                try:
                    user = User.objects.get(username=request.user.username)
                except User.DoesNotExist:
                    logger.error(f"User '{request.user.username}' does not exist")
                    return  # get the User instance
            logger.info(f"User: {user}")
            if created:     
                logger.info(f"Instance created first: {instance}")
                if isinstance(instance, ActorDeContratoNatural):
                    person_type = 'N'
                    full_name = f"{instance.primerNombre} {instance.segundoNombre} {instance.primerApellido} {instance.segundoApellido}"
                else:
                    person_type = 'J'
                    full_name = instance.razonSocialNombre         
                logger.info(f"Full name: {full_name}")       
                instance_json = json.dumps(serialize_instance(instance), cls=DjangoJSONEncoder, ensure_ascii=False)      
                logger.info(f"Instance created: {instance}")        
                Log_Cambios_Create.objects.create(
                    requestId=request_id,
                    contentObject=instance,
                    usuario=user,  # assign the User instance
                    ip=ip,
                    nombreModelo=sender.__name__,                
                    nuevoValor=instance_json,
                    signalId=request_signal,
                    tipoProcesoEjecucion=tipo_proceso
                ) 
                logger.info(f"Instance created: {instance.tipoIdentificacion.tipoDocumento}")
                data = {
                    "customer_Id_Identification_type": instance.tipoIdentificacion.tipoDocumento,
                    "customer_Identification_Number": instance.numeroIdentificacion,
                    "customer_Full_Name": full_name,
                    "customer_Person_Type": person_type,
                    "id_Identification_Type": instance.tipoIdentificacion.tipoDocumento,
                    "identification_Number": instance.numeroIdentificacion,
                    "full_Name": full_name,
                    "relationship_Type": 1,
                    "person_Type": person_type,
                    "id_App": 2,
                    "UserName": "PRUEBAS",
                    "fullNameOrdered": full_name
                }

                # Make the API call
                logger.info(f"API request: {data}")
                response = requests.post("http://192.168.169.145:8089/api/BindingList/ValidateBindingList", json=data, verify=False)
                response_data = response.json()
                logger.info(f"API response: {response_data}")
                # Check if the actor is in any list
                if any(result['result'] for result in response_data['resultData'][0]['resultList']):
                    # Send an email
                    send_mail(
                        'Actor in List',
                        f'El actor {full_name} con tipo de identificacion {instance.tipoIdentificacion} con numero de identificacion {instance.numeroIdentificacion}  esta en una lista.',
                        'recepcionpruebasrendir2@bancocajasocial.com',
                        ['notificacionpruebasrendir@bancocajasocial.com'],
                        fail_silently=False,
                    )
        except IntegrityError:
            logger.info("Ocurrio un error de integridad en la base de datos debido a un constraint")
        except ValidationError:
            logger.info("Un campo contiene un valor invalido")
        except Exception as e:
            logger.info(f"Un error ocurrio: {str(e)}")
    transaction.on_commit(_post_save_receiver)
@receiver(pre_save)
def pre_save_receiver(sender, instance, update_fields,**kwargs):
    def _pre_save_receiver():
        try:
            
            #logger.info(f"pre_save signal received from {sender}")
            logger.info(f"Instance: {instance}")
            if sender is not None:
                logger.info(f"Sender: {sender.__name__}")
                app_name_sender = sender.__name__
            else:
                logger.error("Sender is None")
                return 
            if app_name_sender not in valid_sender:
                #logger.info(f"Invalid sender: {app_name_sender}")
                return
            logger.info(f"pre_save signal received from {sender.__name__} for instance {instance.pk}")
            request = get_current_request()
            signal_id=str(uuid.uuid4()) 
            tipo_proceso = DisparadorEjecucion.objects.get(acronimo='MAN')
            logger.info(f"Request: {request}")
            #logger.info(f"Current task: {current_task}")
           # logger.info(f"Is current task eager: {current_task.request.is_eager if current_task else None}")      
            if current_task and current_task.request.is_eager == False:
                task_result = AsyncResult(current_task.request.id)
                if 'usuario_id' in task_result.result:
                    try:
                        logger.info(f"Task result: {task_result.result}")
                        user_id = task_result.result['usuario_id']
                        user = User.objects.get(pk=user_id)
                        ip = task_result.result['ip_address']
                        request_id=task_result.result['request_id']
                        tp_proceso=task_result.result['disparador']
                        tipo_proceso = DisparadorEjecucion.objects.get(acronimo=tp_proceso)
                    except User.DoesNotExist:
                        logger.error("User does not exist")
                        return 
                else:
                    logger.error("No usuario_id in current task request")
                    return
            else:
                
                request_id=get_request_id()
                if request is not None:
                    ip = get_client_ip(request)
                    logger.error("No current request")
                else:
                    logger.error("Request is None")
                    return
                try:
                    user = User.objects.get(username=request.user.username)
                except User.DoesNotExist:
                    logger.error(f"User '{request.user.username}' does not exist")
                    return  # get the User instance
            logger.info(f"User: {user}")
            
            if instance.pk is None:
                # Instance is new, so it has no old value
                return        
            
            if update_fields is None:
                #changed_fields = instance.__dict__
                changed_fields = serialize_instance_update(instance)
                for field in instance._meta.parents.values():
                    changed_fields.update(field)
            else:
                changed_fields = {field: getattr(instance, field) for field in update_fields}
            if changed_fields is None:
                return  
            logger.info(f"Changed fields: {changed_fields}")
            logger.info(f"Intance: {instance}")
            Log_Cambios_Update.objects.create(
                usuario=user,
                ip=ip,
                nombreModelo=sender.__name__,
                cambiosValor=changed_fields,            
                contentObject=instance,
                requestId=request_id,
                signalId=signal_id,
                tipoProcesoEjecucion=tipo_proceso
            )
        except IntegrityError:
            # Handle the case where the instance violates a database constraint
            logger.info("Ocurrio un error de integridad en la base de datos debido a un constraint")
        except ValidationError:
            # Handle the case where an instance's field data is invalid
            logger.info("Un campo contiene un valor invalido")
        except Exception as e:
            # Handle all other types of errors
            logger.info(f"Un error ocurrio: {str(e)}")
    transaction.on_commit(_pre_save_receiver)
@receiver(pre_delete)
def pre_delete_receiver(sender, instance, **kwargs):
    def _pre_delete_receiver():    
        try:
            #logger.info(f"pre_delete signal received from {sender}")
            #logger.info(f"Instance: {instance}")
            app_name_sender=sender._meta.app_label
            if app_name_sender not in valid_sender:
                #logger.info(f"Invalid sender: {app_name_sender}")
                return
            request = get_current_request()
            request_id=get_request_id()
            signal_id = str(uuid.uuid4()) 
            tipo_proceso = DisparadorEjecucion.objects.get(acronimo='MAN')
            #logger.info(f"Current task: {current_task}")
            #logger.info(f"Is current task eager: {current_task.request.is_eager if current_task else None}")
            if current_task and current_task.request.is_eager == False:
                task_result = AsyncResult(current_task.request.id)
                if 'usuario_id' in task_result.result:
                    
                    try:
                        user_id = task_result.result['usuario_id']
                        user = User.objects.get(pk=user_id)
                        ip = task_result.result['ip_address']
                        request_id=task_result.result['request_id']
                        tp_proceso=task_result.result['disparador']
                        tipo_proceso = DisparadorEjecucion.objects.get(acronimo=tp_proceso)
                    except User.DoesNotExist:
                        logger.error("User does not exist")
                        return 
                else:
                    logger.error("No usuario_id in current task request")
                    return
            else:
                if request is None:
                    logger.error("No current request")
                    return
                ip = get_client_ip(request)
                try:
                    user = User.objects.get(username=request.user.username)
                except User.DoesNotExist:
                    #logger.error(f"User '{request.user.username}' does not exist")
                    return  # get the User instance
            #logger.info(f"User: {user}")
            
            user = User.objects.get(username=request.user.username)
            old_instance_json=json.dumps(serialize_instance(instance), cls=DjangoJSONEncoder, ensure_ascii=False) 
            Log_Cambios_Delete.objects.create(
                usuario=user,
                ip=get_client_ip(request),
                nombreModelo=sender.__name__,
                antiguoValor=old_instance_json,            
                contentObject=instance,
                requestId=request_id,
                signalId=signal_id,
                tipoProcesoEjecucion=tipo_proceso
            )    
    

        except IntegrityError:
            # Handle the case where the instance violates a database constraint
            logger.info("Ocurrio un error de integridad en la base de datos debido a un constraint")
        except ValidationError:
            # Handle the case where an instance's field data is invalid
            logger.info("Un campo contiene un valor invalido")
        except Exception as e:
            # Handle all other types of errors
            logger.info(f"Un error ocurrio: {str(e)}")   
    transaction.on_commit(_pre_delete_receiver)
"""@receiver(m2m_changed)
def save_initial_m2m_state(sender, instance, action, **kwargs):
    if action == "pre_add" or action == "pre_remove" or action == "pre_clear":
        m2m_fields = [field for field in instance._meta.get_fields() if isinstance(field, models.ManyToManyField)]
        instance._initial_m2m_state = {field.name: [obj.pk for obj in getattr(instance, field.name).all()] for field in m2m_fields}
@receiver(m2m_changed)
def log_m2m_changes(sender, instance, action, pk_set, **kwargs):
    
    #Log changes to many-to-many fields.
    
    app_name_sender=sender._meta.app_label
    if app_name_sender not in valid_sender:
        #logger.info(f"Invalid sender: {app_name_sender}")
        return
    if action in ["post_add", "post_remove", "post_clear"]:
        # Get the name of the many-to-many field
        m2m_field_name = kwargs.get('reverse') and instance.__class__.__name__.lower() or sender.__name__.lower()

        # Get the current user
        request = get_current_request()
        try:
            user = User.objects.get(username=request.user.username)
        except User.DoesNotExist:
            user = None

        # Get the content type for the instance
        content_type = ContentType.objects.get_for_model(instance)
        if kwargs.get('reverse'):
            # If reverse is True, the instance is the related model instance and the parent instance is the one that has the many-to-many field
            parent_instance = sender.objects.get(pk=kwargs.get('instance_pk_set')[0])
        else:
            # If reverse is False, the instance is the one that has the many-to-many field and the parent instance is the related model instance
            parent_instance = instance
        content_type_padre = ContentType.objects.get_for_model(parent_instance)  
        # Log the changes
        Log_Cambios_M2M.objects.create(
            usuario=user,
            ip=request.META.get('REMOTE_ADDR'),
            nombreModelo=sender.__name__,
            objectId=str(instance.pk),
            contentType=content_type,
            nombreModeloPadre=parent_instance.__class__.__name__,
            objectIdPadre=str(parent_instance.pk),
            contentTypePadre=content_type_padre,
            jsonValue=json.dumps(list(pk_set)),
            accion=action,
            requestId=str(uuid.uuid4()), 
        )
"""    
def serialize_instance(instance):
    """
    Serialize a Django model instance to a JSON-compatible dictionary.
    """
    serialized = {}
    for field in instance._meta.fields:
        field_name = field.name
        field_value = getattr(instance, field_name)
        if hasattr(field_value, '_meta'):
            serialized[field_name] = field_value.pk
        else:
            serialized[field_name] = field.value_to_string(instance)
    return serialized
def serialize_instance_update(instance):
    """
    Serialize a Django model instance to a JSON-compatible dictionary.
    """
    serialized = {}
    for field in instance._meta.fields:
        field_name = field.name
        if field_name == '_state':
            continue  # Skip the _state field
        field_value = getattr(instance, field_name)
        # If it's a regular field, convert it to a JSON-compatible value
        serialized[field_name] = field.value_to_string(instance)

    # Handle related objects for foreign key relationships
    for related_object in instance._meta.related_objects:
        if related_object.one_to_many:
            # One-to-many relationship
            related_name = related_object.get_accessor_name()
            related_value = getattr(instance, related_name).all()
            serialized[related_name] = [serialize_instance(obj) for obj in related_value]
        elif related_object.one_to_one:
            # One-to-one relationship
            related_name = related_object.get_accessor_name()
            related_value = getattr(instance, related_name, None)
            if related_value is not None:
                serialized[related_name] = serialize_instance(related_value)

    # Handle many-to-many relationships
    for field in instance._meta.many_to_many:
        field_name = field.name
        field_value = getattr(instance, field_name).all()
        serialized[field_name] = [serialize_instance(obj) for obj in field_value]

    return serialized
def model_to_dict_including_abstract(instance):
    data = model_to_dict(instance)
    for field in instance._meta.fields:
        if field.name not in data and isinstance(field, models.Field):
            data[field.name] = field.value_from_object(instance)
    return data
def get_actor_dict(instance):
    if isinstance(instance, ActorDeContratoNatural):
        return model_to_dict(instance, fields=['primerNombre', 'segundoNombre', 'primerApellido', 'segundoApellido'], exclude=['_state'])
    elif isinstance(instance, ActorDeContratoJuridico):
        return model_to_dict(instance, fields=['razonSocial', 'nombreComercial', 'nit'], exclude=['_state'])
    else:
        return model_to_dict(instance, exclude=['_state'])
def serialize_only_changes_to_json(old_instance, new_instance):
    """
    Serialize the changes between two Django model instances to a JSON string.
    """
    old_instance.update_initial_state()
    new_instance.update_initial_state()
    logger.info(f"Old instance before: {old_instance.__dict__}")
    logger.info(f"New instance before: {new_instance.__dict__}")
    if isinstance(old_instance, ActorDeContrato):
        if hasattr(old_instance, 'actordecontratonatural'):
            old_instance = old_instance.actordecontratonatural
        elif hasattr(old_instance, 'actordecontratojuridico'):
            old_instance = old_instance.actordecontratojuridico
        old_instance_dict = getattr(old_instance, '_initial_state', get_actor_dict(old_instance))
    else:
        old_instance_dict = getattr(old_instance, '_initial_state', model_to_dict_including_abstract(old_instance))
    
    if isinstance(new_instance, ActorDeContrato):
        if hasattr(new_instance, 'actordecontratonatural'):
            new_instance = new_instance.actordecontratonatural
        elif hasattr(new_instance, 'actordecontratojuridico'):
            new_instance = new_instance.actordecontratojuridico
        new_instance_dict = get_actor_dict(new_instance)
    else:
        new_instance_dict = model_to_dict_including_abstract(new_instance)
    logger.info(f"Old instance: {old_instance_dict}")
    logger.info(f"New instance: {new_instance_dict}")
    changed_fields = {}
    for field_name, old_value in old_instance_dict.items():
        new_value = new_instance_dict.get(field_name, None)
        if isinstance(old_instance._meta.get_field(field_name), models.ManyToManyField):
            old_value = [related_object.pk for related_object in old_value.all()]
            new_value = [related_object.pk for related_object in new_value.all()] if new_value is not None else None
        elif isinstance(old_value, models.Model):
            old_value = old_value.pk
            new_value = new_value.pk if new_value is not None else None

        if old_value != new_value:
            changed_fields[field_name] = {
                'old': old_value,
                'new': new_value,
            }

    if not changed_fields:
        return None

    return json.dumps(changed_fields, cls=DjangoJSONEncoder, ensure_ascii=False)

def log_change(change_type, instance, old_instance=None, username='celeryautomate'):
    # Get the celeryautomate user
    User = get_user_model()
    celery_user = User.objects.get(username=username)

    # Serialize the instance
    instance_json = json.dumps(serialize_instance(instance), cls=DjangoJSONEncoder, ensure_ascii=False)

    # Serialize the old instance if it exists
    old_instance_json = json.dumps(serialize_instance(old_instance), cls=DjangoJSONEncoder, ensure_ascii=False) if old_instance else None

    # Create the appropriate log entry based on the type of change
    if change_type == 'create':
        Log_Cambios_Create.objects.create(
            usuario=celery_user,
            nombreModelo=instance.__class__.__name__,
            nuevoValor=instance_json,
            requestId=str(uuid.uuid4()),  # Generate a new UUID for the request
            signalId=str(uuid.uuid4()),  # Generate a new UUID for the signal
        )
    elif change_type == 'update':
        # Serialize the changes between the old and new instances
        changed_fields = serialize_only_changes_to_json(old_instance, instance)

        Log_Cambios_Update.objects.create(
            usuario=celery_user,
            nombreModelo=instance.__class__.__name__,
            cambiosValor=changed_fields,
            contentObject=instance,
            requestId=str(uuid.uuid4()),  # Generate a new UUID for the request
            signalId=str(uuid.uuid4()),  # Generate a new UUID for the signal
        )
    elif change_type == 'delete':
        Log_Cambios_Delete.objects.create(
            usuario=celery_user,
            nombreModelo=instance.__class__.__name__,
            antiguoValor=old_instance_json,
            requestId=str(uuid.uuid4()),  # Generate a new UUID for the request
            signalId=str(uuid.uuid4()),  # Generate a new UUID for the signal
        )

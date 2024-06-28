from django.db.models.signals import pre_save, post_save, pre_delete,m2m_changed
from django.dispatch import receiver
from django.core.serializers.json import DjangoJSONEncoder
from sgc_backend.middleware import get_current_request,get_request_id
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from .models import Log_Cambios_Create, Log_Cambios_Update, Log_Cambios_Delete,Log_Cambios_M2M
import logging
import json
import uuid
from celery import current_task
from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from celery.result import AsyncResult
from process.models import DisparadorEjecucion
import logging


valid_sender=['fideicomisos','accounts','public','actores']

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
            #logger.info(f"post_save signal received from {sender}")
            #logger.info(f"Instance: {instance}")
            app_name_sender=sender._meta.app_label
            if app_name_sender not in valid_sender:
                #logger.info(f"Invalid sender: {app_name_sender}")
                return
            request_signal = str(uuid.uuid4())
            request_id=get_request_id()    
            request = get_current_request()
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
                    logger.error(f"User '{request.user.username}' does not exist")
                    return  # get the User instance
            
            if created:                     
                instance_json = json.dumps(serialize_instance(instance), cls=DjangoJSONEncoder, ensure_ascii=False)              
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
        except IntegrityError:
            logger.info("Ocurrio un error de integridad en la base de datos debido a un constraint")
        except ValidationError:
            logger.info("Un campo contiene un valor invalido")
        except Exception as e:
            logger.info(f"Un error ocurrio: {str(e)}")
    transaction.on_commit(_post_save_receiver)
@receiver(pre_save)
def pre_save_receiver(sender, instance, **kwargs):
    def _pre_save_receiver():
        try:
            #logger.info(f"pre_save signal received from {sender}")
            #logger.info(f"Instance: {instance}")
            app_name_sender=sender._meta.app_label
            if app_name_sender not in valid_sender:
                #logger.info(f"Invalid sender: {app_name_sender}")
                return
            print(app_name_sender)
            request = get_current_request()
            request_id=get_request_id()
            signal_id=str(uuid.uuid4()) 
            tipo_proceso = DisparadorEjecucion.objects.get(acronimo='MAN')
            logger.info(f"Current task: {current_task}")
            logger.info(f"Is current task eager: {current_task.request.is_eager if current_task else None}")      
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
                    #logger.error("No current request")
                    return
                ip = get_client_ip(request)
                try:
                    user = User.objects.get(username=request.user.username)
                except User.DoesNotExist:
                    #logger.error(f"User '{request.user.username}' does not exist")
                    return  # get the User instance
            logger.info(f"User: {user}")
            
            if instance.pk is None:
                # Instance is new, so it has no old value
                return        
            old_instance = sender.objects.get(pk=instance.pk)
            changed_fields=serialize_only_changes_to_json(old_instance,instance)

            if changed_fields is None:
                return   
            logger.info(f"User: {user}")
            user = User.objects.get(username=request.user.username)

            Log_Cambios_Update.objects.create(
                usuario=user,
                ip=get_client_ip(request),
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
def serialize_instance(instance):
    """
    Serialize a Django model instance to a JSON-compatible dictionary.
    """
    serialized = {}
    for field in instance._meta.fields:
        field_name = field.name
        field_value = getattr(instance, field_name)
        # Check if the field value is a model instance
        if hasattr(field_value, '_meta'):
            # If it's a model instance, recursively serialize it
            #serialized[field_name] = serialize_instance(field_value)
            serialized[field_name] = field_value.pk
        else:
            # If it's a regular field, convert it to a JSON-compatible value
            serialized[field_name] = field.value_to_string(instance)
    return serialized

def serialize_only_changes_to_json(old_instance, new_instance):
    """
    Serialize the changes between two Django model instances to a JSON string.
    """
    old_instance_serialized = serialize_instance(old_instance)
    new_instance_serialized = serialize_instance(new_instance)

        # Find the fields that have changed
    changed_fields = {
            field_name: {
                'old': old_value,
                'new': new_instance_serialized.get(field_name, None),
            }
            for field_name, old_value in old_instance_serialized.items()
            if old_value != new_instance_serialized.get(field_name, None)
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

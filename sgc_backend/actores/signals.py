from django.contrib.auth.models import User
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from sgc_backend.middleware import get_current_request,get_request_id
import logging
import json
import uuid
from django.core.serializers.json import DjangoJSONEncoder
from .models import ActorDeContrato
from logs_transactions.models import Log_Cambios_M2M
from django.forms.models import model_to_dict
logger = logging.getLogger(__name__)
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@receiver(m2m_changed, sender=ActorDeContrato.fideicomisoAsociado.through)
def m2m_changed_actor_de_contrato(sender, instance, action, model, pk_set, **kwargs):
    try:
        request = get_current_request()
        request_id=get_request_id()
        signal_id = str(uuid.uuid4())        
        if request is None:
            # No current request
            return

        
        user = User.objects.get(username=request.user.username) 
        ip=  get_client_ip(request)
        
        if action == 'post_add':
            related_objects = sender.objects.filter(
                actor_id= instance.id,
                fideicomiso_id__in= pk_set
            ).first()
            if related_objects is None:                
                return     
            
            # Convert the intermediate data to JSON
            intermediate_data = json.dumps(model_to_dict(related_objects), cls=DjangoJSONEncoder, ensure_ascii=False)          

            Log_Cambios_M2M.objects.create(
                usuario=user,
                ip=ip,
                nombreModelo=sender.__name__,
                jsonValue=intermediate_data,
                accion=action,
                contentObject=related_objects,
                contentObjectPadre=instance,
                requestId=request_id,
                nombreModeloPadre=type(instance).__name__,
                signalId=signal_id
            )
    except Exception as e:
        logger.info(f"Un error ocurrio: {str(e)}")
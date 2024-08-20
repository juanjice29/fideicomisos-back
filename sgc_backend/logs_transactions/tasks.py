from process.models import EstadoEjecucion
from celery import shared_task, current_task
from celery import current_task,shared_task
import requests
import logging
from django.core.mail import send_mail
from django.db import IntegrityError
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

@shared_task
def validate_binding_list_task(data, full_name, instance, usuario_id, ip_address, request_id, disparador, ejecucion=None):
    current_task.update_state(state='PROGRESS', meta={'usuario_id': usuario_id, 'ip_address': ip_address, 'request_id': request_id, 'disparador': disparador})
    logger.info(f"usuario_id: {usuario_id}")
    
    if ejecucion:
        ejecucion.estadoEjecucion = EstadoEjecucion.objects.get(acronimo='PPP')
        ejecucion.save()
    
    logger.info("Starting validate_binding_list_task")
    
    try:
        # Make the API call
        logger.info(f"API request: {data}")
        response = requests.post("http://192.168.169.145:8089/api/BindingList/ValidateBindingList", json=data, verify=False)
        response_data = response.json()
        logger.info(f"API response: {response_data}")

        # Check if the actor is in any list
        if any(result['result'] for result in response_data['resultData'][0]['resultList']):
            subject = f'Actor in List {full_name}, {instance.tipoIdentificacion.tipoDocumento}, {instance.numeroIdentificacion}'
            message = 'El actor esta en una lista.'
            from_email = 'pruebas@example.com'
            recipient_list = ['pruebas@example.com',]
            logger.info(f"Email subject: {subject}")
            logger.info(f"Email message: {message}")
            logger.info(f"From email: {from_email}")
            logger.info(f"Recipient list: {recipient_list}")
            send_mail(
                subject,
                message,
                from_email,
                recipient_list,
                fail_silently=False,
            )
    except IntegrityError:
        logger.info("Ocurrio un error de integridad en la base de datos debido a un constraint")
    except ValidationError:
        logger.info("Un campo contiene un valor invalido")
    except Exception as e:
        logger.info(f"Un error ocurrio: {str(e)}")
        logger.debug("Exception details", exc_info=True)
    
    return "Task completed"
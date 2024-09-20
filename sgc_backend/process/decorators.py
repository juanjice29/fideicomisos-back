from functools import wraps
from django.utils import timezone
from .models import Proceso, EjecucionProceso, EstadoEjecucion, DisparadorEjecucion,TareaProceso,LogEjecucionProceso,TipoLog,LogEjecucionTareaProceso
from celery import current_task
from accounts.models import User
import inspect
from enum import Enum
from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver
from functools import wraps
from logs_transactions.signals import log_change
import traceback
import signal
import logging
from rest_framework.exceptions import NotFound, APIException
logger = logging.getLogger(__name__)
class TipoLogEnum(Enum):
    INFO = "INFO"
    ERROR = "ERR"
    WARN = "WARN"    

def track_process(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f'kwargs received: {kwargs}')
        # Obtener el nombre de la función decorada
        function_name = func.__name__        
        # Obtener la instancia del proceso asociado a la función decorada
        try:  
            usuario_id = kwargs.get('usuario_id')
            logger.info(f'Track process started for user_id: {usuario_id}')
            if usuario_id is None:
                logger.error('usuario_id is None')
                raise User.DoesNotExist('usuario_id is None')
            if not User.objects.filter(id=usuario_id).exists():
                logger.error(f'User with id {usuario_id} does not exist.')
                raise User.DoesNotExist(f"User with id {usuario_id} does not exist.")
            usuario = User.objects.get(id=usuario_id)
            logger.info(f'User {usuario_id} found: {usuario}')       
            proceso = Proceso.objects.get(funcionRelacionada=function_name)
            usuario = User.objects.get(id=kwargs.get('usuario_id'))
            
            ejecucion_proceso = EjecucionProceso()
            ejecucion_proceso.proceso = proceso
            ejecucion_proceso.fechaInicio = timezone.now()
            ejecucion_proceso.estadoEjecucion = EstadoEjecucion.objects.get(acronimo='INI')
            ejecucion_proceso.disparador = DisparadorEjecucion.objects.get(acronimo=kwargs.get('disparador'))
            ejecucion_proceso.usuario = usuario
            ejecucion_proceso.celeryTaskId = current_task.request.id

            ejecucion_proceso.save()

            kwargs['ejecucion'] = ejecucion_proceso    
        except Proceso.DoesNotExist:
            # If the process does not exist, just call the function
            guardarLogEjecucionProceso(ejecucion_proceso,TipoLogEnum.ERROR.value,f"No existe un nombre relacionado con el proceso : {tb}"[:250])
            ejecucion_proceso.fechaFin = timezone.now()
            ejecucion_proceso.estadoEjecucion = EstadoEjecucion.objects.get(acronimo='FAIL')
            ejecucion_proceso.save()
            raise ValueError(f"No existe un proceso asociado a la función {function_name}")
        try:        
            result=func(*args, **kwargs)
            ejecucion_proceso.fechaFin = timezone.now()
            ejecucion_proceso.estadoEjecucion = EstadoEjecucion.objects.get(acronimo='FIN')
            ejecucion_proceso.resultado = result
            ejecucion_proceso.save()
            return result        
        except Exception as e:
            tb = traceback.format_exc()
            guardarLogEjecucionProceso(ejecucion_proceso,TipoLogEnum.ERROR.value,f"error : {str(e)} , linea : {tb}"[:250])
            ejecucion_proceso.fechaFin = timezone.now()
            ejecucion_proceso.estadoEjecucion = EstadoEjecucion.objects.get(acronimo='FAIL')
            ejecucion_proceso.save()
            return "No se pudo completar el proceso"
    wrapper._is_decorated_process = True
    return wrapper

def track_sub_task(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        function_name = func.__name__
        try:
            tarea = TareaProceso.objects.get(funcionRelacionada=function_name)            
            kwargs['tarea'] = tarea            
            result=func(*args,**kwargs)
            return result
        except TareaProceso.DoesNotExist:
            raise ValueError(f"No existe una tarea asociada a la función {function_name}")
    return wrapper

def protected_function_process(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        caller = inspect.currentframe().f_back.f_code.co_name
        caller_func = globals()[caller]
        if not getattr(caller_func, '_is_decorated_process', False):
            raise Exception(f"La función {caller} no puede utilizar la función {func.__name__} directamente. Debe ser llamada desde un proceso.")
        return func(*args, **kwargs)
    return wrapper

def protected_function_task(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        caller = inspect.currentframe().f_back.f_code.co_name
        caller_func = globals()[caller]
        if not getattr(caller_func, '_is_decorated_task', False):
            raise Exception(f"La función {caller} no puede utilizar la función {func.__name__} directamente. Debe ser llamada desde un proceso.")
        return func(*args, **kwargs)
    return wrapper

def guardarLogEjecucionProceso(ejecucion,tipo, mensaje,ordenvisualizacion=0):
    log_ejecucion=LogEjecucionProceso()
    log_ejecucion.ejecucionProceso=ejecucion
    log_ejecucion.tipo=TipoLog.objects.get(acronimo=tipo)
    log_ejecucion.mensaje=mensaje
    log_ejecucion.ordenVisualizacion=ordenvisualizacion
    log_ejecucion.save()
    return log_ejecucion

def guardarLogEjecucionTareaProceso(ejecucion,tarea,tipo,mensaje,ordenvisualizacion=0):
    log_ejecucion=LogEjecucionTareaProceso()
    log_ejecucion.ejecucionProceso=ejecucion
    log_ejecucion.tarea=tarea
    log_ejecucion.tipo=TipoLog.objects.get(acronimo=tipo)
    log_ejecucion.mensaje=mensaje
    log_ejecucion.ordenVisualizacion=ordenvisualizacion
    log_ejecucion.save()
    return log_ejecucion

def abort_task(ejecucion):
    ejecucion.estadoEjecucion=EstadoEjecucion.objects.get(acronimo="ABORT")
    ejecucion.save()    
    
def log_changes(signal, sender):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Connect the signal to the log_change function
            signal.connect(log_change, sender=sender)
            try:
                # Call the function
                result = func(*args, **kwargs)
            finally:
                # Disconnect the signal
                signal.disconnect(log_change, sender=sender)
            return result
        return wrapper
    return decorator


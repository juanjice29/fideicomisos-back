from functools import wraps
from django.utils import timezone
from .models import Proceso, EjecucionProceso, EstadoEjecucion, DisparadorEjecucion,TareaProceso,LogEjecucionProceso,TipoLog,LogEjecucionTareaProceso
from celery import current_task
from accounts.models import User
import inspect
from enum import Enum

class TipoLogEnum(Enum):
    INFO = "INFO"
    ERROR = "ERR"
    WARN = "WARN"
    

def track_process(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Obtener el nombre de la función decorada
        function_name = func.__name__        
        # Obtener la instancia del proceso asociado a la función decorada
        try:            
            proceso = Proceso.objects.get(funcionRelacionada=function_name)
            usuario = User.objects.get(id=kwargs.get('usuario_id'))
            ejecucion_proceso = EjecucionProceso()
            ejecucion_proceso.proceso = proceso
            ejecucion_proceso.fechaInicio = timezone.now()
            ejecucion_proceso.estadoEjecucion = EstadoEjecucion.objects.get(acronimio='INI')
            ejecucion_proceso.disparador = DisparadorEjecucion.objects.get(acronimo='MAN')
            ejecucion_proceso.usuario = usuario
            ejecucion_proceso.celeryTaskId = current_task.request.id

            ejecucion_proceso.save()

            kwargs['ejecucion'] = ejecucion_proceso    
        except Proceso.DoesNotExist:
            # If the process does not exist, just call the function
            raise ValueError(f"No existe un proceso asociado a la función {function_name}")
        try:        
            result=func(*args, **kwargs)
            ejecucion_proceso.fechaFin = timezone.now()
            ejecucion_proceso.estadoEjecucion = EstadoEjecucion.objects.get(acronimio='FIN')
            ejecucion_proceso.resultado = result
            ejecucion_proceso.save()
            return result        
        except Exception as e:
            guardarLogEjecucionProceso(ejecucion_proceso,TipoLogEnum.ERROR.value,str(e)[:100])
            ejecucion_proceso.fechaFin = timezone.now()
            ejecucion_proceso.estadoEjecucion = EstadoEjecucion.objects.get(acronimio='FAIL')
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
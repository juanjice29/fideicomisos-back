from celery import Celery,current_task,shared_task
from celery.contrib.abortable import AbortableTask
import time
from datetime import datetime
import os
from .decorators import TipoLogEnum, guardarLogEjecucionProceso, guardarLogEjecucionTareaProceso, track_process,protected_function_process,track_sub_task
from .models import EjecucionProceso,EstadoEjecucion
import signal



@shared_task(bind=True, base=AbortableTask)
@track_process
def task_process_example(self,tiempo_espera,usuario_id, disparador,ejecucion=None):
       
    ejecucion.estadoEjecucion = EstadoEjecucion.objects.get(acronimo='PPP')
    ejecucion.save()
    guardarLogEjecucionProceso(ejecucion,
                               TipoLogEnum.INFO.value,
                               "Iniciando proceso de ejemplo")
    
    saludar(usuario_id) 
     
    guardarLogEjecucionProceso(ejecucion,
                               TipoLogEnum.INFO.value,
                               "Iniciando tarea que espera")       
    esperar(self,tiempo_espera)   
    guardarLogEjecucionProceso(ejecucion,
                               TipoLogEnum.INFO.value,
                               "Iniciando tarea que guarda el archivo 1",)  
    
    guardarArchivoTxt(contenido=f"Estoy escribiendo mi archivo de ejemplo, del proceso {ejecucion.id}, ",
                      ruta="C:\Salida-sgc",
                      nombre_archivo="archivo.txt",
                      ejecucion=ejecucion)
    
    guardarLogEjecucionProceso(ejecucion,
                               TipoLogEnum.INFO.value,
                               "Iniciando tarea que guarda el archivo 2") 
     
    guardarArchivoTxt(contenido=f"Estoy escribiendo mi archivo de ejemplo, del proceso {ejecucion.id}, ",
                      ruta="C:\Salida-que-no-existe",
                      nombre_archivo="archivo.txt",
                      ejecucion=ejecucion)
    
    guardarLogEjecucionProceso(ejecucion,
                               TipoLogEnum.INFO.value,
                               "Proceso finalizado")  
    return "Proceso finalizado"

def saludar(nombre):
    print(f"Hola , {nombre} , estas ejecutando un proceso!")

def esperar(self,tiempo):
    
    print(f"Esperando {tiempo} segundos")
    for i in range(0,tiempo):        
        if(self.is_aborted()):
            return 
        time.sleep(1)
    print(f"Ya espere {tiempo} segundos")

#ejecucion es un parametro obligatorio que se debe mandar en la funcion, la tarea se calcula sola apartir del nombre de la funcion
@track_sub_task
def guardarArchivoTxt(contenido,ruta, nombre_archivo, tarea=None,ejecucion=None):
    #Aqui se puede controlar tambien que pasa si no tarea y ejecucion no son enviados
    # Crear un archivo y escribir el contenido en él    
    guardarLogEjecucionTareaProceso(ejecucion,tarea,TipoLogEnum.INFO.value,f"Creando archivo {nombre_archivo}")
    try:
        with open(f'{ruta}/{nombre_archivo}', 'w') as f:
            f.write(contenido)
    except Exception as e:
        guardarLogEjecucionTareaProceso(ejecucion,tarea,TipoLogEnum.ERROR.value,f"Error al crear el archivo {nombre_archivo} , {str(e)[:100]}")
        return f"Error al crear el archivo {nombre_archivo}"
    return f"Archivo {nombre_archivo} creado"





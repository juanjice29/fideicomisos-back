import logging
import os
from celery import Celery,current_task,shared_task
from process.decorators import TipoLogEnum, guardarLogEjecucionProceso, guardarLogEjecucionTareaProceso, track_process,protected_function_process,track_sub_task,log_changes
from django import forms
import pandas as pd
from django.db.models.signals import pre_save, post_save, pre_delete
from public.models import TipoDeDocumento,TipoDePersona
from actores.models import TipoActorDeContrato,ActorDeContrato,FuturoComprador
from fidecomisos.models import Fideicomiso
from actores.serializers import TipoActorDeContratoSerializer,\
ActorDeContratoNaturalCreateSerializer,\
ActorDeContratoNaturalUpdateSerializer,\
ActorDeContratoJuridicoUpdateSerializer,\
ActorDeContratoJuridicoCreateSerializer,\
FuturoCompradorSerializer
from sgc_backend.middleware import get_request_id
import json
import traceback
from django.contrib.auth import get_user_model
from public.utils import getTipoPersona
from process.models import EstadoEjecucion
from django.db import transaction
from celery import shared_task, current_task
import requests
from django.apps import apps
import logging
from django.core.mail import send_mail
from django.db import IntegrityError
from django.core.exceptions import ValidationError
import os
logger = logging.getLogger(__name__)
api = os.getenv("API_SALA_DE_VENTAS")
@shared_task
def validate_binding_list_task(data, full_name, instance, usuario_id,tipo_documento,numero_identificacion, ejecucion=None):
    logger.info(f"usuario_id: {usuario_id}")
    if ejecucion:
        ejecucion.estadoEjecucion = EstadoEjecucion.objects.get(acronimo='PPP')
        ejecucion.save()
        guardarLogEjecucionProceso(ejecucion, TipoLogEnum.INFO.value, "Inicio validacion del archivo excel")
    
    logger.info("Starting validate_binding_list_task")
    
    try:
        # Make the API call
        logger.info(f"API request: {data}")
        response = requests.post(api, json=data, verify=False)
        response_data = response.json()
        logger.info(f"API response: {response_data}")

        # Check if the actor is in any list
        if any(result['result'] for result in response_data['resultData'][0]['resultList']):
            subject = f'Actor se encuentra en una lista restrictiva {full_name}, {tipo_documento}, {numero_identificacion}'
            message = 'El actor esta en una lista.'
            from_email = '00J9R7C9@fs.net'
            recipient_list = ['USR-SARLAFTFIDUCIARIA@fundaciongruposocialco.onmicrosoft.com',]
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
    
    if ejecucion:
        guardarLogEjecucionProceso(ejecucion, TipoLogEnum.INFO.value, "Fin de proceso")
    
    return "Task completed"
@shared_task
@track_process
def tkpCargarActoresPorFideiExcel(file_path,fideicomiso,usuario_id, disparador,ejecucion=None):
    ejecucion.estadoEjecucion = EstadoEjecucion.objects.get(acronimo='PPP')
    ejecucion.save()
    guardarLogEjecucionProceso(ejecucion,
                               TipoLogEnum.INFO.value,
                               "Inicio validacion del archivo excel")
    
    df=tkExcelActoresPorFideiToPandas(file_path=file_path,fideicomiso=fideicomiso,ejecucion=ejecucion)
    if df is False:
        guardarLogEjecucionProceso(ejecucion,
                               TipoLogEnum.ERROR.value,
                               "No se pudo leer el archivo de excel")
        return "No se pudo procesar el archivo"
    
    guardarLogEjecucionProceso(ejecucion,
                               TipoLogEnum.INFO.value,
                               "Inicio procesamiento de los registros")
    
    resultado= tkProcesarPandasActores(df=df,ejecucion=ejecucion)

    guardarLogEjecucionProceso(ejecucion,
                               TipoLogEnum.INFO.value,
                               "Fin de proceso, resultados: "+str(resultado))
    
    return str(resultado)
logger = logging.getLogger(__name__)
@shared_task
@track_process
def tkpCargarActoresExcel(file_path,usuario_id,ip_address,request_id, disparador,ejecucion=None):
    current_task.update_state(state='PROGRESS', meta={'usuario_id': usuario_id, 'ip_address': ip_address, 'request_id': request_id,'disparador':disparador})
    logger.info(f"usuario_id: {usuario_id}")
    ejecucion.estadoEjecucion = EstadoEjecucion.objects.get(acronimo='PPP')
    ejecucion.save()
    guardarLogEjecucionProceso(ejecucion,
                               TipoLogEnum.INFO.value,
                               "Inicio validacion del archivo excel")
    logger.info("Starting tkpCargarActoresExcel")
    df=tkExcelActoresToPandas(file_path=file_path,ejecucion=ejecucion)
    if df is False:
        guardarLogEjecucionProceso(ejecucion,
                               TipoLogEnum.ERROR.value,
                               "No se pudo leer el archivo de excel")
        return "No se pudo procesar el archivo"
    
    guardarLogEjecucionProceso(ejecucion,
                               TipoLogEnum.INFO.value,
                               "Inicio procesamiento de los registros")
    
    resultado= tkProcesarPandasActores(df=df,ejecucion=ejecucion,usuario_id=usuario_id)

    guardarLogEjecucionProceso(ejecucion,
                               TipoLogEnum.INFO.value,
                               "Fin de proceso, resultados: "+str(resultado))
    
    return str(resultado)

@track_sub_task
def tkExcelActoresToPandas(file_path,tarea=None,ejecucion=None):
    try:
        logger.info("Starting tkExcelActoresToPandas")
        if not os.path.exists(file_path):
            logger.error(f"File does not exist: {file_path}")
            return False
        default_cols=['tipoIdentificacion','numeroIdentificacion','tipoActor','fideicomiso','primerNombre','segundoNombre','primerApellido','segundoApellido','razonSocialNombre','tipoPersona']
        df=pd.read_excel(file_path, header=None)        
        df.columns = default_cols[:len(df.columns)]
        df = df.drop(df.index[0]) 
        logger.info(f"Dataframe leido: {df}")  
        return df
    except PermissionError:
        logger.error(f"No se tienen permisos para leer el archivo: {file_path}\n{traceback.format_exc()}")
        guardarLogEjecucionTareaProceso(ejecucion,tarea,TipoLogEnum.ERROR.value,f"No se tienen permisos para leer el archivo")
        return False
    except ValueError:
        logger.error(f"El archivo de excel no es valido o esta dañado,revisar columnas: {file_path}\n{traceback.format_exc()}")
        guardarLogEjecucionTareaProceso(ejecucion,tarea,TipoLogEnum.ERROR.value,f"El archivo de excel no es valido o esta dañado,revisar columnas")
        return False
    except MemoryError:
        logger.error(f"El archivo excede la capacidad de memoria de el worker: {file_path}\n{traceback.format_exc()}")
        guardarLogEjecucionTareaProceso(ejecucion,tarea,TipoLogEnum.ERROR.value,f"El archivo excede la capacidad de memoria de el worker")
        return False
    except Exception as e:  
        logger.error(f"Error desconocido transformando archivo: {file_path}\n{traceback.format_exc()}")      
        guardarLogEjecucionTareaProceso(ejecucion,tarea,TipoLogEnum.ERROR.value,f"Error desconocido transformando archivo: {str(e)}")
        return False
    
@track_sub_task
def tkExcelActoresPorFideiToPandas(file_path,fideicomiso,tarea=None,ejecucion=None):
    try:
        default_cols=['tipoIdentificacion','numeroIdentificacion','tipoActor','primerNombre','segundoNombre','primerApellido','segundoApellido','razonSocialNombre','tipoPersona']
        df=pd.read_excel(file_path, header=None)        
        df.columns = default_cols[:len(df.columns)]
        logger.info(f"Dataframe leido: {df}")
        df = df.drop(df.index[0])       
        df=df.assign(fideicomiso=fideicomiso)
        logger.info(f"Dataframe con fideicomiso: {df}")        
        return df
    except PermissionError:
        guardarLogEjecucionTareaProceso(ejecucion,tarea,TipoLogEnum.ERROR.value,f"No se tienen permisos para leer el archivo")
        return False
    except ValueError:
        guardarLogEjecucionTareaProceso(ejecucion,tarea,TipoLogEnum.ERROR.value,f"El archivo de excel no es valido o esta dañado,revisar columnas")
        return False
    except MemoryError:
        guardarLogEjecucionTareaProceso(ejecucion,tarea,TipoLogEnum.ERROR.value,f"El archivo excede la capacidad de memoria de el worker")
        return False
    except Exception as e:        
        guardarLogEjecucionTareaProceso(ejecucion,tarea,TipoLogEnum.ERROR.value,f"Error desconocido transformando archivo: {str(e)}")
        return False

@track_sub_task
def tkProcesarPandasActores( df,tarea=None,ejecucion=None,usuario_id=None):
    resultado={
        'errores':0,
        'actualizados':0,
        'creados':0
    }
    for index,row in df.iterrows():
        try:
            tipoActor = TipoActorDeContrato.objects.get(id=row['tipoActor'])            
            if tipoActor.descripcion == 'Futuro Comprador':
                fideicomiso = Fideicomiso.objects.get(codigoSFC=row['fideicomiso'])
                tipoPersona = TipoDePersona.objects.get(id=row['tipoPersona'])
                if tipoPersona.tipoPersona == 'J':
                    futuro_comprador = FuturoComprador.objects.filter(razonSocialNombre=row['razonSocialNombre'], fideicomisoAsociado=fideicomiso).first()
                else:
                    futuro_comprador = FuturoComprador.objects.filter(primerNombre=row['primerNombre'], primerApellido=row['primerApellido'], fideicomisoAsociado=fideicomiso).first()

                if futuro_comprador:
                    row_dict = row.to_dict()

                    if pd.isna(row_dict.get('tipoIdentificacion')):
                        row_dict.pop('tipoIdentificacion', None)

                    if pd.isna(row_dict.get('numeroIdentificacion')):
                        row_dict.pop('numeroIdentificacion', None)
                    serializer = FuturoCompradorSerializer(data=row.to_dict())
                    if serializer.is_valid():
                        with transaction.atomic():
                            serializer.save()
                            resultado['actualizados'] += 1
                            guardarLogEjecucionTareaProceso(ejecucion, tarea, TipoLogEnum.WARN.value, f"Futuro comprador '{row['primerNombre']} {row['primerApellido']}', en la fila {index} se le sobreescriben los datos.")
                    else:
                        resultado['errores'] += 1
                        guardarLogEjecucionTareaProceso(ejecucion, tarea, TipoLogEnum.ERROR.value, f"Error al sobreescribir datos del futuro comprador en la fila {index}, {serializer.errors}")
                else:
                    row_dict = row.to_dict()
                    if pd.isna(row_dict.get('tipoIdentificacion')):
                        row_dict.pop('tipoIdentificacion', None)
                    if pd.isna(row_dict.get('numeroIdentificacion')):
                        row_dict.pop('numeroIdentificacion', None)
                    serializer = FuturoCompradorSerializer(futuro_comprador, data=row_dict)
                    if serializer.is_valid():
                        with transaction.atomic():
                            serializer.save()
                            resultado['creados'] += 1
                            guardarLogEjecucionTareaProceso(ejecucion, tarea, TipoLogEnum.INFO.value, f"Futuro comprador '{row['primerNombre']} {row['primerApellido']}', en la fila {index} creado exitosamente para el fideicomiso {row['fideicomiso']}")
                    else:
                        resultado['errores'] += 1
                        guardarLogEjecucionTareaProceso(ejecucion, tarea, TipoLogEnum.ERROR.value, f"Error al crear el futuro comprador en la fila {index}, {serializer.errors}")
            else:            
                if pd.isna(row['tipoIdentificacion']) or pd.isna(row['numeroIdentificacion']) or pd.isna(row['tipoActor']):
                    resultado['errores']+=1
                    guardarLogEjecucionTareaProceso(ejecucion,tarea,TipoLogEnum.ERROR.value,f"Datos insuficientes para crear el actor en la fila {index}")
                    continue            
                if not TipoDeDocumento.objects.filter(tipoDocumento=row['tipoIdentificacion']).exists():
                    resultado['errores']+=1
                    guardarLogEjecucionTareaProceso(ejecucion,tarea,TipoLogEnum.ERROR.value,f"El tipo de documento en la fila {index} no existe")
                    continue
                if not TipoActorDeContrato.objects.filter(id=row['tipoActor']).exists():
                    resultado['errores']+=1
                    guardarLogEjecucionTareaProceso(ejecucion,tarea,TipoLogEnum.ERROR.value,f"El tipo de actor en la fila {index} no existe")
                
                tipoIdentificacion=row['tipoIdentificacion']
                numeroIdentificacion=row['numeroIdentificacion']
                tipoPersona=getTipoPersona(tipoIdentificacion)
                if (tipoPersona=='N') and (pd.isna(row['primerNombre']) or pd.isna(row['primerApellido'])):
                    resultado['errores']+=1
                    guardarLogEjecucionTareaProceso(ejecucion,tarea,TipoLogEnum.ERROR.value,f"Primer nombre y Primer apellido requeridos {index}")
                    continue
                if((tipoPersona=='J') and (pd.isna(row['razonSocialNombre']))):
                    resultado['errores']+=1
                    guardarLogEjecucionTareaProceso(ejecucion,tarea,TipoLogEnum.ERROR.value,f"Razon social nombre requerida {index}")
                    continue

                actor=ActorDeContrato.objects.filter(tipoIdentificacion=tipoIdentificacion,numeroIdentificacion=numeroIdentificacion).first()    
                if actor:                
                    serializer=serializarActor(row=row,actor=actor,action='UPDATE')  
                    if serializer.is_valid():
                        with transaction.atomic():
                            serializer.save(preserve_non_serialized_tp_actor=True)
                            resultado['actualizados']+=1
                            guardarLogEjecucionTareaProceso(ejecucion,tarea,TipoLogEnum.WARN.value,f"Actor '{row['tipoIdentificacion']} {row['numeroIdentificacion']}',en la fila {index} se le sobreescriben los datos.")
                    else:
                        resultado['errores']+=1
                        guardarLogEjecucionTareaProceso(ejecucion,tarea,TipoLogEnum.ERROR.value,f"Error al sobreescribir datos del el actor en la fila {index}, {serializer.errors}")  
                    continue
                
                serializer=serializarActor(row=row,action='CREATE')                  
                if serializer.is_valid():     
                    with transaction.atomic():           
                        serializer.save()
                        resultado['creados']+=1
                        guardarLogEjecucionTareaProceso(ejecucion,tarea,TipoLogEnum.INFO.value,f"Actor '{row['tipoIdentificacion']} {row['numeroIdentificacion']}',en la fila {index} creado exitosamente para el fideicomiso {row['fideicomiso']}")
                else:
                    resultado['errores']+=1
                    guardarLogEjecucionTareaProceso(ejecucion,tarea,TipoLogEnum.ERROR.value,f"Error al crear el actor en la fila {index}, {serializer.errors}") 
        except Exception as e:
            resultado['errores']+=1
            tb = traceback.format_exc()
            guardarLogEjecucionTareaProceso(ejecucion,tarea,TipoLogEnum.ERROR.value,f"Error al procesar la fila {index}, {str(e)[:200]} \n {tb}")            
            continue
    return resultado


def serializarActor(row,action,actor=None):
    baseDict={
        'tipoIdentificacion':row['tipoIdentificacion'],
        'numeroIdentificacion':row['numeroIdentificacion'],
        'fideicomisoAsociado':[{
            "fideicomiso":row['fideicomiso'],
            "tipoActor":[row['tipoActor']]
        }]
    }
       
    tipoPersona=getTipoPersona(row['tipoIdentificacion'])
    if (tipoPersona=='N'):
        baseDict['primerNombre']=row['primerNombre']
        baseDict['segundoNombre']=row['segundoNombre']
        baseDict['primerApellido']=row['primerApellido']
        baseDict['segundoApellido']=row['segundoApellido']
    if(tipoPersona=='J'):
        baseDict['razonSocialNombre']=row['razonSocialNombre']    
    if(action=='CREATE' and tipoPersona=='N'):
        serializer=ActorDeContratoNaturalCreateSerializer(data=baseDict)  
    if(action=='UPDATE' and tipoPersona=='N'):
        serializer=ActorDeContratoNaturalUpdateSerializer(actor,data=baseDict) 
    if(action=='CREATE' and tipoPersona=='J'):
        serializer=ActorDeContratoJuridicoCreateSerializer(data=baseDict)  
    if(action=='UPDATE' and tipoPersona=='J'):
        serializer=ActorDeContratoJuridicoUpdateSerializer(actor,data=baseDict)   
    return serializer

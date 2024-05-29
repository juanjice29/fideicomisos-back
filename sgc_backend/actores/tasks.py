from celery import Celery,current_task,shared_task
from process.decorators import TipoLogEnum, guardarLogEjecucionProceso, guardarLogEjecucionTareaProceso, track_process,protected_function_process,track_sub_task,log_changes
from django import forms
import pandas as pd
from django.db.models.signals import pre_save, post_save, pre_delete
from public.models import TipoDeDocumento
from actores.models import TipoActorDeContrato,ActorDeContrato
from actores.serializers import TipoActorDeContratoSerializer,\
ActorDeContratoNaturalCreateSerializer,\
ActorDeContratoNaturalUpdateSerializer,\
ActorDeContratoJuridicoUpdateSerializer,\
ActorDeContratoJuridicoCreateSerializer
import json
import traceback
from public.utils import getTipoPersona
from process.models import EstadoEjecucion

@shared_task
@track_process
def tkpCargarActoresPorFideiExcel(file_path,fideicomiso,usuario_id, disparador,ejecucion=None):
    ejecucion.estadoEjecucion = EstadoEjecucion.objects.get(acronimio='PPP')
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

@shared_task
@track_process
def tkpCargarActoresExcel(file_path,usuario_id, disparador,ejecucion=None):
    ejecucion.estadoEjecucion = EstadoEjecucion.objects.get(acronimio='PPP')
    ejecucion.save()
    guardarLogEjecucionProceso(ejecucion,
                               TipoLogEnum.INFO.value,
                               "Inicio validacion del archivo excel")
    
    df=tkExcelActoresToPandas(file_path=file_path,ejecucion=ejecucion)
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

@track_sub_task
def tkExcelActoresToPandas(file_path,tarea=None,ejecucion=None):
    try:
        default_cols=['tipoIdentificacion','numeroIdentificacion','tipoActor','fideicomiso','primerNombre','segundoNombre','primerApellido','segundoApellido','razonSocialNombre']
        df=pd.read_excel(file_path, header=None)        
        df.columns = default_cols[:len(df.columns)]
        df = df.drop(df.index[0])   
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
def tkExcelActoresPorFideiToPandas(file_path,fideicomiso,tarea=None,ejecucion=None):
    try:
        default_cols=['tipoIdentificacion','numeroIdentificacion','tipoActor','primerNombre','segundoNombre','primerApellido','segundoApellido','razonSocialNombre']
        df=pd.read_excel(file_path, header=None)        
        df.columns = default_cols[:len(df.columns)]
        df = df.drop(df.index[0])       
        df=df.assign(fideicomiso=fideicomiso)        
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
@log_changes(post_save, ActorDeContrato)
@log_changes(pre_save, ActorDeContrato)
@log_changes(pre_delete, ActorDeContrato) 
@track_sub_task
def tkProcesarPandasActores(df,tarea=None,ejecucion=None):
    resultado={
        'errores':0,
        'actualizados':0,
        'creados':0
    }
    
    for index,row in df.iterrows():
        try:            
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
                    serializer.save(preserve_non_serialized_tp_actor=True)
                    resultado['actualizados']+=1
                    guardarLogEjecucionTareaProceso(ejecucion,tarea,TipoLogEnum.WARN.value,f"Actor '{row['tipoIdentificacion']} {row['numeroIdentificacion']}',en la fila {index} se le sobreescriben los datos.")
                else:
                    resultado['errores']+=1
                    guardarLogEjecucionTareaProceso(ejecucion,tarea,TipoLogEnum.ERROR.value,f"Error al sobreescribir datos del el actor en la fila {index}, {serializer.errors}")  
                continue
            
            serializer=serializarActor(row=row,action='CREATE')                  
            if serializer.is_valid():                
                serializer.save()
                resultado['creados']+=1
                guardarLogEjecucionTareaProceso(ejecucion,tarea,TipoLogEnum.INFO.value,f"Actor '{row['tipoIdentificacion']} {row['numeroIdentificacion']}',en la fila {index} creado exitosamente para el fideicomiso {row['fideicomiso']}")
            else:
                resultado['errores']+=1
                guardarLogEjecucionTareaProceso(ejecucion,tarea,TipoLogEnum.ERROR.value,f"Error al crear el actor en la fila {index}, {serializer.errors}") 
        except Exception as e:
            resultado['errores']+=1
            guardarLogEjecucionTareaProceso(ejecucion,tarea,TipoLogEnum.ERROR.value,f"Error al procesar la fila {index}, {str(e)[:200]}")            
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

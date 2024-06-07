from .models import RpbfCandidatos,RpbfHistorico,ConsecutivosRpbf
from public.models import TipoNovedadRPBF
from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import update
from rest_framework.renderers import JSONRenderer
from celery import Celery
from celery import shared_task, chain
from django.http import JsonResponse
from django.http import FileResponse
from rest_framework import status
import logging
from .querys.semilla import *
from rest_framework.response import Response
from .utils import *
import pandas as pd
import xml.etree.ElementTree as ET
import xml.dom.minidom
import datetime
import os
import zipfile
import subprocess
from .variables import *
import traceback
import pdb 
from enum import Enum
from process.decorators import TipoLogEnum, \
guardarLogEjecucionProceso, \
guardarLogEjecucionTareaProceso, \
track_process,protected_function_process,track_sub_task \
    
from process.models import EjecucionProceso,EstadoEjecucion
from public.models import ParametrosGenericos
logger = logging.getLogger(__name__)
celery = Celery()

class TipoParamEnum(Enum):
    SALIDA_RPBF = "SALIDA_RPBF"    
    
def progress_callback(current, total):
    logger.info('Task progress: {}%'.format(current / total * 100))
    

@shared_task
@track_process
def tkpCalcularBeneficiariosFinales(fondo,calc_cod_post,calc_total_data,corte,usuario_id, disparador,ejecucion=None):
    ejecucion.estadoEjecucion = EstadoEjecucion.objects.get(acronimo='PPP')
    ejecucion.save()
    #0. obtener corte
    last_period=bef_period(get_current_period())
    last_corte=get_last_day_of_period(last_period.split("-")[0],last_period.split("-")[1])    
    corte=last_corte if (not(corte)) else corte
    
    guardarLogEjecucionProceso(ejecucion,
                               TipoLogEnum.INFO.value,
                               "Inicio calculo de reporte beneficiarios finales")
    
    guardarLogEjecucionProceso(ejecucion,
                               TipoLogEnum.INFO.value,
                               f"""Inicio calculo de reporte beneficiarios finales parametrización correspondiente al proceso es \n 
                                  fondo = {fondo} ,\n                                  
                                  calc_cod_post = {calc_cod_post} , \n 
                                  calc_total_data = {calc_total_data} , \n                                   
                                  corte = {corte}
                               """)    
    #1.calcular codigos postales
    if(calc_cod_post):
        guardarLogEjecucionProceso(ejecucion,
                               TipoLogEnum.INFO.value,
                               "Inicio el calculo de codigos postales")
        result=tkFillPostalCodeView(ejecucion=ejecucion)
        guardarLogEjecucionProceso(ejecucion,
                               TipoLogEnum.INFO.value,
                               f"Finalizo calculo de codigos postales resultado: {result_t1}")
    else:
        guardarLogEjecucionProceso(ejecucion,
                               TipoLogEnum.INFO.value,
                               "Se omite el calculo de codigos postales")    
    #2.calcular candidatos    
     
    if(calc_total_data):
        guardarLogEjecucionProceso(ejecucion,
                                TipoLogEnum.INFO.value,
                                "Inicio el calculo de candidatos")
        result=tkCalculateCandidates(fondo=fondo,corte=corte,ejecucion=ejecucion)
        
    else:
        guardarLogEjecucionProceso(ejecucion,
                                TipoLogEnum.INFO.value,
                                "Se omite el procesamiento general de todos los registros.")    
    #3.generar xml
    guardarLogEjecucionProceso(ejecucion,
                                TipoLogEnum.INFO.value,
                                "Inicio el generacion de archivos xml")
    result=tkGenerateXML(fondo=fondo,ejecucion=ejecucion)
    
    guardarLogEjecucionProceso(ejecucion,
                               TipoLogEnum.INFO.value,
                               "Fin de proceso, resultados: "+str(result))
     

@track_sub_task
def tkGenerateXML(fondo,tarea=None,ejecucion=None):
    try:
        report=get_reporte_final(fondo)   
        print(report)     
    except Exception as e:
        tb = traceback.format_exc()
        guardarLogEjecucionTareaProceso(ejecucion,tarea,TipoLogEnum.ERROR.value,f"Fallo al ejecutar el query del reporte final , error : {str(e)} , linea : {tb}"[:250])
        return f"Fallo al ejecutar el query del reporte final"
    
    try:        
        dataframes_por_novedades = {}  
        numer_envio_instancia=ConsecutivosRpbf.objects.get(fondo=fondo)
        numero_envio = numer_envio_instancia.consecutivo
        
        for valor, grupo in report.groupby('TNOV'):
                dataframes_por_novedades[valor] = grupo
                
        for clave_novedad,df_nov in dataframes_por_novedades.items():
            tamano_bloque = 5000
            valorTotal = len(df_nov)
            total_bloques = (valorTotal // tamano_bloque) + 1
            for i in range(total_bloques):
                inicio = i*tamano_bloque
                fin = (i+1)*tamano_bloque
                bloque_actual = df_nov.iloc[inicio:fin]
                root = ET.Element("mas")
                root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
                root.set("xsi:noNamespaceSchemaLocation", "../xsd/2688.xsd")
                cab_element = ET.SubElement(root, "Cab")
                ET.SubElement(cab_element, "Ano").text = str(anio_actual)
                ET.SubElement(cab_element, "CodCpt").text = "1"
                ET.SubElement(cab_element, "Formato").text = "2688"
                ET.SubElement(cab_element, "Version").text = "1"
                ET.SubElement(cab_element, "NumEnvio").text = str(numero_envio)
                ET.SubElement(cab_element, "FecEnvio").text = fecEnvio
                ET.SubElement(cab_element, "FecInicial").text = fecInicial
                ET.SubElement(cab_element, "FecFinal").text = str(fecFinal)
                ET.SubElement(cab_element, "ValorTotal").text = str(valorTotal)
                ET.SubElement(cab_element, "CantReg").text = str(valorTotal)
                for index, fila in bloque_actual.iterrows():
                    attributes = {}
                    for columna, valor in fila.items():
                        if not (valor == '' or pd.isnull(valor)) and columna != 'FONDO':
                            attributes[columna.lower()] = valor

                    genElement = ET.SubElement(root, "bene", attrib=attributes)

                tree = ET.ElementTree(root)
                xml_str = ET.tostring(root, encoding="ISO-8859-1")
                dom = xml.dom.minidom.parseString(xml_str)
                formatted_xml_str = dom.toprettyxml(indent="\t")
                directorio = ParametrosGenericos.objects.get(nombre=TipoParamEnum.SALIDA_RPBF.value).valorParametro
                directorio=directorio+f"/fondo_{fondo}"+f"/novedad_{clave_novedad}"
                os.makedirs(directorio, exist_ok=True)
                with open(f"{directorio}/"+file_name.format(str(numero_envio)), "wb") as file:
                        file.write(formatted_xml_str.encode("iso-8859-1"))
                with open(f"{directorio}/"+file_name.format(str(numero_envio)), "r", encoding="ISO-8859-1") as file:
                    lines = file.readlines()
                lines[0] = '<?xml version="1.0" encoding="ISO-8859-1"?>\n'
                with open(f"{directorio}/"+file_name.format(str(numero_envio)), "w", encoding="ISO-8859-1") as file:
                    file.writelines(lines)
                numero_envio += 1
                numer_envio_instancia.consecutivo=numero_envio
    except Exception as e:
        tb = traceback.format_exc()
        guardarLogEjecucionTareaProceso(ejecucion,tarea,TipoLogEnum.ERROR.value,f"Fallo al convertir el resultado final a xml , error : {str(e)} , linea : {tb}"[:250])
        return f"Fallo al convertir el resultado final a xml."      
    
    return "Se transformaron exitosamente 'detalle de la generacion'"
            
@track_sub_task
def tkCalculateCandidates(fondo,corte,tarea=None,ejecucion=None):   
    
    try:        
        result=RpbfCandidatos.objects.filter(fondo=fondo).delete()
        deleteCandidatosExternos()
        guardarLogEjecucionTareaProceso(ejecucion,tarea,TipoLogEnum.INFO.value,f"Se eliminaron {result} registros temporales correctamente")
    except Exception as e:
        tb = traceback.format_exc()
        guardarLogEjecucionTareaProceso(ejecucion,tarea,TipoLogEnum.ERROR.value,f"Fallo al intentar eliminar los registros temporales , error : {str(e)[:250]} , linea : {tb}")
        return "Fallo al eliminar los candidatos temporales."
    
    try:
        saldo=get_saldo_fondo(fondo=fondo,corte=corte)
        guardarLogEjecucionTareaProceso(ejecucion,tarea,TipoLogEnum.INFO.value,f"Se calcula el saldo general del fondo al corte {corte}, Fondo : {fondo}, Saldo : {saldo} ") 
    except Exception as e:
        tb = traceback.format_exc()
        guardarLogEjecucionTareaProceso(ejecucion,tarea,TipoLogEnum.ERROR.value,f"Fallo al obtener el saldo general del fondo, error : {str(e)} , linea : {tb}"[:250])
        return f"Fallo al obtener el saldo general del fondo."
    
    try:
        df_historico=pd.DataFrame.from_records(RpbfHistorico.objects.filter(fondo=fondo).values())
        if len(df_historico)<1:
            return f"No hay datos del historicos para comparar revisar la tabla."
        
        df_current=get_semilla(fondo,corte,saldo)
        guardarLogEjecucionTareaProceso(ejecucion,tarea,TipoLogEnum.INFO.value,f"""Se calculan los registros, historico : {len(df_historico)},
                                        semilla : {len(df_current)}
                                        """)    
    except Exception as e:
        tb = traceback.format_exc()
        guardarLogEjecucionTareaProceso(ejecucion,tarea,TipoLogEnum.ERROR.value,f"Fallo al obtener los datos historicos y actuales , error : {str(e)} , linea : {tb}"[:250])        
        return f"Fallo al obtener los datos historicos y actuales."   
    
    try:
        candidatos = []
        for index,row in df_current.iterrows():
            nro_identif = row["NRO_IDENTIF"]
            max_feccre = row["MAX_FECCRE"]
            porcentaje = row["PORCENTAJE_SALDO"]
            porcentaje = f"{float(porcentaje):.5f}"            
            filtered_df = df_historico[df_historico["niben"].astype(
                str) == str(nro_identif)]
            novedad_t = "1"
            
            if (len(filtered_df) > 0):
                max_index = filtered_df["periodo"].idxmax()
                last_state = filtered_df.loc[max_index]

                if (last_state["tnov"] == "1"):
                    novedad_t = TipoNovedadRPBF.objects.filter(id="2")
                if (last_state["tnov"] == "2"):
                    novedad_t = TipoNovedadRPBF.objects.get(id="2")
                if (last_state["tnov"] == "3"):
                    novedad_t = TipoNovedadRPBF.objects.get(id="1")
                candidatos.append({"nroIdentif":nro_identif,
                                    "tipoNovedad":novedad_t,
                                    "fechaCreacion":max_feccre,
                                    "fondo":fondo,
                                    "porcentaje":porcentaje
                             })
            else:
                novedad_t = TipoNovedadRPBF.objects.get(id="1")
                candidatos.append({"nroIdentif":nro_identif,
                                    "tipoNovedad":novedad_t,
                                    "fechaCreacion":max_feccre,
                                    "fondo":fondo,
                                    "porcentaje":porcentaje
                             })
            
            instances = [RpbfCandidatos(nroIdentif=candidato["nroIdentif"],
                                       tipoNovedad=candidato["tipoNovedad"],
                                       fondo=candidato["fondo"],
                                       porcentaje=candidato["porcentaje"],
                                       fechaCreacion=candidato["fechaCreacion"]) for candidato in candidatos]
            
        result=RpbfCandidatos.objects.bulk_create(instances)            
        guardarLogEjecucionTareaProceso(ejecucion,tarea,TipoLogEnum.ERROR.value,
                                        f"Se calcularon exitosamente  {len(result)} : candidatos de novedad 1 y 2 para reportar")      
    
                
    except Exception as e:
        tb = traceback.format_exc()  
        guardarLogEjecucionTareaProceso(ejecucion,tarea,TipoLogEnum.ERROR.value,f"""Fallo calculando candidatos novedad 1 y 2 , \n 
                                            error : {str(e)} , \n
                                            linea : {tb}
                                        """[:250])        
        return f"""Fallo calculando candidatos novedad 1 y 2."""
                                        
    try:
        historico_last_state = df_historico.loc[df_historico.groupby(
            ["niben"])["tnov"].idxmax()]
        historico_last_state = historico_last_state[(historico_last_state["tnov"] == "1") | (
            historico_last_state["tnov"] == "2")]
        cancelaciones_df=get_cancelaciones(fondo,corte)
        registros_not_inseed = 0        
        candidatos = []
        instances = []
        result=0
        for index, row in historico_last_state.iterrows():
            nro_identif = str(row["niben"])
            filtered_df = df_current[df_current["NRO_IDENTIF"].astype(
                str) == nro_identif]

            if (len(filtered_df) == 0):

                registros_not_inseed += 1
                candidato_tn3 = cancelaciones_df[cancelaciones_df["niben"] == nro_identif]
                novedad_t = "3"

                if (len(candidato_tn3) > 0):
                    last_cancelation = candidato_tn3.iloc[0]
                    porcentaje= row["pppjepj"] if row["pppjepj"] else row["pbpjepj"]
                    candidatos.append({"nroIdentif":nro_identif,
                                        "tipoNovedad":novedad_t,
                                        "fechaCreacion":row["feciniben"],
                                        "fechaCancelacion":last_cancelation["fecfinben"],
                                        "fondo":fondo,
                                        "porcentaje":porcentaje
                                })
                    instances = [RpbfCandidatos(nroIdentif=candidato["nroIdentif"],
                                       tipoNovedad=candidato["tipoNovedad"],
                                       fondo=candidato["fondo"],
                                       porcentaje=candidato["porcentaje"],
                                       fechaCreacion=candidato["fechaCreacion"],
                                       fechaCancelacion=candidato["fechaCancelacion"]) for candidato in candidatos]
        
        result=RpbfCandidatos.objects.bulk_create(instances)            
        guardarLogEjecucionTareaProceso(ejecucion,tarea,TipoLogEnum.ERROR.value,
                                        f"Se calcularon exitosamente  {len(result)} : candidatos de novedad 3 para reportar")      
    
            
        
    except Exception as e:
        tb = traceback.format_exc()  
        guardarLogEjecucionTareaProceso(ejecucion,tarea,TipoLogEnum.ERROR.value,f"""Fallo calculando los candidatos novedad 3, \n 
                                            error : {str(e)} , \n
                                            linea : {tb}
                                        """[:250])        
        
        return f"""Fallo calculando los candidatos novedad 3"""
    
    return f"Se calcularon exitosamente todos los tipos de novedad para el fondo {fondo}" 

@shared_task
def VerifyDataIntegrityView():
    dsn_tns = cx_Oracle.makedsn(
        url, port, service_name=service_name)
    conn = cx_Oracle.connect(
        user=user, password=password, dsn=dsn_tns)
    cur = conn.cursor()
    return Response({"status": "200"})

@shared_task
def ZipFile():
    carpeta_a_comprimir = 'D:/BENEFICIARIO_FINAL2024/resultados'
    archivo_salida = 'D:/BENEFICIARIO_FINAL2024/resultados.zip'

    comprimir_carpeta(carpeta_a_comprimir, archivo_salida)

    return Response({"status": "200"})

@track_sub_task
def tkFillPostalCodeView(tarea=None,ejecucion=None):
        
    engine = create_engine(
        f'oracle+cx_oracle://{user}":{password}@{url}:{port}/?service_name={service_name}')
    sql = """
        SELECT DIREC_DIREC ID_CLIENTE,CIUD_DEPTO||CIUD_DANE AS ID_CIUDAD_RESIDENCIA,CIUD_DEPTO AS ID_DPTO_RESIDENCIA,'COL' AS ID_PAIS_RESIDENCIA,
        DIREC_DIRECCION AS DIRECCION_RECIDENCIAL,NVL(DIREC_BARRIO,'-') BARRIO_DIR_RESIDENCIAL
        FROM TEMP_RPBF_CANDIDATES 
        INNER JOIN CL_TDIREC D1 ON D1.DIREC_NROIDENT=NRO_IDENTIF
        INNER JOIN (SELECT DIREC_NROIDENT,MAX(DIREC_DIREC) MAX_DIREC FROM CL_TDIREC 
        WHERE DIREC_POSTAL IS NULL AND DIREC_ESTADO='ACT' AND DIREC_TPDIR='RES'  AND DIREC_DIRECCION IS NOT NULL
        GROUP BY DIREC_NROIDENT) D2 ON D1.DIREC_DIREC=D2.MAX_DIREC
        INNER JOIN GE_TCIUD ON DIREC_CIUD=CIUD_CIUD
        INNER JOIN GE_TDEPTO ON DEPTO_DEPTO=CIUD_DEPTO
        INNER JOIN GE_TPAIS ON PAIS_PAIS=DEPTO_PAIS
        """
    df = pd.read_sql(sql, engine)
    df.columns = df.columns.str.upper()
    df = df.astype(str)
    df.to_excel('cod_postal.xlsx', index=False)
    return Response({"status": "200"})

@shared_task
def RunJarView():
    renderer_classes = [JSONRenderer]
    result = subprocess.run(['java', '-Dhttp.proxyHost=10.1.5.2', '-Dhttp.proxyPort=80', '-Dhttps.proxyHost=10.1.5.2',
                                '-Dhttps.proxyPort=80', '-jar', 'cp.jar', '-separador', ',', '-entrada', 'cod_postal.xlsx', '-salida', 'salida.csv'], check=True)
    df = pd.read_csv('salida.csv')
    engine = create_engine(
             f'oracle+cx_oracle://{user}":{password}@{url}:{port}/?service_name={service_name}')
    metadata = MetaData()
    metadata.bind = engine
    cl_tdirec = Table('cl_tdirec', metadata, autoload_with=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    for index, row in df.iterrows():
        if pd.isnull(row['CP']):
            continue
        stmt = update(cl_tdirec).where(cl_tdirec.c.direc_direc ==
                                       row['ID_CLIENTE']).values(direc_postal=row['CP'])
        session.execute(stmt)
        logger.info(f"Updated cl_tdirec: direc_direc={row['ID_CLIENTE']}, direc_postal={row['CP']}")
    session.commit()
    return Response({"status": "200"})
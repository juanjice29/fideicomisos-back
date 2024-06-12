from .models import RpbfCandidatos,RpbfHistorico,ConsecutivosRpbf
from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import update
from rest_framework.renderers import JSONRenderer
from celery import Celery
from celery import shared_task, chain
from django.http import JsonResponse
from django.http import FileResponse
from rest_framework import status
from .querys.semilla import *
from rest_framework.response import Response
from .utils import *
import pandas as pd
import xml.etree.ElementTree as ET
import xml.dom.minidom
import datetime,os,zipfile,subprocess,traceback,pdb,logging,glob
from .variables import *
from process.decorators import TipoLogEnum, \
guardarLogEjecucionProceso, \
guardarLogEjecucionTareaProceso, \
track_process,protected_function_process,track_sub_task 
from process.models import EjecucionProceso,EstadoEjecucion
from public.models import ParametrosGenericos,TipoParamEnum,TipoNovedadRPBF
logger = logging.getLogger(__name__)
celery = Celery()
    
def progress_callback(current, total):
    logger.info('Task progress: {}%'.format(current / total * 100))
    

@track_sub_task
def tkLeerArchivoXmlRPBF(dir,periodo,fondo,tarea=None,ejecucion=None):
    try:
        guardarLogEjecucionTareaProceso(ejecucion,tarea,TipoLogEnum.INFO.value,f"Archivos en el {dir} transformados en pandas exitosamente")
        ruta_archivos = glob.glob(os.path.join(dir, '*.xml'))
    
        for ruta_archivo in ruta_archivos:           
            
            # Aquí puedes agregar el código para procesar cada archivo XML
            tree = ET.parse(ruta_archivo)
            root = tree.getroot()
            
            # Procesar elementos 'bene'
            for bene in root.findall('bene'):
                rpbf_historico = RpbfHistorico(
                    periodo=periodo,  # Ajusta según corresponda
                    fondo=fondo,  # Ajusta según corresponda
                    tipoNovedad=TipoNovedadRPBF.objects.get(id=int(bene.get('tnov'))),
                    bepjtit=bene.get('bepjtit'),
                    bepjben=bene.get('bepjben'),
                    bepjcon=bene.get('bepjcon'),
                    bepjrl=bene.get('bepjrl'),
                    bespjfcp=bene.get('bespjfcp'),
                    bespjf=bene.get('bespjf'),
                    bespjcf=bene.get('bespjcf'),
                    bespjfb=bene.get('bespjfb'),
                    bespjcfe=bene.get('bespjcfe'),
                    tdocben=bene.get('tdocben'),
                    niben=bene.get('niben'),
                    paexben=bene.get('paexben'),
                    nitben=bene.get('nitben'),
                    paexnitben=bene.get('paexnitben'),
                    pape=bene.get('pape'),
                    sape=bene.get('sape'),
                    pnom=bene.get('pnom'),
                    onom=bene.get('onom'),
                    fecnac=bene.get('fecnac'),
                    panacb=bene.get('panacb'),
                    pnacion=bene.get('pnacion'),
                    paresb=bene.get('paresb'),
                    dptoben=bene.get('dptoben'),
                    munben=bene.get('munben'),
                    dirben=bene.get('dirben'),
                    codpoben=bene.get('codpoben'),
                    emailben=bene.get('emailben'),
                    pppjepj=bene.get('pppjepj'),
                    pbpjepj=bene.get('pbpjepj'),
                    feiniben=bene.get('feiniben'),  # Ajusta según corresponda
                    fecfinben=bene.get('fecfinben'),  # Ajusta según corresponda
                    tnov=bene.get('tnov')
                )
                rpbf_historico.save()
                    
    except Exception as e:
        tb = traceback.format_exc()
        guardarLogEjecucionTareaProceso(ejecucion,tarea,TipoLogEnum.ERROR.value,f"Fallo al ejecutar la lectura de los archivos en el {dir}, error : {str(e)} , linea : {tb}"[:250])
        return f"Fallo al ejecutar la lectura de los archivos" 
 

@track_sub_task
def tkGenerateXML(fondo,tarea=None,ejecucion=None):
    try:
        report=get_reporte_final(fondo)   
        guardarLogEjecucionTareaProceso(ejecucion,tarea,TipoLogEnum.INFO.value,f"Se obtiene el resultado del repote final exitosamente.")
        
    except Exception as e:
        tb = traceback.format_exc()
        guardarLogEjecucionTareaProceso(ejecucion,tarea,TipoLogEnum.ERROR.value,f"Fallo al ejecutar el query del reporte final , error : {str(e)} , linea : {tb}"[:250])
        return f"Fallo al ejecutar el query del reporte final"
    directorio_1 = ParametrosGenericos.objects.get(nombre=TipoParamEnum.SALIDA_RPBF.value).valorParametro
    for i in range(1,4):        
        carpeta=directorio_1+f"/fondo_{fondo}"+f"/novedad_{i}"
    
        if os.path.exists(carpeta):
            # Itera sobre todos los archivos y carpetas en la carpeta dada
            for filename in os.listdir(carpeta):
                file_path = os.path.join(carpeta, filename)
                try:
                    # Si es un archivo, elimínalo
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    # Si es una carpeta, elimina todo su contenido
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    tb= traceback.format_exex()
                    guardarLogEjecucionTareaProceso(ejecucion,tarea,TipoLogEnum.ERROR.value,f"Fallo al eliminar las carpetas actuales , error : {str(e)} , linea : {tb}"[:250])

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
                
                directorio=directorio_1+f"/fondo_{fondo}"+f"/novedad_{clave_novedad}"
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
                numer_envio_instancia.save()
        guardarLogEjecucionTareaProceso(ejecucion,tarea,TipoLogEnum.INFO.value,f"Transformación a xml exitosa.")
        
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
        guardarLogEjecucionTareaProceso(ejecucion,tarea,TipoLogEnum.INFO.value,
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
        guardarLogEjecucionTareaProceso(ejecucion,tarea,TipoLogEnum.INFO.value,
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

@track_sub_task
def tkZipFileRPBF(tarea=None,ejecucion=None):
    try:
        carpeta_a_comprimir = ParametrosGenericos.objects.get(nombre=TipoParamEnum.SALIDA_RPBF.value).valorParametro
        archivo_salida = carpeta_a_comprimir+'.zip'
        comprimir_carpeta(carpeta_a_comprimir, archivo_salida)
        guardarLogEjecucionTareaProceso(ejecucion,tarea,TipoLogEnum.INFO.value,f"""Los archivos se comprimieron y fueron ubicados exitosamente en la ruta {carpeta_a_comprimir}""")
    except Exception as e:
        tb = traceback.format_exc()  
        guardarLogEjecucionTareaProceso(ejecucion,tarea,TipoLogEnum.ERROR.value,f"""Fallo al comprimir los archivos de beneficiario final, \n 
                                            error : {str(e)} , \n
                                            linea : {tb}
                                        """[:250])
        return f"""Fallo al comprimir los archivos de beneficiario final."""
    
    return f"Archivos comprimidos correctamente en la ruta {carpeta_a_comprimir}"

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


import datetime
import math
import zipfile
import os
from .querys.semilla import *
import cx_Oracle
import pandas as pd
from .models import RpbfCandidatos,RpbfHistorico
from sqlalchemy import create_engine

db_name_sifi = os.getenv("DB_NAME_SIFI")
db_user_sifi = os.getenv("DB_USER_SIFI")
db_pass_sifi = os.getenv("DB_PASS_SIFI")
db_host_sifi = os.getenv("DB_HOST_SIFI")
db_port_sifi = os.getenv("DB_PORT_SIFI")

db_name_sgc = os.getenv("DB_NAME_SGC")
db_user_sgc = os.getenv("DB_USER_SGC")
db_pass_sgc = os.getenv("DB_PASS_SGC")
db_host_sgc = os.getenv("DB_HOST_SGC")
db_port_sgc = os.getenv("DB_PORT_SGC")

identif_map = {
    'CC': '13',
    'TI': '12',
    'CE': '22',
    'PA': '41',
    'RC': '11',
    'PEP': '47'
}
inverse_identif_map = {v: k for k, v in identif_map.items()}


def get_current_period():
    anio,mes = datetime.datetime.now().strftime("%Y-%m").split("-")
    period=math.floor((int(mes)-1)/3)+1    
    return anio+"-"+str(period)

def bef_period(current_period):
    year,period=current_period.split("-")
    period=int(period)
    year=int(year)
    new_period=period-1
    if(new_period==0):
        return str(year-1)+"-"+str(4)
    else:
        return str(year)+"-"+str(new_period)

def next_period(current_period):
    year,period=current_period.split("-")
    period=int(period)
    year=int(year)
    new_period=period+1
    if(new_period>4):
        return str(year+1)+"-"+str(1)
    else:
        return str(year)+"-"+str(new_period)
 
def add_period(period,add_periods=0):    
    if add_periods<0:
        for i in range(0,abs(add_periods)):
            period=bef_period(period)
        return period 
    else:           
        for i in range(0,add_periods):
            period=next_period(period)
        return period 
    
def get_last_day_of_period(year,quarter):
    year = int(year)
    quarter = int(quarter)
    
    # Diccionario para los últimos días de cada trimestre
    last_days = {
        1: (3, 31),  # Q1: Enero - Marzo
        2: (6, 30),  # Q2: Abril - Junio
        3: (9, 30),  # Q3: Julio - Septiembre
        4: (12, 31)  # Q4: Octubre - Diciembre
    }
    
    month, day = last_days[quarter]
    return datetime.date(year, month, day)

def comprimir_carpeta(carpeta_a_comprimir, archivo_salida):
    # Crear un objeto ZipFile en modo escritura
    with zipfile.ZipFile(archivo_salida, 'w') as zipf:
        # Recorrer todos los archivos y subdirectorios dentro de la carpeta
        for raiz, _, archivos in os.walk(carpeta_a_comprimir):
            # Agregar cada archivo a la carpeta comprimida
            for archivo in archivos:
                ruta_completa = os.path.join(raiz, archivo)
                # Agregar el archivo a la carpeta comprimida usando su ruta completa
                zipf.write(ruta_completa)

def get_saldo_fondo(fondo,corte):
        
    dsn_tns = cx_Oracle.makedsn(
        db_host_sifi, db_port_sifi, service_name=db_name_sifi)
    conn = cx_Oracle.connect(
        user=db_user_sifi, password=db_pass_sifi, dsn=dsn_tns)
    cur = conn.cursor()
    
    saldo = cur.execute(saldo_fondo.format(
            corte, fondo)).fetchone()    
    saldo = str(saldo[0]).replace(",", ".")    
    cur.close()
    conn.close()
    return saldo

def get_reporte_final(fondo):
    dsn_tns = cx_Oracle.makedsn(
        db_host_sgc, db_port_sgc, service_name=db_name_sgc)
    conn = cx_Oracle.connect(
        user=db_user_sgc, password=db_pass_sgc, dsn=dsn_tns)
    cur = conn.cursor()
    cur.execute("SELECT * FROM RPBF_REPORTE_FINAL WHERE FONDO={0}".format(fondo))
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    report = pd.DataFrame(rows, columns=columns, dtype="string").fillna('')    
    cur.close()
    conn.close() 
    
    candidatos_3 = RpbfCandidatos.objects.filter(tipoNovedad__id=3).values('nroIdentif', 'fechaCancelacion')
    df_candidatos_3 = pd.DataFrame.from_records(candidatos_3)

    # Renombrar columnas en df_candidatos_3
    df_candidatos_3 = df_candidatos_3.rename(columns={'nroIdentif': 'niben', 'fechaCancelacion': 'fecfinben'})

    # Agregar la columna BECESPJ
    df_candidatos_3['BECESPJ'] = ''

    # Obtener datos de RpbfHistorico
    subquery = RpbfHistorico.objects.filter(fondo=fondo).values()
    df_comp_historico = pd.DataFrame.from_records(subquery).drop(columns=['fecfinben'])

    # Convertir la columna 'id' a numérica y obtener el índice máximo para cada 'niben'
    df_comp_historico['id'] = pd.to_numeric(df_comp_historico['id'], errors='coerce')
    idx = df_comp_historico.groupby('niben')['id'].idxmax()
    df_historico = df_comp_historico.loc[idx]

    # Realizar el merge
    report_3 = pd.merge(df_historico, df_candidatos_3, on='niben', how='inner')

    # Eliminar columnas no deseadas
    report_3 = report_3.drop(columns=['id', 'cargue', 'periodo', 'tipoNovedad_id'])

    # Convertir los nombres de las columnas a mayúsculas
    report_3.columns = report_3.columns.str.upper()

    # Agregar la columna TNOV
    report_3["TNOV"] = "3"
    
    print("longitud reporte novedad 3",len(report_3))
    df_final=pd.concat([report,report_3],axis=0)
    df_final.to_csv('resultado_2.csv', index=False) 
    
    report.to_csv('resultado_1.csv', index=False)   
     
    return df_final

def get_semilla(fondo,corte,saldo):
    
    dsn_tns = cx_Oracle.makedsn(
        db_host_sifi, db_port_sifi, service_name=db_name_sifi)
    conn = cx_Oracle.connect(
        user=db_user_sifi, password=db_pass_sifi, dsn=dsn_tns)
    cur = conn.cursor()
    rows = cur.execute(query.format(saldo, corte, fondo))   
    rows = cur.fetchall()  
    columns = [desc[0] for desc in cur.description]
    df_current = pd.DataFrame(rows, columns=columns, dtype="string")
        
    cur.close()
    conn.close()

    return df_current

def get_cancelaciones(fondo,corte):  
    dsn_tns = cx_Oracle.makedsn(
        db_host_sifi, db_port_sifi, service_name=db_name_sifi)
    conn = cx_Oracle.connect(
        user=db_user_sifi, password=db_pass_sifi, dsn=dsn_tns)
    cur = conn.cursor()
    
    
    dsn_tns2 = cx_Oracle.makedsn(
        db_host_sgc, db_port_sgc, service_name=db_name_sgc)
    conn2 = cx_Oracle.connect(
        user=db_user_sgc, password=db_pass_sgc, dsn=dsn_tns)
    cur2 = conn.cursor()
    
    if (fondo == "14"):
        rows = cur.execute(
            cancelaciones_rendir.format(corte))  
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
    if (fondo == "12"):
        rows = cur.execute(
            cancelaciones_rentafacil.format(corte))  
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
    if (fondo == "10"):
        rows = cur.execute(
            cancelaciones_universitas.format(corte))
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]        
    if(fondo  =="16"):
        rows = cur.execute(
            cancelaciones_cortoplazo.format(corte))
        rows = cur.fetchall() 
        columns = [desc[0] for desc in cur.description]        
    if(fondo=="18"):
        rows = cur.execute(
            cancelaciones_retiro.format(corte))
        rows = cur.fetchall()   
        columns = [desc[0] for desc in cur.description]        
    if(fondo=="00"):
        rows = cur2.execute(
            cancelaciones_cambio_tpidentif.format(corte))
        rows = cur2.fetchall()
        columns = [desc[0] for desc in cur2.description]  
    
    
    cancelaciones_df = pd.DataFrame(rows, columns=columns, dtype="string")
    cur.close()
    conn.close()
    cur2.close()
    conn2.close()
    return cancelaciones_df
    

def get_identif_value(identif):
    return identif_map.get(identif, 'CC')

def get_identif_key(value):
    return inverse_identif_map.get(value, 'CC')

def get_engine_sifi():
    engine = create_engine(
             f'oracle+cx_oracle://{db_user_sifi}":{db_pass_sifi}@{db_host_sifi}:{db_port_sifi}/?service_name={db_name_sifi}')
    return engine

def make_sifi_query_pandas(query):
    try:
        dsn_tns = cx_Oracle.makedsn(
            db_host_sifi, db_port_sifi, service_name=db_name_sifi)
        conn = cx_Oracle.connect(
            user=db_user_sifi, password=db_pass_sifi, dsn=dsn_tns)
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        
        result = pd.DataFrame(rows, columns=columns, dtype="string").fillna('') 
        cur.close()
        conn.close() 
        result.columns = result.columns.str.upper()
        result = result.astype(str)
        return result        
    except Exception as e:
        print("Error de conexion")

def get_postal_code_pandas():

    dsn_tns = cx_Oracle.makedsn(
        db_host_sifi, db_port_sifi, service_name=db_name_sifi)
    conn = cx_Oracle.connect(
        user=db_user_sifi, password=db_pass_sifi, dsn=dsn_tns)
    cur = conn.cursor()
    cur.execute("""
        SELECT DIREC_DIREC ID_CLIENTE,CIUD_DEPTO||CIUD_DANE AS ID_CIUDAD_RESIDENCIA,CIUD_DEPTO AS ID_DPTO_RESIDENCIA,'COL' AS ID_PAIS_RESIDENCIA,
        DIREC_DIRECCION AS DIRECCION_RECIDENCIAL,NVL(DIREC_BARRIO,'-') BARRIO_DIR_RESIDENCIAL
        FROM RPBF_CANDIDATOS@DBLINK_FIDUCRM 
        INNER JOIN CL_TDIREC D1 ON D1.DIREC_NROIDENT=NROIDENTIF
        INNER JOIN (SELECT DIREC_NROIDENT,MAX(DIREC_DIREC) MAX_DIREC FROM CL_TDIREC 
        WHERE DIREC_POSTAL IS NULL AND DIREC_ESTADO='ACT' AND DIREC_TPDIR='RES'  AND DIREC_DIRECCION IS NOT NULL
        GROUP BY DIREC_NROIDENT) D2 ON D1.DIREC_DIREC=D2.MAX_DIREC
        INNER JOIN GE_TCIUD ON DIREC_CIUD=CIUD_CIUD
        INNER JOIN GE_TDEPTO ON DEPTO_DEPTO=CIUD_DEPTO
        INNER JOIN GE_TPAIS ON PAIS_PAIS=DEPTO_PAIS
        """)
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    
    result = pd.DataFrame(rows, columns=columns, dtype="string").fillna('') 
    cur.close()
    conn.close() 
    result.columns = result.columns.str.upper()
    result = result.astype(str)
    return result
    
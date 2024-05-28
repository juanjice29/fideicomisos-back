import datetime
import math
import zipfile
import os
from .querys.semilla import *
import cx_Oracle

db_name = os.getenv("DB_NAME_SIFI")
db_user = os.getenv("DB_USER_SIFI")
db_pass = os.getenv("DB_PASS_SIFI")
db_host = os.getenv("DB_HOST_SIFI")
db_port = os.getenv("DB_PORT_SIFI")

def get_current_period():
    anio,mes = datetime.datetime.now().strftime("%Y-%m").split("-")
    period=math.floor(int(mes)/4)+1    
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
        db_host, db_port, service_name=db_name)
    conn = cx_Oracle.connect(
        user=db_user, password=db_pass, dsn=dsn_tns)
    cur = conn.cursor()
    saldo = cur.execute(saldo_fondo.format(
            corte, fondo)).fetchone()    
    saldo = str(saldo[0]).replace(",", ".")    
    cur.close()
    conn.close()
    return saldo

def get_semilla(fondo,corte,saldo):
    
    dsn_tns = cx_Oracle.makedsn(
        db_host, db_port, service_name=db_name)
    conn = cx_Oracle.connect(
        user=db_user, password=db_pass, dsn=dsn_tns)
    cur = conn.cursor()
    rows = cur.execute(query.format(saldo, corte, fondo))   
    rows = cur.fetchall()  
    columns = [desc[0] for desc in cur.description]
    df_current = pd.DataFrame(rows, columns=columns, dtype="string")
        
    cur.close()
    conn.close()

    return df_current
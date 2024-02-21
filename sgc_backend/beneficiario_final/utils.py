import datetime
import math
import zipfile
import os

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

from process.decorators import TipoLogEnum, \
guardarLogEjecucionProceso, \
track_process,protected_function_process  ,abort_task
from celery import Celery
from celery import shared_task, chain
from celery.contrib.abortable import AbortableTask
from .tasks import tkFillPostalCodeView, \
    tkCalculateCandidates, \
    tkGenerateXML, \
    tkZipFileRPBF, \
    tkLeerArchivoXmlRPBF, \
    tkGenerateMirrorXML
from process.models import EjecucionProceso,EstadoEjecucion
from .utils import *
from public.models import ParametrosGenericos,TipoParamEnum,TipoNovedadRPBF
from celery.contrib.abortable import AbortableTask

@shared_task(bind=True, base=AbortableTask)
@track_process
def tkpCalcularBeneficiariosFinales(self,fondo,calc_cod_post,calc_total_data,corte,usuario_id, disparador,ejecucion=None):
    ejecucion.estadoEjecucion = EstadoEjecucion.objects.get(acronimo='PPP')
    ejecucion.save()
    #0. obtener corte
    last_period=bef_period(get_current_period())
    last_corte=get_last_day_of_period(last_period.split("-")[0],last_period.split("-")[1])    
    corte=last_corte if (not(corte)) else corte
    if(self.is_aborted()):
        abort_task(ejecucion=ejecucion)
        return 
    guardarLogEjecucionProceso(ejecucion,
                               TipoLogEnum.INFO.value,
                               f"""Inicio calculo de reporte beneficiarios finales, la parametrización correspondiente al proceso es \n 
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
        result=tkFillPostalCodeView(self,ejecucion=ejecucion)
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
        result=tkCalculateCandidates(self,fondo=fondo,corte=corte,ejecucion=ejecucion)
        
    else:
        guardarLogEjecucionProceso(ejecucion,
                                TipoLogEnum.INFO.value,
                                "Se omite el procesamiento general de todos los registros.")    
    #3.generar xml
    guardarLogEjecucionProceso(ejecucion,
                                TipoLogEnum.INFO.value,
                                "Inicio el generacion de archivos xml")
    
    result=tkGenerateXML(self,fondo=fondo,ejecucion=ejecucion)
    if(fondo=="10"):
        guardarLogEjecucionProceso(ejecucion,
                                TipoLogEnum.INFO.value,
                                "Inicio la generacion de los archivos espejos")
        result=tkGenerateMirrorXML(self,fondo=fondo,ejecucion=ejecucion)
    else:
        guardarLogEjecucionProceso(ejecucion,
                               TipoLogEnum.INFO.value,
                               "Se omite la generacion de archivos espejos")
        
    #4.Comprimir archivos y alistarlos en la ruta
    guardarLogEjecucionProceso(ejecucion,
                                TipoLogEnum.INFO.value,
                                "Inicio la compresion de archivos")
    result=tkZipFileRPBF(self,ejecucion=ejecucion)
    guardarLogEjecucionProceso(ejecucion,
                               TipoLogEnum.INFO.value,
                               "Fin de proceso, resultados: "+str(result))


'''@shared_task
@track_process   
def tkpConfirmarReportBeneficiarioFinal(fondos,novedades,periodo,usuario_id, disparador,ejecucion=None):
    ejecucion.estadoEjecucion = EstadoEjecucion.objects.get(acronimo='PPP')
    ejecucion.save()
    guardarLogEjecucionProceso(ejecucion,
                               TipoLogEnum.INFO.value,                               
                               f"""Inicio confirmacion de reporte beneficiarios finales,archvios en ruta , la parametrización correspondiente al proceso es \n 
                                  fondos = {fondos} ,\n                                  
                                  novedades = {novedades} , \n 
                                  periodo = {periodo},
                               """)
    
    directorio_1 = ParametrosGenericos.objects.get(nombre=TipoParamEnum.ENTRADA_RPBF.value).valorParametro
    for i in fondos:
        for j in novedades:
            directorio=directorio_1+f"/fondo_{i}"+f"/novedad_{j}"
            result=tkLeerArchivoXmlRPBF(dir=directorio,ejecucion=ejecucion,periodo=periodo,fondo=i)
'''
@shared_task
@track_process
def tkpConfirmarArchivosRPBF(file_path,fondo,novedad,periodo,usuario_id,disparador,ejecucion=None):
    ejecucion.estadoEjecucion = EstadoEjecucion.objects.get(acronimo='PPP')
    ejecucion.save()
    guardarLogEjecucionProceso(ejecucion,
                               TipoLogEnum.INFO.value,                               
                               f"""Inicio confirmacion de reporte beneficiarios finales, la parametrización correspondiente al proceso es \n 
                                  fondo = {fondo} ,\n                                  
                                  novedad = {novedad} , \n 
                                  periodo = {periodo}, \n
                                  ruta= {file_path}
                               """)
    result=tkLeerArchivoXmlRPBF(dir=file_path,ejecucion=ejecucion,periodo=periodo,fondo=fondo,novedad=novedad)
    
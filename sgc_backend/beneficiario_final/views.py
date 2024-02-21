
from rest_framework import generics
from django.db import connection
from .serializers import Beneficiario_ReporteSerializer
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse, JsonResponse,FileResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Beneficiario_Reporte_Dian, File, RPBF_HISTORICO, RPBF_PERIODOS
from xml.etree import ElementTree as ET
from datetime import datetime
from rest_framework.views import APIView, View
from rest_framework.permissions import IsAuthenticated
from django.http import FileResponse
from rest_framework.parsers import MultiPartParser, FormParser
import hashlib
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import logging
from .tasks import run_tasks_in_order,test_task
from .utils import *
from .querys import semilla
import cx_Oracle
import pandas as pd
import xml.etree.ElementTree as ET
import xml.dom.minidom
import datetime
from .variables import *
import os
import zipfile

class CalculateBFCandidates(APIView):
    def get(self, request, *args, **kwargs):
        fondos=["14","12"]
        dsn_tns = cx_Oracle.makedsn('192.168.168.175', '1521', service_name='SIFIVAL')
        conn = cx_Oracle.connect(user='FS_SGC_US', password='fs_sgc_us', dsn=dsn_tns)
        cur = conn.cursor()   
        sql_delete_candidates="DELETE FROM RPBF_CANDIDATES"   
        cur.execute(sql_delete_candidates)
        conn.commit()
        
        for i in fondos:
            fondo=i
            novedades=[1,2,3] 
                    
            last_report_regs=RPBF_HISTORICO.objects.filter(FONDO=fondo) 
            df_historico=pd.DataFrame.from_records(last_report_regs.values())        
            df_historico["PERIODO_REPORTADO_id"]=df_historico["PERIODO_REPORTADO_id"].apply(lambda x: int("".join(x.split("-")))).astype(int)            
            
            saldo= cur.execute(semilla.saldo_fondo.format("2023-12-31",fondo)).fetchone()
            saldo=str(saldo[0]).replace(",",".")             
            
            cur.execute(semilla.query.format(saldo,"2023-12-31",fondo))        
            rows=cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            
            df_current = pd.DataFrame(rows, columns=columns, dtype="string")
            result=[]
            
            for index,row in df_current.iterrows():
                nro_identif=row["NRO_IDENTIF"]  
                max_feccre=row["MAX_FECCRE"] 
                porcentaje=row["PORCENTAJE_SALDO"]
                porcentaje=f"{float(porcentaje):.5f}"        
                filtered_df=df_historico[df_historico["NRO_IDENTIF"].astype(str)==str(nro_identif)]
                novedad_t="1"
                #Calculo de 1 y 2
                if(len(filtered_df)>0):
                    max_index=filtered_df["PERIODO_REPORTADO_id"].idxmax()            
                    last_state=filtered_df.loc[max_index]
                    
                    if(last_state["TIPO_NOVEDAD"]=="1"):
                        novedad_t="2"
                    if(last_state["TIPO_NOVEDAD"]=="2"):
                        novedad_t="2"
                    if(last_state["TIPO_NOVEDAD"]=="3"):
                        novedad_t="1"  
                    result.append((nro_identif,novedad_t,fondo,max_feccre,'',porcentaje))                 
                else:
                    novedad_t="1"                
                    result.append((nro_identif,novedad_t,fondo,max_feccre,'',porcentaje))
                    
            #del historico de las novedades 1 y 2 , determinar cuales ya salieron
            historico_last_state=df_historico.loc[df_historico.groupby(["NRO_IDENTIF"])["PERIODO_REPORTADO_id"].idxmax()]            
            historico_last_state=historico_last_state[(historico_last_state["TIPO_NOVEDAD"]=="1") | (historico_last_state["TIPO_NOVEDAD"]=="2")]
            
            if(fondo=="14"):
                cancelaciones_df=cur.execute(semilla.cancelaciones_rendir.format("2023-12-31"))            
                
            if(fondo=="12"):
                cancelaciones_df=cur.execute(semilla.cancelaciones_rentafacil.format("2023-12-31")) 
            
            rows=cur.fetchall()
            columns = [desc[0] for desc in cur.description]    
            cancelaciones_df = pd.DataFrame(rows, columns=columns, dtype="string")
            
            registros_not_inseed=0
            cancelaciones_df["NRO_IDENTIF"]=cancelaciones_df["NRO_IDENTIF"].astype(str)
            
            for index,row in historico_last_state.iterrows():
                nro_identif=str(row["NRO_IDENTIF"] )
                filtered_df=df_current[df_current["NRO_IDENTIF"].astype(str)==nro_identif]        
                    
                if(len(filtered_df)==0):  
                    
                    registros_not_inseed+=1       
                    candidato_tn3=cancelaciones_df[cancelaciones_df["NRO_IDENTIF"]==nro_identif]
                    novedad_t="3"
                    
                    if (len(candidato_tn3)>0):                         
                        last_cancelation=candidato_tn3.iloc[0]  
                        temp_result=(nro_identif,novedad_t,fondo,row["FECHA_CREACION"],last_cancelation["FECCAN"],row["PORCENTAJE_SALDO"])        
                        result.append(temp_result)
            
            sql_insert = "INSERT INTO RPBF_CANDIDATES (NRO_IDENTIF, NOVEDAD,FONDO,FECCRE,FECCAN,PORCENTAJE_SALDO) VALUES (:1, :2, :3, :4, :5, :6)"            
            # Ejecutar la sentencia SQL con la lista de registros
            cur.executemany(sql_insert, result)    
            conn.commit()   
        cur.close()
        conn.close()      
        return Response({"status":"200","longitud":len(result)}) 
    
class VerifyDataIntegrityView():
    def get(self, request, *args, **kwargs):
        dsn_tns = cx_Oracle.makedsn('192.168.168.175', '1521', service_name='SIFIVAL')
        conn = cx_Oracle.connect(user='FS_SGC_US', password='fs_sgc_us', dsn=dsn_tns)
        cur = conn.cursor()
        return Response({"status":"200"})
    
class TableToXmlView(APIView):
    def get(self, request, *args, **kwargs):
        dsn_tns = cx_Oracle.makedsn('192.168.168.175', '1521', service_name='SIFIVAL')
        conn = cx_Oracle.connect(user='FS_SGC_US', password='fs_sgc_us', dsn=dsn_tns)
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM RPBF_REPORTE_FINAL")        
        rows=cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        report = pd.DataFrame(rows, columns=columns, dtype="string").fillna('')
        
        dataframes_por_fondos = {}
        
        for valor, grupo in report.groupby('FONDO'):
            dataframes_por_fondos[valor] = grupo
            
        for clave_fondo,df_per_fondo in dataframes_por_fondos.items():
            dataframes_por_novedades={}
            cur.execute("SELECT CONSECUTIVO FROM RPBF_CONSECUTIVOS WHERE FONDO='{0}'".format(clave_fondo))        
            row=cur.fetchone()
            numero_envio=row[0]
            
            for valor, grupo in df_per_fondo.groupby('TNOV'):
                dataframes_por_novedades[valor] = grupo
                
            for clave_novedad,df_per_nov in dataframes_por_novedades.items():
                tamano_bloque=5000
                valorTotal=len(df_per_nov)
                total_bloques=(valorTotal // tamano_bloque) + 1
                for i in range(total_bloques):
                    inicio =i*tamano_bloque
                    fin=(i+1)*tamano_bloque
                    bloque_actual=df_per_nov.iloc[inicio:fin]                   
                    
                    root = ET.Element("mas")
                    root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
                    root.set("xsi:noNamespaceSchemaLocation", "../xsd/2688.xsd")
                    cab_element = ET.SubElement(root, "Cab")                
                    ET.SubElement(cab_element, "Ano").text = str(anio_actual)
                    ET.SubElement(cab_element, "CodCpt").text = "1"
                    ET.SubElement(cab_element, "Formato").text = "2688"
                    ET.SubElement(cab_element, "Version").text = "1"
                    ET.SubElement(cab_element, "NumEnvio").text = str(numero_envio)
                    ET.SubElement(cab_element, "FecEnvio").text =  fecEnvio
                    ET.SubElement(cab_element, "FecInicial").text = fecInicial
                    ET.SubElement(cab_element, "FecFinal").text = str(fecFinal)
                    ET.SubElement(cab_element, "ValorTotal").text = str(valorTotal)
                    ET.SubElement(cab_element, "CantReg").text = str(valorTotal)
                    for index,fila in bloque_actual.iterrows():
                        attributes={}
                        for columna,valor in fila.items():                            
                            if not(valor=='' or pd.isnull(valor)) and columna!='FONDO':
                                attributes[columna.lower()] = valor
                                
                        genElement=ET.SubElement(root, "bene",attrib=attributes)
                           
                    tree = ET.ElementTree(root)
                    xml_str = ET.tostring(root, encoding="ISO-8859-1")
                    dom = xml.dom.minidom.parseString(xml_str)
                    formatted_xml_str = dom.toprettyxml(indent="\t")
                    directorio=f"D:/BENEFICIARIO_FINAL2024/resultados/fondo_{clave_fondo}/novedad_{clave_novedad}"
                    os.makedirs(directorio, exist_ok=True)
                    with open(f"{directorio}/"+file_name.format(str(numero_envio)), "wb") as file:
                        file.write(formatted_xml_str.encode("iso-8859-1"))

                    with open(f"{directorio}/"+file_name.format(str(numero_envio)), "r",encoding="ISO-8859-1") as file:
                        lines = file.readlines()
                    lines[0]='<?xml version="1.0" encoding="ISO-8859-1"?>\n'

                    with open(f"{directorio}/"+file_name.format(str(numero_envio)), "w",encoding="ISO-8859-1") as file:
                        file.writelines(lines)
                    numero_envio+=1
        cur.close()
        conn.close()
        
        return Response({"status":"200","num_envio":str(len(dataframes_por_fondos))})
class ZipFile(APIView):
    def get(self,request,*args,**kwargs):
        carpeta_a_comprimir = 'D:/BENEFICIARIO_FINAL2024/resultados'
        archivo_salida = 'D:/BENEFICIARIO_FINAL2024/resultados.zip'

        comprimir_carpeta(carpeta_a_comprimir, archivo_salida)
        
        return Response({"status":"200"})
    
class DownloadDianReport(APIView):
    def get(self,request,*args,**kwargs):
        ruta_archivo = 'D:/BENEFICIARIO_FINAL2024/resultados.zip'
        if os.path.exists(ruta_archivo):
            # Abrir el archivo y devolverlo como respuesta
            archivo=open(ruta_archivo, 'rb')            
            return FileResponse(archivo, as_attachment=True, filename=os.path.basename(ruta_archivo))
        else:
            # Devolver una respuesta indicando que el archivo no existe
            return Response({'error': 'El archivo no existe.'}, status=status.HTTP_404_NOT_FOUND)
        
class FillPostalCodeView():
    
    pass

   
class RunTasksView(APIView):
    def get(self, request, format=None):
        run_tasks_in_order.apply_async()
        return Response({'status': 'Tasks started'})
class BeneficiarioDianCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Beneficiario_Reporte_Dian.objects.all()
    serializer_class = Beneficiario_ReporteSerializer
class BeneficiarioDianDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Beneficiario_Reporte_Dian.objects.all()
    serializer_class = Beneficiario_ReporteSerializer
    lookup_field = 'Id_Cliente'
class BeneficiarioDianByUserTypeView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = Beneficiario_ReporteSerializer
    def get_queryset(self):
        user_type = self.kwargs.get('Tipo_Novedad')
        return Beneficiario_Reporte_Dian.objects.filter(user_type=user_type)

logger = logging.getLogger(__name__)
class UpdateBeneficiarioDianView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, format=None):
        xml_file = request.FILES['xml']  # get the XML file from the request files
        file_content = xml_file.read()  # read the file content
        # calculate the hash of the file content
        file_hash = hashlib.md5(file_content).hexdigest()
        # check if a file with the same hash already exists
        if File.objects.filter(file_hash=file_hash).exists():
            return Response({'error': 'File already exists'}, status=status.HTTP_400_BAD_REQUEST)
        # save the file
        file_name = default_storage.save('uploads/' + xml_file.name, ContentFile(file_content))
        # save the file hash
        File.objects.create(file_name=file_name, file_hash=file_hash)
        # parse the XML file
        xml_data = ET.fromstring(file_content)
        product = request.data.get('FONDO')
        period = request.data.get('PERIODO_REPORTADO')
        for item in xml_data.findall('bene'):
            NRO_IDENTIF = item.get('niben')
            Tipo_Novedad = item.get('tnov')
            TIPO_IDENTIF = item.get('tdocben')
            NRO_IDENTIF_set = set()
            period_instance = RPBF_PERIODOS.objects.get(PERIODO=period)
            obj, created = RPBF_HISTORICO.objects.update_or_create(
                NRO_IDENTIF=NRO_IDENTIF,
                defaults={
                    'TIPO_NOVEDAD': Tipo_Novedad,
                    'TIPO_IDENTIF': TIPO_IDENTIF,
                    'FONDO': product,
                    'PERIODO_REPORTADO': period_instance,
                
                }
            )
            if created:
                logger.info(f'Created record with NRO_IDENTIF={NRO_IDENTIF}')
            else:
                logger.info(f'Updated record with NRO_IDENTIF={NRO_IDENTIF}')    
        return Response(status=status.HTTP_200_OK)
    
class UpdateBeneficiarioReporteDianView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        current_period = request.data.get('period')  # get the period from the request data

        # calculate the last period taking into account the year change
        year, quarter = map(int, current_period.split('-'))
        last_period = f'{year - 1 if quarter == 1 else year}-{4 if quarter == 1 else quarter - 1}'

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT TIPO_IDENTIF, NRO_IDENTIF, FONDO FROM RPBF_HISTORICO WHERE PERIODO_REPORTADO = %s AND TIPO_NOVEDAD != '3'
            """, [last_period])
            rows = cursor.fetchall()

        for row in rows:
            TIPO_IDENTIF = row[0]
            NRO_IDENTIF = row[1]
            FONDO = row[2]

            # check if the record exists in the last period
            exists_in_last_period = RPBF_HISTORICO.objects.exclude(TIPO_NOVEDAD='3').filter(TIPO_IDENTIF=TIPO_IDENTIF, NRO_IDENTIF=NRO_IDENTIF, FONDO=FONDO, PERIODO_REPORTADO=last_period).exists()
            TIPO_NOVEDAD = '2' if exists_in_last_period else '1'

            RPBF_HISTORICO.objects.update_or_create(
                TIPO_IDENTIF=TIPO_IDENTIF,
                NRO_IDENTIF=NRO_IDENTIF,
                FONDO=FONDO,
                PERIODO_REPORTADO=current_period,
                defaults={
                    'TIPO_NOVEDAD': TIPO_NOVEDAD,
                }
            )

        # For each record in the last period that doesn't exist in the current period, create a new record with TIPO_NOVEDAD = '3'
        last_period_records = RPBF_HISTORICO.objects.filter(PERIODO_REPORTADO=last_period).exclude(TIPO_NOVEDAD='3')
        for record in last_period_records:
            if not RPBF_HISTORICO.objects.filter(TIPO_IDENTIF=record.TIPO_IDENTIF, NRO_IDENTIF=record.NRO_IDENTIF, FONDO=record.FONDO, PERIODO_REPORTADO=current_period).exists():
                RPBF_HISTORICO.objects.create(
                    TIPO_IDENTIF=record.TIPO_IDENTIF,
                    NRO_IDENTIF=record.NRO_IDENTIF,
                    FONDO=record.FONDO,
                    PERIODO_REPORTADO=current_period,
                    TIPO_NOVEDAD='3'
                )

        return Response(status=status.HTTP_200_OK)
class CheckIntegrityView(View):
    def get(self, request, *args, **kwargs):
        # retrieve all unique periods from the table
        periods = RPBF_HISTORICO.objects.values_list('PERIODO_REPORTADO', flat=True).distinct()

        for current_period in periods:
            # calculate the last period taking into account the year change
            year, quarter = map(int, current_period.split('-'))
            last_period = f'{year - 1 if quarter == 1 else year}-{4 if quarter == 1 else quarter - 1}'

            # retrieve all active records from the last period
            last_period_records = RPBF_HISTORICO.objects.filter(PERIODO_REPORTADO=last_period, Activo=True)

            for record in last_period_records:
                # check if the record exists in the current period
                current_period_record = RPBF_HISTORICO.objects.filter(NRO_IDENTIF=record.NRO_IDENTIF, PERIODO_REPORTADO=current_period,TIPO_IDENTIF=record.TIPO_IDENTIF ).first()

                if current_period_record:
                    # if the record exists in the current period and its type is 2, create a new record with the same data but with the current period
                    if current_period_record.TIPO_NOVEDAD == '2':
                        RPBF_HISTORICO.objects.create(
                            NRO_IDENTIF=record.NRO_IDENTIF,
                            TIPO_IDENTIF=record.TIPO_IDENTIF,
                            TIPO_NOVEDAD='2',
                            FONDO=record.FONDO,
                            PERIODO_REPORTADO=current_period,
                            
                        )
                else:
                    # if the record doesn't exist in the current period, add it to the current period with type 3
                    RPBF_HISTORICO.objects.create(
                        NRO_IDENTIF=record.NRO_IDENTIF,
                        TIPO_IDENTIF=record.TIPO_IDENTIF,
                        TIPO_NOVEDAD='2',
                        FONDO=record.FONDO,
                        PERIODO_REPORTADO=current_period,
                    )

            # for each record in the current period that doesn't exist in the last period, set its type to 1
            current_period_records = RPBF_HISTORICO.objects.filter(Periodo=current_period)
            for record in current_period_records:
                if not RPBF_HISTORICO.objects.filter(client_id=record.client_id, Periodo=last_period).exists():
                    record.Tipo_Novedad = '1'

        # save the changes to the database
        RPBF_HISTORICO.objects.bulk_update(current_period_records, ['Tipo_Novedad'])

        # return a response indicating that the integrity check is complete
        return JsonResponse({'status': 'Integrity check complete'})
    

        
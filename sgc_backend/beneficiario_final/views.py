
from rest_framework import generics
from django.db import connection
from .serializers import Beneficiario_ReporteSerializer
from rest_framework.response import Response
from rest_framework import status
from django.http import  JsonResponse,FileResponse
from rest_framework.views import APIView, View
from rest_framework.permissions import IsAuthenticated
import logging
from .utils import *
from .variables import *
from celery.result import AsyncResult
from .process import tkpCalcularBeneficiariosFinales,tkpConfirmarArchivosRPBF
#VerifyDataIntegrityView,\
#TableToXmlView,\
#ZipFile,\
#FillPostalCodeView,\
#RunJarView,\
from .forms import UploadFileForm
from celery import chain
from rest_framework.exceptions import APIException
from public.models import ParametrosGenericos,TipoParamEnum
from datetime import datetime
from django.core.files.storage import default_storage,FileSystemStorage
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DownloadDianReport(APIView):
    
    def get(self, request, *args, **kwargs):
        directorio = ParametrosGenericos.objects.get(nombre=TipoParamEnum.SALIDA_RPBF.value).valorParametro
        ruta_archivo = directorio+'.zip'
        
        if os.path.exists(ruta_archivo):
            # Abrir el archivo y devolverlo como respuesta
            archivo = open(ruta_archivo, 'rb')
            return FileResponse(archivo, as_attachment=True, filename=os.path.basename(ruta_archivo))
        else:
            # Devolver una respuesta indicando que el archivo no existe
            return Response({'error': 'El archivo no existe.'}, status=status.HTTP_404_NOT_FOUND)
        


class GenerateRPBF(APIView):
    
    def post(self,request):
        try:
            fondos=request.data.get('fondos')
            if (not(fondos) or len(fondos)<1 ):
                return Response({'detail':'Se requiere al menos un fondo para calcular los reportes.'},status=status.HTTP_400_BAD_REQUEST)                      
            calc_cod_post=request.data.get('enableCalcCodPostal',False)
            calc_total_data=request.data.get('enableCalcTotalData',True)
            corte=request.data.get('fechaCorte')
            print(corte)
            tasks=[]
            print(request.user.id)
            for i in fondos:
                result=tkpCalcularBeneficiariosFinales.delay(
                fondo=i,                
                calc_cod_post=calc_cod_post,
                calc_total_data=calc_total_data,
                corte=corte,
                usuario_id=request.user.id,
                disparador="MAN")
                tasks.append({
                    "fondo":i,
                    "procesoId":result.id
                })
            
            return Response({'Procesos:':tasks,'message': 'Los procesos se ha iniciado correctamente.'}, status=status.HTTP_202_ACCEPTED)
            
        except Exception as e:
            raise APIException(detail=str(e))    

'''class ConfirmRPBF(APIView):
    
    def post(self,request):
        try:
            fondos=request.data.get('fondos')
            if (not(fondos) or len(fondos)<1 ):
                return Response({'detail':'Se requiere al menos un fondo para confirmar los reportes.'},status=status.HTTP_400_BAD_REQUEST)                      
            periodo=request.data.get('periodo')
            if(not(periodo)):
                return Response({'detail':'Se requiere el periodo para confirmar los reportes.'},status=status.HTTP_400_BAD_REQUEST)    
            novedades=request.data.get('novedades')
            if (not(novedades) or len(novedades)<1 ):
                return Response({'detail':'Se requiere al menos una novedad para confirmar los reportes.'},status=status.HTTP_400_BAD_REQUEST) 
            tasks=[]
            result=tkpConfirmarReportBeneficiarioFinal.delay(
                fondos=fondos,
                novedades=novedades,
                periodo=periodo,
                usuario_id=request.user.id,
                disparador="MAN"
            )
            return Response({'PocesoId:':result.id,'message': 'Los procesos se ha iniciado correctamente.'}, status=status.HTTP_202_ACCEPTED)            
        except Exception as e:
            raise APIException(detail=str(e))  '''  

class ConfirmFilesRPBF(APIView):
    
    def post(self,request):
        
        try:
                
            fondo=request.data.get('fondo')                
            if (not(fondo) or len(fondo)<1 ):
                return Response({'detail':'Se requiere un fondo para confirmar los archivos.'},status=status.HTTP_400_BAD_REQUEST)                      
            periodo=request.data.get('periodo')
            if(not(periodo)):
                return Response({'detail':'Se requiere un periodo para confirmar los archivos.'},status=status.HTTP_400_BAD_REQUEST)    
            novedad=request.data.get('novedad')
            if (not(novedad) or len(novedad)<1 ):
                return Response({'detail':'Se requiere una novedad para confirmar los archivos.'},status=status.HTTP_400_BAD_REQUEST) 
            
            files = request.FILES
            if not files:
                return Response({'detail': 'Se requiere al menos un archivo.'}, status=status.HTTP_400_BAD_REQUEST)
            
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            
            dir_name = (
                ParametrosGenericos.objects
                .get(nombre=TipoParamEnum.ENTRADA_RPBF.value)
                .valorParametro + f"/{timestamp}/fondo{fondo}_novedad{novedad}_periodo{periodo}"
            )
            
            for key in files:
                file = files[key]
                fs = FileSystemStorage(location=dir_name)
                fs.save(file.name, file)
                            
            tasks=[]
            result=tkpConfirmarArchivosRPBF.delay(
                file_path=dir_name,
                fondo=fondo,
                novedad=novedad,
                periodo=periodo,
                usuario_id=request.user.id,
                disparador="MAN"
            )            
            return Response({'PocesoId:':result.id,'message': 'Los procesos se ha iniciado correctamente.'}, status=status.HTTP_202_ACCEPTED)            
        
        except Exception as e:
            print(str(e))
            raise APIException(detail=str(e)) 
    
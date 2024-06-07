
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
from .tasks import tkpCalcularBeneficiariosFinales
#VerifyDataIntegrityView,\
#TableToXmlView,\
#ZipFile,\
#FillPostalCodeView,\
#RunJarView,\
from celery import chain
from rest_framework.exceptions import APIException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GenerateRPBF(APIView):
    
    def post(self,request):
        try:
            fondos=request.data.get('fondos')
            if (not(fondos) or len(fondos)<1 ):
                return Response({'detail':'Se requiere al menos un fondo para calcular los reportes.'},status=status.HTTP_400_BAD_REQUEST)                      
            calc_cod_post=request.data.get('enableCalcCodPostal',False)
            calc_total_data=request.data.get('enableCalcTotalData',True)
            corte=request.data.get('fechaCorte')
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
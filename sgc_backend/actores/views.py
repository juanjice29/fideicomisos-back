from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from public.models import TipoDeDocumento
from .models import ActorDeContrato
from django.core.exceptions import ValidationError
from .models import ActorDeContrato
from .serializers import ActorDeContratoSerializer,\
ActorDeContratoNaturalCreateSerializer,\
ActorDeContratoNaturalUpdateSerializer,\
ActorDeContratoJuridicoCreateSerializer,\
ActorDeContratoJuridicoUpdateSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics 
from sgc_backend.permissions import HasRolePermission, LoggingJWTAuthentication
from rest_framework.exceptions import ParseError
from rest_framework.exceptions import APIException
from rest_framework import filters
from django.db import IntegrityError
from .forms import UploadFileForm
from .tasks import tkpCargarActoresPorFideiExcel,tkpCargarActoresExcel
from django.core.files.storage import default_storage,FileSystemStorage
from datetime import datetime
import os

class ActorView(APIView):
    authentication_classes = [LoggingJWTAuthentication]
    permission_classes = [IsAuthenticated, HasRolePermission]
    def get_object_by_id(self,pk):
        try:
            return ActorDeContrato.objects.get(ActorDeContrato.id==pk)        
        except  ActorDeContrato.DoesNotExist:
            raise NotFound(detail='Actor de contrato no encontrado')
        except Exception as e:
            raise APIException(detail=str(e)) 
    def get_object(self,tipo_id,nro_id):
        try:
            return ActorDeContrato.objects.get(tipoIdentificacion=tipo_id,numeroIdentificacion=nro_id)        
        except  ActorDeContrato.DoesNotExist:
            raise NotFound(detail='Actor de contrato no encontrado')
        except Exception as e:
            raise APIException(detail=str(e))   
        
    def get(self,request,tipo_id,nro_id,formate=None):               
        actor=self.get_object(tipo_id,nro_id)        
        serializer=ActorDeContratoSerializer(actor)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    def put(self,request,tipo_id,nro_id):
        actor=self.get_object(tipo_id,nro_id)
        tipo_persona=getTipoPersona(tipo_id)
        if(tipo_persona=='N'):
            serializer=ActorDeContratoNaturalUpdateSerializer(actor,data=request.data)
        elif(tipo_persona=='J'):
            serializer=ActorDeContratoJuridicoUpdateSerializer(actor,data=request.data)
        else:
            return Response({'detail':'Tipo de persona no soportado'},status=status.HTTP_400_BAD_REQUEST)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    def delete(self,request,tipo_id,nro_id):
        actor=self.get_object(tipo_id,nro_id)
        actor.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)         

class ActorListView(generics.ListCreateAPIView):
    authentication_classes = [LoggingJWTAuthentication]
    permission_classes = [IsAuthenticated, HasRolePermission]

    queryset=ActorDeContrato.objects.all()
    ordering = ['-fechaActualizacion','-fechaCreacion']
    serializer_class=ActorDeContratoSerializer
    filter_backends=[filters.SearchFilter,filters.OrderingFilter] 
    search_fields = ['numeroIdentificacion','actordecontratonatural__primerNombre', 'actordecontratonatural__segundoNombre', 'actordecontratojuridico__razonSocialNombre']
    
    def get_queryset(self):
        try:            
            return self.queryset
        except ValidationError as e:
            raise ParseError(detail=str(e))
        except Exception as e:
            raise APIException(detail=str(e)) 
    def post(self,request):
        try:
            tpidentif=request.data.get('tipoIdentificacion')
            nroidentif=request.data.get('numeroIdentificacion')
            tipo_persona=getTipoPersona(tpidentif)
            

            
            if(tipo_persona=='N'):
                print("soy natural")
                serializer=ActorDeContratoNaturalCreateSerializer(data=request.data)
            elif(tipo_persona=='J'):
                print("soy juridico")
                serializer=ActorDeContratoJuridicoCreateSerializer(data=request.data)
            else:
                return Response({'detail':'Tipo de persona no soportado'},status=status.HTTP_400_BAD_REQUEST)
            if serializer.is_valid():
                serializer.save()                
                return Response(serializer.data,status=status.HTTP_201_CREATED)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            raise ParseError(detail=str(e))
        except IntegrityError as e:
            if 'ORA-00001' in str(e):
                return Response({'detail':'Ya existe un actor con el mismo tipo y número de identificación'},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            raise APIException(detail=str(e))
    def put(self,request):
        try:
            tpidentif=request.data.get('tipoIdentificacion')
            nroidentif=request.data.get('numeroIdentificacion')
            tipo_persona=getTipoPersona(tpidentif)            
            actor=ActorView.get_object(self,tpidentif,nroidentif)
            if(tipo_persona=='N'):            
                serializer=ActorDeContratoNaturalUpdateSerializer(actor,data=request.data)
            elif(tipo_persona=='J'):
                serializer=ActorDeContratoJuridicoUpdateSerializer(actor,data=request.data)
            else:
                return Response({'detail':'Tipo de persona no soportado'},status=status.HTTP_400_BAD_REQUEST)
            
            if serializer.is_valid():
                serializer.save(delete_non_serialized=True)
                return Response(serializer.data,status=status.HTTP_201_CREATED)
            else:
                error_messages = []
                errors = serializer.errors
                for field, field_errors in errors.items():
                    if field == "fideicomisoAsociado":
                        for error in field_errors:
                            if (error): error_messages.append(f"{error}")
                    else:
                        error_messages.append(f"{field}: {field_errors}")
                return Response({"detail": error_messages},status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            raise ParseError(detail=str(e))
        except Exception as e:
            raise APIException(detail=str(e))
        
    def delete(self,request):
        try:
            self.queryset.delete()  
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            raise APIException(detail=str(e)) 


class ActoresByFideiFileUploadView(APIView):    

    def post(self, request, codigo_SFC):
        form = UploadFileForm(request.POST, request.FILES)
       
        try:
            if form.is_valid():         
                file = form.cleaned_data['file'] 
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                dir_name = f'C:/Salida-SGC/actores/temp/masivo_por_fideicomiso/actores_'+ timestamp
                fs = FileSystemStorage(location=dir_name)
                file_name = fs.save(file.name, file)   
                print(file_name)             
                result=tkpCargarActoresPorFideiExcel.delay(
                    file_path=dir_name+"/"+file_name, 
                    fideicomiso=codigo_SFC, 
                    usuario_id=request.user.id,
                    disparador="MAN")
                
                return Response({'procesoId:':result.id,'message': 'La tarea se ha iniciado correctamente.'}, status=status.HTTP_202_ACCEPTED)
            else:
                return Response({'detail':'El archivo no es valido'},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            raise APIException(detail=str(e))
        
        
class ActoresFileUploadView(APIView):    

    def post(self, request):
        form = UploadFileForm(request.POST, request.FILES)
       
        try:
            if form.is_valid():         
                file = form.cleaned_data['file'] 
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                dir_name = f'C:/Salida-SGC/actores/temp/masivo_general/actores_'+ timestamp
                fs = FileSystemStorage(location=dir_name)
                file_name = fs.save(file.name, file)   
                print(file_name)             
                result=tkpCargarActoresExcel.delay(
                    file_path=dir_name+"/"+file_name,
                    usuario_id=request.user.id,
                    disparador="MAN")
                
                return Response({'proceso:':str(result.id),'message': 'La tarea se ha iniciado correctamente.'}, status=status.HTTP_202_ACCEPTED)
            else:
                return Response({'detail':'El archivo no es valido'},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            raise APIException(detail=str(e))

def getTipoPersona(tpidentif):
    tipo_documento = TipoDeDocumento.objects.get(tipoDocumento=tpidentif)
    tipo_persona = tipo_documento.idTipoPersona.tipoPersona
    return tipo_persona


from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from .models import ActorDeContrato
from django.core.exceptions import ValidationError
from .models import ActorDeContrato
from .serializers import ActorDeContratoReadSerializer,ActorDeContratoCreateSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics 
from sgc_backend.permissions import HasRolePermission, LoggingJWTAuthentication
from rest_framework.exceptions import ParseError
from rest_framework.exceptions import APIException
from rest_framework import filters


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
        serializer=ActorDeContratoReadSerializer(actor)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    def put(self,request,tipo_id,nro_id):
        actor=self.get_object(tipo_id,nro_id)
        serializer=ActorDeContratoCreateSerializer(actor,data=request.data)
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
    serializer_class=ActorDeContratoReadSerializer
    filter_backends=[filters.SearchFilter,filters.OrderingFilter] 
    search_fields = ['numeroIdentificacion', 'primerNombre','primerApellido','fideicomisoAsociado__tipoActor']
    def get_queryset(self):
        try:            
            return self.queryset
        except ValidationError as e:
            raise ParseError(detail=str(e))
        except Exception as e:
            raise APIException(detail=str(e)) 
        
    def post(self,request):
        try:
            serializer=ActorDeContratoCreateSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,status=status.HTTP_201_CREATED)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            raise ParseError(detail=str(e))
        except Exception as e:
            raise APIException(detail=str(e))
    def put(self,request):
        try:
            tpidentif=request.data.get('tipoIdentificacion')
            nroidentif=request.data.get('numeroIdentificacion')
            actor=ActorView.get_object(self,tpidentif,nroidentif)
            serializer=ActorDeContratoCreateSerializer(actor,data=request.data,context={'restart_relations': True})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,status=status.HTTP_201_CREATED)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            raise ParseError(detail=str(e))
from rest_framework import generics
from actores.models import ActorDeContrato
from actores.serializers import ActorDeContratoSerializer
from .models import Fideicomiso
from .serializers import FideicomisoSerializer
from rest_framework.views import APIView
from django.core.exceptions import ValidationError
import cx_Oracle
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from .models import Encargo, Fideicomiso
from .serializers import EncargoSerializer
from sgc_backend.pagination import CustomPageNumberPagination
from rest_framework.permissions import IsAuthenticated
from sgc_backend.permissions import HasRolePermission, LoggingJWTAuthentication
import logging
from rest_framework.exceptions import ParseError
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import EncargoSerializer
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound
from .tasks import CargueFideicomisoEncargos
from rest_framework import filters
from django.shortcuts import get_object_or_404

class FideicomisoList(generics.ListAPIView):
    authentication_classes = [LoggingJWTAuthentication]
    permission_classes = [IsAuthenticated, HasRolePermission] 
    
    search_fields=["codigoSFC","nombre"]
    ordering = ['-fechaCreacion']  
    filter_backends=[filters.SearchFilter,filters.OrderingFilter] 
    queryset = Fideicomiso.objects.all() 
    
    serializer_class = FideicomisoSerializer
    pagination_class = CustomPageNumberPagination
    
    def get_queryset(self):
        try:            
            exclude_ids = self.request.query_params.get('exclude_ids', None)
            if exclude_ids is not None:
                exclude_ids = [str(id) for id in exclude_ids.split(',')]
                return self.queryset.exclude(codigoSFC__in=exclude_ids)
            return self.queryset
        except ValidationError as e:
            raise ParseError(detail=str(e))
        except Exception as e:
            raise APIException(detail=str(e)) 
        
class EncargoListView(APIView):
    authentication_classes = [LoggingJWTAuthentication]
    permission_classes = [IsAuthenticated, HasRolePermission]
    pagination_class = CustomPageNumberPagination
    def get(self, request, codigo_sfc):
        try:
            fideicomiso = Fideicomiso.objects.get(codigoSFC=codigo_sfc)
        except ObjectDoesNotExist:
            raise NotFound('No existe ese fideicomiso .-.')
        except Exception as e:
            return Response({'detail': str(e)}, status=500)
        try:
            encargo = Encargo.objects.filter(fideicomiso=fideicomiso).order_by('numeroEncargo')
            for field, value in request.query_params.items():
                if field in [f.name for f in Encargo._meta.get_fields()]:
                    encargo = encargo.filter(**{field: value})
            paginator = CustomPageNumberPagination()
            paginated_encargo = paginator.paginate_queryset(encargo, request)
            encargo_serializer = EncargoSerializer(paginated_encargo, many=True)
            return paginator.get_paginated_response(encargo_serializer.data)
        except ObjectDoesNotExist:
            return Response({'detail': 'No se encuentra encargos'}, status=404)
        except Exception as e:
            return Response({'detail': str(e)}, status=500)
        
class ActoresByFideicomisoList(APIView):    
    authentication_classes = [LoggingJWTAuthentication]
    permission_classes = [IsAuthenticated, HasRolePermission]    
    
    def get(self, request, codigo_sfc):
        try:

            fideicomiso = get_object_or_404(Fideicomiso, codigoSFC=codigo_sfc)
            actores = ActorDeContrato.objects.filter(fideicomisoAsociado=fideicomiso).order_by('-fechaActualizacion','-fechaCreacion')
            paginator = CustomPageNumberPagination()
            paginated_actor=paginator.paginate_queryset(actores,request)
            serializer = ActorDeContratoSerializer(paginated_actor, many=True)        
            return paginator.get_paginated_response(serializer.data)
        
        except ObjectDoesNotExist:
            return Response({'detail':"No se encuentra fideicomiso"},status=404)
        except Exception as e:
            return Response({'detail': str(e)}, status=500)

class FideicomisoView(APIView):
    authentication_classes = [LoggingJWTAuthentication]
    permission_classes = [IsAuthenticated, HasRolePermission]
    
    def get_object_by_id(self,pk):
        try:
            return Fideicomiso.objects.get(pk=pk)
        except Fideicomiso.DoesNotExist:
            raise NotFound(detail='Fideicomiso no encontrado')
        except Exception as e:
            raise APIException(detail=str(e))

    def get(self, request, codigo_sfc):
        try:
            fideicomiso = self.get_object_by_id(codigo_sfc)
            serializer=FideicomisoSerializer(fideicomiso)
            return Response(serializer.data ,status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            raise NotFound('No existe ese fideicomiso.')
        except Exception as e:
            return Response({'error': str(e)}, status=500)        
         
logger = logging.getLogger(__name__)
class CargueFideicomisoEncargosView(APIView):
    authentication_classes = [LoggingJWTAuthentication]
    permission_classes = [IsAuthenticated, HasRolePermission]
    def post(self, request):
        try:
            user_id = request.user.id
            logger.info(f'User {user_id} requested to start the task')
            disparador="MAN"
            result = CargueFideicomisoEncargos.delay(usuario_id=request.user.id, 
                                                     disparador='MAN')
            logger.info(f'Task started with user_id: {user_id}, task_id: {result.id}')
            return Response({'status': 'Task started', 'task_id': result.id})
        except Fideicomiso.DoesNotExist:
            raise NotFound('Fideicomiso not found')
        except ParseError as e:
            raise e
        except Exception as e:
            raise APIException(detail=str(e))
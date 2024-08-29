from django.apps import apps
from rest_framework.views import APIView
from rest_framework import generics
from .serializers import LogCreateSerializer,LogCambiosM2MSerializer,LogUpdateSerializer
from .models import Log_Cambios_Create,Log_Cambios_M2M,Log_Cambios_Update,Log_Cambios_Delete
from sgc_backend.permissions import HasRolePermission, LoggingJWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from rest_framework.exceptions import ParseError
from rest_framework.exceptions import APIException
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.contrib.contenttypes.models import ContentType
from rest_framework.pagination import PageNumberPagination

class LogCreateView(APIView):
    authentication_classes = [LoggingJWTAuthentication]
    permission_classes = [IsAuthenticated, HasRolePermission]
    def get_object(self,model_name,object_key):
        try:
            return Log_Cambios_Create.objects.get(nombreModelo=model_name,objectId=object_key)
        except  Log_Cambios_Create.DoesNotExist:
            raise NotFound(detail='Log de creacion no encontrado')
        except Exception as e:
            raise APIException(detail=str(e))
    def get(self,request,model_name,object_key,format=None):
        log=self.get_object(model_name,object_key)
        serializer=LogCreateSerializer(log)
        return Response(serializer.data,status=status.HTTP_200_OK)
        
class LogCreateListView(generics.ListAPIView):
    authentication_classes = [LoggingJWTAuthentication]
    permission_classes = [IsAuthenticated, HasRolePermission]
    serializer_class=LogCreateSerializer
    queryset = Log_Cambios_Create.objects.all()
    search_fields = ['=nombreModelo','=objectId']
    def get_queryset(self):
        try:            
            return self.queryset
        except ValidationError as e:
            raise ParseError(detail=str(e))
        except Exception as e:
            raise APIException(detail=str(e))

class LogRelateView(APIView):
    authentication_classes = [LoggingJWTAuthentication]
    permission_classes = [IsAuthenticated, HasRolePermission]
    def get_object_childs(self,model_name,object_key):
        try:
            results=Log_Cambios_M2M.objects.filter(nombreModeloPadre=model_name,objectIdPadre=object_key).values('nombreModelo','objectId').distinct()
            if results.exists():
                return results
            else:
                return False
        except Exception as e:
            return False
        
class LogUpdateListView(APIView):
    authentication_classes = [LoggingJWTAuthentication]
    permission_classes = [IsAuthenticated, HasRolePermission]    
    def get_all_objects(self, model_name, object_key):
        result_list = list(self.get_object(model_name, object_key, Log_Cambios_Update))
        result_list += list(self.get_object(model_name, object_key, Log_Cambios_Delete))
        result_list += list(self.get_object(model_name, object_key, Log_Cambios_Create))

        # Check if model_name is ActorDeContrato
        if model_name == 'ActorDeContrato':
            # Check if ActorDeContratoJuridico or ActorDeContratoNatural exists with the given object_key
            if self.object_exists('ActorDeContratoJuridico', object_key) or self.object_exists('ActorDeContratoNatural', object_key):
                result_list += list(self.get_object(model_name, object_key, Log_Cambios_Create))

        child_relations = LogRelateView.get_object_childs(self, model_name, object_key)
        if child_relations:
            for child in child_relations:
                result_list += list(self.get_object(child['nombreModelo'], child['objectId'], Log_Cambios_Update))
                result_list += list(self.get_object(child['nombreModelo'], child['objectId'], Log_Cambios_Delete))
                result_list += list(self.get_object(child['nombreModelo'], child['objectId'], Log_Cambios_Create))
        return sorted(result_list, key=lambda x: x.tiempoAccion, reverse=True)

    def get_object(self, model_name, object_key, model):
        try:
            return model.objects.filter(nombreModelo=model_name, objectId=object_key)
        except Exception as e:
            return model.objects.none()
    def object_exists(self, model_name, object_key):
        try:
            content_type = ContentType.objects.get(model=model_name.lower())
            model = apps.get_model(app_label=content_type.app_label, model_name=model_name)
            return model.objects.filter(id=object_key).exists()
        except ContentType.DoesNotExist:
            return False
    def get(self, request, model_name, object_key):
        try:
            queryset = self.get_all_objects(model_name, object_key)
            paginator = PageNumberPagination()
            paginator.page_size = 10
            paginated_queryset = paginator.paginate_queryset(queryset, request)
            serializer = LogUpdateSerializer(paginated_queryset, many=True)
            return paginator.get_paginated_response(serializer.data)
        except ValidationError as e:
            raise ParseError(detail=str(e))
        except Exception as e:
            raise APIException(detail=str(e))
def track_changes(request, model_name, object_id):
    # Get the ContentType for the model
    content_type = ContentType.objects.get(model=model_name)

    # Fetch the log entries for the given model and object ID
    create_logs = Log_Cambios_Create.objects.filter(contentType=content_type, objectId=object_id)
    update_logs = Log_Cambios_Update.objects.filter(contentType=content_type, objectId=object_id)
    delete_logs = Log_Cambios_Delete.objects.filter(contentType=content_type, objectId=object_id)
    m2m_logs = Log_Cambios_M2M.objects.filter(contentType=content_type, objectId=object_id)

    # Convert the log entries to JSON and return them
    return JsonResponse({
        'create_logs': list(create_logs.values()),
        'update_logs': list(update_logs.values()),
        'delete_logs': list(delete_logs.values()),
        'm2m_logs': list(m2m_logs.values()),
    })
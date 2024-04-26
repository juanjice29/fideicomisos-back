from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Log_Cambios_Create, Log_Cambios_Update, Log_Cambios_Delete,Log_Cambios_M2M
from .serializers import LogCreateSerializer, LogUpdateSerializer, LogDeleteSerializer,LogCambiosM2MSerializer
from actores_de_contrato_cargue.models import ActorDeContrato
from django.forms.models import model_to_dict
from collections import defaultdict
class LogView(APIView):
    def get(self, request, nombre_modelo):
        try:
            logs_create = Log_Cambios_Create.objects.filter(NombreModelo=nombre_modelo)
            logs_update = Log_Cambios_Update.objects.filter(NombreModelo=nombre_modelo)
            logs_delete = Log_Cambios_Delete.objects.filter(NombreModelo=nombre_modelo)

            logs_create_serializer = LogCreateSerializer(logs_create, many=True)
            logs_update_serializer = LogUpdateSerializer(logs_update, many=True)
            logs_delete_serializer = LogDeleteSerializer(logs_delete, many=True)

            return Response({
                'create_logs': logs_create_serializer.data,
                'update_logs': logs_update_serializer.data,
                'delete_logs': logs_delete_serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ChangesView(APIView):
    def post(self, request):
        # Get the numeroidentificacion from the data
        try:
            model=request.data.get('model')
            key=request.data.get('key')
            key_value=request.data.get('keyValue')
            object_id=Log_Cambios_Create.objects.filter(NombreModelo=model,NombreCampo=key,NuevoValor=key_value).first()
            #NumeroIdentificacion = request.data.get('NumeroIdentificacion')
            if object_id:
                object_id=object_id.object_id
            else:
                return Response({'status': 'error', 'message': 'No se encontro historial de cambios'}, status=status.HTTP_404_NOT_FOUND)
            # Get the ActorDeContrato object with the given numeroidentificacion
            #actor = ActorDeContrato.objects.get(NumeroIdentificacion=NumeroIdentificacion)

            # Get the changes from the create, update, and delete logs
            create_logs = Log_Cambios_Create.objects.filter(object_id=object_id).order_by('TiempoAccion')
            update_logs = Log_Cambios_Update.objects.filter(object_id=object_id).order_by('TiempoAccion')
            delete_logs = Log_Cambios_Delete.objects.filter(object_id=object_id).order_by('TiempoAccion')
            m2m_logs_add = Log_Cambios_M2M.objects.filter(object_id=object_id,Action="pre_add").order_by('TiempoAccion')
            m2m_logs_del=Log_Cambios_M2M.objects.filter(object_id=object_id,Action="pre_remove").order_by('TiempoAccion')
            response_dict={"create":[],"update":[],"delete":[]}
            log_cambios_serializer=LogCreateSerializer(create_logs, many=True)
            log_update_serializer=LogUpdateSerializer(update_logs, many=True)       
            log_delete_serializer=LogDeleteSerializer(delete_logs, many=True)    
            
            individual_logs_id_create=[]
            individual_log_create=[]
            for log in log_cambios_serializer.data:
                request_id = log["request_id"]
                if request_id not in individual_logs_id_create:
                    individual_log_create.append({"requestId":request_id,
                                           "user":log["Usuario"],
                                           "type":"create",
                                           "timeAction":log["TiempoAccion"],
                                           "ip":log["Ip"],
                                           "modelName":log["NombreModelo"],
                                           "changes":[]})
                    individual_logs_id_create.append(request_id)   

                for ind_log in individual_log_create:
                    if ind_log["requestId"]==request_id:
                        ind_log["changes"].append({
                            "id":log["id"],
                            "field":log["NombreCampo"],  
                            "oldValue":None,                          
                            "newValue":log["NuevoValor"],
                            "jsonValue":None
                        })       

            response_dict["create"]=individual_log_create  

            log_m2m_add_serializer=LogCambiosM2MSerializer(m2m_logs_add, many=True)
            log_m2m_del_serializer=LogCambiosM2MSerializer(m2m_logs_del, many=True)

            individual_logs_id_update=[]
            individual_log_update=[]                
            for log in log_update_serializer.data:
                request_id = log["request_id"]
                if request_id not in individual_logs_id_update:
                    individual_log_update.append({"requestId":request_id,
                                           "user":log["Usuario"],
                                           "type":"update",
                                           "timeAction":log["TiempoAccion"],
                                           "ip":log["Ip"],
                                           "modelName":log["NombreModelo"],
                                           "changes":[]})
                    individual_logs_id_update.append(request_id)

                for ind_log in individual_log_update:
                    if ind_log["requestId"]==request_id:
                        ind_log["changes"].append({
                            "id":log["id"],                            
                            "field":log["NombreCampo"],
                            "oldValue":log["AntiguoValor"],
                            "newValue":log["NuevoValor"],
                            "jsonValue":None
                        })   
            for log in log_m2m_add_serializer.data:
                request_id = log["request_id"]
                if request_id not in individual_logs_id_update:
                    individual_log_update.append({"requestId":request_id,
                                           "user":log["Usuario"],
                                           "type":"asociate",
                                           "timeAction":log["TiempoAccion"],
                                           "ip":log["Ip"],
                                           "modelName":log["NombreModelo"],
                                           "changes":[]})
                    individual_logs_id_update.append(request_id)

                for ind_log in individual_log_update:
                    if ind_log["requestId"]==request_id:
                        ind_log["changes"].append({
                            "id":log["id"],                            
                            "field":log["NombreCampo"],
                            "oldValue":None,
                            "newValue":log["Valor"],
                            "jsonValue":log["JsonValue"]
                        }) 
            sorted_update=sorted(individual_log_update,key=lambda x:x["timeAction"],reverse=True)
            response_dict["update"]=sorted_update
            

            individual_logs_id_delete=[]
            individual_log_delete=[]
            for log in log_delete_serializer.data:
                request_id = log["request_id"]
                if request_id not in individual_logs_id_delete:
                    individual_log_delete.append({"requestId":request_id,
                                           "user":log["Usuario"],
                                           "type":"delete",
                                           "timeAction":log["TiempoAccion"],
                                           "ip":log["Ip"],
                                           "modelName":log["NombreModelo"],
                                           "changes":[]})
                    individual_logs_id_delete.append(request_id)

                for ind_log in individual_log_delete:
                    if ind_log["requestId"]==request_id:
                        ind_log["changes"].append({
                            "id":log["id"],                            
                            "field":log["NombreCampo"],
                            "oldValue":log["AntiguoValor"],
                            "newValue":None,
                            "jsonValue":None                        
                        })

            for log in log_m2m_del_serializer.data:
                request_id = log["request_id"]
                if request_id not in individual_logs_id_delete:
                    individual_log_delete.append({"requestId":request_id,
                                           "user":log["Usuario"],
                                           "type":"disociate",
                                           "timeAction":log["TiempoAccion"],
                                           "ip":log["Ip"],
                                           "modelName":log["NombreModelo"],
                                           "changes":[]})
                    individual_logs_id_delete.append(request_id)

                for ind_log in individual_log_delete:
                    if ind_log["requestId"]==request_id:
                        ind_log["changes"].append({
                            "id":log["id"],                            
                            "field":log["NombreCampo"],
                            "oldValue":log["Valor"],
                            "newValue":None,
                            "jsonValue":log["JsonValue"]
                        })
            sorted_delete=sorted(individual_log_delete,key=lambda x:x["timeAction"],reverse=True)
            response_dict["delete"]=sorted_delete

            return Response(response_dict)        
            
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
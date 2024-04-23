from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Log_Cambios_Create, Log_Cambios_Update, Log_Cambios_Delete
from .serializers import LogCreateSerializer, LogUpdateSerializer, LogDeleteSerializer
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
        NumeroIdentificacion = request.data.get('NumeroIdentificacion')

        # Get the ActorDeContrato object with the given numeroidentificacion
        actor = ActorDeContrato.objects.get(NumeroIdentificacion=NumeroIdentificacion)

        # Get the changes from the create, update, and delete logs
        create_logs = Log_Cambios_Create.objects.filter(object_id=actor.id).order_by('TiempoAccion')
        update_logs = Log_Cambios_Update.objects.filter(object_id=actor.id).order_by('TiempoAccion')
        delete_logs = Log_Cambios_Delete.objects.filter(object_id=actor.id).order_by('TiempoAccion')

        changes_by_request = defaultdict(lambda: {'create': [], 'update': [], 'delete': [], 'timestamp': None})
        for log in create_logs:
            request_id = log.request_id
            changes_by_request[request_id]['create'].append(model_to_dict(log))
            if changes_by_request[request_id]['timestamp'] is None:
                changes_by_request[request_id]['timestamp'] = log.TiempoAccion.strftime('%Y-%m-%d %H:%M:%S')
        for log in update_logs:
            request_id = log.request_id
            changes_by_request[request_id]['update'].append(model_to_dict(log))
            if changes_by_request[request_id]['timestamp'] is None:
                changes_by_request[request_id]['timestamp'] = log.TiempoAccion.strftime('%Y-%m-%d %H:%M:%S')
        for log in delete_logs:
            request_id = log.request_id
            changes_by_request[request_id]['delete'].append(model_to_dict(log))
            if changes_by_request[request_id]['timestamp'] is None:
                changes_by_request[request_id]['timestamp'] = log.TiempoAccion.strftime('%Y-%m-%d %H:%M:%S')

        # Return the changes as a JSON response
        return Response(dict(changes_by_request))        
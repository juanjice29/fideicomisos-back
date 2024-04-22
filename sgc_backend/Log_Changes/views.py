from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Log_Cambios_Create, Log_Cambios_Update, Log_Cambios_Delete
from .serializers import LogCreateSerializer, LogUpdateSerializer, LogDeleteSerializer

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
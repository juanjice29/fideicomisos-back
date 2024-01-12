from rest_framework import generics
from .models import Fideicomiso
from .serializers import FideicomisoSerializer
from django.http import JsonResponse
from django.views import View
from dateutil.parser import parse
from django.http import HttpRequest
from rest_framework.views import APIView
from django.core.exceptions import ValidationError
import cx_Oracle
from .models import Fideicomiso, TipoDeDocumento
from dateutil.relativedelta import relativedelta
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from .models import TipoDeDocumento
from dateutil.relativedelta import relativedelta
from django.shortcuts import get_object_or_404
from rest_framework import generics
from .models import Encargo, Fideicomiso, EncargoTemporal
from .serializers import EncargoSerializer
from django.db import connection
from django.db import transaction
from django.db import IntegrityError
from django.contrib import messages
import logging
import hashlib
from sgc_backend.pagination import CustomPageNumberPagination, ActorDeContratoPagination, EncargoPagination
from django.core.cache import cache
from .serializers import TipoDeDocumentoSerializer
from rest_framework.permissions import IsAuthenticated
from sgc_backend.permissions import HasRolePermission, LoggingJWTAuthentication
import logging
from django.core.paginator import Paginator
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ParseError
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import EncargoSerializer
from actores_de_contrato_cargue.serializers import ActorDeContratoSerializer
from actores_de_contrato_cargue.models import ActorDeContrato
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound
from .tasks import update_fideicomiso
class TipoDeDocumentoListView(generics.ListAPIView):
    authentication_classes = [LoggingJWTAuthentication]
    permission_classes = [IsAuthenticated, HasRolePermission]
    queryset = TipoDeDocumento.objects.all()
    serializer_class = TipoDeDocumentoSerializer   

class EncargoListView(APIView):
    authentication_classes = [LoggingJWTAuthentication]
    permission_classes = [IsAuthenticated, HasRolePermission]
    pagination_class = CustomPageNumberPagination
    def get(self, request, codigo_sfc):
        try:
            fideicomiso = Fideicomiso.objects.get(CodigoSFC=codigo_sfc)
        except ObjectDoesNotExist:
            raise NotFound('No existe ese fideicomiso .-.')
        except Exception as e:
            return Response({'error': str(e)}, status=500)
        try:
            encargo = Encargo.objects.filter(Fideicomiso=fideicomiso).order_by('NumeroEncargo')
            for field, value in request.query_params.items():
                if field in [f.name for f in Encargo._meta.get_fields()]:
                    encargo = encargo.filter(**{field: value})
            paginator = CustomPageNumberPagination()
            paginated_encargo = paginator.paginate_queryset(encargo, request)
            encargo_serializer = EncargoSerializer(paginated_encargo, many=True)
            return paginator.get_paginated_response(encargo_serializer.data)
        except ObjectDoesNotExist:
            return Response({'error': 'No se encuentra encargos'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
class FideicomisoDetailView(APIView):
    authentication_classes = [LoggingJWTAuthentication]
    permission_classes = [IsAuthenticated, HasRolePermission]
    pagination_class = CustomPageNumberPagination
    def get(self, request, codigo_sfc):
        try:
            fideicomiso = Fideicomiso.objects.get(CodigoSFC=codigo_sfc)
        except ObjectDoesNotExist:
            raise NotFound('No existe ese fideicomiso .-.')
        except Exception as e:
            return Response({'error': str(e)}, status=500)
        encargo_paginator = EncargoPagination()
        encargo_paginator.page_size = 10
        actores_de_contrato_paginator = ActorDeContratoPagination()
        actores_de_contrato_paginator.page_size = 10
        encargo = Encargo.objects.filter(Fideicomiso=fideicomiso).order_by('NumeroEncargo')
        for field, value in request.query_params.items():
            if field in [f.name for f in Encargo._meta.get_fields()]:
                encargo = encargo.filter(**{field: value})
        actores_de_contrato = ActorDeContrato.objects.filter(FideicomisoAsociado=fideicomiso).order_by('NumeroIdentificacion')
        for field, value in request.query_params.items():
            if field in [f.name for f in ActorDeContrato._meta.get_fields()]:
                actores_de_contrato = actores_de_contrato.filter(**{field: value}) 
        encargo = encargo_paginator.paginate_queryset(encargo, request)
        actores_de_contrato = actores_de_contrato_paginator.paginate_queryset(actores_de_contrato, request)
        encargo_serializer = EncargoSerializer(encargo, many=True)
        actores_de_contrato_serializer = ActorDeContratoSerializer(actores_de_contrato, many=True)
        return Response({
            'encargo': encargo_serializer.data,
            'actores_de_contrato': actores_de_contrato_serializer.data,
            #'beneficiario_final': beneficiario_final_serializer.data,
        })

class ActorFideicomisoListView(APIView):
    authentication_classes = [LoggingJWTAuthentication]
    permission_classes = [IsAuthenticated, HasRolePermission]

    def get(self, request, numero_identificacion):
        try:
            actor = ActorDeContrato.objects.get(NumeroIdentificacion=numero_identificacion)
            fideicomisos = actor.FideicomisoAsociado.all()

            for field, value in request.query_params.items():
                if field in [f.name for f in Fideicomiso._meta.get_fields()]:
                    fideicomisos = fideicomisos.filter(**{field: value})

            paginator = CustomPageNumberPagination()
            paginator.page_size = 10  # set the page size here
            paginated_fideicomisos = paginator.paginate_queryset(fideicomisos, request)
            fideicomiso_serializer = FideicomisoSerializer(paginated_fideicomisos, many=True)

            return paginator.get_paginated_response(fideicomiso_serializer.data)
        except ObjectDoesNotExist:
            return Response({'error': 'No se encuentran los fideicomisos :O'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
class FideicomisoList(generics.ListAPIView):
    authentication_classes = [LoggingJWTAuthentication]
    permission_classes = [IsAuthenticated, HasRolePermission]
    serializer_class = FideicomisoSerializer
    pagination_class = CustomPageNumberPagination
    def get_queryset(self):
        try:
            queryset = Fideicomiso.objects.all()
            codigo_sfc = self.request.query_params.get('codigo_sfc', None)
            nombre = self.request.query_params.get('nombre', None)
            order_by = self.request.query_params.get('order_by', 'FechaCreacion')
            order_direction = self.request.query_params.get('order_direction', 'asc')

            if codigo_sfc is not None:
                queryset = queryset.filter(CodigoSFC__icontains=codigo_sfc)

            if nombre is not None:
                queryset = queryset.filter(Nombre__icontains=nombre)

            if order_by in ['CodigoSFC', 'FechaCreacion', 'Estado']:
                if order_direction == 'desc':
                    order_by = '-' + order_by
                queryset = queryset.order_by(order_by, 'CodigoSFC')
            return queryset
        except ValidationError as e:
            raise ParseError(detail=str(e))
        except Exception as e:
            raise APIException(detail=str(e))
    def post(self, request, *args, **kwargs):
            try:
                codigo_sfc = request.data.get('codigo_sfc', None)
                nombre = request.data.get('nombre', None)
                order_by = request.data.get('order_by', 'FechaCreacion')
                order_direction = request.data.get('order_direction', 'asc')

                queryset = Fideicomiso.objects.all()

                if codigo_sfc is not None:
                    queryset = queryset.filter(CodigoSFC__icontains=codigo_sfc)

                if nombre is not None:
                    queryset = queryset.filter(Nombre__icontains=nombre)

                if order_by in ['CodigoSFC', 'FechaCreacion', 'Estado']:
                    if order_direction == 'desc':
                        order_by = '-' + order_by
                    queryset = queryset.order_by(order_by)
                page_size = request.data.get('page_size', 10)
                page_number = request.data.get('page_number', 1)
                paginator = PageNumberPagination()
                paginator.page_size = page_size
                request.query_params._mutable = True
                request.query_params['page'] = page_number
                request.query_params._mutable = False
                paginator = PageNumberPagination()
                paginator.page_size = page_size
                paginated_queryset = paginator.paginate_queryset(queryset, request)
                serializer = FideicomisoSerializer(paginated_queryset, many=True)
                return paginator.get_paginated_response(serializer.data)
            except ValidationError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class UpdateFideicomisoView(APIView):
    authentication_classes = [LoggingJWTAuthentication]
    permission_classes = [IsAuthenticated, HasRolePermission]
    def get(self, request, *args, **kwargs):
        try:
            # Connect to the Oracle database
            dsn_tns = cx_Oracle.makedsn('192.168.168.175', '1521', service_name='SIFIUN43')
            conn = cx_Oracle.connect(user='VU_SFI', password='VU_SFI43', dsn=dsn_tns)
            cur = conn.cursor()

            # Determine the number of rows in the table
            cur.execute("SELECT COUNT(*) FROM FD_TFIDE")
            num_rows = cur.fetchone()[0]

            # Determine the number of pages
            rows_per_page = 1000
            num_pages = num_rows // rows_per_page
            if num_rows % rows_per_page != 0:
                num_pages += 1

            # Fetch and process the data page by page
            for page in range(num_pages):
                cur.execute(f"""
                SELECT * FROM (
                        SELECT FD.FIDE_FIDE, FD.FIDE_CIAS, FD.FIDE_FECCRE, FD.FIDE_FECHVENCI, GE.CIAS_DESCRI,GE.CIAS_STATUS, ROWNUM RN
                        FROM FD_TFIDE FD
                        JOIN GE_TCIAS GE ON FD.FIDE_CIAS = GE.CIAS_CIAS
                        WHERE ROWNUM <= {(page + 1) * rows_per_page}
                        ORDER BY FD.FIDE_FECCRE ASC
                    )
                    WHERE RN > {page * rows_per_page}
                """)
                rows = cur.fetchall()
                update_fideicomiso.delay(rows)
            transaction.commit()
            cur.close()
            conn.close()
            return Response({'status': 'Exito'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'status': 'error', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

logger = logging.getLogger(__name__)
class UpdateEncargoTemp(APIView):
    authentication_classes = [LoggingJWTAuthentication]
    permission_classes = [IsAuthenticated, HasRolePermission]
    def get(self, request, *args, **kwargs):
        try:
            # Connect to the Oracle database
            
            dsn_tns = cx_Oracle.makedsn('192.168.168.175', '1521', service_name='SIFIUN43')
            conn = cx_Oracle.connect(user='VU_SFI', password='vu_sfi', dsn=dsn_tns)
            cur = conn.cursor()

            cur.execute("""
                SELECT FD.FIDE_FIDE, PL.PLAN_PLAN, PL.PLAN_DESCRI
                FROM FD_TFIDE FD
                JOIN SF_TPTPL PT ON FD.FIDE_FIDE = PT.PTPL_FDEI
                JOIN SF_TPLAN PL ON PT.PTPL_PLAN = PL.PLAN_PLAN
            """)

            rows = []
            while True:
                row = cur.fetchone()
                if row is None:
                    break
                rows.append(row)
            hasher = hashlib.sha256()
            hasher.update(str(rows).encode('utf-8'))
            new_hash = hasher.hexdigest()
            logger.info(f"Fetched {len(rows)} rows from the database")
            old_hash = cache.get('encargo_temporal_hash')
            if old_hash != new_hash:
                for i, row in enumerate(rows, start=1):
                    encargotemporal, created = EncargoTemporal.objects.update_or_create(
                        NumeroEncargo=row[1],
                        Fideicomiso=row[0],
                        defaults={
                            'Descripcion': row[2]
                            }
                        )
                    if i % 1000 == 0:
                        logger.info(f"Updated or created {i} records")
            cache.set('encargo_temporal_hash', new_hash)
            transaction.commit()
            logger.info(f"Updated or created {len(rows)} records in total")
            cur.close()
            conn.close()    
            return Response({'status': 'success'}, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return Response({'status': 'error', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class UpdateEncargoFromTemp(APIView):
    authentication_classes = [LoggingJWTAuthentication]
    permission_classes = [IsAuthenticated, HasRolePermission]
    def get(self, request, *args, **kwargs):
        # First, call the UpdateEncargoTemp view
        update_encargo_temp_view = UpdateEncargoTemp.as_view()

        # Create a new HttpRequest object and populate it with the necessary attributes
        http_request = HttpRequest()
        http_request.method = request.method
        http_request.user = request.user
        http_request.META = request.META

        response = update_encargo_temp_view(http_request)
        if response.status_code != status.HTTP_200_OK:
            return response  # If the UpdateEncargoTemp view failed, return its response

        # Then, update the Encargo model with the fields from the EncargoTemp model
        encargos_temp = EncargoTemporal.objects.all()
        for encargo_temp in encargos_temp:
            try:
                # Get the Fideicomiso instance by comparing the Fideicomiso of the EncargoTemp to CodigoSFC of Fideicomiso model
                fideicomiso_instance = Fideicomiso.objects.get(CodigoSFC=encargo_temp.Fideicomiso)
                # Update or create the Encargo instance
                try:
                    Encargo.objects.update_or_create(
                        Fideicomiso=fideicomiso_instance,
                        NumeroEncargo=encargo_temp.NumeroEncargo,
                        defaults={'Descripcion': encargo_temp.Descripcion}
                    )
                except IntegrityError:
                    pass  # Ignore EncargoTemp instances with duplicate NumeroEncargo
            except Fideicomiso.DoesNotExist:
                pass  # Ignore EncargoTemp instances with non-existent Fideicomiso

        return Response({'status': 'success'}, status=status.HTTP_200_OK)
from rest_framework import generics
from .models import Fideicomiso
from .serializers import FideicomisoSerializer
from django.http import JsonResponse
from django.views import View
from dateutil.parser import parse
from rest_framework.views import APIView
import cx_Oracle
from .models import Fideicomiso, TipoDeDocumento
from dateutil.relativedelta import relativedelta
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import TipoDeDocumento
from dateutil.relativedelta import relativedelta
from django.shortcuts import get_object_or_404
from rest_framework import generics
from .models import Encargo, Fideicomiso
from .serializers import EncargoSerializer
from django.db import connection
class EncargoListView(generics.ListAPIView):
    queryset = Encargo.objects.all()
    serializer_class = EncargoSerializer
class FideicomisoList(generics.ListAPIView):
    serializer_class = FideicomisoSerializer
    pagination_class = PageNumberPagination
    def get_queryset(self):
        try:
            queryset = Fideicomiso.objects.all().order_by('-FechaCreacion')
            return queryset
        except Exception as e:
            raise Exception(f"Error occurred: {str(e)}")
class UpdateFideicomisoView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            # Connect to the Oracle database
            dsn_tns = cx_Oracle.makedsn('192.168.168.175', '1521', service_name='SIFIUN43')
            conn = cx_Oracle.connect(user='VU_SFI', password='vu_sfi', dsn=dsn_tns)
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
                        ORDER BY FD.FIDE_FECCRE DESC
                    )
                    WHERE RN > {page * rows_per_page}
                """)
                rows = cur.fetchall()
                tipo_identificacion = TipoDeDocumento.objects.get(TipoDocumento='NJ')
                # Update Django objects
                for row in rows:
                    fecha_vencimiento = row[3] if row[3] else None
                    fideicomiso, created = Fideicomiso.objects.update_or_create(
                        CodigoSFC=row[0],
                        defaults={
                            'TipoIdentificacion': tipo_identificacion,
                            'Nombre': row[4],
                            'FechaCreacion': row[2] if row[2] else None,
                            'FechaVencimiento': fecha_vencimiento,
                            'FechaProrroga': fecha_vencimiento + relativedelta(years=30) if fecha_vencimiento else None,
                            'Estado': row[5]
                        }
                    )
            cur.close()
            conn.close()
            return Response({'status': 'success'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'status': 'error', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class UpdateEncargoView(generics.UpdateAPIView):
    def get(self, request, *args, **kwargs):
        try:
            # Connect to the Oracle database
            dsn_tns = cx_Oracle.makedsn('192.168.168.175', '1521', service_name='SIFIUN43')
            conn = cx_Oracle.connect(user='VU_SFI', password='vu_sfi', dsn=dsn_tns)
            cur = conn.cursor()

            with connection.cursor() as cur:
                cur.execute("""
                    SELECT FD.FIDE_FIDE, PL.PLAN_PLAN, PL.PLAN_DESCRI
                    FROM FD_TFIDE FD
                    JOIN SF_TPTPL PT ON FD.FIDE_FIDE = PT.PTPL_FDEI
                    JOIN SF_TPLAN PL ON PT.PTPL_PLAN = PL.PLAN_PLAN
                """,)
                rows = cur.fetchall()

            for row in rows:
                encargo, created = Encargo.objects.update_or_create(
                    NumeroEncargo=row[1],
                    defaults={
                    'Fideicomiso' : row[0],
                    'Descripcion' : row[2]
                    }
                )
            cur.close()
            conn.close()
            return Response({'status': 'success'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'status': 'error', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return encargo
class FetchFideicomisoView(APIView):
    pagination_class = PageNumberPagination
    def get(self, request, *args, **kwargs):
        try:
            dsn_tns = cx_Oracle.makedsn('192.168.168.175', '1521', service_name='SIFIUN43')
            conn = cx_Oracle.connect(user='VU_SFI', password='vu_sfi', dsn=dsn_tns)
            cur = conn.cursor()

            # Determine the number of rows in the table
            cur.execute("SELECT COUNT(*) FROM FD_TFIDE")
            num_rows = cur.fetchone()[0]

            # Determine the number of pages
            rows_per_page = 10
            num_pages = num_rows // rows_per_page
            if num_rows % rows_per_page != 0:
                num_pages += 1     
            data = []
            for page in range(num_pages):
                cur.execute(f"""
                SELECT * FROM (
                        SELECT FD.FIDE_FIDE, FD.FIDE_CIAS, FD.FIDE_FECCRE, FD.FIDE_FECHVENCI, GE.CIAS_DESCRI, ROWNUM RN
                        FROM FD_TFIDE FD
                        JOIN GE_TCIAS GE ON FD.FIDE_CIAS = GE.CIAS_CIAS
                        WHERE ROWNUM <= {(page + 1) * rows_per_page}
                    )
                    WHERE RN > {page * rows_per_page}
                """)
                rows = cur.fetchall()
                tipo_identificacion = TipoDeDocumento.objects.get(TipoDocumento='NJ')
                for row in rows:
                    fecha_vencimiento = row[3] if row[3] else None
                    fecha_prorroga = fecha_vencimiento + relativedelta(years=30) if fecha_vencimiento else None
                    data.append({
                        'CodigoSFC': row[0],
                        'TipoIdentificacion': tipo_identificacion.Descripcion,
                        'Nombre': row[4],
                        'FechaCreacion': row[2] if row[2] else None,
                        'FechaVencimiento': fecha_vencimiento,
                        'FechaProrroga': fecha_prorroga
                    })

            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'status': 'error', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
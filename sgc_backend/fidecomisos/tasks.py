from celery import shared_task
from .models import Fideicomiso, TipoDeDocumento
from django.core.cache import cache
from dateutil.relativedelta import relativedelta
import hashlib
import cx_Oracle
import hashlib
from django.core.cache import cache
from django.db import transaction
from dateutil.relativedelta import relativedelta
from .models import Fideicomiso, TipoDeDocumento
from django.core.cache import cache
from django.db import transaction
from .models import EncargoTemporal
from .models import EncargoTemporal, Fideicomiso, Encargo
from django.db import IntegrityError
from process.models import EstadoEjecucion
from process.decorators import TipoLogEnum, guardarLogEjecucionProceso, track_process
from celery import current_task
import logging
import os
db_name_sifi= os.getenv("DB_NAME_SIFI")
db_user_sifi = os.getenv("DB_USER_SIFI")
db_pass_sifi = os.getenv("DB_PASS_SIFI")
db_host_sifi = os.getenv("DB_HOST_SIFI")
db_port_sifi = os.getenv("DB_PORT_SIFI")
@shared_task
def process_fideicomisos():
    try:
        dsn_tns = cx_Oracle.makedsn(db_host_sifi, db_port_sifi, service_name=db_name_sifi)
        conn = cx_Oracle.connect(user=db_user_sifi, password=db_pass_sifi, dsn=dsn_tns)
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
            tipo_identificacion = TipoDeDocumento.objects.get(tipoDocumento='NJ')
            hasher = hashlib.sha256()
            hasher.update(str(rows).encode('utf-8'))
            new_hash = hasher.hexdigest()
            old_hash = cache.get('fideicomiso_hash')
            if old_hash != new_hash:
                for row in rows:
                    fecha_vencimiento = row[3] if row[3] else None
                    fideicomiso, created = Fideicomiso.objects.update_or_create(
                        codigoSFC=row[0],
                        defaults={
                            'tipoIdentificacion': tipo_identificacion,
                            'nombre': row[4],
                            'fechaCreacion': row[2] if row[2] else None,
                            'fechaVencimiento': fecha_vencimiento,
                            'fechaProrroga': fecha_vencimiento + relativedelta(years=30) if fecha_vencimiento else None,
                            'estado': row[5]
                        }
                    )
                cache.set('fideicomiso_hash', new_hash)
        transaction.commit()
        cur.close()
        conn.close()
        return {'status': 'Exito'}
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

@shared_task
def process_encargo_temporal():
    try:
        # Connect to the Oracle database
        dsn_tns = cx_Oracle.makedsn(db_host_sifi, db_port_sifi, service_name=db_name_sifi)
        conn = cx_Oracle.connect(user=db_user_sifi, password=db_pass_sifi, dsn=dsn_tns)
        cur = conn.cursor()

        # Execute the query
        cur.execute("""
            SELECT FD.FIDE_FIDE, PL.PLAN_PLAN, PL.PLAN_DESCRI
            FROM FD_TFIDE FD
            JOIN SF_TPTPL PT ON FD.FIDE_FIDE = PT.PTPL_FDEI
            JOIN SF_TPLAN PL ON PT.PTPL_PLAN = PL.PLAN_PLAN
        """)

        # Fetch the rows
        rows = []
        while True:
            row = cur.fetchone()
            if row is None:
                break
            rows.append(row)

        # Hash the fetched rows
        hasher = hashlib.sha256()
        hasher.update(str(rows).encode('utf-8'))
        new_hash = hasher.hexdigest()

        # Check if the hash has changed
        old_hash = cache.get('encargo_temporal_hash')
        if old_hash != new_hash:
            for i, row in enumerate(rows, start=1):
                EncargoTemporal.objects.update_or_create(
                    numeroEncargo=row[1],
                    fideicomiso=row[0],
                    defaults={
                        'descripcion': row[2]
                    }
                )
            # Update the cache with the new hash
            cache.set('encargo_temporal_hash', new_hash)
        # Commit the transaction
        transaction.commit()
        # Close the cursor and connection
        cur.close()
        conn.close()

        return {'status': 'success'}
    except Exception as e:
        return {'status': 'error', 'error': str(e)}
    
@shared_task
def update_encargo_task():
    try:
        # Update the Encargo model with the fields from the EncargoTemp model
        encargos_temp = EncargoTemporal.objects.all()
        for encargo_temp in encargos_temp:
            try:
                # Get the Fideicomiso instance by comparing the Fideicomiso of the EncargoTemp to codigoSFC of Fideicomiso model
                fideicomiso_instance = Fideicomiso.objects.get(codigoSFC=encargo_temp.fideicomiso)
                
                # Update or create the Encargo instance
                try:
                    Encargo.objects.update_or_create(
                        fideicomiso=fideicomiso_instance,
                        numeroEncargo=encargo_temp.numeroEncargo,
                        defaults={'descripcion': encargo_temp.descripcion}
                    )
                except IntegrityError:
                    pass  # Ignore EncargoTemp instances with duplicate NumeroEncargo
            except Fideicomiso.DoesNotExist:
                pass  # Ignore EncargoTemp instances with non-existent Fideicomiso
        
        return {'status': 'success'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}
logger = logging.getLogger(__name__)
@shared_task
@track_process
def CargueFideicomisoEncargos(usuario_id, disparador, ejecucion=None):
    try:
        logger.info(f'Starting task for user_id: {usuario_id}')
        # Update execution state
        ejecucion.estadoEjecucion = EstadoEjecucion.objects.get(acronimo='PPP')
        ejecucion.save()
        # Log the start of the process
        guardarLogEjecucionProceso(ejecucion, TipoLogEnum.INFO.value, "Inicio Actualizacion Fideicomisos")
        process_fideicomisos()
        # Log the progress
        guardarLogEjecucionProceso(ejecucion, TipoLogEnum.INFO.value, "Inicio cargue encargos Temporales")
        process_encargo_temporal()
        # Log the progress
        guardarLogEjecucionProceso(ejecucion, TipoLogEnum.INFO.value, "Inicio cargue encargos")
        update_encargo_task()
        # Log the end of the process
        guardarLogEjecucionProceso(ejecucion, TipoLogEnum.INFO.value, "Fin de proceso")
        return {'status': 'success'}
    except Exception as e:
        # Log the error
        guardarLogEjecucionProceso(ejecucion, TipoLogEnum.ERROR.value, f"Error: {str(e)}")
        return {'status': 'error', 'message': str(e)}
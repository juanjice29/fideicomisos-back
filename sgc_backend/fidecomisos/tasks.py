from celery import shared_task
from .models import Fideicomiso, TipoDeDocumento
from django.core.cache import cache
from dateutil.relativedelta import relativedelta
import hashlib

@shared_task
def update_fideicomiso(rows):
    tipo_identificacion = TipoDeDocumento.objects.get(TipoDocumento='NJ')
    hasher = hashlib.sha256()
    hasher.update(str(rows).encode('utf-8'))
    new_hash = hasher.hexdigest()
    old_hash = cache.get('fideicomiso_hash')
    if old_hash != new_hash:
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
        cache.set('fideicomiso_hash', new_hash)
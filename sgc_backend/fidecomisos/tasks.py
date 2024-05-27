from celery import shared_task
from .models import Fideicomiso, TipoDeDocumento
from django.core.cache import cache
from dateutil.relativedelta import relativedelta
import hashlib

@shared_task
def update_fideicomiso(rows):
    tipo_identificacion = TipoDeDocumento.objects.get(tipoDocumento='NJ')
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
                    'tipoIdentificacion': tipo_identificacion,
                    'nombre': row[4],
                    'fechaCreacion': row[2] if row[2] else None,
                    'fechaVencimiento': fecha_vencimiento,
                    'fechaProrroga': fecha_vencimiento + relativedelta(years=30) if fecha_vencimiento else None,
                    'estado': row[5]
                }
            )
        cache.set('fideicomiso_hash', new_hash)
        
@shared_task
def add(x, y):
    return x + y
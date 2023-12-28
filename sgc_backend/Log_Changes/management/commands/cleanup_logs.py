from django.utils import timezone
from datetime import timedelta
from your_app.models import Log_Cambios_Create, Log_Cambios_Update
from your_project.celery import app

@app.task
def cleanup_logs():
    cutoff_date = timezone.now() - timedelta(days=365)  # 365 days ago
    Log_Cambios_Create.objects.filter(Tiempo_Accion__lt=cutoff_date).delete()
    Log_Cambios_Update.objects.filter(Tiempo_Accion__lt=cutoff_date).delete()
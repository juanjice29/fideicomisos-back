from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery import shared_task, chain
from beneficiario_final.tasks import compare_with_db, generate_xml, replace_table
from celery.schedules import crontab
# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sgc_backend.settings')

app = Celery('sgc_backend')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()



app.conf.beat_schedule = {
    'cleanup-every-midnight': {
        'task': 'Log_Changes.tasks.cleanup_logs',
        'schedule': crontab(hour=0, minute=0),
    },
    'beneficiario-final-task-every-3-months': {
        'task': 'beneficiario_final.tasks.add',  # Replace with the name of your task
        'schedule': crontab(minute="*/1"),
        'args': (16, 16)
    },
    #Example of another task
    #'another-task-every-hour': {
    #    'task': 'my_app.tasks.another_task',
    #    'schedule': crontab(minute=0),
    #},
}
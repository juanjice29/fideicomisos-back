from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
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
    #Example of another task
    #'another-task-every-hour': {
    #    'task': 'my_app.tasks.another_task',
    #    'schedule': crontab(minute=0),
    #},
}
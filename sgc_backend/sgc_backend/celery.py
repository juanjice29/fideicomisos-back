from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
import django
# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sgc_backend.settings')

app = Celery('sgc_backend')
app.conf.broker_transport_options = {'confirm_publish': True, 'ack_emulation': True, 'visibility_timeout': 18000}  # 5 hours
app.conf.update(result_extended=True)
# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.conf.beat_max_loop_interval = 60 

app.conf.beat_schedule = {    
    #Example of another task
    #'another-task-every-hour': {
    #    'task': 'my_app.tasks.another_task',
    #    'schedule': crontab(minute=0),
    #},
}

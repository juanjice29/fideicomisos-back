from django.core.management.base import BaseCommand
from accounts.models import TaskSchedule
from importlib import import_module
from croniter import croniter
from datetime import datetime

class Command(BaseCommand):
    help = 'Runs scheduled tasks'

    def handle(self, *args, **options):
        now = datetime.now()
        schedules = TaskSchedule.objects.all()
        for schedule in schedules:
            cron = croniter(schedule.cron_string, now)
            next_run = cron.get_next(datetime)
            if now >= next_run:
                # If the task is due to run, import and call the task function
                module_name, task_name = schedule.task_name.rsplit('.', 1)
                module = import_module(module_name)
                task = getattr(module, task_name)
                task.delay()  # Use .delay() to run the task asynchronously
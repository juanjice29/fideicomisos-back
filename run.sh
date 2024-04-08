#Example of run configuration with celery
#!/bin/bash

# Start Django
gunicorn sgc_backend.wsgi:application --bind 0.0.0.0:8000 &

# Start Celery worker
celery -A sgc_backend worker --loglevel=info &

# Start Celery beat
celery -A sgc_backend beat --loglevel=info &

# Keep script running
wait
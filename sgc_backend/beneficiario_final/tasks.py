from celery import Celery
from celery import shared_task, chain
import logging
import pdb 
logger = logging.getLogger(__name__)
celery = Celery()
def progress_callback(current, total):
    print('Task progress: {}%'.format(current / total * 100))
# Task 1
@celery.task
def compare_with_db():
    # Query the database
    db_data = query_database()
    # Get data from RPBF_HISTORICO
    rpbf_data = get_rpbf_data()
    # Compare the data
    new_records = compare_data(db_data, rpbf_data)
    # Pass the new records to the next task and start it
    generate_xml.delay(new_records)
@celery.task
def generate_xml(new_records):
    # Generate XML from new records
    xml_data = generate_xml_from_records(new_records)
    # Pass the XML data to the next task and start it
    replace_table.delay(xml_data)
celery = Celery()
# Task 3
@celery.task
def replace_table(xml_data):
    # Replace RPBF_HISTORICO table with new data
    replace_rpbf_table(xml_data)
    
@shared_task
def run_tasks_in_order():
    task1 = compare_with_db.s()
    task2 = generate_xml.s()
    task3 = replace_table.s()

    # Chain the tasks
    chain(task1 | task2 | task3).apply_async()
    
@celery.task
def add(x, y):
    logger.info("hpta")
    return x + y

logger = logging.getLogger(__name__)

@shared_task
def create_role(total_roles):
    try:
        from accounts.models import Role
        for i in range(total_roles):
            Role.objects.create(name='sap')
        progress_callback(i+1, total_roles)
        logger.info("Role 'sap' created.")
        pdb.set_trace()
    except Exception as e:
        logger.error(f"Error creating role 'sap': {e}")
        pdb.set_trace()
@shared_task
def create_random_user_accounts(total):
    import string
    from django.contrib.auth.models import User
    from django.utils.crypto import get_random_string
    from celery import shared_task
    pdb.set_trace()
    for i in range(total):
        username = 'user_{}'.format(get_random_string(10, string.ascii_letters))
        email = '{}@example.com'.format(username)
        password = get_random_string(50)
        User.objects.create_user(username=username, email=email, password=password)
    return '{} random users created with success!'.format(total)
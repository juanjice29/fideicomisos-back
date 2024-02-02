from .models import RPBF_PERIODOS,RPBF_HISTORICO
from celery import Celery
from celery import shared_task, chain
import logging
from .utils import *
import pdb 
import pandas as pd
from django.http import JsonResponse

logger = logging.getLogger(__name__)
def progress_callback(current, total):
    logger.info('Task progress: {}%'.format(current / total * 100))

#Task 1 extract data. 
@shared_task 
def test_task():
    
    print("hola mundo")
    try:
        current_period=get_current_period()
        last_report_period= add_period(current_period,-3)        
        last_report_regs=RPBF_HISTORICO.objects.filter(PERIODO_REPORTADO=last_report_period) 
        df=pd.DataFrame.from_records(last_report_regs.values())
        nov_1=df[df["TIPO_NOVEDAD"]=="1"]
        nov_2=df[df["TIPO_NOVEDAD"]=="2"]
        nov_3=df[df["TIPO_NOVEDAD"]=="3"]
        print(nov_1)    
    except Exception as err:
        raise Exception("failed to cksjda:" +str(err))
    
    #nov_2=
    #nov_3=
    
# Task 1
@shared_task 
def compare_with_db():
    # Query the database
    db_data = query_database()
    # Get data from RPBF_HISTORICO
    rpbf_data = get_rpbf_data()
    # Compare the data
    new_records = compare_data(db_data, rpbf_data)
    # Pass the new records to the next task and start it
    generate_xml.delay(new_records)
@shared_task 
def generate_xml(new_records):
    # Generate XML from new records
    xml_data = generate_xml_from_records(new_records)
    # Pass the XML data to the next task and start it
    replace_table.delay(xml_data)
celery = Celery()
# Task 3
@shared_task 
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
    
@shared_task 
def add(x, y):
    logger.info("hpta")
    return x + y

logger = logging.getLogger(__name__)

@shared_task
def create_role(total_roles):
    logger.info("create_role task started")
    try:
        from accounts.models import Role
        for i in range(total_roles):
            Role.objects.create(name='sap')
            progress_callback(i+1, total_roles)
        logger.info("Role 'sap' created.")
        
    except Exception as e:
        logger.error(f"Error creating role 'sap': {e}")   
    logger.info("create_role task finished")
       
@shared_task
def create_random_user_accounts(total):
    import string
    from django.contrib.auth.models import User
    from django.utils.crypto import get_random_string
    from celery import shared_task
  
    for i in range(total):
        username = 'user_{}'.format(get_random_string(10, string.ascii_letters))
        email = '{}@example.com'.format(username)
        password = get_random_string(50)
        User.objects.create_user(username=username, email=email, password=password)
    return '{} random users created with success!'.format(total)
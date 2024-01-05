from celery import Celery
from celery import shared_task, chain
celery = Celery()
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
# Register this blueprint by adding the following line of code 
# to your entry point file.  
# app.register_functions(temp) 
# 
# Please refer to https://aka.ms/azure-functions-python-blueprints


import azure.functions as func
import logging

temp = func.Blueprint()


@temp.queue_trigger(arg_name="azqueue", queue_name="processing-queue",
                               connection="MyBlobConnectionString") 
def queue_trigger_temp(azqueue: func.QueueMessage):
    logging.info('Python Queue trigger processed a message: %s',
                azqueue.get_body().decode('utf-8'))

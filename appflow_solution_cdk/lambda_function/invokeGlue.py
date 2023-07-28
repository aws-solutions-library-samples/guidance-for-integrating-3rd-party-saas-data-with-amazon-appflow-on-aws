import json
import boto3
import os
glue_client = boto3.client('glue')
def lambda_handler (event, context):
    print(event)
    response = glue_client.start_job_run(
        JobName = os.environ['glue_job_name']
    )
    return {
        'statusCode': 200,
        'body': response
    }

import json
import boto3
import logging
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')

def transformar_datos(json_data):
    transformed_data = {}
    for key, value in json_data.items():
        if 'S' in value:
            transformed_data[key] = value['S']
        elif 'N' in value:
            transformed_data[key] = int(value['N'])
    return transformed_data

def lambda_handler(event, context):
    for record in event['Records']:
        try:
            sqs_body = json.loads(record['body'])
            
            # Logic for when SQS message comes from DynamoDB Stream
            if 'dynamodb' in sqs_body:
                dynamodb_data = sqs_body['dynamodb']
                new_image = dynamodb_data['NewImage']
                transformed_data = transformar_datos(new_image)
                
                file_name = f"libro_{transformed_data['id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
                
                # S3 Bucket Name - CHANGE THIS IN EXAM
                BUCKET_NAME = 'mi-bucket-libros-2024'
                
                s3.put_object(
                    Bucket=BUCKET_NAME,
                    Key=file_name,
                    Body=json.dumps(transformed_data),
                    ContentType='application/json'
                )
                logger.info(f"File saved to S3: {file_name}")

        except Exception as e:
            logger.error(f"Error processing message: {e}")
        
    return {
        'statusCode': 200,
        'body': json.dumps('Data processed successfully')
    }

import json
import boto3
from datetime import datetime
from uuid import uuid4

sns_client = boto3.client('sns')
dynamodb = boto3.resource('dynamodb')

# CHANGE THIS ARN IN THE EXAM
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:123456789012:TemaEbook'
DDB_TABLE_NAME = 'ContactMessages'
table = dynamodb.Table(DDB_TABLE_NAME)

def lambda_handler(event, context):
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Content-Type': 'application/json'
    }

    # CORS Preflight
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }

    try:
        body = json.loads(event.get('body', '{}'))

        name = body.get('name', '').strip()
        email = body.get('email', '').strip()
        phone = body.get('phone', '').strip()
        message = body.get('message', '').strip()

        if not name or not email:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Fields name and email are required'})
            }

        timestamp = datetime.utcnow().isoformat()

        sns_message = {
            'name': name,
            'email': email,
            'phone': phone if phone else 'N/A',
            'message': message if message else 'Ebook download request',
            'timestamp': timestamp
        }

        # === 1) Save to DynamoDB ===
        item = {
            'id': str(uuid4()), # PK
            'name': sns_message['name'],
            'email': sns_message['email'],
            'phone': sns_message['phone'],
            'message': sns_message['message'],
            'timestamp': sns_message['timestamp']
        }

        table.put_item(Item=item)

        # === 2) Publish to SNS ===
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=f'New Ebook Request - {name}',
            Message=json.dumps(sns_message, indent=2, ensure_ascii=False)
        )

        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'success': True,
                'message': 'Request sent successfully'
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Error processing request',
                'details': str(e)
            })
        }

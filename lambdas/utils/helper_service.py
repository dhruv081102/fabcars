import os
import boto3
import json
import uuid
import requests
from datetime import datetime
from time import sleep
import logging
import random
from bson import ObjectId
SQS = boto3.client('sqs', region_name='us-east-1')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def aggregate_messages_by_mobile_number():
    pass


def retry_with_jitter(retries=3, jitter_range=(1, 3)):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.RequestException as e:
                    error_message = str(e)
                    logger.error(f'{datetime.now()} - Attempt {attempt + 1} - {error_message}')
                    logger.error(f'Error: {error_message}')
                    
                    if attempt < retries - 1:
                        sleep_time = random.uniform(*jitter_range)
                        logger.debug(f'Retrying in {sleep_time:.2f} seconds...')
                        sleep(sleep_time)
                    else:
                        raise e
                except json.JSONDecodeError as e:
                    error_message = f'Failed to parse JSON response: {str(e)}'
                    logger.error(f'{datetime.now()} - Attempt {attempt + 1} - {error_message}')
                    logger.error(f'Error: {error_message}')
                    if attempt == retries - 1:
                        raise e
                except Exception as e:
                    error_message = f'Unexpected error: {str(e)}'
                    logger.error(f'{datetime.now()} - Attempt {attempt + 1} - {error_message}')
                    logger.debug(f'Error: {error_message}')
                    if attempt == retries - 1:
                        raise e
            return None
        return wrapper
    return decorator


_cached_queue_urls = {}

def get_queue_url(queue_name):
    if queue_name in _cached_queue_urls:
        return _cached_queue_urls[queue_name]

    try:
        response = SQS.get_queue_url(QueueName=queue_name)
        _cached_queue_urls[queue_name] = response['QueueUrl']
        return _cached_queue_urls[queue_name]
    except Exception as e:
        logger.error(f"Error retrieving queue URL for {queue_name}: {e}")
        raise e


def send_message_to_queue(queue_url, message, MessageDeduplicationId=None, MessageGroupId='default'):
    return SQS.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(message),
        MessageDeduplicationId=MessageDeduplicationId or str(uuid.uuid4()),
        MessageGroupId=MessageGroupId
    )


META_ACCESS_TOKEN = os.environ.get("META_ACCESS_TOKEN")

def divide_response_into_chunks(response_text: str):
    max_chunk_size = 1000
    chunks = []
    remaining_text = response_text

    while len(remaining_text) > 0:

        if len(response_text) <= max_chunk_size:
            chunks.append(remaining_text)
            break
    
        chunk = remaining_text[:max_chunk_size]
        last_new_line_index = chunk.rfind('\n\n')

        if last_new_line_index == -1:
            chunk = remaining_text[:max_chunk_size]
            remaining_text = remaining_text[max_chunk_size:]
        else:
            chunk = remaining_text[:last_new_line_index + 2]
            remaining_text = remaining_text[last_new_line_index + 2:]

        chunks.append(chunk)
    
    return chunks

@retry_with_jitter(retries=2, jitter_range=(2, 5))
def send_meta_text_message(recipient_phone_number:str, message_body:str):
    """
       This function sends a whatsapp message using META WHATSAPP API.

       Args:
           recipient_phone_number (str): The recepient's full phone number example '9198xxxxxx87' including the country code at the beginning.
           message_body (str): The message to be sent to the user.

       Returns:
           dict: A dictionary that provides success status and message with a timestamp.
       """

    url = 'https://graph.facebook.com/v20.0/334150016449900/messages'
    headers = {
        'Authorization': f'Bearer {META_ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_phone_number,
        "type": "text",
        "text": {
            "body": message_body
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    print(response.json())

    if response.status_code == 200:
        print("Message sent successfully.")
        return response.json()
    else:
        print(f"Failed to send message. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return None


def build_response(status_code, message, data=None, error_code=None, additional_data=None):
    body = {
        'status': 'success' if status_code >=200 and status_code <= 299  else 'error',
        'message': message,
    }

    if data is not None:
        body['data'] = convert_objectid(data)

    if error_code:
        body['error_code'] = error_code

    if additional_data is not None:
        body['additional_data'] = additional_data

    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(body)
    }


def convert_objectid(data):
    if isinstance(data, list):
        return [convert_objectid(item) for item in data]
    elif isinstance(data, dict):
        return {key: convert_objectid(value) for key, value in data.items()}
    elif isinstance(data, ObjectId):
        return str(data)
    else:
        return data

if __name__ == '__main__':
    send_meta_text_message("9833359485", "Hello there!")

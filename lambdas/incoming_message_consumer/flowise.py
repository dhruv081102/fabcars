import requests
import json
import os
import logging

#from utils.helper_service import retry_with_jitter
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


#@retry_with_jitter(retries=3, jitter_range=(4, 10))
def send_flowise_message(message, phone_number, chat_flow_id=None, chat_id=None, session_id=None):
    base_url = os.environ.get("FLOWISE_BASE_URL", 'http://18.214.47.225')
    chat_flow_app_id = chat_flow_id or os.environ.get("FLOWISE_CHAT_APP_ID")

    flowise_url = f'{base_url}/api/v1/prediction/{chat_flow_app_id}'
    print(flowise_url)
    payload = {
        'question': f'phone_number: {phone_number} \n{message}'  # TODO: Why send phone number ?
    }

    if chat_id:
        payload['chatId'] = chat_id
    if session_id:
        payload['sessionId'] = session_id

    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(flowise_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()

        res = response.json()
        logging.info(f'Flowise Response: {res}')

        print({
            'text': res.get('text'),
            'question': res.get('question'),
            'chatId': res.get('chatId'),
            'chatMessageId': res.get('chatMessageId'),
            'sessionId': res.get('sessionId'),
            'memoryType': res.get('memoryType'),
            'chat_flow_id': chat_flow_app_id
        })
        # TODO: Handle expiry of session
        return res

    except requests.exceptions.RequestException as e:
        error_message = str(e)
        logging.error(f'{datetime.now()} - Call AI - {error_message}')
        print(f'Error: {error_message}')
        raise e

    except json.JSONDecodeError as e:
        error_message = f'Failed to parse JSON response: {str(e)}'
        logging.error(f'{datetime.now()} - Call AI - {error_message}')
        print(f'Error: {error_message}')
        raise e

    except Exception as e:
        error_message = f'Unexpected error: {str(e)}'
        logging.error(f'{datetime.now()} - Call AI - {error_message}')
        print(f'Error: {error_message}')
        raise e

if __name__ == "__main__":
    response = send_flowise_message(
        message="Hello, how can I help you?",
        phone_number="1234567890"
    )
    print(response)

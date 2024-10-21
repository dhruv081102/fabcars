import json
import os

# Set your verification token as an environment variable
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN', 'your_verification_token')

def handler(event, context):
    try:
        print(f'event_parsed: ', event)
        print(f'queryStringParameters: ',  event['queryStringParameters'])
        params =  event['queryStringParameters']
        print(f'params.get(hub.mode): ',  params.get('hub.mode'))
        print(f'params.get(hub.challenge): ',  params.get('hub.challenge'))
        # return {
        #         'statusCode': 200,
        #         'body': params['hub.challenge']
        #     }
        if params and params.get('hub.mode') == 'subscribe' and params.get('hub.verify_token') == VERIFY_TOKEN:
            # Return the challenge token if the verification token matches
            return {
                'statusCode': 200,
                'body': params['hub.challenge']
            }
        else:
            return {
                'statusCode': 403,
                'body': json.dumps({
                    'status': 'Verification token mismatch'
                })
            }

    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'status': 'Error handling the request',
                'error': str(e)
            })
        }

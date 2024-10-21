import logging
import json
from message_handlers import handle_meta_business_whatsapp_message
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def message_type_handler_mapping(message_type):
    message_type_mapping = {
        "whatsapp_business_account": handle_meta_business_whatsapp_message
    }
    return message_type_mapping.get(message_type)


def process_message(record):
    body = json.loads(record.get("body", "{}"))
    message_type = body.get("message_type")
    event_payload = body.get("event_payload")
    handler_fn = message_type_handler_mapping(message_type)
    if not handler_fn:
        logger.error(f"Handler not found for message_type: {message_type}")
    try:
        handler_fn(body)
        logger.log(event_payload)
    except Exception as e:
        logger.error(f"Handler failed for message_type: {message_type} with error: {e}")


def handler(event, context):
    # Incase you need to add failed message backs
    # input_queue_url = os.environ['INCOMING_INTERAKT_MESSAGE_WEBHOOK_QUEUE']
    print(f'event_parsed: ', event)
    for record in event['Records']:
        logger.info(f'Message body: {record["body"]}')
        process_message(record)


test_context = {}
test_event = {
    'Records': [
        {
            'messageId': '0b013d2f-b9d8-41bf-8f65-c947cf8e3a4a',
            'receiptHandle': 'AQEBkl7wmI5iPaAi+KwwlSwCxRuKGgBmjpzr1jYDGzuCVbMprlsNaBCCzhfvKXVWGU8XawRK3skYPoV34nR2fCbDnScwyXQQEzA2PZaZquMicigu5t6Q09RTZucgc04kqPEg56OJUKKSLNTHLClzfGEx72JV6Z4S8aJYAVmYDuY6Dpfh22Us9eCxloJ+jLoxnbHUpVybl9V6/9ZE5VqrWag+qXib5BmLt9E0e13gYovZqyJ4QczIkVzfYTLXWYudf85/99EmdsQTq3+zJQfQWNVyBsuTcKWHvRxheA0sYtz77z2m6t1igaEnMQCUU9L4vW1n',
            'body': '{"message_type": "meta_whats_app_api_incoming_webhook", "event_payload": {"object": "whatsapp_business_account", "entry": [{"id": "356983300825428", "changes": [{"value": {"messaging_product": "whatsapp", "metadata": {"display_phone_number": "917710016178", "phone_number_id": "334150016449900"}, "contacts": [{"profile": {"name": "Sneh Shah"}, "wa_id": "919870647356"}], "messages": [{"from": "919870647356", "id": "wamid.HBgMOTE5ODcwNjQ3MzU2FQIAEhgWM0VCMEQ0NzI0NkE5Njk4N0IwQjE4MgA=", "timestamp": "1729149683", "text": {"body": "if there is no job why should I do it?"}, "type": "text"}]}, "field": "messages"}]}]}}',
            'attributes': {
                'ApproximateReceiveCount': '1',
                'AWSTraceHeader': 'Root=1-6710baf4-714ce748028bcdea0714251a;Parent=78b5389f863590a8;Sampled=0;Lineage=1:1e679905:0',
                'SentTimestamp': '1729149684392',
                'SequenceNumber': '18889406392913903616',
                'MessageGroupId': 'default',
                'SenderId': 'AROA44QZRXXCT7ZMA6AGA:irm-service-v1-dev-incoming_meta_wa_webhook_api',
                'MessageDeduplicationId': 'a2f3c5b3-b25b-4a50-a9fb-a1d08bb20188',
                'ApproximateFirstReceiveTimestamp': '1729149684392'
            },
            'messageAttributes': {},
            'md5OfBody': '374f863dcf3743d1e095ea7cc3fbd925',
            'eventSource': 'aws:sqs',
            'eventSourceARN': 'arn:aws:sqs:us-east-1:885890596293:irm_incoming_meta_api_message_queue_v1.fifo',
            'awsRegion': 'us-east-1'
        }
    ]
}
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    # Simulate invoking the Lambda function handler with the test event and context
    handler(test_event, test_context)

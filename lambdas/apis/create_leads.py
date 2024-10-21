import sys
import os

# Add the lambdas directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from infra.mongodb_connection import get_collection
from utils.helper_service import build_response
from datetime import datetime
import json

# Your existing functions go here


def get_client_org_name():
    client_org_name = os.getenv('CLIENT_ORG_NAME')
    if not client_org_name:
        raise ValueError('Client organization name is required')
    return client_org_name

def get_database_and_collection():
    # Fetch database and collection name directly from mongodb_connection.py
    return get_collection()

def validate_payload(data):
    # required_fields = ['distributorId', 'company_type', 'claimType', 'phoneNumber', 'invoiceNumber', 'productDescription', 'issueDescription']
    required_fields = ['name', 'phone_number', 'email_id', 'paper_type', 'gsm', 'pe_coating', 'aluminum_foil', 'dimensions','quantity','application','custom_printing_branding','call_time','conversationSummary' ]
    if any(field not in data for field in required_fields):
        raise ValueError('Missing required fields')

def create_lead(leads_collection, data):
    data['created_at'] = datetime.now().isoformat()
    # Remove claim_number generation and directly include phone number
    data['_v'] = 1
    result = leads_collection.insert_one(data)
    return result.inserted_id  # Return only the lead_id

def handler(event, context):
    try:
        print(f'event_parsed: ', event)
        client_org_name = get_client_org_name()
        leads_collection = get_database_and_collection()

        # Ensure 'body' is provided in the event; if not, raise an error
        if not event.get('body'):
            raise ValueError('No data provided')

        data = json.loads(event['body'])
        validate_payload(data)

        lead_id = create_lead(leads_collection, data)
        return build_response(201, 'Lead created successfully', data={"lead_id": lead_id})

    except json.JSONDecodeError:
        return build_response(400, 'Invalid JSON payload', error_code='JSON_PARSE_ERROR')
    except ValueError as ve:
        return build_response(400, str(ve), error_code='VALIDATION_ERROR')
    except Exception as e:
        return build_response(500, 'An internal error occurred', error_code='INTERNAL_SERVER_ERROR', additional_data={'error_message': str(e)})


if __name__ == '__main__':
    handler({
        "resource": "/irm/lead",
        "path": "/kp_packaging/lead",
        "httpMethod": "POST",
        "headers": {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "CloudFront-Forwarded-Proto": "https",
            "CloudFront-Is-Desktop-Viewer": "True",
            "CloudFront-Is-Mobile-Viewer": "False",
            "CloudFront-Is-SmartTV-Viewer": "False",
            "CloudFront-Is-Tablet-Viewer": "False",
            "CloudFront-Viewer-ASN": "24560",
            "CloudFront-Viewer-Country": "IN",
            "Content-Type": "application/json",
            "Host": "qtw2ht3bpl.execute-api.us-east-1.amazonaws.com",
            "Postman-Token": "75d44021-07f7-4721-b65f-589bceb51534",
            "User-Agent": "PostmanRuntime/7.41.2",
            "Via": "1.1 147e8b4a67415ed6ed50ac5b9ae901ac.cloudfront.net (CloudFront)",
            "X-Amz-Cf-Id": "2Fy4fVzqgE5I-Ww8ODdzK-MnQpJtVEWy74XzmE-xeQhHYX9BnzvQxg==",
            "X-Amzn-Trace-Id": "Root=1-66d32770-260377195c0e090a2ac67613",
            "X-Forwarded-For": "110.226.178.95, 18.68.57.118",
            "X-Forwarded-Port": "443",
            "X-Forwarded-Proto": "https"
        },
        "multiValueHeaders": {
            "Accept": ["*/*"],
            "Accept-Encoding": ["gzip, deflate, br"],
            "CloudFront-Forwarded-Proto": ["https"],
            "CloudFront-Is-Desktop-Viewer": ["True"],
            "CloudFront-Is-Mobile-Viewer": ["False"],
            "CloudFront-Is-SmartTV-Viewer": ["False"],
            "CloudFront-Is-Tablet-Viewer": ["False"],
            "CloudFront-Viewer-ASN": ["24560"],
            "CloudFront-Viewer-Country": ["IN"],
            "Content-Type": ["application/json"],
            "Host": ["qtw2ht3bpl.execute-api.us-east-1.amazonaws.com"],
            "Postman-Token": ["75d44021-07f7-4721-b65f-589bceb51534"],
            "User-Agent": ["PostmanRuntime/7.41.2"],
            "Via": ["1.1 147e8b4a67415ed6ed50ac5b9ae901ac.cloudfront.net (CloudFront)"],
            "X-Amz-Cf-Id": ["2Fy4fVzqgE5I-Ww8ODdzK-MnQpJtVEWy74XzmE-xeQhHYX9BnzvQxg=="],
            "X-Amzn-Trace-Id": ["Root=1-66d32770-260377195c0e090a2ac67613"],
            "X-Forwarded-For": ["110.226.178.95, 18.68.57.118"],
            "X-Forwarded-Port": ["443"],
            "X-Forwarded-Proto": ["https"]
        },
        "queryStringParameters": None,
        "multiValueQueryStringParameters": None,
        "pathParameters": None,
        "stageVariables": None,
        "requestContext": {
            "resourceId": "x2lic3",
            "resourcePath": "/kp_packaging/lead",
            "httpMethod": "POST",
            "extendedRequestId": "dYMZsFaoIAMEIUQ=",
            "requestTime": "31/Aug/2024:14:23:44 +0000",
            "path": "/dev/kp_packaging/lead",
            "accountId": "885890596293",
            "protocol": "HTTP/1.1",
            "stage": "dev",
            "domainPrefix": "qtw2ht3bpl",
            "requestTimeEpoch": 1725114224940,
            "requestId": "448eaa28-3c8f-4291-b874-0cfc2a362b00",
            "identity": {
            "cognitoIdentityPoolId": None,
            "accountId": None,
            "cognitoIdentityId": None,
            "caller": None,
            "sourceIp": "110.226.178.95",
            "principalOrgId": None,
            "accessKey": None,
            "cognitoAuthenticationType": None,
            "cognitoAuthenticationProvider": None,
            "userArn": None,
            "userAgent": "PostmanRuntime/7.41.2",
            "user": None
            },
            "domainName": "qtw2ht3bpl.execute-api.us-east-1.amazonaws.com",
            "deploymentId": "gzkgtb",
            "apiId": "qtw2ht3bpl"
        },
        "body": json.dumps({
            "name": "gaurav",
            "phone_number": "985644575",
            "email_id": "sneh@gmail.com",
            "paper_type": "cupstock",
            "gsm": "200",
            "pe_coating": "100",
            "aluminum_foil": "10",
            "dimensions": "12x12",
            "quantity":"500",
            "application":"no",
            "custom_printing_branding":"no",
            "call_time":"tom 12 am",
            "conversationSummary":"123"

        }),
        "isBase64Encoded": False
    }, None)

# if __name__ == '__main__':
#     handler({
#         "resource": "/irm/lead",
#         "path": "/cello/lead",
#         "httpMethod": "POST",
#         "headers": {
#             "Content-Type": "application/json",
#         },
#         "body": json.dumps({
#             "name": "sneh",
#             "phone_number": "985644575",
#             "email_id": "sneh@gmail.com",
#             "paper_type": "cupstock",
#             "gsm": "200",
#             "pe_coating": "100",
#             "aluminum_foil": "10",
#             "dimensions": "12x12",
#             "quantity":"500",
#             "application":"no",
#             "custom_printing_branding":"no",
#             "call_time":"tom 12 am",
#             "conversationSummary":"123"

#         }),
#         "isBase64Encoded": False
#     }, None)

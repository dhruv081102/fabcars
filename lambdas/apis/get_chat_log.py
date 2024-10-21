import sys
import os

# Add the root directory of your project to PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import logging
import json
from lambdas.infra.mongodb_connection import get_collection
from lambdas.utils.helper_service import build_response  # Update this line to reference the full path
from pymongo import ASCENDING, DESCENDING
from dotenv import load_dotenv



# Load environment variables from .env file
load_dotenv()

# # Access environment variables
# db_uri = os.getenv('DATABASE_URI')

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_client_org_name():
    client_org_name = os.getenv('CLIENT_ORG_NAME')
    if not client_org_name:
        raise ValueError('Client organization name is required')
    logger.info(f'Client organization name retrieved: {client_org_name}')
    return str(client_org_name).lower()


def get_database_and_collection(client_org_name, collection_name):
    db_name = f'{client_org_name}_db'
    logger.info(f'Connecting to database: {db_name}, collection: {collection_name}')
    return get_collection(db_name, collection_name)


def build_query(filters):
    query = {}
    if '_id' in filters:
        query['_id'] = filters['_id']
    if 'created_at' in filters:
        query['created_at'] = filters['createdAt']
    if 'user_profile_name' in filters:
        query['event_payload.user_profile_name'] = {"$regex": filters['user_profile_name'], "$options": "i"}
    if 'phone_number' in filters:
        query['phone_number'] = {"$regex": filters['phone_number'], "$options": "i"}
    if 'question' in filters:
        query['question'] = {"$regex": filters['question'], "$options": "i"}
    if 'statuses' in filters:
        query['statuses'] = filters['statuses']
    if 'ai_response' in filters:
        query['ai_response'] = filters['ai_response']
    # Add more filters as needed
    logger.info(f'Query built: {query}')
    return query


def handler(event, context):
    try:
        logger.info('Handler invoked with event: %s', json.dumps(event))

        client_org_name = get_client_org_name()
        collection_name = f'{client_org_name}_chat_log'
        chat_session_logs_collection = get_database_and_collection(client_org_name, collection_name)

        # Extract filters from query string parameters
        filters = event.get('queryStringParameters', {}) or {}
        page_number = int(filters.pop('page', 1))
        limit = int(filters.pop('limit', 10))
        # sort_field = filters.pop('sort', '_id')
        # sort_order = ASCENDING if filters.pop('order', 'asc') == 'asc' else DESCENDING

        logger.info(f'Filters extracted: {filters}, page: {page_number}, limit: {limit}')

        match_query = build_query(filters)
        skip = (page_number - 1) * limit

        # Execute the query with pagination and sorting
        logger.info(f'Executing query with skip: {skip}, limit: {limit}')

        pipeline = [
            {
                "$facet": {
                    "pagination": [
                        {"$match": match_query},
                        {"$sort": {"_id": -1}},
                        {"$skip": (page_number - 1) * limit},
                        {"$limit": limit},
                        {
                            "$project": {
                                "_id": 1,
                                "created_at": 1,
                                "phone_number": 1,
                                "event_payload.user_profile_name": 1,
                                "ai_response.question": 1,
                                "statuses": 1,
                                "ai_response.text": 1
                            }
                        }
                    ],
                    "count": [
                        {"$match": match_query},
                        {"$count": "total"}
                    ],
                }
            }
        ]

        result = list(chat_session_logs_collection.aggregate(pipeline))

        # Count total documents that match the query
        leads = result[0]['pagination']
        total_count = result[0]['count'][0]['total'] if result[0]['count'] else 0
        total_pages = (total_count + limit - 1) // limit

        logger.info(f'Query executed successfully. Total leads found: {total_count}, Total pages: {total_pages}')
        response_data = {
            "data": {
                "chats": leads,
                "pagination": {
                    'page_size': limit,
                    "current_page": page_number,
                    "total_pages": total_pages,
                    "total_items": total_count
                }
            }
        }

        return build_response(200, 'Leads retrieved successfully', data=response_data)

    except ValueError as ve:
        logger.error(f'Validation error: {ve}')
        return build_response(400, str(ve), error_code='VALIDATION_ERROR')
    except Exception as e:
        logger.exception('An internal error occurred')
        return build_response(500, 'An internal error occurred', error_code='INTERNAL_SERVER_ERROR',
                              additional_data={'error_message': str(e)})

if __name__ == '__main__':
    event = {
        "queryStringParameters": {
            "page": "1",
            "limit": "10",
            "phone_number": "9876543210"
        }
    }
    context = None
    response = handler(event, context)
    print(json.dumps(response, indent=4))




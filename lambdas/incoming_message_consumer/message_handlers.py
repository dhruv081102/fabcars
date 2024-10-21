import os
import json
import logging
from datetime import datetime

from incoming_message_consumer.flowise import send_flowise_message
from utils.helper_service import send_message_to_queue
from infra.mongodb_connection import get_collection
from incoming_message_consumer.distributor_checker import search_phone_number

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

response_queue_url = os.environ['META_WA_RESPONSE_QUEUE']

def event_payload_builder(entry):
    try:
        sender_id = entry.get("id")
        changes_entity = entry.get("changes")[0]
        contacts_entity = changes_entity.get("value").get("contacts")[0]
        messages_entity = changes_entity.get("value").get("messages")[0]

        messaging_product = changes_entity.get("value").get("messaging_product")
        metadata = changes_entity.get("value").get("metadata")

        user_profile_name = contacts_entity.get("profile").get("name")
        user_wa_id = contacts_entity.get("wa_id")





        user_phone_number = messages_entity.get("from")


        user_message_id = messages_entity.get("id")
        timestamp = messages_entity.get("timestamp")
        message_type = messages_entity.get("type")
        message_body = messages_entity.get(message_type)

        event_payload = {
            "sender_id": sender_id,
            "messaging_product": messaging_product,
            "metadata": metadata,
            "user_profile_name": user_profile_name,
            "user_wa_id": user_wa_id,
            "user_phone_number": user_phone_number,
            "user_message_id": user_message_id,
            "timestamp": timestamp,
            "message_type": message_type,
            "message_body": message_body
        }
        logger.debug(f"Event payload built: {event_payload}")
        return event_payload
    except Exception as e:
        logger.error(f"Error building event payload: {e}")
        raise


def handle_meta_api_text(event_payload, chat_session_log_collection, chat_log_collection, chat_log_id):
    try:
        user_message = event_payload.get("message_body").get("body")
        phone_number = event_payload.get("user_phone_number")
        # Call search_phone_number with the raw phone number
        blacklist_org = get_client_org_name()
        blacklist_number = get_database_and_collection(blacklist_org)
        blacklist_number_search =  blacklist_number.find_one({"phone_number": phone_number })
        if blacklist_number_search:
            logger.info(f"Phone number found: {blacklist_number_search}")
        else:
            search_result = search_phone_number(phone_number)
            if search_result.get('success') and search_result.get('row'):
                chat_flow_id = os.environ.get("FLOWISE_CHAT_APP_ID") # take chat flow id from assigned number
                session_entity = chat_session_log_collection.find_one({
                    "phone_number": phone_number,
                    "chat_flow_id": chat_flow_id
                })
                chat_id = session_entity.get("chat_id") if session_entity else None
                session_id = session_entity.get("session_id") if session_entity else None
                if not session_entity:
                    distributor_id = search_result[0]
                    distributor_agency = search_result[1]
                    email_address = search_result[3]


                    distributor_info = (
                        f"\nDistributor Id: {distributor_id}\n"
                        f"Distributor Agency: {distributor_agency}\n"
                        f"Email Address: {email_address}"
                    )
                    user_message += distributor_info

                flowise_response = send_flowise_message(
                    message=user_message,
                    phone_number=phone_number,
                    chat_flow_id=chat_flow_id,
                    chat_id=chat_id,
                    session_id=session_id
                )

                if not session_entity:
                    chat_session_log_collection.insert_one({
                        "phone_number": phone_number,
                        "chat_flow_id": chat_flow_id,
                        "chat_id": flowise_response.get("chatId"),
                        "session_id": flowise_response.get("sessionId"),
                    })

                flowise_text_response = flowise_response.get("text")

                filter_query = {"_id": chat_log_id}
                update = {
                    '$push': {
                        "statuses": {
                            "status": "AI_RESPONSE_GENERATED",
                            "timestamp": datetime.now().isoformat()
                        }},
                    '$set': {"ai_response": flowise_response}
                }
                chat_log_collection.update_one(filter_query, update)
            else:

                flowise_test_response = 'This number is not registered'
                chat_log_id = 'Not generated as user is Not Registered'
                add_to_blacklist(phone_number, blacklist_number)
                logger.info(flowise_test_response)
            sqs_response = send_message_to_queue(response_queue_url, {
                "phone_number": phone_number,
                "message": flowise_text_response,
                "created_at": datetime.now().isoformat(),
                "chat_log_id": str(chat_log_id),
                "response_service_name": "META_WHATSAPP_API",
                "response_type": "TEXT"
            })
            logger.info(f'SQS response sent: {sqs_response}')
    except Exception as e:
        logger.error(f"Error handling meta API text: {e}")
        raise


def handle_meta_business_whatsapp_message(whatsapp_webhook_event):
    chat_log_id = None
    try:
        entry = whatsapp_webhook_event.get("entry", [])[0]
        event_payload = event_payload_builder(entry)
        logger.debug(f"Received event payload: {event_payload}")
        message_type = event_payload.get("message_type")
        message_handler_fn = get_meta_message_handler(message_type)

        client_org_name = str(os.environ['CLIENT_ORG_NAME']).lower()
        db_name = f'{client_org_name}_db'
        chat_session_log_collection_name = f'{client_org_name}_chat_session_log'
        chat_log_collection_name = f'{client_org_name}_chat_log'
        chat_session_log_collection = get_collection(db_name, chat_session_log_collection_name)
        chat_log_collection = get_collection(db_name, chat_log_collection_name)
            
        created_at = datetime.now().isoformat()

        mongo_db_result = chat_log_collection.insert_one({
            "created_at": created_at,
            "external_message_id": event_payload.get("user_message_id"),
            "webhook_event": whatsapp_webhook_event,
            "event_payload": event_payload,
            "message_type": message_type,
            "phone_number": event_payload.get("user_phone_number"),
            "statuses": [{
                "status": "MESSAGE_RECEIVED",
                "timestamp": created_at
            }]
        })
        chat_log_id = mongo_db_result.inserted_id
        logger.info(f"Chat log inserted with ID: {chat_log_id}")

        if message_handler_fn:
            message_handler_fn(event_payload, chat_session_log_collection, chat_log_collection, chat_log_id)
        else:
            logger.warning(f"No handler found for message type: {message_type}")

    except Exception as error:
        logger.error(f"Error processing WhatsApp message: {error}")
        if chat_log_id:
            filter_query = {"_id": chat_log_id}
            update = {
                '$push': {"statuses": {
                    "status": "FAILED_TO_GENERATE_AI_RESPONSE",
                    "timestamp": datetime.now().isoformat()
                }}
            }
            chat_log_collection.update_one(filter_query, update)


def get_meta_message_handler(message_type):
    message_handler_map = {
        "text": handle_meta_api_text,
        "reaction": handle_meta_api_reaction,
        "image": handle_meta_api_image,
        "audio": handle_meta_api_audio,
        "document": handle_meta_api_document,
        "location": handle_meta_api_location,
        "sticker": handle_meta_api_sticker,
        "unknown": handle_meta_api_unknown_message
    }
    return message_handler_map.get(message_type, None)


def handle_meta_api_image(event_payload, chat_log_collection, chat_log_id):
    try:
        image = event_payload.get("message_body").get("image")
        image_url = image.get("url")
        image_caption = image.get("caption")
        created_at = datetime.now().isoformat()
        
        filter_query = {"_id": chat_log_id}
        update = {
            '$push': {
                "statuses": {
                    "status": "IMAGE_RECEIVED",
                    "timestamp": created_at
                }},
            '$set': {"image_url": image_url, "image_caption": image_caption}
        }
        chat_log_collection.update_one(filter_query, update)
        
        logger.info(f"Image received and logged with ID: {chat_log_id}")
    except Exception as e:
        logger.error(f"Error handling image: {e}")

def handle_meta_api_audio(event_payload, chat_log_collection, chat_log_id):
    try:
        audio = event_payload.get("message_body").get("audio")
        audio_url = audio.get("url")
        created_at = datetime.now().isoformat()
        
        filter_query = {"_id": chat_log_id}
        update = {
            '$push': {
                "statuses": {
                    "status": "AUDIO_RECEIVED",
                    "timestamp": created_at
                }},
            '$set': {"audio_url": audio_url}
        }
        chat_log_collection.update_one(filter_query, update)
        
        logger.info(f"Audio received and logged with ID: {chat_log_id}")
    except Exception as e:
        logger.error(f"Error handling audio: {e}")

def handle_meta_api_document(event_payload, chat_log_collection, chat_log_id):
    try:
        document = event_payload.get("message_body").get("document")
        document_url = document.get("url")
        document_filename = document.get("filename")
        created_at = datetime.now().isoformat()
        
        filter_query = {"_id": chat_log_id}
        update = {
            '$push': {
                "statuses": {
                    "status": "DOCUMENT_RECEIVED",
                    "timestamp": created_at
                }},
            '$set': {"document_url": document_url, "document_filename": document_filename}
        }
        chat_log_collection.update_one(filter_query, update)
        
        logger.info(f"Document received and logged with ID: {chat_log_id}")
    except Exception as e:
        logger.error(f"Error handling document: {e}")

def handle_meta_api_location(event_payload, chat_log_collection, chat_log_id):
    try:
        location = event_payload.get("message_body").get("location")
        latitude = location.get("latitude")
        longitude = location.get("longitude")
        name = location.get("name")
        address = location.get("address")
        created_at = datetime.now().isoformat()
        
        filter_query = {"_id": chat_log_id}
        update = {
            '$push': {
                "statuses": {
                    "status": "LOCATION_RECEIVED",
                    "timestamp": created_at
                }},
            '$set': {"latitude": latitude, "longitude": longitude, "name": name, "address": address}
        }
        chat_log_collection.update_one(filter_query, update)
        
        logger.info(f"Location received and logged with ID: {chat_log_id}")
    except Exception as e:
        logger.error(f"Error handling location: {e}")

def handle_meta_api_sticker(event_payload, chat_log_collection, chat_log_id):
    try:
        sticker = event_payload.get("message_body").get("sticker")
        sticker_url = sticker.get("url")
        created_at = datetime.now().isoformat()
        
        filter_query = {"_id": chat_log_id}
        update = {
            '$push': {
                "statuses": {
                    "status": "STICKER_RECEIVED",
                    "timestamp": created_at
                }},
            '$set': {"sticker_url": sticker_url}
        }
        chat_log_collection.update_one(filter_query, update)
        
        logger.info(f"Sticker received and logged with ID: {chat_log_id}")
    except Exception as e:
        logger.error(f"Error handling sticker: {e}")

def handle_meta_api_reaction(event_payload, chat_log_collection, chat_log_id):
    try:
        reaction = event_payload.get("message_body").get("reaction")
        emoji = reaction.get("emoji")
        reacted_message_id = reaction.get("message_id")
        created_at = datetime.now().isoformat()
        
        filter_query = {"_id": chat_log_id}
        update = {
            '$push': {
                "statuses": {
                    "status": "REACTION_RECEIVED",
                    "timestamp": created_at
                }},
            '$set': {"reaction_emoji": emoji, "reacted_message_id": reacted_message_id}
        }
        chat_log_collection.update_one(filter_query, update)
        
        logger.info(f"Reaction received and logged with ID: {chat_log_id}")
    except Exception as e:
        logger.error(f"Error handling reaction: {e}")


def handle_meta_api_unknown_message(event_payload, chat_log_collection, chat_log_id):
    try:
        created_at = datetime.now().isoformat()

        filter_query = {"_id": chat_log_id}
        update = {
            '$push': {
                "statuses": {
                    "status": "UNKNOWN_MESSAGE_RECEIVED",
                    "timestamp": created_at
                }},
            '$set': {"unknown_message_payload": event_payload}
        }
        chat_log_collection.update_one(filter_query, update)
        
        logger.warning(f"Unknown message type received and logged with ID: {chat_log_id}")
    except Exception as e:
        logger.error(f"Error handling unknown message type: {e}")

def get_client_org_name():
    client_org_name = os.getenv('CLIENT_ORG_NAME')
    if not client_org_name:
        raise ValueError('Client organization name is required')
    return client_org_name


def get_database_and_collection(client_org_name):
    db_name = f'{client_org_name}_db'
    collection_name = f'{client_org_name}_blacklist'
    return get_collection(db_name, collection_name)


def add_to_blacklist(phone_number, blacklist):
    try:

        record = {
            "phone_number": phone_number,
            "created_at": datetime.now().isoformat()
        }
        blacklist.insert_one(record)

        logger.info(f"Phone number {phone_number} added to blacklist successfully.")

    except Exception as e:
        logger.error(f"Error inserting record for phone number {phone_number}: {e}")

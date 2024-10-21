import sys
import os

# Add the lambdas directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.helper_service import divide_response_into_chunks, send_meta_text_message
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_whatsapp_text_message( response_service_name:str ,phone_number: str, message: str):
    message_chunks = divide_response_into_chunks(message)

    final_response = []

    for  chunk_number, message_chunk in enumerate(message_chunks, start=1):
        try:
            if response_service_name == "META_WHATSAPP_API":
                whatsapp_response = send_meta_text_message(phone_number, message_chunk)
                if (whatsapp_response and whatsapp_response.get("messages")):
                    logger.debug("Whatsapp Sent Successfully")
                    final_response.append({
                        "chunk_number": chunk_number,
                        "text": message_chunk,
                        "status": "SUCCESS",
                        "message_id": whatsapp_response.get("messages")[0].get("id")
                    })

        except Exception as error:
            logger.debug(f"Failed to send whatsapp {error}")
            final_response.append({
                    "chunk_number": chunk_number,
                    "text": message_chunk,
                    "status": "FAILED",
                    "message": str(error)
                })
    logger.error(final_response, "Final response")
    return final_response


# Example usage:
access_token = ''
recipient_id = '919833359485'
message_body = 'Hey There D here!'

if __name__ == '__main__':
    send_whatsapp_text_message("META_WHATSAPP_API",recipient_id, message_body)

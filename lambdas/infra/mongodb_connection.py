import pymongo
import os
import time
import logging
import random
from dotenv import load_dotenv  # Importing to load environment variables

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

mongo_client = None
collection_map = dict()

def _create_connection():
    try:
        global mongo_client
        logger.info("MongoDB Creating New Connection.")
        host = os.environ.get("MONGO_DB_HOST")
        user = os.environ.get("MONGO_DB_USERNAME")
        password = os.environ.get("MONGO_DB_PASSWORD")
        print(host)
        print(user)
        print(password)

        # Constructing the MongoDB connection string
        mongo_client = pymongo.MongoClient(f"mongodb+srv://{user}:{password}@{host}/?retryWrites=true&w=majority&tls=true&tlsAllowInvalidCertificates=true")
        return mongo_client
    except Exception as e:
        logger.critical(f"Error in creating Mongo DB connection - {e}")
        raise e
        
def _connect(minimum_retry_attempts=3):
    global mongo_client
    try:
        if not mongo_client:
            mongo_client = _create_connection()
        mongo_client.admin.command('ping')
        return mongo_client
    except Exception as e:
        logger.critical(f"MongoDB connection failed, retries left: {minimum_retry_attempts}")
        if minimum_retry_attempts > 0:
            jitter = 2 + random.uniform(1, 5)
            logger.info(f"MongoDB Connection retrying with jitter: {jitter}")
            time.sleep(jitter)
            mongo_client = None
            _connect(minimum_retry_attempts - 1)
        else:
            raise e

def get_mongo_client():
    try:
        global mongo_client
        if mongo_client:
            try:
                mongo_client.admin.command('ping')
            except Exception as e:
                logger.error(f'Error in get_mongo_client: {e}')
                mongo_client = _connect()
            return mongo_client
        mongo_client = _connect()
        return mongo_client
    except Exception as e:
        logger.critical(f'Error in get_mongo_client: {e}')
        raise e

# Modify this function to accept parameters for the database and collection names
def get_collection(db_name, collection_name):
    try:
        global collection_map
        global mongo_client

        # Check if the collection is already cached
        collection = collection_map.get(db_name, {}).get(collection_name, None)
        if collection is not None:
            return collection

        mongo_client = _connect()

        # Use the provided database and collection names
        db = mongo_client[db_name]
        collection = db[collection_name]
        
        # Update the collection_map
        if db_name not in collection_map:
            collection_map[db_name] = dict()
        collection_map[db_name][collection_name] = collection
        
        return collection
    except Exception as e:
        logger.critical(f'Error in get_collection: {str(e)}')
        raise e

# Example usage
if __name__ == '__main__':
    try:
        # Pass specific db_name and collection_name when calling the function
        collection = get_collection("my_database", "my_collection")
        print(collection)
        print("Successfully connected to the collection.")
    except Exception as e:
        print(f"Failed to connect: {str(e)}")


        
# def get_collection():
#     try:
#         global collection_map
#         global mongo_client

#         # Get the organization name from environment variable
#         client_org_name = os.getenv('CLIENT_ORG_NAME')
#         db_name = f"{client_org_name.lower()}_db"
#         collection_name = f"{client_org_name.lower()}_leads"
#         print(client_org_name)
#         print(db_name)
#         print(collection_name)

#         # Check if the collection is already cached
#         collection = collection_map.get(db_name, {}).get(collection_name, None)
#         if collection is not None:
#             return collection

#         mongo_client = _connect()

#         # Use the provided database and collection names
#         db = mongo_client[db_name]
#         collection = db[collection_name]
        
#         # Update the collection_map
#         if db_name not in collection_map:
#             collection_map[db_name] = dict()
#         collection_map[db_name][collection_name] = collection
        
#         return collection
#     except Exception as e:
#         logger.critical(f'Error in get_collection: {str(e)}')
#         raise e

# # Specify your database and collection when calling get_collection
# if __name__ == '__main__':
#     # Example usage
#     try:
#         collection = get_collection()
#         print(collection)
#         print("Successfully connected to the collection.")
#     except Exception as e:
#         print(f"Failed to connect: {str(e)}")










# cello

# import pymongo
# import os
# import time
# import logging
# import random
# logger = logging.getLogger()
# logger.setLevel(logging.DEBUG)
# mongo_client = None
# collection_map = dict()


# def _create_connection():
#     try:
#         global mongo_client
#         logger.info("MongoDB Creating New Connection.")
#         host = os.environ.get("MONGO_DB_HOST")
#         user = os.environ.get("MONGO_DB_USERNAME")
#         password = os.environ.get("MONGO_DB_PASSWORD")
#         mongo_client = pymongo.MongoClient(f"mongodb+srv://{user.strip()}:{password.strip()}@{host.strip()}/?tls=true&tlsAllowInvalidCertificates=true")
#         return mongo_client
#     except Exception as e:
#         logger.critical(f"Error in creating Mongo DB connection - {e}")
#         raise e


# def _connect(minimum_retry_attempts=3):
#     global mongo_client
#     try:
#         if not mongo_client:
#             mongo_client = _create_connection()
#         mongo_client.admin.command('ping')
#         return mongo_client
#     except Exception as e:
#         logger.critical(f"MongoDB connection failed, retries left: {minimum_retry_attempts}")
#         if minimum_retry_attempts > 0:
#             jitter = 2 + random.uniform(1, 5)
#             logger.info(f"MongoDB Connection retrying with jitter: {jitter}")
#             time.sleep(jitter)
#             mongo_client = None
#             _connect(minimum_retry_attempts - 1)
#         else:
#             raise e


# def get_mongo_client():
#     try:
#         global mongo_client
#         if mongo_client:
#             try:
#                 mongo_client.admin.command('ping')
#             except Exception as e:
#                 logger.error(f'Error in get_mongo_client: {e}')
#                 mongo_client = _connect()
#             return mongo_client
#         mongo_client = _connect()
#         return mongo_client
#     except Exception as e:
#         logger.critical(f'Error in get_mongo_client: {e}')
#         raise e


# def get_collection(db_name, collection_name):
#     try:
#         global collection_map
#         global mongo_client
#         collection = collection_map.get(db_name, {}).get(collection_name, None)
#         if collection is not None:
#             return collection
#         mongo_client = _connect()
#         db = mongo_client[db_name]
#         collection = db[collection_name]
#         collection_map[db_name] = dict()
#         collection_map[db_name][collection_name] = collection
#         return collection
#     except Exception as e:
#         logger.critical(f'Error in get_collection: {str(e)}')
#         raise e





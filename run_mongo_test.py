from lambdas.infra.mongodb_connection import get_mongo_client, get_collection
from dotenv import load_dotenv
load_dotenv()

def main():
    try:
        client = get_mongo_client()
        print("MongoDB Client connected successfully!")

        db_name = "kp_packaging_db"  # Change as needed
        collection_name = "kp_packaging_leads"     # Change as needed

        collection = get_collection(db_name, collection_name)
        print(f"Collection '{collection_name}' accessed successfully in database '{db_name}'!")

        count = collection.count_documents({})
        print(f"Total documents in '{collection_name}': {count}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

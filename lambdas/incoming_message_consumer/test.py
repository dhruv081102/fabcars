import os
from flowise import send_flowise_message  # Assuming your function is in send_flowise_message_module.py

# Set up environment variables (only if not already set)
os.environ['FLOWISE_BASE_URL'] = 'https://demo.neuraleap.co'
os.environ['FLOWISE_CHAT_APP_ID'] = 'e1d1104a-05bd-4639-8097-55350cf1a36b'  # Replace with your actual app ID

def test_send_flowise_message():
    # Test data
    message = "Hello, this is a test message!"
    phone_number = "1234567890"
    chat_flow_id = "e1d1104a-05bd-4639-8097-55350cf1a36b"  # Replace with actual flow ID if available
    # chat_id = "chat_id_example"  # Optional: Replace with actual chat ID if available
    # session_id = "session_id_example"  # Optional: Replace with actual session ID if available

    try:
        # Call the function
        response = send_flowise_message(
            message=message,
            phone_number=phone_number,
            chat_flow_id=chat_flow_id,
            #chat_id=chat_id,
            #session_id=session_id
        )
        
        # Print the response
        print("Test Response:")
        print(response)

    except Exception as e:
        print(f"Error during test: {str(e)}")

# Run the test
if __name__ == "__main__":
    test_send_flowise_message()
